"""Scaling exponent fitting and comparison against UTAC β-clusters.

Only runs after null_hypothesis_test.py confirms significant coupling.
Reports whether the fitted exponent's confidence interval overlaps with
known UTAC clusters — it does NOT claim cluster membership without
interval overlap.

References
----------
Virkar Y, Clauset A (2014). Power-law distributions in binned empirical data.
    Ann Appl Stat 8(1), 89–119. [MLE power-law fitting]
GenesisAeon UTAC framework — β-cluster registry (internal reference).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Known UTAC β-cluster centres and 95% CI half-widths (internal registry).
# Values are illustrative placeholders — replace with real cluster parameters
# from the live UTAC registry before production use.
UTAC_BETA_CLUSTERS: dict[str, dict[str, float]] = {
    "informational": {"centre": 4.5, "half_width": 0.8},
    "biological": {"centre": 7.4, "half_width": 1.2},
}


@dataclass
class BetaFitResult:
    """Result of scaling-exponent fit and UTAC cluster comparison."""

    subject_id: str
    exponent: float
    exponent_ci_low: float
    exponent_ci_high: float
    n_points: int
    r_squared: float
    # For each UTAC cluster: True if CI overlaps, False otherwise
    cluster_overlap: dict[str, bool]
    compatible_clusters: list[str]
    notes: str = ""


def fit_scaling_exponent(
    values: np.ndarray,
    subject_id: str = "unknown",
    ci_level: float = 0.95,
    n_bootstrap: int = 1000,
    seed: int | None = None,
) -> BetaFitResult:
    """Fit a power-law scaling exponent via log-log OLS + bootstrap CI.

    Parameters
    ----------
    values:
        Positive scalar series to fit (e.g. per-frequency TE values,
        or coupling strength as a function of temporal scale).
    ci_level:
        Confidence level for bootstrap interval (default 0.95).
    n_bootstrap:
        Bootstrap iterations for CI estimation.

    Returns
    -------
    BetaFitResult — always includes CI; cluster_overlap is only
    meaningful when ``r_squared`` is acceptable (>0.7 suggested).
    """
    values = np.asarray(values, dtype=float)
    if len(values) < 5:
        raise ValueError(f"Need at least 5 points for scaling fit, got {len(values)}.")
    if not (values > 0).all():
        raise ValueError("All values must be strictly positive for log-log fit.")

    x = np.log(np.arange(1, len(values) + 1, dtype=float))
    y = np.log(values)

    exp, intercept = _ols(x, y)
    r_sq = _r_squared(x, y, exp, intercept)

    rng = np.random.default_rng(seed)
    bootstrap_exps = _bootstrap_exponent(x, y, n_bootstrap, rng)

    alpha = 1 - ci_level
    ci_low = float(np.percentile(bootstrap_exps, 100 * alpha / 2))
    ci_high = float(np.percentile(bootstrap_exps, 100 * (1 - alpha / 2)))

    overlap, compatible = _check_cluster_overlap(ci_low, ci_high)

    if r_sq < 0.5:
        logger.warning(
            "R²=%.2f for %s — scaling fit is poor; exponent is unreliable.", r_sq, subject_id
        )

    notes = _build_notes(r_sq, compatible, ci_low, ci_high)
    logger.info(
        "%s β=%.2f [%.2f, %.2f] R²=%.2f compatible_clusters=%s",
        subject_id,
        exp,
        ci_low,
        ci_high,
        r_sq,
        compatible or "none",
    )

    return BetaFitResult(
        subject_id=subject_id,
        exponent=float(exp),
        exponent_ci_low=ci_low,
        exponent_ci_high=ci_high,
        n_points=len(values),
        r_squared=float(r_sq),
        cluster_overlap=overlap,
        compatible_clusters=compatible,
        notes=notes,
    )


def _ols(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    A = np.column_stack([x, np.ones_like(x)])
    result = np.linalg.lstsq(A, y, rcond=None)
    slope, intercept = result[0]
    return float(slope), float(intercept)


def _r_squared(x: np.ndarray, y: np.ndarray, slope: float, intercept: float) -> float:
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def _bootstrap_exponent(
    x: np.ndarray, y: np.ndarray, n: int, rng: np.random.Generator
) -> np.ndarray:
    n_pts = len(x)
    exps = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, n_pts, size=n_pts)
        slope, _ = _ols(x[idx], y[idx])
        exps[i] = slope
    return exps


def _check_cluster_overlap(
    ci_low: float, ci_high: float
) -> tuple[dict[str, bool], list[str]]:
    overlap: dict[str, bool] = {}
    compatible: list[str] = []
    for name, cluster in UTAC_BETA_CLUSTERS.items():
        c = cluster["centre"]
        hw = cluster["half_width"]
        cluster_low = c - hw
        cluster_high = c + hw
        overlaps = ci_low <= cluster_high and ci_high >= cluster_low
        overlap[name] = overlaps
        if overlaps:
            compatible.append(name)
    return overlap, compatible


def _build_notes(
    r_sq: float, compatible: list[str], ci_low: float, ci_high: float
) -> str:
    parts = []
    if r_sq < 0.5:
        parts.append(f"R²={r_sq:.2f}: poor fit — treat exponent as indicative only.")
    if compatible:
        parts.append(
            f"CI [{ci_low:.2f}, {ci_high:.2f}] overlaps cluster(s): {', '.join(compatible)}. "
            f"This is a compatibility test, not membership assignment."
        )
    else:
        parts.append(
            f"CI [{ci_low:.2f}, {ci_high:.2f}] does not overlap any known UTAC cluster — "
            f"possibly a new class, or insufficient evidence."
        )
    return " ".join(parts)
