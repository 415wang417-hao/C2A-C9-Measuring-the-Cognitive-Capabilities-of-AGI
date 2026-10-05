"""Baselines and ablations -- all numbers are computed from real run data.

The point of this module is to answer two reviewer questions:

1. *Is the metric trivially satisfiable?*  Random / constant confidence policies
   are scored with exactly the same metric code as the model, so the model's
   AUROC2 / ECE can be read against a trivial-agent floor.
2. *Is "good calibration" the same thing as "metacognition"?*  We re-calibrate
   the model's own confidences with temperature scaling and isotonic regression.
   Temperature scaling is a *strictly* monotone map, so it can move ECE while
   leaving the ranking (AUROC2) bit-for-bit identical: calibration can be
   purchased, discrimination cannot.  Isotonic regression (PAVA) is monotone but
   collapses adjacent violations into ties; because the tie-corrected AUROC
   awards 0.5 credit to tied pairs, a tie-creating map can move AUROC2 slightly in
   **either** direction -- an artefact of the tie convention, not a genuine change
   in discrimination.  The *raw* AUROC2 is therefore treated as the headline
   number and the isotonic deltas are reported transparently.

Nothing here is hard-coded: every baseline is derived from the run's
``(confidence, correct)`` pairs.
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from . import metrics as M
from .calibrators import (apply_isotonic, apply_temperature, fit_isotonic,
                          fit_temperature)


def _pack(conf: Sequence[float], correct: Sequence[bool]) -> Dict[str, Any]:
    return {
        "accuracy": M.accuracy(correct),
        "auroc2": M.auroc2(conf, correct),
        "ece10": M.ece(conf, correct, 10),
        "brier": M.brier(conf, correct),
        "delta_e": M.delta_e(conf, correct),
        "abs_delta_e": M.abs_delta_e(conf, correct),
    }


def kb_a_baselines(correct: Sequence[bool], conf: Sequence[float],
                   seed: int = 0) -> Dict[str, Dict[str, Any]]:
    """Trivial confidence policies vs. the model, on identical items."""
    n = len(list(correct))
    rng = random.Random(seed)
    out: Dict[str, Dict[str, Any]] = {}
    out["model"] = _pack(conf, correct)
    out["random_confidence"] = _pack([rng.random() for _ in range(n)], correct)
    out["constant_100"] = _pack([1.0] * n, correct)
    out["constant_50"] = _pack([0.5] * n, correct)
    out["oracle_confidence"] = _pack([1.0 if c else 0.0 for c in correct], correct)
    if n:
        out["_reference"] = {"n_items": n,
                             "base_rate": sum(1 for c in correct if c) / n}
    return out


def calibration_ablation(conf: Sequence[float], correct: Sequence[bool],
                         seed: int = 0) -> Dict[str, Any]:
    """ECE / AUROC2 before and after monotone recalibration.

    Note the honest caveat reported alongside the numbers: the calibration map
    is fitted on the *same* items it is evaluated on, so the post-hoc ECE is an
    optimistically biased estimate of generalisation; AUROC2, being invariant to
    monotone maps, is reported as the leakage-free comparison.
    """
    conf = list(conf)
    correct = list(correct)
    pairs = [(c, k) for c, k in zip(conf, correct) if c is not None]
    if len(pairs) < 3:
        return {"available": False, "reason": "fewer than 3 usable confidence values"}
    c2 = [c for c, _ in pairs]
    k2 = [bool(k) for _, k in pairs]

    T = fit_temperature(c2, k2)
    conf_t = apply_temperature(c2, T)
    knots = fit_isotonic(c2, k2)
    conf_i = apply_isotonic(c2, knots)

    def block(vals):
        return {"ece10": M.ece(vals, k2, 10),
                "auroc2": M.auroc2(vals, k2),
                "brier": M.brier(vals, k2),
                "delta_e": M.delta_e(vals, k2)}

    return {
        "available": True,
        "n_items": len(k2),
        "temperature": T,
        "isotonic_knots": len(list(zip(*knots))) if knots and len(knots) == 2 else 0,
        "before": block(c2),
        "after_temperature": block(conf_t),
        "after_isotonic": block(conf_i),
        "auroc2_change": {
            "temperature": block(conf_t)["auroc2"] - block(c2)["auroc2"],
            "isotonic": block(conf_i)["auroc2"] - block(c2)["auroc2"],
        },
        "caveat": "calibrators are fitted and evaluated on the same items (optimistic ECE); "
                  "temperature scaling is strictly monotone so its AUROC2 change is exactly 0, "
                  "while isotonic creates ties, and the 0.5-credit tie convention can shift "
                  "AUROC2 either way -- such a shift is an artefact, not extra discrimination; "
                  "the raw AUROC2 is therefore the headline metric",
    }


def kb_b_controls(records: Sequence[dict]) -> Dict[str, Any]:
    """Behavioural controls for the abstention decision."""
    unans = [not r["answerable"] for r in records]
    abstain = [bool(r.get("abstain")) for r in records]
    conf = [r.get("confidence") if r.get("confidence") is not None else 0.5 for r in records]
    correct = [bool(r.get("correct")) for r in records]
    # a 'certainty' score for abstention: low confidence => should abstain
    need_help = [1.0 - c for c in conf]
    return {
        "always_abstain": {"balanced_abstention": M.balanced_abstention_score(
            [True] * len(records), unans),
            "accuracy": M.accuracy([False] * len(records)),
            "cheat_flag": "collapses to max abstention recall, zero answer recall"},
        "never_abstain": {"balanced_abstention": M.balanced_abstention_score(
            [False] * len(records), unans),
            "accuracy": M.accuracy(correct)},
        "model": {
            "balanced_abstention": M.balanced_abstention_score(abstain, unans),
            "abstention_auroc_from_confidence": M.abstention_auroc(need_help, unans),
            "over_claim_rate": M.over_claim_rate([not a for a in abstain], unans),
        },
    }


def kb_c_policies(items: Sequence[dict], awarded_points: Sequence[float],
                  decisions: Sequence[str], budget: int = 6,
                  discount: float = 0.7) -> Dict[str, Any]:
    """Score the model's policy against reference policies on the same items.

    Reference policies are evaluated under the same budget rule.  ``always_do_it``
    and ``oracle`` assume a perfect solver on answerable items (an upper bound on
    what any policy could earn); ``always_ask_help`` spends the budget in item
    order, which is what a model without metacognition effectively does.
    """
    items = list(items)
    n = len(items)
    unans = [not it["answerable"] for it in items]

    def score(policy_mask: List[bool]) -> float:
        tokens = budget
        total = 0.0
        for i, helped in enumerate(policy_mask):
            if helped and tokens > 0:
                tokens -= 1
                total += discount
            else:
                total += 0.0 if unans[i] else 1.0
        return total / n if n else float("nan")

    always_do_it = score([False] * n)
    always_help = score([True] * n)
    oracle_mask = [u for u in unans]                      # help exactly on unanswerable
    oracle = score(oracle_mask)
    model_mask = [d == "ask_help" for d in decisions]

    helped_idx = [i for i, h in enumerate(model_mask) if h]
    helpful_share = (sum(1 for i in helped_idx if unans[i]) / len(helped_idx)
                     if helped_idx else float("nan"))

    return {
        "model": {"utility": sum(awarded_points) / n if n else float("nan"),
                  "help_calls": len(helped_idx),
                  "helpful_share_unanswerable": helpful_share,
                  "ask_help_auroc_vs_unanswerable":
                      M.abstention_auroc([1.0 if d == "ask_help" else 0.0 for d in decisions],
                                         unans)},
        "always_do_it": always_do_it,
        "always_ask_help": always_help,
        "oracle_policy": oracle,
        "chance_utility": (always_do_it + always_help) / 2.0,
        "normalised_utility": ((sum(awarded_points) / n - always_do_it)
                               / (oracle - always_do_it)
                               if n and oracle > always_do_it else float("nan")),
    }
