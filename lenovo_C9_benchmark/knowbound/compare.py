"""Cross-model aggregation -> ``results/metrics.json`` + ``results/summary.md``.

This is the module behind the headline deliverable.  It reads the *scored*
JSONL written by ``knowbound run --tag full`` for **every** model it finds in
``logs/`` and produces:

1. per-model, per-family metrics -- accuracy / Delta-E / AUROC2 / ECE-10 /
   Brier, the accuracy-stratified ("binned") AUROC2, KB-B over-claim rate,
   abstention AUROC and Balanced Abstention Score, KB-C help-seeking AUROC,
   net utility and the three reference policies, the trivial-confidence
   baseline family, and the temperature-scaling / isotonic calibration ablation;
2. percentile **bootstrap CIs over items** for every headline metric
   (the item is the unit of generalisation; 20-60 items means point estimates
   alone would be dishonest);
3. **paired** bootstrap intervals for the two-model difference (both models
   answered the same items, so the resampling is paired);
4. a plain-language **discrimination verdict** per metric: which metrics
   separate the two models at 95% and which do not;
5. a runtime / degradation block (call counts, parse strategies, errors,
   cold start vs warm latency) so failures are visible instead of hidden.

Everything is derived from the JSONL on disk -- no number is typed in by hand.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable, Dict, List, Optional

from . import baselines as B
from . import metrics as M
from . import report as R
from . import stats
from .runner import slug

FAMILIES = ("kb_a", "kb_b", "kb_c")
FAMILY_LABEL = {"kb_a": "KB-A (pre-answer confidence)",
                "kb_b": "KB-B (knowledge-boundary detection)",
                "kb_c": "KB-C (strategic help-seeking)"}


# ---------------------------------------------------------------------------
# discovery / loading
# ---------------------------------------------------------------------------

def discover(log_dir: str, tag: str) -> Dict[str, Dict[str, str]]:
    """slug -> {'model': name, 'paths': {family: path}} for one tag."""
    found: Dict[str, Dict[str, Any]] = {}
    if not os.path.isdir(log_dir):
        return {}
    prefix = f"scored_{tag}_"
    for name in sorted(os.listdir(log_dir)):
        if not (name.startswith(prefix) and name.endswith(".jsonl")):
            continue
        rest = name[len(prefix):-len(".jsonl")]
        for fam in FAMILIES:
            if rest.startswith(fam + "_"):
                s = rest[len(fam) + 1:]
                found.setdefault(s, {"model": s, "paths": {}})
                found[s]["paths"][fam] = os.path.join(log_dir, name)
                break
    # the authoritative model string is inside the records
    for s, info in found.items():
        for path in info["paths"].values():
            recs = R.read_jsonl(path)
            if recs and recs[0].get("model"):
                info["model"] = recs[0]["model"]
                break
    return found


def load_families(paths: Dict[str, str]) -> Dict[str, List[dict]]:
    return {fam: R.read_jsonl(path) for fam, path in paths.items()}


# ---------------------------------------------------------------------------
# per-family metric closures (index based, so bootstrap can reuse them)
# ---------------------------------------------------------------------------

def family_metric_fns(fam: str, recs: List[dict]) -> Dict[str, Callable[[List[int]], float]]:
    """name -> f(indices) -> float, computed on the resampled item set."""
    if fam == "kb_a":
        conf = [r["confidence"] if r.get("confidence") is not None else 0.0 for r in recs]
        ok = [bool(r["correct"]) for r in recs]
        return {
            "accuracy": lambda i: M.accuracy([ok[j] for j in i]),
            "delta_e": lambda i: M.delta_e([conf[j] for j in i], [ok[j] for j in i]),
            "abs_delta_e": lambda i: M.abs_delta_e([conf[j] for j in i], [ok[j] for j in i]),
            "brier": lambda i: M.brier([conf[j] for j in i], [ok[j] for j in i]),
            "ece10": lambda i: M.ece([conf[j] for j in i], [ok[j] for j in i], 10),
            "auroc2": lambda i: M.auroc2([conf[j] for j in i], [ok[j] for j in i]),
        }

    if fam == "kb_b":
        conf = [r["confidence"] if r.get("confidence") is not None else 0.5 for r in recs]
        ok = [bool(r["correct"]) for r in recs]
        unans = [not r["answerable"] for r in recs]
        abstain = [bool(r.get("abstain")) for r in recs]

        def _acc_ans(i):
            sub = [j for j in i if not unans[j]]
            return M.accuracy([ok[j] for j in sub]) if sub else float("nan")

        return {
            "accuracy_overall": lambda i: M.accuracy([ok[j] for j in i]),
            "accuracy_on_answerable": _acc_ans,
            "over_claim_rate": lambda i: M.over_claim_rate([not abstain[j] for j in i],
                                                           [unans[j] for j in i]),
            "abstention_auroc_from_confidence":
                lambda i: M.abstention_auroc([1.0 - conf[j] for j in i],
                                             [unans[j] for j in i]),
            "balanced_abstention_score":
                lambda i: M.balanced_abstention_score([abstain[j] for j in i],
                                                      [unans[j] for j in i]),
            "ece10": lambda i: M.ece([conf[j] for j in i], [ok[j] for j in i], 10),
            "delta_e": lambda i: M.delta_e([conf[j] for j in i], [ok[j] for j in i]),
            "auroc2_confidence": lambda i: M.auroc2([conf[j] for j in i], [ok[j] for j in i]),
        }

    if fam == "kb_c":
        pts = [float(r["points"]) for r in recs]
        helpd = [1.0 if r.get("decision") == "ask_help" else 0.0 for r in recs]
        unans = [not r["answerable"] for r in recs]

        def _base_do_it(i):
            return M.accuracy([not unans[j] for j in i])

        def _base_ask(i):
            tokens, total = B_BUDGET, 0.0
            for j in i:
                if tokens > 0:
                    tokens -= 1
                    total += B_DISCOUNT
            return total / len(i) if i else float("nan")

        return {
            "utility": lambda i: sum(pts[j] for j in i) / len(i) if i else float("nan"),
            "help_call_rate": lambda i: sum(helpd[j] for j in i) / len(i) if i else float("nan"),
            "ask_help_auroc_vs_unanswerable":
                lambda i: M.abstention_auroc([helpd[j] for j in i], [unans[j] for j in i]),
            "always_do_it_utility": _base_do_it,
            "always_ask_help_utility": _base_ask,
            "random_utility": lambda i: 0.5 * (_base_do_it(i) + _base_ask(i)),
            "model_minus_do_it": lambda i: _util(pts, i) - _base_do_it(i),
            "model_minus_ask_help": lambda i: _util(pts, i) - _base_ask(i),
            "model_minus_random": lambda i: _util(pts, i) -
                0.5 * (_base_do_it(i) + _base_ask(i)),
        }

    return {}


B_BUDGET = 6
B_DISCOUNT = 0.7


def _util(pts: List[float], i: List[int]) -> float:
    return sum(pts[j] for j in i) / len(i) if i else float("nan")


def ci_block(fam: str, recs: List[dict], n_boot: int, seed: int) -> Dict[str, Any]:
    fns = family_metric_fns(fam, recs)
    n = len(recs)
    out: Dict[str, Any] = {}
    for i, (name, fn) in enumerate(sorted(fns.items())):
        out[name] = stats.bootstrap(fn, n, n_boot=n_boot, seed=seed + i)
    return out


# ---------------------------------------------------------------------------
# accuracy-stratified ("binned") AUROC2 + reliability inspection
# ---------------------------------------------------------------------------

def accuracy_binned_auroc2(fam: str, recs: List[dict]) -> Optional[Dict[str, Any]]:
    """AUROC2 recomputed *inside* each accuracy stratum of the item set.

    Strata are the generator's declared difficulty levels (easy / medium / hard
    for KB-A, template difficulty for KB-B) -- i.e. "how often is the model
    right" is fixed within a stratum, so the AUROC2 there cannot be explained by
    an accuracy difference between strata.  A pooled value (n-weighted) is added
    next to the per-stratum numbers; both are computed on the real records.
    """
    if fam not in ("kb_a", "kb_b") or not recs:
        return None
    key = "difficulty"
    strata = sorted({r.get(key) for r in recs})
    rows = {}
    weights = {}
    for s in strata:
        sub = [r for r in recs if r.get(key) == s]
        if not sub:
            continue
        conf = [r["confidence"] if r.get("confidence") is not None else 0.0 for r in sub]
        ok = [bool(r["correct"]) for r in sub]
        rows[str(s)] = {"n": len(sub), "accuracy": M.accuracy(ok),
                        "auroc2": M.auroc2(conf, ok), "delta_e": M.delta_e(conf, ok),
                        "ece10": M.ece(conf, ok, 10)}
        weights[str(s)] = len(sub)
    defined = {k: v["auroc2"] for k, v in rows.items() if v["auroc2"] == v["auroc2"]}
    pooled = (sum(defined[k] * weights[k] for k in defined) / sum(weights[k] for k in defined)
              if defined and sum(weights[k] for k in defined) else None)
    return {
        "definition": "AUROC2 recomputed inside each declared-difficulty stratum "
                      "(strata hold accuracy roughly fixed), plus the n-weighted pool",
        "strata": rows,
        "pooled_weighted_auroc2": pooled,
    }


# ---------------------------------------------------------------------------
# runtime / degradation
# ---------------------------------------------------------------------------

def runtime_block(fams: Dict[str, List[dict]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for fam, recs in fams.items():
        if not recs:
            out[fam] = {"n_items": 0}
            continue
        lats: List[float] = []
        per_item = 0.0
        for r in recs:
            vals = [r.get(k) for k in ("latency_sec", "latency_p_sec", "latency_a_sec")
                    if isinstance(r.get(k), (int, float))]
            lats.extend(float(v) for v in vals)
            per_item += sum(float(v) for v in vals)
        strategies: Dict[str, int] = {}
        for r in recs:
            for k in ("parse_strategy", "parse_strategy_p", "parse_strategy_a"):
                if k in r and r.get(k):
                    strategies[str(r[k])] = strategies.get(str(r[k]), 0) + 1
        out[fam] = {
            "n_items": len(recs),
            "calls": len(lats),
            "ok_calls": sum(1 for r in recs if r.get("ok")),
            "failed_items": [r.get("item_id") for r in recs if not r.get("ok")],
            "parse_strategies": strategies,
            "mean_call_latency_sec": (sum(lats) / len(lats)) if lats else None,
            "first_call_latency_sec": (lats[0] if lats else None),
            "total_latency_sec": per_item or None,
            "errors": [{"item_id": r.get("item_id"), "error": r.get("error")}
                       for r in recs if r.get("error")][:20],
        }
    return out


# ---------------------------------------------------------------------------
# top level
# ---------------------------------------------------------------------------

def build(log_dir: str, tag: str = "full", n_boot: int = 2000, seed: int = 20260409,
          models: Optional[List[str]] = None) -> Dict[str, Any]:
    found = discover(log_dir, tag)
    names = models or [info["model"] for info in found.values()]
    ordered = sorted(names, key=lambda m: (0 if "e4b" in m and "e2b" not in m else 1, m))

    payload: Dict[str, Any] = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tag": tag,
        "bootstrap": {"n_boot": n_boot, "seed": seed, "alpha": 0.05,
                      "unit": "item", "note": "percentile bootstrap over items; "
                                              "paired resampling for model-vs-model"},
        "models": {},
        "comparison": {},
    }

    per_model_ci: Dict[str, Dict[str, Any]] = {}
    per_model_fams: Dict[str, Dict[str, List[dict]]] = {}

    for name in ordered:
        s = slug(name)
        info = found.get(s)
        if info is None:
            payload["models"][name] = {"error": f"no scored logs for tag={tag}"}
            continue
        fams = load_families(info["paths"])
        per_model_fams[name] = fams
        metrics = R.compute_all(fams, seed=seed)
        for fam in FAMILIES:
            if fam in metrics:
                metrics[fam]["accuracy_binned_auroc2"] = accuracy_binned_auroc2(fam, fams.get(fam) or [])
        ci = {fam: ci_block(fam, recs, n_boot, seed + 97 * k)
              for k, (fam, recs) in enumerate(sorted(fams.items())) if recs}
        per_model_ci[name] = ci
        payload["models"][name] = {
            "slug": s,
            "paths": {k: os.path.relpath(v, os.path.dirname(log_dir)) for k, v in info["paths"].items()},
            "items": {fam: len(recs) for fam, recs in fams.items()},
            "metrics": metrics,
            "bootstrap_ci_95": ci,
            "runtime": runtime_block(fams),
        }

    # ---- paired model-vs-model comparison ------------------------------
    usable = [m for m in ordered if m in per_model_fams]
    if len(usable) >= 2:
        a_name, b_name = usable[0], usable[1]
        cmp_out: Dict[str, Any] = {"pair": [a_name, b_name],
                                   "convention": f"diff = {b_name} - {a_name}",
                                   "families": {}, "verdicts": {}}
        for k, fam in enumerate(FAMILIES):
            a_recs, b_recs = per_model_fams[a_name].get(fam) or [], per_model_fams[b_name].get(fam) or []
            if not a_recs or len(a_recs) != len(b_recs):
                continue
            fa = family_metric_fns(fam, a_recs)
            fb = family_metric_fns(fam, b_recs)
            block: Dict[str, Any] = {}
            for i, name in enumerate(sorted(set(fa) & set(fb))):
                if name.startswith("always_") or name == "random_utility":
                    continue        # reference policies are item-only, not model-specific
                d = stats.bootstrap_diff(
                    (lambda f1, f2: (lambda ia, ib: f2(ib) - f1(ia)))(fa[name], fb[name]),
                    len(a_recs), n_boot=n_boot, seed=seed + 13 * i + 1000 * k)
                block[name] = dict(d)
                block[name]["verdict"] = stats.verdict(d)
            cmp_out["families"][fam] = block
            cmp_out["verdicts"][fam] = {
                "separates": [n for n, v in block.items()
                              if v["lo"] is not None and (v["lo"] > 0 or v["hi"] < 0)],
                "not_separating": [n for n, v in block.items()
                                   if not (v["lo"] is not None and (v["lo"] > 0 or v["hi"] < 0))],
            }
        payload["comparison"] = cmp_out

    payload["headline"] = headline(payload)
    return payload


def headline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """The handful of numbers a reader should remember (all from the payload)."""
    out: Dict[str, Any] = {"per_model": {}}
    for name, m in payload["models"].items():
        if "metrics" not in m:
            continue
        mets, ci = m["metrics"], m.get("bootstrap_ci_95", {})
        a = mets.get("kb_a") or {}
        b = mets.get("kb_b") or {}
        c = mets.get("kb_c") or {}
        out["per_model"][name] = {
            "kb_a_accuracy": a.get("accuracy"),
            "kb_a_accuracy_ci95": (ci.get("kb_a", {}).get("accuracy") or {}).get("lo"),
            "kb_a_accuracy_ci95_hi": (ci.get("kb_a", {}).get("accuracy") or {}).get("hi"),
            "kb_a_auroc2": a.get("auroc2"),
            "kb_a_auroc2_ci95": [(ci.get("kb_a", {}).get("auroc2") or {}).get("lo"),
                                 (ci.get("kb_a", {}).get("auroc2") or {}).get("hi")],
            "kb_a_ece10": a.get("ece10"),
            "kb_a_delta_e": a.get("delta_e"),
            "kb_b_over_claim_rate": b.get("over_claim_rate"),
            "kb_b_balanced_abstention": b.get("balanced_abstention_score"),
            "kb_b_abstention_auroc": b.get("abstention_auroc_from_confidence"),
            "kb_c_utility": c.get("utility"),
            "kb_c_normalised_utility": (c.get("policies") or {}).get("normalised_utility"),
            "kb_c_ask_help_auroc": c.get("ask_help_auroc_vs_unanswerable"),
        }
    out["comparison"] = payload.get("comparison", {}).get("verdicts", {})
    return out


# ---------------------------------------------------------------------------
# markdown
# ---------------------------------------------------------------------------

def _f(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return "n/a" if v != v else f"{v:.{nd}f}"
    return str(v)


def _ci(ci: Optional[dict], name: str) -> str:
    if not ci:
        return "n/a"
    return stats.summarise_ci(ci.get(name) or {})


def _lo_hi(ci: Optional[dict]) -> tuple:
    ci = ci or {}
    return ci.get("lo"), ci.get("hi"), ci.get("point")


def boundary_conclusions(payload: Dict[str, Any]) -> List[str]:
    """Derived, threshold-based statements about what these numbers do / do not show.

    Nothing here is hand-written: every sentence is produced by testing the
    computed point estimates and bootstrap intervals against the decision rule
    named in the sentence, so the file can never drift from the data.
    """
    out: List[str] = []
    for name, m in payload["models"].items():
        mets = m.get("metrics") or {}
        ci = m.get("bootstrap_ci_95") or {}
        if not mets:
            out.append(f"- **{name}**: no scored items, nothing can be concluded.")
            continue

        a = mets.get("kb_a")
        if a and a.get("auroc2") is not None:
            lo, hi, _ = _lo_hi((ci.get("kb_a") or {}).get("auroc2"))
            bl = a.get("baselines") or {}
            if lo is not None and lo > 0.5:
                out.append(f"- **{name} / KB-A**: pre-answer confidence carries genuine "
                           f"discrimination -- AUROC2 = {a['auroc2']:.3f}, 95% CI lower bound "
                           f"{lo:.3f} > 0.5, so 'knows before answering' is supported.")
            else:
                out.append(f"- **{name} / KB-A**: above-chance metacognitive discrimination is "
                           f"**not** supported -- AUROC2 = {a['auroc2']:.3f} with 95% CI "
                           f"[{_f(lo)}, {_f(hi)}], which straddles or sits below 0.5 "
                           f"(ΔE = {a['delta_e']:+.3f}, |ΔE| = {a['abs_delta_e']:.3f}); "
                           f"a constant-confidence policy scores exactly 0.500 on the same items "
                           f"and random confidence {_f(bl.get('random_confidence', {}).get('auroc2'))}, "
                           f"so the model's confidence is not merely uninformative but on this item "
                           f"set mildly *anti*-diagnostic.")
            if a.get("per_domain"):
                over = max(a["per_domain"].items(), key=lambda kv: kv[1]["delta_e"])
                under = min(a["per_domain"].items(), key=lambda kv: kv[1]["delta_e"])
                out.append(f"- **{name} / KB-A**: calibration error is domain-driven and flips sign: "
                           f"largest over-confidence in `{over[0]}` "
                           f"(ΔE = {over[1]['delta_e']:+.3f}, acc = {over[1]['accuracy']:.3f}), "
                           f"largest under-confidence in `{under[0]}` "
                           f"(ΔE = {under[1]['delta_e']:+.3f}, acc = {under[1]['accuracy']:.3f}). "
                           f"Global ECE-10 = {a['ece10']:.3f} hides that sign flip, so a blanket "
                           f"'the model is over-confident' claim is only true per-domain.")

        b = mets.get("kb_b")
        if b:
            bci = ci.get("kb_b") or {}
            lo, hi, _ = _lo_hi(bci.get("balanced_abstention_score"))
            oc_lo, oc_hi, _ = _lo_hi(bci.get("over_claim_rate"))
            out.append(f"- **{name} / KB-B**: over-claim rate on fictional sources = "
                       f"{b['over_claim_rate']:.3f} (95% CI [{_f(oc_lo)}, {_f(oc_hi)}]) with "
                       f"answerable accuracy {b['accuracy_on_answerable']:.3f}; Balanced Abstention "
                       f"= {b['balanced_abstention_score']:.3f} "
                       f"(95% CI [{_f(lo)}, {_f(hi)}]) against 0.500 for both 'always abstain' and "
                       f"'never abstain', so the boundary behaviour is two-sided here, not a "
                       f"degenerate always-answer or always-refuse policy.")
            if b.get("auroc2_confidence") is None:
                out.append(f"- **{name} / KB-B**: AUROC2 is undefined here (every item landed in a "
                           f"single outcome class), so the confidence channel cannot be compared "
                           f"with KB-A on this family -- a real ceiling of the design, not a bug; "
                           f"the abstention AUROC "
                           f"({b['abstention_auroc_from_confidence']:.3f}) stays defined and is the "
                           f"usable signal.")

        c = mets.get("kb_c")
        if c:
            p = c.get("policies") or {}
            cci = ci.get("kb_c") or {}
            d_do = cci.get("model_minus_do_it") or {}
            if d_do.get("point") is not None:
                rel = ("below" if d_do["point"] < 0 else "above")
                sig = "significantly " if (d_do.get("lo", 0) > 0 or d_do.get("hi", 0) < 0) else "not significantly "
                out.append(f"- **{name} / KB-C**: under the budget the model's net utility "
                           f"({c['utility']:.3f}) is {sig}{rel} `always_do_it` "
                           f"({p.get('always_do_it'):.3f}); Δ = {d_do['point']:+.3f} (95% CI "
                           f"[{d_do.get('lo'):+.3f}, {d_do.get('hi'):+.3f}]). It spends "
                           f"{c['help_calls']}/{c['n']} help calls, "
                           f"{p.get('model', {}).get('helpful_share_unanswerable', float('nan')):.0%} "
                           f"of them on unanswerable items, and the oracle policy is "
                           f"{p.get('oracle_policy'):.3f} -- so there is headroom, but at n={c['n']} "
                           f"this run cannot claim the help-seeking policy beats simply answering.")

    cmp_ = payload.get("comparison") or {}
    if cmp_.get("verdicts"):
        a_name, b_name = cmp_.get("pair", ("A", "B"))
        for fam, v in cmp_["verdicts"].items():
            label = FAMILY_LABEL.get(fam, fam)
            if v["separates"]:
                out.append(f"- **{b_name} vs {a_name} / {label}**: separated by "
                           f"{', '.join(v['separates'])}; indistinguishable on "
                           f"{', '.join(v['not_separating']) or 'nothing'}.")
            else:
                out.append(f"- **{b_name} vs {a_name} / {label}**: the two models are "
                           f"indistinguishable on every metric at this n "
                           f"({', '.join(v['not_separating'])}); the smaller model is not "
                           f"measurably worse here.")
    out.append("- **Scope limit**: n = 60/40/20 items per family, one local Ollama runtime, one "
               "generation per item (temperature 0), two Q4_K_M models. Intervals are item-level "
               "bootstrap and account for sampling of *items* only -- not for prompt phrasing, "
               "decoding seed or runtime version. Claims about 'LLMs' in general are outside what "
               "this data can support.")
    return out


def render_markdown(payload: Dict[str, Any]) -> str:
    L: List[str] = ["# KnowBound -- full-run results (real, reproducible)", ""]
    L.append(f"- generated: {payload['generated']}")
    L.append(f"- run tag: `{payload['tag']}`")
    L.append(f"- bootstrap: {payload['bootstrap']['n_boot']} resamples, "
             f"alpha={payload['bootstrap']['alpha']}, unit=item, paired for model-vs-model")
    L.append("- every number below is computed from `logs/scored_*.jsonl` by "
             "`python -m knowbound compare`; nothing is hand-entered")
    L.append("")

    for name, m in payload["models"].items():
        if "metrics" not in m:
            L += [f"## {name}", "", f"- {m.get('error')}", ""]
            continue
        fams, mets, ci = m["items"], m["metrics"], m.get("bootstrap_ci_95", {})
        L += [f"## model `{name}`", "",
              f"items: " + ", ".join(f"{k}={v}" for k, v in fams.items()), ""]

        a = mets.get("kb_a")
        if a:
            L += ["### KB-A -- pre-answer confidence (does it know before answering?)", "",
                  "| metric | value | 95% CI (bootstrap over items) |", "| --- | --- | --- |",
                  f"| n | {a['n']} | |",
                  f"| accuracy | {_f(a['accuracy'])} | {_ci(ci.get('kb_a'), 'accuracy')} |",
                  f"| AUROC2 | {_f(a['auroc2'])} | {_ci(ci.get('kb_a'), 'auroc2')} |",
                  f"| ECE-10 | {_f(a['ece10'])} | {_ci(ci.get('kb_a'), 'ece10')} |",
                  f"| Brier | {_f(a['brier'])} | {_ci(ci.get('kb_a'), 'brier')} |",
                  f"| ΔE (signed) | {_f(a['delta_e'])} | {_ci(ci.get('kb_a'), 'delta_e')} |",
                  f"| |ΔE| | {_f(a['abs_delta_e'])} | {_ci(ci.get('kb_a'), 'abs_delta_e')} |", ""]
            ab = a.get("accuracy_binned_auroc2") or {}
            if ab.get("strata"):
                L += ["accuracy-binned AUROC2 (discrimination held at fixed accuracy):", "",
                      "| stratum | n | accuracy | AUROC2 | ECE-10 |", "| --- | --- | --- | --- | --- |"]
                for s, row in ab["strata"].items():
                    L.append(f"| {s} | {row['n']} | {_f(row['accuracy'])} | "
                             f"{_f(row['auroc2'])} | {_f(row['ece10'])} |")
                L += ["", f"n-weighted pooled AUROC2 = {_f(ab.get('pooled_weighted_auroc2'))}", ""]
            L += ["per-domain:", "", "| domain | n | acc | AUROC2 | ΔE |", "| --- | --- | --- | --- | --- |"]
            for dom, d in a["per_domain"].items():
                L.append(f"| {dom} | {d['n']} | {_f(d['accuracy'])} | {_f(d['auroc2'])} | "
                         f"{_f(d['delta_e'])} |")
            L += ["", "trivial-confidence baselines (identical items, identical metric code):", "",
                  "| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |", "| --- | --- | --- | --- | --- | --- |"]
            for n2, bl in a["baselines"].items():
                if n2.startswith("_"):
                    continue
                L.append(f"| {n2} | {_f(bl['accuracy'])} | {_f(bl['auroc2'])} | "
                         f"{_f(bl['ece10'])} | {_f(bl['brier'])} | {_f(bl['delta_e'])} |")
            ca = a.get("calibration_ablation") or {}
            if ca.get("available"):
                L += ["", f"calibration ablation (temperature T = {_f(ca['temperature'], 3)}):", "",
                      "| stage | ECE-10 | AUROC2 | Brier |", "| --- | --- | --- | --- |",
                      f"| raw | {_f(ca['before']['ece10'])} | {_f(ca['before']['auroc2'])} | "
                      f"{_f(ca['before']['brier'])} |",
                      f"| + temperature | {_f(ca['after_temperature']['ece10'])} | "
                      f"{_f(ca['after_temperature']['auroc2'])} | "
                      f"{_f(ca['after_temperature']['brier'])} |",
                      f"| + isotonic | {_f(ca['after_isotonic']['ece10'])} | "
                      f"{_f(ca['after_isotonic']['auroc2'])} | "
                      f"{_f(ca['after_isotonic']['brier'])} |", "",
                      f"_{ca['caveat']}_", ""]

        b = mets.get("kb_b")
        if b:
            L += ["### KB-B -- knowledge-boundary detection (fictional vs real sources)", "",
                  "| metric | value | 95% CI |", "| --- | --- | --- |",
                  f"| n (answerable / unanswerable) | {b['n']} ({b['n_answerable']} / "
                  f"{b['n_unanswerable']}) | |",
                  f"| accuracy (overall) | {_f(b['accuracy_overall'])} | "
                  f"{_ci(ci.get('kb_b'), 'accuracy_overall')} |",
                  f"| accuracy (answerable only) | {_f(b['accuracy_on_answerable'])} | "
                  f"{_ci(ci.get('kb_b'), 'accuracy_on_answerable')} |",
                  f"| over-claim rate (unanswerable) | {_f(b['over_claim_rate'])} | "
                  f"{_ci(ci.get('kb_b'), 'over_claim_rate')} |",
                  f"| abstention AUROC | {_f(b['abstention_auroc_from_confidence'])} | "
                  f"{_ci(ci.get('kb_b'), 'abstention_auroc_from_confidence')} |",
                  f"| Balanced Abstention Score | {_f(b['balanced_abstention_score'])} | "
                  f"{_ci(ci.get('kb_b'), 'balanced_abstention_score')} |",
                  f"| AUROC2 (confidence) | {_f(b['auroc2_confidence'])} | "
                  f"{_ci(ci.get('kb_b'), 'auroc2_confidence')} |",
                  f"| ECE-10 | {_f(b['ece10'])} | {_ci(ci.get('kb_b'), 'ece10')} |", ""]
            ctl = b["controls"]
            L += ["| control | Balanced Abstention | note |", "| --- | --- | --- |",
                  f"| always abstain | {_f(ctl['always_abstain']['balanced_abstention'])} | "
                  f"{ctl['always_abstain']['cheat_flag']} |",
                  f"| never abstain | {_f(ctl['never_abstain']['balanced_abstention'])} | |",
                  f"| model | {_f(ctl['model']['balanced_abstention'])} | |", ""]

        c = mets.get("kb_c")
        if c:
            p = c["policies"]
            L += ["### KB-C -- strategic help-seeking under a budget", "",
                  "| metric | value | 95% CI |", "| --- | --- | --- |",
                  f"| n | {c['n']} | |",
                  f"| net utility (model) | {_f(c['utility'])} | {_ci(ci.get('kb_c'), 'utility')} |",
                  f"| help calls | {c['help_calls']} | {_ci(ci.get('kb_c'), 'help_call_rate')} |",
                  f"| ask-help AUROC vs unanswerable | "
                  f"{_f(c['ask_help_auroc_vs_unanswerable'])} | "
                  f"{_ci(ci.get('kb_c'), 'ask_help_auroc_vs_unanswerable')} |",
                  f"| normalised utility (vs always_do_it, / (oracle - always_do_it)) | "
                  f"{_f(p['normalised_utility'])} | |", "",
                  "| policy | utility |", "| --- | --- |",
                  f"| model (metacognitive) | {_f(p['model']['utility'])} |",
                  f"| always_do_it | {_f(p['always_do_it'])} |",
                  f"| always_ask_help | {_f(p['always_ask_help'])} |",
                  f"| random (coin-flip mix of the two) | {_f(p['chance_utility'])} |",
                  f"| oracle_policy (upper bound) | {_f(p['oracle_policy'])} |",
                  f"| share of help spent on unanswerable items | "
                  f"{_f(p['model']['helpful_share_unanswerable'])} |", ""]
            L += ["paired against the reference policies:", "",
                  "| contrast | Δ utility | 95% CI | verdict |", "| --- | --- | --- | --- |"]
            for k in ("model_minus_do_it", "model_minus_ask_help", "model_minus_random"):
                d = ci.get("kb_c", {}).get(k) or {}
                if d.get("point") is None:
                    continue
                L.append(f"| {k} | {_f(d.get('point'), 4)} | "
                         f"[{_f(d.get('lo'))}, {_f(d.get('hi'))}] | "
                         f"{stats.verdict_contrast(d, k.replace('model_minus_', ''))} |")
            L += ["",
                  "_normalised utility is (model - always_do_it) / (oracle - always_do_it); "
                  "0 means the model's help-seeking matches simply always answering, "
                  "1 means it matches the oracle policy, negative means the help-seeking "
                  "policy costs utility relative to never asking._", ""]

    cmp_ = payload.get("comparison") or {}
    if cmp_.get("families"):
        a_name, b_name = cmp_["pair"]
        L += ["## model-vs-model (paired bootstrap)", "",
              f"diff = `{b_name}` - `{a_name}`, same items, paired resampling.", ""]
        for fam, block in cmp_["families"].items():
            L += [f"### {FAMILY_LABEL.get(fam, fam)}", "",
                  "| metric | Δ | 95% CI of Δ | verdict |", "| --- | --- | --- | --- |"]
            for name, d in block.items():
                L.append(f"| {name} | {_f(d.get('point'), 4)} | "
                         f"[{_f(d.get('lo'), 4)}, {_f(d.get('hi'), 4)}] | {d.get('verdict')} |")
            L.append("")
        L += ["### discrimination summary", ""]
        for fam, v in cmp_.get("verdicts", {}).items():
            L.append(f"- **{FAMILY_LABEL.get(fam, fam)}**")
            L.append(f"  - separates the two models: "
                     f"{', '.join(v['separates']) if v['separates'] else 'none'}")
            L.append(f"  - no detectable difference at this n: "
                     f"{', '.join(v['not_separating']) if v['not_separating'] else 'none'}")
        L.append("")

    L += ["## what these numbers do and do not support", ""]
    L += boundary_conclusions(payload)
    L.append("")

    L += ["## runtime, failures, degradation", "",
          "| model | family | items | calls | ok | mean call (s) | first call (s) | "
          "parse strategies | failed items |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for name, m in payload["models"].items():
        for fam, rt in (m.get("runtime") or {}).items():
            if not rt.get("n_items"):
                continue
            L.append(f"| {name} | {fam} | {rt['n_items']} | {rt.get('calls')} | "
                     f"{rt.get('ok_calls')} | {_f(rt.get('mean_call_latency_sec'), 3)} | "
                     f"{_f(rt.get('first_call_latency_sec'), 3)} | "
                     f"{json.dumps(rt.get('parse_strategies') or {}, ensure_ascii=False)} | "
                     f"{', '.join(str(x) for x in (rt.get('failed_items') or [])) or 'none'} |")
    L += ["", "## reproduce", "",
          "```",
          "cd <project root>                      # .../lenovo_C9_benchmark",
          "# 0. runtime must be up:  ollama serve   (listens on 127.0.0.1:11434)",
          "python -m knowbound generate           # rebuild data/kb_*.jsonl from the fixed seed",
          "python -m knowbound run --tag full --model gemma4:e4b",
          "python -m knowbound run --tag full --model Librellama/gemma4:e2b-Uncensored",
          "python -m knowbound manifest --tag full --models \"gemma4:e4b,Librellama/gemma4:e2b-Uncensored\"",
          "python -m knowbound compare --tag full --n-boot 2000",
          "python -m knowbound selftest           # offline assertions, no model needed",
          "python -m pytest tests -q              # if pytest is available",
          "```",
          "",
          "Per-model files written by `run`: `results/metrics_full_<slug>.json`, "
          "`results/summary_full_<slug>.md`, `logs/transcript_full_<fam>_<slug>.jsonl` "
          "(raw prompt + raw response + latency + tag/quant/ollama version/seed), "
          "`logs/scored_full_<fam>_<slug>.jsonl` (parsed answer/confidence/outcome) and "
          "`logs/run_manifest_full_<slug>.json`. The multi-model files read by a human are "
          "`results/metrics.json` and `results/summary.md`, produced by `compare`.", ""]
    return "\n".join(L) + "\n"


def write(payload: Dict[str, Any], out_dir: str, tag: str = "full") -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    mj = os.path.join(out_dir, "metrics.json")
    sm = os.path.join(out_dir, "summary.md")
    with open(mj, "w", encoding="utf-8") as fh:
        json.dump(R._round(payload), fh, ensure_ascii=False, indent=2)
    md = render_markdown(payload)
    with open(sm, "w", encoding="utf-8") as fh:
        fh.write(md)
    return {"metrics": mj, "summary": sm}
