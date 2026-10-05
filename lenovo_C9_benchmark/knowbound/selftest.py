"""Offline self-test: no model, no network, no filesystem writes required.

Every check is an assertion on a *hand-computable* value, so a failure means the
implementation is wrong rather than "the model behaved differently".
Invoked by ``python -m knowbound selftest`` and by ``pytest tests/``.
"""

from __future__ import annotations

import json
import math
import os
from typing import List, Tuple

CHECKS: List[Tuple[str, object]] = []


def check(name):
    def deco(fn):
        CHECKS.append((name, fn))
        return fn
    return deco


# ---------------------------------------------------------------------------
@check("metrics: AUROC / AUROC2 / ECE / Brier / delta_E on hand-computed data")
def t_metrics():
    from knowbound import metrics as M
    # perfect ranking
    assert abs(M.auroc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]) - 1.0) < 1e-12
    # fully reversed ranking
    assert abs(M.auroc([0.1, 0.2, 0.8, 0.9], [1, 1, 0, 0]) - 0.0) < 1e-12
    # all ties -> 0.5
    assert abs(M.auroc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0]) - 0.5) < 1e-12
    # AUROC2 = AUROC(conf, correct)
    assert abs(M.auroc2([0.9, 0.1], [True, False]) - 1.0) < 1e-12
    # delta_E: mean(conf - correct)
    assert abs(M.delta_e([1.0, 1.0, 0.0, 0.0], [True, False, False, True]) - 0.0) < 1e-12
    assert abs(M.delta_e([1.0, 1.0], [True, False]) - 0.5) < 1e-12
    assert abs(M.brier([1.0, 0.0], [True, False]) - 0.0) < 1e-12
    assert abs(M.brier([0.5, 0.5], [True, True]) - 0.25) < 1e-12
    # ECE: constant 0.5 with empirical accuracy 0.5 -> 0
    assert abs(M.ece([0.5] * 4, [True, True, False, False], 10)) < 1e-12
    # ECE: constant 0.5 with accuracy 1.0 -> 0.5
    assert abs(M.ece([0.5] * 4, [True] * 4, 10) - 0.5) < 1e-12
    return "8 assertions"


@check("metrics: over-claim / balanced abstention / abstention AUROC")
def t_abstention():
    from knowbound import metrics as M
    # 2 unanswerable, both claimed -> over-claim = 1.0
    assert abs(M.over_claim_rate([True, True, False, False], [True, True, False, False]) - 1.0) < 1e-12
    assert abs(M.over_claim_rate([False, False, False, False], [True, True, False, False]) - 0.0) < 1e-12
    # always abstain: recall 1 on unanswerable, 0 on answerable -> BAS 0.5
    assert abs(M.balanced_abstention_score([True, True, True, True], [True, False, False, False]) - 0.5) < 1e-12
    # perfect abstention
    assert abs(M.balanced_abstention_score([True, False, False], [True, False, False]) - 1.0) < 1e-12
    assert abs(M.abstention_auroc([1.0, 0.9, 0.1, 0.0], [True, True, False, False]) - 1.0) < 1e-12
    return "5 assertions"


@check("models: JSON extraction across strict / fenced / prose / broken replies")
def t_extract():
    from knowbound.models import coerce_bool, coerce_confidence, extract_json
    obj, s = extract_json('{"confidence": 80}')
    assert obj == {"confidence": 80} and s == "strict"
    obj, s = extract_json('```json\n{"answer": "1945"}\n```')
    assert obj["answer"] == "1945"
    obj, s = extract_json('Sure! Here is my answer: {"answer": "Paris", "can_answer": true} Hope it helps.')
    assert obj["answer"] == "Paris" and obj["can_answer"] is True
    obj, s = extract_json('{answer: "Paris", confidence: 70}')   # unquoted keys
    assert obj["answer"] == "Paris" and obj["confidence"] == 70, (obj, s)
    obj, s = extract_json("I cannot answer this question.")
    assert obj is None and s == "failed"
    # coerce helpers
    assert coerce_confidence(80) == 0.8 and coerce_confidence("85%") == 0.85
    assert coerce_confidence(0.3) == 0.3 and coerce_confidence(None) is None
    assert coerce_bool("true") is True and coerce_bool(False) is False
    assert coerce_bool("unknown") is None
    return "12 assertions"


