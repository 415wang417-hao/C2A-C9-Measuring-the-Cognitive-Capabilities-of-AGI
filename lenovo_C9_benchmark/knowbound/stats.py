"""Non-parametric bootstrap utilities (pure Python, no scipy).

Item-level metrics in KnowBound live on 20-60 items, so point estimates need an
uncertainty band and cross-model claims need a test. We therefore use the
**percentile bootstrap over items**:

* resample items with replacement (the item is the unit of analysis, which is
  what we want to generalise over: *new items of the same families*),
* recompute the metric on every resample,
* report the 2.5% / 97.5% percentiles as a 95% interval.

For two models the *same* item indices are drawn for both models (the two runs
see an identical item set), i.e. a **paired** bootstrap; the interval of the
difference is then the honest object to look at, and "the interval excludes 0"
is the significance statement used in the report.

Nothing here assumes normality, and degenerate resamples (e.g. all-correct
samples where AUROC is undefined) are dropped rather than silently replaced.
"""

from __future__ import annotations

import random
from typing import Callable, Dict, List, Optional, Sequence


def percentile(values: Sequence[float], q: float) -> Optional[float]:
    """Linear-interpolated percentile (q in [0, 1]). None for an empty input."""
    vals = sorted(v for v in values if v == v)          # drop NaN
    if not vals:
        return None
    if len(vals) == 1:
        return float(vals[0])
    pos = q * (len(vals) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(vals) - 1)
    frac = pos - lo
    return float(vals[lo] * (1.0 - frac) + vals[hi] * frac)


def bootstrap(
    stat_fn: Callable[[List[int]], float],
    n_items: int,
    n_boot: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
) -> Dict[str, Optional[float]]:
    """Percentile bootstrap for ``stat_fn(indices) -> float``.

    Returns ``{"point", "lo", "hi", "n_boot", "n_defined", "alpha"}`` where
    ``point`` is the statistic on the full sample (indices ``range(n_items)``).
    """
    rng = random.Random(seed)
    point = _safe(stat_fn(list(range(n_items))))
    samples = []
    for _ in range(n_boot):
        idx = [rng.randrange(n_items) for _ in range(n_items)]
        v = _safe(stat_fn(idx))
        if v == v:
            samples.append(v)
    return {
        "point": point,
        "lo": percentile(samples, alpha / 2.0),
        "hi": percentile(samples, 1.0 - alpha / 2.0),
        "n_boot": n_boot,
        "n_defined": len(samples),
        "alpha": alpha,
    }


def bootstrap_diff(
    stat_fn: Callable[[List[int], List[int]], float],
    n_items: int,
    n_boot: int = 2000,
    seed: int = 0,
    alpha: float = 0.05,
) -> Dict[str, Optional[float]]:
    """Paired bootstrap for ``stat_fn(idx_a, idx_b) -> float`` (e.g. B - A).

    The two index lists are drawn for the same resampled *items*, which is what
    makes the interval a paired statement (both models answered the same items).
    """
    rng = random.Random(seed)
    point = _safe(stat_fn(list(range(n_items)), list(range(n_items))))
    samples = []
    for _ in range(n_boot):
        idx = [rng.randrange(n_items) for _ in range(n_items)]
        v = _safe(stat_fn(idx, list(idx)))
        if v == v:
            samples.append(v)
    return {
        "point": point,
        "lo": percentile(samples, alpha / 2.0),
        "hi": percentile(samples, 1.0 - alpha / 2.0),
        "n_boot": n_boot,
        "n_defined": len(samples),
        "alpha": alpha,
    }


def _safe(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def verdict(diff: Dict[str, Optional[float]]) -> str:
    """Turn a paired-difference interval into the report's significance wording."""
    lo, hi = diff.get("lo"), diff.get("hi")
    if lo is None or hi is None:
        return "undefined (too few defined resamples)"
    if lo > 0 or hi < 0:
        return "separates the two models (95% CI excludes 0)"
    return f"no detectable difference at this n (95% CI [{lo:+.4f}, {hi:+.4f}] spans 0)"


def verdict_contrast(diff: Dict[str, Optional[float]], reference: str) -> str:
    """Same test, but for a contrast against a *reference policy*, not a model.

    ``diff`` is (model - reference); the wording names the direction so a
    negative point estimate is never silently read as "better".
    """
    lo, hi = diff.get("lo"), diff.get("hi")
    if lo is None or hi is None:
        return "undefined (too few defined resamples)"
    if lo > 0:
        return f"above {reference} (95% CI excludes 0)"
    if hi < 0:
        return f"below {reference} (95% CI excludes 0)"
    return f"indistinguishable from {reference} at this n (95% CI [{lo:+.4f}, {hi:+.4f}] spans 0)"


def summarise_ci(ci: Dict[str, Optional[float]], nd: int = 4) -> str:
    if ci.get("point") is None or ci.get("lo") is None:
        return "n/a"
    return f"{ci['point']:.{nd}f} [{ci['lo']:.{nd}f}, {ci['hi']:.{nd}f}]"
