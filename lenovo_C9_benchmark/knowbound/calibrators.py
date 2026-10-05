"""Post-hoc calibration baselines for KnowBound.

Two standard recalibration maps are fitted on the *same* items that are then
scored, which is the usual in-domain (oracle) recalibration setting. This is
intentional: it gives recalibration the best possible chance, so that the
benchmark can show that **calibration error and metacognitive discrimination
are different things** -- both maps below are monotone in the raw confidence,
therefore they cannot change AUROC2.

  * temperature scaling : p' = sigmoid(logit(p) / T), T fitted by minimising
                          log loss on a grid;
  * isotonic regression : monotone step function fitted with the
                          pool-adjacent-violators algorithm (PAVA).
"""

from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

_EPS = 1e-6


def _clip(p):
    return np.clip(np.asarray(p, dtype=float), _EPS, 1 - _EPS)


def _logit(p):
    p = _clip(p)
    return np.log(p / (1 - p))


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def log_loss(conf: Sequence[float], correct: Sequence[bool]) -> float:
    p = _clip(conf)
    y = np.asarray([1.0 if k else 0.0 for k in correct])
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


# ---------------------------------------------------------------------------
# temperature scaling
# ---------------------------------------------------------------------------

def fit_temperature(conf: Sequence[float], correct: Sequence[bool],
                    lo: float = 0.02, hi: float = 50.0, iters: int = 200) -> float:
    """Golden-section search for T minimising log loss (1-D, no scipy needed)."""
    z = _logit(conf)
    y = np.asarray([1.0 if k else 0.0 for k in correct])

    def loss(T):
        p = _clip(_sigmoid(z / T))
        p = np.clip(p, _EPS, 1 - _EPS)
        return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))

    gr = (5 ** 0.5 - 1) / 2
    a, b = lo, hi
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = loss(c), loss(d)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = loss(c)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = loss(d)
        if abs(b - a) < 1e-8:
            break
    return float((a + b) / 2)


def apply_temperature(conf: Sequence[float], T: float):
    return list(_sigmoid(_logit(conf) / T))


# ---------------------------------------------------------------------------
# isotonic regression (PAVA)
# ---------------------------------------------------------------------------

def fit_isotonic(conf: Sequence[float], correct: Sequence[bool]) -> Tuple[List[float], List[float]]:
    """Return (x_knots, y_knots) of the monotone non-decreasing fit."""
    order = np.argsort(np.asarray(conf, dtype=float), kind="mergesort")
    xs = np.asarray(conf, dtype=float)[order]
    ys = np.asarray([1.0 if k else 0.0 for k in correct])[order]
    w = np.ones_like(ys)
    # PAVA
    val, wt, cnt = [], [], []
    for y in ys:
        val.append(y)
        wt.append(1.0)
        cnt.append(1)
        while len(val) > 1 and val[-2] > val[-1]:
            v2, w2, c2 = val.pop(), wt.pop(), cnt.pop()
            v1, w1, c1 = val.pop(), wt.pop(), cnt.pop()
            val.append((v1 * w1 + v2 * w2) / (w1 + w2))
            wt.append(w1 + w2)
            cnt.append(c1 + c2)
    yy = []
    for v, c in zip(val, cnt):
        yy.extend([v] * c)
    return list(xs), list(yy)


def apply_isotonic(conf: Sequence[float], knots) -> List[float]:
    xs, ys = knots
    return list(np.interp(np.asarray(conf, dtype=float), xs, ys))
