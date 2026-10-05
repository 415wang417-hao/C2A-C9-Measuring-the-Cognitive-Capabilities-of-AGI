"""KnowBound metrics.

All metrics follow the KSTAR-style metacognition formulation used by this
benchmark. Confidence is always expressed on [0, 1] internally.

Definitions (also mirrored in README.md and task_description.md)
----------------------------------------------------------------
DeltaE        = confidence - correctness, averaged over items   (bias)
|DeltaE|     = mean absolute calibration gap
AUROC2        = AUROC of confidence in separating correct from incorrect items
ECE-10        = expected calibration error with 10 equal-width confidence bins
Brier         = mean((confidence - correctness)^2)
over-claim    = P(model claims to be able to answer | item is unanswerable)
AUROC_abstain = AUROC of the abstention score in separating unanswerable from
                answerable items
BAS           = balanced abstention score
                = 0.5 * (abstention rate on unanswerable
                         + answer rate on answerable)
"""

from __future__ import annotations

from typing import Iterable, List, Sequence


# ---------------------------------------------------------------------------
# ranking
# ---------------------------------------------------------------------------

def _rankdata(values: Sequence[float]) -> List[float]:
    """Average ranks (1-based) with proper tie handling."""
    idx = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and values[idx[j + 1]] == values[idx[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[idx[k]] = avg
        i = j + 1
    return ranks


def auroc(scores: Sequence[float], labels: Sequence[int]) -> float:
    """AUROC with tie-aware ranks. Returns float('nan') when undefined."""
    pairs = [(s, int(l)) for s, l in zip(scores, labels)]
    pos = [s for s, l in pairs if l == 1]
    neg = [s for s, l in pairs if l == 0]
    if not pos or not neg:
        return float("nan")
    allv = [s for s, _ in pairs]
    ranks = _rankdata(allv)
    rank_sum_pos = 0.0
    for (s, l), r in zip(pairs, ranks):
        if l == 1:
            rank_sum_pos += r
    n_pos, n_neg = len(pos), len(neg)
    return (rank_sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)


# ---------------------------------------------------------------------------
# core calibration metrics
# ---------------------------------------------------------------------------

def accuracy(correct: Sequence[bool]) -> float:
    correct = list(correct)
    return sum(1 for c in correct if c) / len(correct) if correct else float("nan")


def delta_e(conf: Sequence[float], correct: Sequence[bool]) -> float:
    """Mean signed gap = mean(confidence - correctness)."""
    conf, correct = list(conf), list(correct)
    if not conf:
        return float("nan")
    return sum(c - (1.0 if k else 0.0) for c, k in zip(conf, correct)) / len(conf)


def abs_delta_e(conf: Sequence[float], correct: Sequence[bool]) -> float:
    conf, correct = list(conf), list(correct)
    if not conf:
        return float("nan")
    return sum(abs(c - (1.0 if k else 0.0)) for c, k in zip(conf, correct)) / len(conf)


def brier(conf: Sequence[float], correct: Sequence[bool]) -> float:
    conf, correct = list(conf), list(correct)
    if not conf:
        return float("nan")
    return sum((c - (1.0 if k else 0.0)) ** 2 for c, k in zip(conf, correct)) / len(conf)


def ece(conf: Sequence[float], correct: Sequence[bool], bins: int = 10) -> float:
    """Expected calibration error with equal-width bins over [0, 1]."""
    conf, correct = list(conf), list(correct)
    if not conf:
        return float("nan")
    n = len(conf)
    total = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        members = [(c, k) for c, k in zip(conf, correct)
                   if (lo <= c < hi) or (b == bins - 1 and c == 1.0)]
        if not members:
            continue
        m = len(members)
        acc = sum(1 for _, k in members if k) / m
        avg_conf = sum(c for c, _ in members) / m
        total += (m / n) * abs(acc - avg_conf)
    return total


def reliability_bins(conf: Sequence[float], correct: Sequence[bool], bins: int = 10):
    """Return per-bin (lo, hi, count, avg_conf, accuracy, gap) for reporting."""
    conf, correct = list(conf), list(correct)
    out = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        members = [(c, k) for c, k in zip(conf, correct)
                   if (lo <= c < hi) or (b == bins - 1 and c == 1.0)]
        if not members:
            out.append({"bin": f"[{lo:.1f},{hi:.1f})", "n": 0,
                        "avg_confidence": None, "accuracy": None, "gap": None})
            continue
        m = len(members)
        acc = sum(1 for _, k in members if k) / m
        ac = sum(c for c, _ in members) / m
        out.append({"bin": f"[{lo:.1f},{hi:.1f})", "n": m,
                    "avg_confidence": ac, "accuracy": acc, "gap": acc - ac})
    return out


def auroc2(conf: Sequence[float], correct: Sequence[bool]) -> float:
    return auroc(list(conf), [1 if k else 0 for k in correct])


# ---------------------------------------------------------------------------
# KB-B / KB-C specific
# ---------------------------------------------------------------------------

def over_claim_rate(can_answer: Sequence[bool], unanswerable: Sequence[bool]) -> float:
    """P(can_answer = True | item is unanswerable)."""
    hits = [(c, u) for c, u in zip(can_answer, unanswerable) if u]
    if not hits:
        return float("nan")
    return sum(1 for c, _ in hits if c) / len(hits)


def balanced_abstention_score(abstain: Sequence[bool], unanswerable: Sequence[bool]) -> float:
    """0.5 * (abstention recall on unanswerable + answer recall on answerable)."""
    un = [(a, u) for a, u in zip(abstain, unanswerable)]
    pos = [a for a, u in un if u]
    neg = [a for a, u in un if not u]
    if not pos or not neg:
        return float("nan")
    tpr = sum(1 for a in pos if a) / len(pos)          # abstain on unanswerable
    tnr = sum(1 for a in neg if not a) / len(neg)      # answer on answerable
    return 0.5 * (tpr + tnr)


def abstention_auroc(need_help_score: Sequence[float], unanswerable: Sequence[bool]) -> float:
    """Higher `need_help_score` must mean 'more likely unanswerable'."""
    return auroc(list(need_help_score), [1 if u else 0 for u in unanswerable])


# ---------------------------------------------------------------------------
# stratified analysis (metacognition vs first-order ability)
# ---------------------------------------------------------------------------

def stratify(items: Sequence[dict], conf: Sequence[float], correct: Sequence[bool],
             tol: float = 0.15, model_names: Sequence[str] = ("a", "b")):
    """Compare AUROC2 inside difficulty bins where the two models' accuracies match."""
    out = {}
    for it, c, k in zip(items, conf, correct):
        out.setdefault(it.get("difficulty", 2), []).append((c, k))
    table = []
    for d in sorted(out):
        rec = {"difficulty": d, "n": len(out[d])}
        rec["accuracy"] = accuracy([k for _, k in out[d]])
        rec["auroc2"] = auroc2([c for c, _ in out[d]], [k for _, k in out[d]])
        table.append(rec)
    return table
