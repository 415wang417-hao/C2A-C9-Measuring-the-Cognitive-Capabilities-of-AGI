"""Aggregation: scored records -> metrics.json / summary.md / smoke_report.md."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from . import baselines as B
from . import metrics as M
from .runner import slug


def read_jsonl(path: str) -> List[dict]:
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    return out


def collect(log_dir: str, tag: str, model: str,
            families=("kb_a", "kb_b", "kb_c")) -> Dict[str, List[dict]]:
    s = slug(model)
    return {f: read_jsonl(os.path.join(log_dir, f"scored_{tag}_{f}_{s}.jsonl"))
            for f in families}


def _latencies(records: List[dict]) -> List[float]:
    vals = []
    for r in records:
        for key in ("latency_sec", "latency_p_sec", "latency_a_sec"):
            v = r.get(key)
            if isinstance(v, (int, float)):
                vals.append(float(v))
    return vals


def _np_mean(vals):
    return sum(vals) / len(vals) if vals else None


def _parse_failures(records: List[dict]) -> int:
    """Count calls whose *stored* parse strategy is explicitly 'failed'.

    Only keys that are actually present are considered: a missing key means the
    call does not exist for that record (e.g. single-stage families carry no
    ``parse_strategy_a``), not that parsing failed.
    """
    n = 0
    for r in records:
        for key in ("parse_strategy", "parse_strategy_p", "parse_strategy_a"):
            if key in r and str(r.get(key)).lower() == "failed":
                n += 1
    return n


def _cold_start(records: List[dict]) -> Optional[float]:
    """First call latency of a run = model load + first inference."""
    for r in records:
        for key in ("latency_sec", "latency_p_sec", "latency_a_sec"):
            v = r.get(key)
            if isinstance(v, (int, float)):
                return float(v)
    return None


def _round(obj, nd=4):
    if isinstance(obj, float):
        return None if obj != obj else round(obj, nd)   # NaN -> None (JSON-safe)
    if isinstance(obj, dict):
        return {k: _round(v, nd) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round(v, nd) for v in obj]
    return obj


def compute_all(records: Dict[str, List[dict]], seed: int = 0) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    # ---- KB-A ----------------------------------------------------------
    a = records.get("kb_a") or []
    if a:
        conf = [r["confidence"] if r.get("confidence") is not None else 0.0 for r in a]
        correct = [bool(r["correct"]) for r in a]
        per_domain = {}
        for dom in sorted({r.get("domain") for r in a}):
            sub = [r for r in a if r.get("domain") == dom]
            if not sub:
                continue
            sc = [r["confidence"] if r.get("confidence") is not None else 0.0 for r in sub]
            sk = [bool(r["correct"]) for r in sub]
            per_domain[dom] = {
                "n": len(sub), "accuracy": M.accuracy(sk),
                "auroc2": M.auroc2(sc, sk), "delta_e": M.delta_e(sc, sk),
                "abs_delta_e": M.abs_delta_e(sc, sk),
                "over_claim_rate_on_unanswerable":
                    M.over_claim_rate([r["confidence"] is not None and r["confidence"] > 0.5
                                       for r in sub if not r["answerable"]],
                                      [True] * sum(1 for r in sub if not r["answerable"]))
                    if any(not r["answerable"] for r in sub) else None,
            }
        out["kb_a"] = {
            "n": len(a),
            "accuracy": M.accuracy(correct),
            "delta_e": M.delta_e(conf, correct),
            "abs_delta_e": M.abs_delta_e(conf, correct),
            "brier": M.brier(conf, correct),
            "ece10": M.ece(conf, correct, 10),
            "auroc2": M.auroc2(conf, correct),
            "reliability_bins": M.reliability_bins(conf, correct, 10),
            "difficulty_strata": M.stratify(a, conf, correct),
            "per_domain": per_domain,
            "baselines": B.kb_a_baselines(correct, conf, seed=seed),
            "calibration_ablation": B.calibration_ablation(conf, correct, seed=seed),
        }

    # ---- KB-B ----------------------------------------------------------
    b = records.get("kb_b") or []
    if b:
        unans = [not r["answerable"] for r in b]
        abstain = [bool(r.get("abstain")) for r in b]
        conf = [r["confidence"] if r.get("confidence") is not None else 0.5 for r in b]
        need_help = [1.0 - c for c in conf]
        real = [r for r in b if r["answerable"]]
        out["kb_b"] = {
            "n": len(b), "n_answerable": len(real), "n_unanswerable": len(unans) - len(real),
            "accuracy_overall": M.accuracy([bool(r["correct"]) for r in b]),
            "accuracy_on_answerable": M.accuracy([bool(r["correct"]) for r in real]),
            "over_claim_rate": M.over_claim_rate([not x for x in abstain], unans),
            "abstention_auroc_from_confidence": M.abstention_auroc(need_help, unans),
            "balanced_abstention_score": M.balanced_abstention_score(abstain, unans),
            "auroc2_confidence": M.auroc2(conf, [bool(r["correct"]) for r in b]),
            "ece10": M.ece(conf, [bool(r["correct"]) for r in b], 10),
            "delta_e": M.delta_e(conf, [bool(r["correct"]) for r in b]),
            "controls": B.kb_b_controls(b),
        }

    # ---- KB-C ----------------------------------------------------------
    c = records.get("kb_c") or []
    if c:
        decisions = [r.get("decision") for r in c]
        unans = [not r["answerable"] for r in c]
        forced = _load_items_for(records, "kb_c")
        out["kb_c"] = {
            "n": len(c),
            "utility": _np_mean([float(r["points"]) for r in c]),
            "help_calls": sum(1 for r in c if r.get("help_granted")),
            "ask_help_auroc_vs_unanswerable":
                M.abstention_auroc([1.0 if d == "ask_help" else 0.0 for d in decisions], unans),
            "policies": B.kb_c_policies(forced or c, [float(r["points"]) for r in c],
                                        [d or "none" for d in decisions]),
            "by_kind": {k: {"n": len([r for r in c if r.get("kind") == k]),
                            "utility": _np_mean([float(r["points"]) for r in c
                                                 if r.get("kind") == k]),
                            "help_calls": sum(1 for r in c
                                              if r.get("kind") == k and r.get("help_granted"))}
                        for k in sorted({r.get("kind") for r in c})},
        }
    return out


def _load_items_for(records: Dict[str, List[dict]], family: str) -> List[dict]:
    """Recover the `answerable` flag list from the scored records themselves."""
    return [{"answerable": bool(r["answerable"])} for r in (records.get(family) or [])]


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def _fmt(v, nd=4):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def render_summary(metrics: Dict[str, Any], meta: Dict[str, Any]) -> str:
    L = ["# KnowBound -- results summary", ""]
    L.append(f"- model: `{meta.get('model')}`")
    L.append(f"- tag: `{meta.get('tag')}`")
    L.append(f"- items: " + ", ".join(f"{k}={v}" for k, v in (meta.get("counts") or {}).items()))
    L.append(f"- generated: {meta.get('timestamp')}")
    L.append("")

    a = metrics.get("kb_a")
    if a:
        L += ["## KB-A  pre-answer confidence prediction", "",
              "| metric | value |", "| --- | --- |",
              f"| n | {a['n']} |",
              f"| accuracy | {_fmt(a['accuracy'])} |",
              f"| AUROC2 | {_fmt(a['auroc2'])} |",
              f"| ECE-10 | {_fmt(a['ece10'])} |",
              f"| Brier | {_fmt(a['brier'])} |",
              f"| delta_E (signed) | {_fmt(a['delta_e'])} |",
              f"| |delta_E| | {_fmt(a['abs_delta_e'])} |", ""]
        L += ["### per-domain", "", "| domain | n | acc | AUROC2 | ΔE | |ΔE| |",
              "| --- | --- | --- | --- | --- | --- |"]
        for dom, d in a["per_domain"].items():
            L.append(f"| {dom} | {d['n']} | {_fmt(d['accuracy'])} | {_fmt(d['auroc2'])} | "
                     f"{_fmt(d['delta_e'])} | {_fmt(d['abs_delta_e'])} |")
        L += ["", "### baselines (identical items, identical metric code)", "",
              "| policy | acc | AUROC2 | ECE-10 | Brier | ΔE |", "| --- | --- | --- | --- | --- | --- |"]
        for name, bl in a["baselines"].items():
            if name.startswith("_"):
                continue
            L.append(f"| {name} | {_fmt(bl['accuracy'])} | {_fmt(bl['auroc2'])} | "
                     f"{_fmt(bl['ece10'])} | {_fmt(bl['brier'])} | {_fmt(bl['delta_e'])} |")
        ca = a.get("calibration_ablation") or {}
        if ca.get("available"):
            L += ["", "### calibration ablation (calibration != metacognition)", "",
                  f"temperature T = {_fmt(ca['temperature'], 3)}", "",
                  "| stage | ECE-10 | AUROC2 | Brier |", "| --- | --- | --- | --- |",
                  f"| raw | {_fmt(ca['before']['ece10'])} | {_fmt(ca['before']['auroc2'])} | "
                  f"{_fmt(ca['before']['brier'])} |",
                  f"| temperature | {_fmt(ca['after_temperature']['ece10'])} | "
                  f"{_fmt(ca['after_temperature']['auroc2'])} | "
                  f"{_fmt(ca['after_temperature']['brier'])} |",
                  f"| isotonic | {_fmt(ca['after_isotonic']['ece10'])} | "
                  f"{_fmt(ca['after_isotonic']['auroc2'])} | "
                  f"{_fmt(ca['after_isotonic']['brier'])} |", "",
                  f"_caveat_: {ca['caveat']}"]
        L += ["", "### difficulty strata", "", "| difficulty | n | acc | AUROC2 |",
              "| --- | --- | --- | --- |"]
        for row in a.get("difficulty_strata") or []:
            L.append(f"| {row['difficulty']} | {row['n']} | {_fmt(row['accuracy'])} | "
                     f"{_fmt(row['auroc2'])} |")
        L.append("")

    b = metrics.get("kb_b")
    if b:
        L += ["## KB-B  knowledge-boundary detection", "",
              "| metric | value |", "| --- | --- |",
              f"| n (answerable / unanswerable) | {b['n']} ({b['n_answerable']} / "
              f"{b['n_unanswerable']}) |",
              f"| accuracy (answerable only) | {_fmt(b['accuracy_on_answerable'])} |",
              f"| over-claim rate on unanswerable | {_fmt(b['over_claim_rate'])} |",
              f"| abstention AUROC (from confidence) | "
              f"{_fmt(b['abstention_auroc_from_confidence'])} |",
              f"| balanced abstention score | {_fmt(b['balanced_abstention_score'])} |",
              f"| AUROC2 (confidence) | {_fmt(b['auroc2_confidence'])} |",
              f"| ECE-10 | {_fmt(b['ece10'])} |", "",
              "| control | balanced abstention | note |", "| --- | --- | --- |",
              f"| always abstain | {_fmt(b['controls']['always_abstain']['balanced_abstention'])} "
              f"| {b['controls']['always_abstain']['cheat_flag']} |",
              f"| never abstain | {_fmt(b['controls']['never_abstain']['balanced_abstention'])} | "
              f"| |",
              f"| model | {_fmt(b['controls']['model']['balanced_abstention'])} | |", ""]

    c = metrics.get("kb_c")
    if c:
        p = c["policies"]
        L += ["## KB-C  strategic help-seeking", "",
              "| metric | value |", "| --- | --- |",
              f"| n | {c['n']} |",
              f"| utility (mean points) | {_fmt(c['utility'])} |",
              f"| help calls granted | {c['help_calls']} |",
              f"| ask-help AUROC vs unanswerable | {_fmt(c['ask_help_auroc_vs_unanswerable'])} |",
              f"| normalised utility vs oracle | {_fmt(p['normalised_utility'])} |", "",
              "| policy | utility |", "| --- | --- |",
              f"| model | {_fmt(p['model']['utility'])} |",
              f"| always_do_it | {_fmt(p['always_do_it'])} |",
              f"| always_ask_help | {_fmt(p['always_ask_help'])} |",
              f"| oracle | {_fmt(p['oracle_policy'])} |", ""]
    return "\n".join(L) + "\n"


def render_smoke(records: Dict[str, List[dict]], cfg: Dict[str, Any],
                 model: str, client_stats: Optional[dict] = None) -> str:
    counts = {k: len(v) for k, v in records.items()}
    total_items = sum(counts.values())
    L = ["# KnowBound -- smoke test report", "",
         "Purpose: prove the full chain `generate -> prompt -> local model -> JSON parse "
         "-> grade -> aggregate` works end to end on a small slice, and measure the "
         "per-call latency needed to size the full run.", "",
         "| field | value |", "| --- | --- |",
         f"| model | `{model}` |",
         f"| items (per family) | {counts} |",
         f"| total items | {total_items} |",
         f"| generated | {cfg.get('timestamp')} |", ""]

    if client_stats:
        L += ["| calls | value |", "| --- | --- |",
              f"| total calls | {client_stats.get('calls')} |",
              f"| failed calls | {client_stats.get('errors')} |",
              f"| mean latency per call (s) | {_fmt(client_stats.get('avg_latency'), 3)} |", ""]

    L += ["## per family", "",
          "| family | items | ok items | raw calls | mean call latency (s) "
          "| mean latency per item (s) | first-call (cold) latency (s) | JSON parse failures |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for fam, recs in records.items():
        if not recs:
            L.append(f"| {fam} | 0 | 0 | 0 | n/a | n/a | n/a | 0 |")
            continue
        ok = sum(1 for r in recs if r.get("ok"))
        lats = _latencies(recs)
        per_item = _np_mean([sum(v for v in (r.get(k) for k in
                                             ("latency_sec", "latency_p_sec",
                                              "latency_a_sec"))
                                 if isinstance(v, (int, float))) for r in recs])
        L.append(f"| {fam} | {len(recs)} | {ok} | {len(lats)} | {_fmt(_np_mean(lats), 3)} | "
                 f"{_fmt(per_item, 3)} | {_fmt(_cold_start(recs), 3)} | "
                 f"{_parse_failures(recs)} |")

    L += ["", "## per item", "",
          "| item | family | latency sum (s) | ok | parse | correct | confidence | model answer |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for fam, recs in records.items():
        for r in recs:
            lats = [r.get(k) for k in ("latency_sec", "latency_p_sec", "latency_a_sec")
                    if isinstance(r.get(k), (int, float))]
            ps = "|".join(str(r.get(k)) for k in
                          ("parse_strategy", "parse_strategy_p", "parse_strategy_a")
                          if r.get(k))
            ans = str(r.get("model_answer", ""))[:40].replace("|", "/")
            L.append(f"| {r.get('item_id')} | {fam} | {_fmt(sum(lats), 3)} | "
                     f"{'yes' if r.get('ok') else 'NO'} | {ps} | "
                     f"{'yes' if r.get('correct') else 'no'} | "
                     f"{_fmt(r.get('confidence'), 2)} | {ans} |")
    errs = [(r.get("item_id"), r.get("error")) for recs in records.values() for r in recs
            if r.get("error")]
    L += ["", "## errors", ""]
    L += [f"- `{i}`: {e}" for i, e in errs] or ["- none"]

    # ---- sizing implication (computed, never assumed) --------------------
    all_lats = [v for recs in records.values() for v in _latencies(recs)]
    warm = all_lats[1:] if len(all_lats) > 1 else all_lats
    cold = all_lats[0] if all_lats else None
    gen = (cfg or {}).get("generator") or {}
    try:
        full_items = {
            "kb_a": 4 * int(gen["kb_a"]["per_domain"]),
            "kb_b": int(gen["kb_b"]["n_real"]) + int(gen["kb_b"]["n_fictional"]),
            "kb_c": int(gen["kb_c"]["n_total"]),
        }
        full_calls = full_items["kb_a"] * 2 + full_items["kb_b"] + full_items["kb_c"]
        warm_mean = _np_mean(warm)
        est = None if warm_mean is None else full_calls * warm_mean + (cold or 0.0)
        L += ["", "## sizing implication for the full run", "",
              f"- planned items: {full_items} (KB-A is two-stage, so {full_items['kb_a']}x2 calls)",
              f"- planned model calls: {full_calls}",
              f"- measured warm call latency: {_fmt(warm_mean, 3)} s "
              f"(cold start {_fmt(cold, 3)} s, excluded)",
              f"- estimated full-run wall clock: {_fmt(est / 60.0, 1)} min "
              f"({full_calls} calls + one model load)" if est else "- estimated full-run time: n/a"]
    except (KeyError, TypeError, ValueError):
        pass
    L.append("")
    return "\n".join(L) + "\n"


def write_outputs(out_dir: str, metrics: Dict[str, Any], summary: str,
                  metrics_name: str = "metrics.json") -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, metrics_name)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(_round(metrics), fh, ensure_ascii=False, indent=2)
    return path