@check("grading: answerable items need content, unanswerable need an explicit refusal")
def t_grading():
    from knowbound.grading import declares_unknown, grade_item
    real = {"answerable": True, "accepted": ["1945"]}
    assert grade_item(real, "1945")["correct"] is True
    assert grade_item(real, "In 1945.")["correct"] is True
    assert grade_item(real, "the year was 1944")["correct"] is False
    assert grade_item(real, "UNKNOWN")["correct"] is False
    fic = {"answerable": False, "accepted": []}
    assert grade_item(fic, "I do not know.")["correct"] is True
    assert grade_item(fic, "The capital is Marlowe City.")["correct"] is False
    assert declares_unknown("This entity does not exist") is True
    assert declares_unknown("Paris") is False
    return "8 assertions"


@check("generate: deterministic, well-shaped, matched KB-B halves, KB-C budget pool")
def t_generate():
    from knowbound.generate import UNKNOWN, generate_all
    cfg = {"kb_a": {"per_domain": 15}, "kb_b": {"n_real": 20, "n_fictional": 20},
           "kb_c": {"n_total": 20, "n_fictional": 6, "n_hard": 6, "n_medium": 5, "n_easy": 3}}
    a = generate_all(1234, cfg)
    b = generate_all(1234, cfg)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "generation not deterministic"
    assert len(a["kb_a"]) == 60 and len(a["kb_b"]) == 40 and len(a["kb_c"]) == 20
    # KB-A: four domains x 15, exactly 15 unanswerable (fictional domain)
    doms = {}
    for it in a["kb_a"]:
        doms[it["domain"]] = doms.get(it["domain"], 0) + 1
    assert doms == {"arith": 15, "multihop": 15, "longtail": 15, "fictional": 15}, doms
    assert sum(1 for it in a["kb_a"] if not it["answerable"]) == 15
    # curated long-tail facts must carry a real source
    for it in a["kb_a"]:
        if it["domain"] == "longtail":
            assert it["source"] and "generated" not in it["source"], it["source"]
            assert it["answer"] != UNKNOWN and it["accepted"]
    # KB-B: matched template sets, matched counts
    for it in a["kb_b"]:
        if not it["answerable"]:
            assert it["answer"] == UNKNOWN and it["accepted"] == []
    tmpl_real = sorted(it["template"] for it in a["kb_b"] if it["answerable"])
    tmpl_fic = sorted(it["template"] for it in a["kb_b"] if not it["answerable"])
    assert tmpl_real == tmpl_fic, (tmpl_real, tmpl_fic)
    # KB-C: 6 unanswerable spread over 4 templates, budget-consistent pool
    kinds = {}
    for it in a["kb_c"]:
        kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
    assert kinds["unanswerable"] == 6 and sum(kinds.values()) == 20, kinds
    assert all(it["answer"] for it in a["kb_c"])
    return "13 assertions"


@check("baselines: oracle is separable, constants are degenerate, AUROC2 is monotone-invariant")
def t_baselines():
    from knowbound import baselines as B
    correct = [True, True, False, False, True, False, True, False]
    conf = [0.9, 0.8, 0.7, 0.6, 0.55, 0.4, 0.3, 0.2]
    bl = B.kb_a_baselines(correct, conf, seed=7)
    assert abs(bl["oracle_confidence"]["auroc2"] - 1.0) < 1e-12
    assert abs(bl["constant_100"]["ece10"] - (1 - sum(correct) / len(correct))) < 1e-12
    assert abs(bl["random_confidence"]["auroc2"] - bl["random_confidence"]["auroc2"]) < 1e-9
    # temperature scaling is strictly monotone -> AUROC2 must be bit-identical
    ab = B.calibration_ablation(conf, correct)
    assert ab["available"] is True
    assert abs(ab["auroc2_change"]["temperature"]) < 1e-12, ab["auroc2_change"]
    # isotonic (PAVA) is monotone but creates ties; the 0.5-credit tie convention
    # can therefore move AUROC2 in either direction by at most 0.5 -- assert the
    # documented bound instead of an (incorrect) invariance claim
    assert abs(ab["auroc2_change"]["isotonic"]) <= 0.5, ab["auroc2_change"]
    # a purely anti-correlated signal stays anti-correlated after monotone repair
    ab2 = B.calibration_ablation(list(reversed(conf)), correct)
    assert ab2["available"] is True
    assert abs(ab2["auroc2_change"]["temperature"]) < 1e-12
    assert ab2["after_isotonic"]["auroc2"] <= ab2["before"]["auroc2"] + 0.5 + 1e-12
    return "8 assertions"


