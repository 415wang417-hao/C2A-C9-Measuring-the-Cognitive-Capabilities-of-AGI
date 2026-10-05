#!/usr/bin/env python
"""Score a human-baseline CSV with the *same* metric code as the model runs.

Why this file exists
--------------------
The claim "humans were scored on the same footing as the models" is only
credible if it is mechanically true.  Therefore this script does **not**
re-implement a single metric: it imports ``knowbound.grading``,
``knowbound.metrics``, ``knowbound.baselines`` and ``knowbound.stats`` -- the
very modules that produced ``results/metrics.json`` -- and only adds the CSV IO
and the presentation-order budget rule for KB-C.

Input  : a CSV following human_baseline/lenovo_human_baseline_protocol.md
Output : human_results.json + human_results.md (in --out-dir, default = this dir)

If the CSV has no usable rows, the script reports "no human data collected"
and writes no metrics file at all -- a human baseline must never be invented.

Usage
-----
    python human_baseline/lenovo_human_scoring.py --csv <data.csv>
    python human_baseline/lenovo_human_scoring.py --csv <data.csv> --validate-only
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import sys
from typing import Dict, List, Optional, Sequence

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from knowbound import baselines as B      # noqa: E402
from knowbound import grading as G        # noqa: E402
from knowbound import metrics as M        # noqa: E402
from knowbound import stats as S          # noqa: E402

COLUMNS = ["participant_id", "family", "item_id", "p_confidence", "a_confidence",
           "answer", "can_answer", "decision", "rt_sec", "notes"]
FAMILIES = ("KB-A", "KB-B", "KB-C")
ITEM_FILES = {"KB-A": "kb_a.jsonl", "KB-B": "kb_b.jsonl", "KB-C": "kb_c.jsonl"}
BUDGET, DISCOUNT = 6, 0.7
N_BOOT = 2000


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------

def load_items() -> Dict[str, dict]:
    items: Dict[str, dict] = {}
    for fam, fn in ITEM_FILES.items():
        with open(os.path.join(ROOT, "data", fn), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    it = json.loads(line)
                    it["_family"] = fam
                    items[it["id"]] = it
    return items


def read_rows(path: str) -> List[dict]:
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rdr = csv.DictReader(fh)
        fields = rdr.fieldnames or []
        missing = [c for c in COLUMNS if c not in fields]
        if missing:
            raise SystemExit(f"[header error] missing columns {missing}; expected {COLUMNS}")
        rows = [r for r in rdr if (r.get("participant_id") or "").strip()]
    return rows


def fnum(v) -> Optional[float]:
    s = (v or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def conf01(v) -> Optional[float]:
    """0-100 integer on the form, [0,1] float internally (model convention)."""
    x = fnum(v)
    if x is None:
        return None
    if x < 0 or x > 100:
        return None
    return x / 100.0


def tri(v) -> Optional[bool]:
    s = (v or "").strip().lower()
    if s in ("true", "1", "yes", "y", "t"):
        return True
    if s in ("false", "0", "no", "n", "f"):
        return False
    return None


def _pack(conf: Sequence[float], correct: Sequence[bool]) -> Dict[str, float]:
    return {
        "n": len(list(correct)),
        "accuracy": M.accuracy(correct),
        "delta_e": M.delta_e(conf, correct),
        "abs_delta_e": M.abs_delta_e(conf, correct),
        "auroc2": M.auroc2(conf, correct),
        "ece10": M.ece(conf, correct, 10),
        "brier": M.brier(conf, correct),
    }


def _ci(vals_conf: Sequence[float], vals_correct: Sequence[bool], fn, n_boot: int):
    """Percentile bootstrap of ``fn`` over responses (unit = one response)."""
    if len(vals_correct) < 3:
        return None
    conf, correct = list(vals_conf), list(vals_correct)

    def stat(idx: List[int]) -> float:
        return fn([conf[i] for i in idx], [correct[i] for i in idx])

    r = S.bootstrap(stat, len(correct), n_boot=n_boot, seed=20261005)
    return {k: r[k] for k in ("point", "lo", "hi", "n_defined")}


# ---------------------------------------------------------------------------
# per-family scoring
# ---------------------------------------------------------------------------

def score_kb_a(rows: List[dict], items: Dict[str, dict], excluded: List[dict]) -> Dict:
    conf, correct, conf_post = [], [], []
    for r in rows:
        it = items.get(r["item_id"])
        if it is None or it["_family"] != "KB-A":
            excluded.append({"row": r["item_id"], "reason": "unknown item_id / family mismatch"})
            continue
        c = conf01(r.get("p_confidence"))
        if c is None:
            excluded.append({"row": r["item_id"], "reason": "missing or out-of-range p_confidence"})
            continue
        ans = r.get("answer")
        if ans is None or not str(ans).strip():
            excluded.append({"row": r["item_id"], "reason": "missing answer"})
            continue
        conf.append(c)
        correct.append(bool(G.grade_item(it, ans)["correct"]))
        cp = conf01(r.get("a_confidence"))
        if cp is not None:
            conf_post.append((cp, correct[-1]))
    out = {"pre_answer": _pack(conf, correct)} if correct else {"pre_answer": None}
    if len(conf_post) == len(correct) and conf_post:
        out["post_answer"] = _pack([c for c, _ in conf_post], [k for _, k in conf_post])
    if correct:
        out["ci"] = {
            "auroc2": _ci(conf, correct, M.auroc2, N_BOOT),
            "delta_e": _ci(conf, correct, M.delta_e, N_BOOT),
            "ece10": _ci(conf, correct, M.ece, N_BOOT),
        }
        out["baselines"] = B.kb_a_baselines(correct, conf, seed=20261005)
        out["calibration_ablation"] = B.calibration_ablation(conf, correct)
        out["reliability_bins"] = M.reliability_bins(conf, correct, 10)
        out["accuracy_binned_auroc2"] = _binned(correct, conf)
    return out


def _binned(correct: Sequence[bool], conf: Sequence[float]) -> Dict:
    """AUROC2 within coarse performance strata (guards against matching simply
    by first-order ability, as with the model-side stratified analysis)."""
    if not correct:
        return {}
    n = len(correct)
    order = sorted(range(n), key=lambda i: (conf[i], i))
    out = {}
    for label, lo, hi in (("low_conf_half", 0, n // 2), ("high_conf_half", n // 2, n)):
        idx = order[lo:hi]
        out[label] = {"n": len(idx),
                      "accuracy": M.accuracy([correct[i] for i in idx]),
                      "auroc2": M.auroc2([conf[i] for i in idx], [correct[i] for i in idx])}
    return out


def score_kb_b(rows: List[dict], items: Dict[str, dict], excluded: List[dict]) -> Dict:
    conf, correct, abstain, unans = [], [], [], []
    for r in rows:
        it = items.get(r["item_id"])
        if it is None or it["_family"] != "KB-B":
            excluded.append({"row": r["item_id"], "reason": "unknown item_id / family mismatch"})
            continue
        c = conf01(r.get("a_confidence"))
        if c is None:
            excluded.append({"row": r["item_id"], "reason": "missing or out-of-range a_confidence"})
            continue
        ans = r.get("answer") or ""
        grade = G.grade_item(it, ans)
        ca = tri(r.get("can_answer"))
        if ca is None:                       # same fallback as runner.run_kb_b
            ca = not bool(grade["declared_unknown"]) if str(ans).strip() else None
        conf.append(c)
        correct.append(bool(grade["correct"]))
        abstain.append(ca is False)
        unans.append(not bool(it["answerable"]))
    out: Dict = {"n": len(correct)}
    if not correct:
        return {"n": 0}
    out.update({
        "confidence_metrics": _pack(conf, correct),
        "ci": {"auroc2": _ci(conf, correct, M.auroc2, N_BOOT),
               "delta_e": _ci(conf, correct, M.delta_e, N_BOOT)},
        "over_claim_rate": M.over_claim_rate([not a for a in abstain], unans),
        "balanced_abstention": M.balanced_abstention_score(abstain, unans),
        "abstention_auroc_from_confidence": M.abstention_auroc([1.0 - c for c in conf], unans),
        "controls": B.kb_b_controls(
            [{"answerable": not u, "abstain": a, "confidence": c, "correct": k}
             for u, a, c, k in zip(unans, abstain, conf, correct)]),
        "accuracy_binned_auroc2": _binned(correct, conf),
        "reliability_bins": M.reliability_bins(conf, correct, 10),
    })
    return out


def score_kb_c(rows: List[dict], items: Dict[str, dict], excluded: List[dict]) -> Dict:
    """Budget is consumed in CSV row order, exactly like runner.run_kb_c."""
    tokens = BUDGET
    recs, used_items = [], []
    for r in rows:
        it = items.get(r["item_id"])
        if it is None or it["_family"] != "KB-C":
            excluded.append({"row": r["item_id"], "reason": "unknown item_id / family mismatch"})
            continue
        d = (r.get("decision") or "").strip().lower()
        d = "ask_help" if "help" in d else ("do_it" if d in ("do_it", "doit", "do") else None)
        if d is None:
            excluded.append({"row": r["item_id"], "reason": "missing/invalid decision"})
            continue
        ans = r.get("answer") or ""
        granted = bool(d == "ask_help" and tokens > 0)
        if granted:
            tokens -= 1
            points = DISCOUNT                 # oracle supplies the ground truth
        else:
            points = 1.0 if G.grade_item(it, ans)["correct"] else 0.0
        recs.append({"decision": d, "points": points, "granted": granted})
        used_items.append(it)
    if not recs:
        return {"n": 0}
    points = [x["points"] for x in recs]
    decisions = [x["decision"] for x in recs]
    res = {
        "n": len(recs),
        "utility": sum(points) / len(points),
        "help_calls_granted": sum(1 for x in recs if x["granted"]),
        "tokens_left": tokens,
        "confidence_metrics": None,
        "policies": B.kb_c_policies(used_items, points, decisions, BUDGET, DISCOUNT),
    }
    return res


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Score a KnowBound human-baseline CSV.")
    ap.add_argument("--csv", required=True, help="CSV following the collection protocol")
    ap.add_argument("--out-dir", default=HERE, help="where to write human_results.{json,md}")
    ap.add_argument("--validate-only", action="store_true",
                    help="only check the header/shape, never compute metrics")
    args = ap.parse_args(argv)

    items = load_items()
    try:
        rows = read_rows(args.csv)
    except FileNotFoundError:
        print(f"[error] CSV not found: {args.csv}")
        return 2

    parts = sorted({(r.get("participant_id") or "").strip() for r in rows})
    print(f"[info] csv={args.csv}  rows={len(rows)}  participants={len(parts)}")
    if args.validate_only:
        counts = {f: sum(1 for r in rows if (r.get('family') or '').strip() == f) for f in FAMILIES}
        print(f"[info] rows per family: {counts}")
        print("[validate] header and shape OK (no metrics computed)")
        return 0

    if not rows:
        print("[info] no human data collected yet -> no metrics written "
              "(a human baseline must never be invented).")
        return 0

    excluded: List[dict] = []
    by_fam: Dict[str, List[dict]] = {f: [] for f in FAMILIES}
    for r in rows:
        fam = (r.get("family") or "").strip().upper()
        if fam in by_fam:
            by_fam[fam].append(r)
        else:
            excluded.append({"row": r.get("item_id"), "reason": f"unknown family '{fam}'"})

    pooled = {
        "KB-A": score_kb_a(by_fam["KB-A"], items, excluded),
        "KB-B": score_kb_b(by_fam["KB-B"], items, excluded),
        "KB-C": score_kb_c(by_fam["KB-C"], items, excluded),
    }

    per_part: Dict[str, Dict] = {}
    for p in parts:
        sub = {f: [r for r in by_fam[f] if (r.get("participant_id") or "").strip() == p]
               for f in FAMILIES}
        ex: List[dict] = []
        per_part[p] = {
            "KB-A": score_kb_a(sub["KB-A"], items, ex),
            "KB-B": score_kb_b(sub["KB-B"], items, ex),
            "KB-C": score_kb_c(sub["KB-C"], items, ex),
            "excluded": ex,
        }

    payload = {
        "generated": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_csv": os.path.abspath(args.csv),
        "n_rows": len(rows),
        "n_participants": len(parts),
        "participants": parts,
        "unit_of_analysis": "one (participant x item) response; bootstrap resamples responses",
        "excluded_rows": excluded,
        "pooled": pooled,
        "per_participant": per_part,
        "metric_source": "knowbound.{grading,metrics,baselines,stats} (identical code path as model runs)",
        "caveat": "human data scored on the same code as the models, but the collection channel "
                  "(verbal/paper + CSV entry) and the analysis unit (participant x item) differ "
                  "from the model runs (item); intervals are response-level and understate "
                  "within-participant dependence.",
    }

    os.makedirs(args.out_dir, exist_ok=True)
    jpath = os.path.join(args.out_dir, "human_results.json")
    with open(jpath, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    mpath = os.path.join(args.out_dir, "human_results.md")
    with open(mpath, "w", encoding="utf-8") as fh:
        fh.write(render_md(payload))
    print(f"[ok] wrote {jpath}")
    print(f"[ok] wrote {mpath}")
    return 0


def _fmt(v, nd=4):
    if v is None or (isinstance(v, float) and v != v):
        return "n/a"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def render_md(p: Dict) -> str:
    L = ["# KnowBound 人类基线结果 / Human baseline results", "",
         f"- 生成时间：{p['generated']}",
         f"- 数据来源：`{p['source_csv']}`（{p['n_rows']} 行，{p['n_participants']} 名被试）",
         f"- 计分代码：{p['metric_source']}（与模型评测同一份实现）",
         f"- 分析单位：{p['unit_of_analysis']}", "",
         f"> 口径差异声明：{p['caveat']}", ""]

    a = p["pooled"].get("KB-A") or {}
    if a.get("pre_answer"):
        pre = a["pre_answer"]
        L += ["## KB-A（60 题，两阶段）", "",
              "| 指标 | 值 |", "| --- | --- |",
              f"| n | {pre['n']} |",
              f"| accuracy | {_fmt(pre['accuracy'])} |",
              f"| DeltaE (confidence - correctness) | {_fmt(pre['delta_e'])} |",
              f"| |DeltaE| | {_fmt(pre['abs_delta_e'])} |",
              f"| AUROC2 | {_fmt(pre['auroc2'])} |",
              f"| ECE-10 | {_fmt(pre['ece10'])} |",
              f"| Brier | {_fmt(pre['brier'])} |", ""]
        ci = a.get("ci") or {}
        if ci.get("auroc2"):
            L += [f"- AUROC2 (response-level bootstrap): {S.summarise_ci(ci['auroc2'])}",
                  f"- DeltaE 95% CI: {S.summarise_ci(ci['delta_e'])}",
                  f"- ECE-10 95% CI: {S.summarise_ci(ci['ece10'])}", ""]
        if a.get("post_answer"):
            L += [f"- 作答后置信度 AUROC2（次级）：{_fmt(a['post_answer']['auroc2'])}，"
                  f"ΔE = {_fmt(a['post_answer']['delta_e'])}", ""]

    b = p["pooled"].get("KB-B") or {}
    if b.get("confidence_metrics"):
        cm = b["confidence_metrics"]
        L += ["## KB-B（40 题）", "",
              "| 指标 | 值 |", "| --- | --- |",
              f"| n | {b['n']} |",
              f"| accuracy | {_fmt(cm['accuracy'])} |",
              f"| AUROC2 | {_fmt(cm['auroc2'])} |",
              f"| ECE-10 | {_fmt(cm['ece10'])} |",
              f"| over-claim rate | {_fmt(b['over_claim_rate'])} |",
              f"| Balanced Abstention Score | {_fmt(b['balanced_abstention'])} |",
              f"| 弃答 AUROC (1-confidence) | {_fmt(b['abstention_auroc_from_confidence'])} |", ""]

    c = p["pooled"].get("KB-C") or {}
    if c.get("utility") is not None and c.get("n"):
        pol = c.get("policies") or {}
        L += ["## KB-C（20 题，预算 6，求助折扣 0.7）", "",
              "| 策略 | 效用 |", "| --- | --- |",
              f"| 人类实际决策 | {_fmt(c['utility'])} |",
              f"| always_do_it（完美解题者） | {_fmt(pol.get('always_do_it'))} |",
              f"| always_ask_help（按题序耗令牌） | {_fmt(pol.get('always_ask_help'))} |",
              f"| random / chance_utility | {_fmt(pol.get('chance_utility'))} |",
              f"| oracle 上界（只在不可答时求助） | {_fmt(pol.get('oracle_policy'))} |",
              f"| 归一化效用（相对 do_it/oracle 区间） | {_fmt(pol.get('normalised_utility'))} |", "",
              f"- 实际消耗令牌：{c['help_calls_granted']} / {BUDGET}（剩余 {c['tokens_left']}）",
              f"- 求助决策 AUROC（vs 不可答）："
              f"{_fmt((pol.get('model') or {}).get('ask_help_auroc_vs_unanswerable'))}", ""]

    if p["excluded_rows"]:
        L += ["## 被排除的行", ""]
        for e in p["excluded_rows"]:
            L.append(f"- `{e['row']}`：{e['reason']}")
        L.append("")

    L += ["## 与模型数字的对照", "",
          "模型侧数字见 `../results/summary.md`（两个模型的 KB-A/KB-B/KB-C 全部指标与 bootstrap CI）。",
          "文献参照值见 `lenovo_human_baseline_literature.md`（非本地实测数据）。", ""]
    return "\n".join(L)


if __name__ == "__main__":
    raise SystemExit(main())