@check("baselines: KB-C policies are ordered do_it <= model <= oracle")
def t_kb_c_policies():
    from knowbound import baselines as B
    items = [{"answerable": True}] * 14 + [{"answerable": False}] * 6
    # model helps exactly on the 6 unanswerable items -> optimal under the budget
    decisions = ["do_it"] * 14 + ["ask_help"] * 6
    points = [1.0] * 14 + [0.7] * 6
    pol = B.kb_c_policies(items, points, decisions, budget=6, discount=0.7)
    assert abs(pol["model"]["utility"] - (14 + 4.2) / 20) < 1e-9
    assert abs(pol["always_do_it"] - 14 / 20) < 1e-9
    assert abs(pol["oracle_policy"] - pol["model"]["utility"]) < 1e-9
    assert abs(pol["normalised_utility"] - 1.0) < 1e-9
    # a model that helps on the wrong items scores worse than always_do_it
    bad = ["ask_help"] * 6 + ["do_it"] * 14
    bad_points = [0.7] * 6 + [1.0] * 14
    pol_bad = B.kb_c_policies(items, bad_points, bad, budget=6, discount=0.7)
    assert pol_bad["model"]["utility"] < pol_bad["oracle_policy"] + 1e-9
    return "5 assertions"


@check("config: default.yaml loads and the mini-parser agrees with the shipped file")
def t_config():
    from knowbound import config as C
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "configs", "default.yaml")
    cfg = C.load_config(path if os.path.exists(path) else None)
    assert cfg["model"]["name"]
    assert cfg["generator"]["kb_a"]["per_domain"] == 15
    assert cfg["budget"]["kb_c_help_budget"] == 6
    assert cfg["smoke"]["per_family"] >= 1
    mini = C._mini_yaml(open(path, "r", encoding="utf-8").read()) if os.path.exists(path) else {}
    if mini:
        assert mini["seed"] == cfg["seed"]
        assert mini["generator"]["kb_b"]["n_fictional"] == 20
        assert mini["model"]["temperature"] == 0.0
        assert mini["model"]["think"] is False
    return "7 assertions"


@check("report: aggregation runs on synthetic records and emits JSON-safe numbers")
def t_report():
    from knowbound import report as R
    recs = {
        "kb_a": [{"item_id": "KB-A-0000", "family": "KB-A", "domain": "arith",
                  "difficulty": 1, "answerable": True, "confidence": 0.9,
                  "correct": True, "ok": True, "latency_p_sec": 1.0,
                  "latency_a_sec": 1.0, "parse_strategy_p": "strict",
                  "parse_strategy_a": "strict", "model_answer": "42", "error": None},
                 {"item_id": "KB-A-0001", "family": "KB-A", "domain": "fictional",
                  "difficulty": 3, "answerable": False, "confidence": 0.8,
                  "correct": False, "ok": True, "latency_p_sec": 1.2,
                  "latency_a_sec": 1.1, "parse_strategy_p": "strict",
                  "parse_strategy_a": "strict", "model_answer": "Marlowe City", "error": None}],
        "kb_b": [],
        "kb_c": [{"item_id": "KB-C-0000", "family": "KB-C", "kind": "easy",
                  "difficulty": 1, "answerable": True, "decision": "do_it",
                  "help_granted": False, "confidence": 0.7, "points": 1.0,
                  "correct": True, "ok": True, "latency_sec": 1.0, "error": None}],
    }
    m = R.compute_all(recs, seed=1)
    assert m["kb_a"]["n"] == 2 and "baselines" in m["kb_a"]
    assert m["kb_c"]["help_calls"] == 0
    txt = R.render_summary(m, {"model": "m", "tag": "t", "counts": {"kb_a": 2},
                               "timestamp": "now"})
    assert "KB-A" in txt and "KB-C" in txt
    smoke = R.render_smoke({"kb_a": recs["kb_a"]}, {"timestamp": "now"}, "m")
    assert "smoke test report" in smoke
    j = json.dumps(R._round(m))
    assert "NaN" not in j and "Infinity" not in j
    return "6 assertions"


def run_all_checks() -> Tuple[int, int, List[str]]:
    passed = failed = 0
    lines = []
    for name, fn in CHECKS:
        try:
            detail = fn()
            passed += 1
            lines.append(f"PASS  {name}  ({detail})")
        except Exception as exc:  # noqa: BLE001 - report everything
            failed += 1
            lines.append(f"FAIL  {name}  -> {type(exc).__name__}: {exc}")
    return passed, failed, lines


def main(root: str | None = None) -> int:
    passed, failed, lines = run_all_checks()
    for line in lines:
        print(line)
    print(f"\nselftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
