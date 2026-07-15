"""Cross-scale coherence metrics between HRV (autonomic) and EEG (CNS).

Two complementary metrics are computed:
- Cross-correlation: linear, lag-resolved coupling
- Transfer entropy: directed, nonlinear information flow

References
----------
Schreiber T (2000). Measuring information transfer.
    Phys Rev Lett 85(2), 461–464. [Transfer entropy]
Box GEP, Jenkins GM (1976). Time Series Analysis.
    [Cross-correlation]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)

# Bins for Transfer Entropy histogram estimation
_TE_BINS = 16

# Allowed lag range for cross-correlation (in samples)
_MAX_LAG_FRACTION = 0.1


@dataclass
class CoherenceResult:
    """Coupling metrics between one HRV and one EEG time series."""

    subject_id: str
    # Cross-correlation
    xcorr_peak: float
    xcorr_peak_lag: int
    xcorr_values: np.ndarray
    xcorr_lags: np.ndarray
    # Transfer entropy (HRV→EEG and EEG→HRV)
    te_hrv_to_eeg: float
    te_eeg_to_hrv: float
    te_asymmetry: float  # te_hrv_to_eeg - te_eeg_to_hrv
    # Metadata
    n_samples_hrv: int
    n_samples_eeg: int
    method_notes: str = (
        "xcorr: Pearson cross-correlation on z-scored series; "
        "TE: histogram estimator (Schreiber 2000), k=1 lag, 16 bins"
    )


def compute_coherence(
    hrv_series: np.ndarray,
    eeg_series: np.ndarray,
    subject_id: str = "unknown",
    allow_stubs: bool = False,
) -> CoherenceResult:
    """Compute cross-correlation and transfer entropy between HRV and EEG.

    Both series are resampled to equal length via linear interpolation before
    analysis. This is appropriate when they represent the same temporal span
    (e.g. one sleep epoch) but different native sampling rates.

    Parameters
    ----------
    hrv_series:
        1D array of RR intervals (ms) or any HRV-derived scalar series.
    eeg_series:
        1D array of EEG coherence values (one per epoch) or spectral power.
    subject_id:
        Identifier for logging/reporting.
    allow_stubs:
        Set ``True`` only in unit tests with synthetic data; production
        analysis should always pass real data.

    Returns
    -------
    CoherenceResult
    """
    if len(hrv_series) < 10 or len(eeg_series) < 10:
        raise ValueError(
            f"Time series too short for coherence estimation "
            f"(HRV: {len(hrv_series)}, EEG: {len(eeg_series)}, minimum: 10)."
        )

    if not np.isfinite(hrv_series).all() or not np.isfinite(eeg_series).all():
        raise ValueError("Input series contain NaN or Inf values. Clean the data first.")

    n = min(len(hrv_series), len(eeg_series))
    hrv = _zscore(_resample(hrv_series, n))
    eeg = _zscore(_resample(eeg_series, n))

    xcorr, lags = _cross_correlation(hrv, eeg)
    peak_idx = int(np.argmax(np.abs(xcorr)))
    xcorr_peak = float(xcorr[peak_idx])
    xcorr_peak_lag = int(lags[peak_idx])

    te_hrv_to_eeg = _transfer_entropy(hrv, eeg)
    te_eeg_to_hrv = _transfer_entropy(eeg, hrv)

    return CoherenceResult(
        subject_id=subject_id,
        xcorr_peak=xcorr_peak,
        xcorr_peak_lag=xcorr_peak_lag,
        xcorr_values=xcorr,
        xcorr_lags=lags,
        te_hrv_to_eeg=te_hrv_to_eeg,
        te_eeg_to_hrv=te_eeg_to_hrv,
        te_asymmetry=te_hrv_to_eeg - te_eeg_to_hrv,
        n_samples_hrv=len(hrv_series),
        n_samples_eeg=len(eeg_series),
    )


def _zscore(x: np.ndarray) -> np.ndarray:
    std = np.std(x)
    if std < 1e-12:
        return np.zeros_like(x)
    return (x - np.mean(x)) / std


def _resample(x: np.ndarray, n: int) -> np.ndarray:
    if len(x) == n:
        return x.astype(float)
    old_idx = np.linspace(0, 1, len(x))
    new_idx = np.linspace(0, 1, n)
    return np.interp(new_idx, old_idx, x.astype(float))


def _cross_correlation(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Normalized Pearson cross-correlation for a range of lags."""
    n = len(x)
    max_lag = max(1, int(n * _MAX_LAG_FRACTION))
    lags = np.arange(-max_lag, max_lag + 1)
    xcorr = np.array([_pearson_at_lag(x, y, int(lag)) for lag in lags])
    return xcorr, lags


def _pearson_at_lag(x: np.ndarray, y: np.ndarray, lag: int) -> float:
    if lag >= 0:
        a, b = x[lag:], y[: len(x) - lag]
    else:
        a, b = x[: len(x) + lag], y[-lag:]
    if len(a) < 2:
        return 0.0
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _transfer_entropy(source: np.ndarray, target: np.ndarray, k: int = 1) -> float:
    """Histogram-based transfer entropy (Schreiber 2000).

    TE(source → target) = H(target_t | target_{t-1}) - H(target_t | target_{t-1}, source_{t-1})

    Uses equal-width binning. For small samples, this estimator is biased;
    correct by comparing against surrogate distribution in null_hypothesis_test.py.
    """
    bins = _TE_BINS
    s = source[:-1]
    t_past = target[:-1]
    t_fut = target[1:]

    # Joint and marginal histograms
    def _hist(*arrays: np.ndarray) -> np.ndarray:
        edges = [np.linspace(a.min(), a.max() + 1e-9, bins + 1) for a in arrays]
        counts, _ = np.histogramdd(np.column_stack(arrays), bins=edges)
        p = counts / counts.sum()
        return p

    p_tfut_tpast_s = _hist(t_fut, t_past, s)
    p_tpast_s = _hist(t_past, s)
    p_tfut_tpast = _hist(t_fut, t_past)
    p_tpast = _hist(t_past)

    # TE = sum p(t_fut, t_past, s) * log[ p(t_fut|t_past,s) / p(t_fut|t_past) ]
    # Reindex: p_tfut_tpast_s has shape (bins_tfut, bins_tpast, bins_s)
    p3 = p_tfut_tpast_s
    p2s = np.broadcast_to(p_tpast_s[np.newaxis, :, :], p3.shape)  # (tf, tp, s)
    p2 = np.broadcast_to(p_tfut_tpast[:, :, np.newaxis], p3.shape)
    p1 = np.broadcast_to(p_tpast[np.newaxis, :, np.newaxis], p3.shape)

    valid = (p3 > 0) & (p2s > 0) & (p2 > 0) & (p1 > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(valid, np.log2(np.where(valid, p3 * p1 / (p2s * p2), 1.0)), 0.0)
    te = float(np.sum(p3 * ratio))
    return max(0.0, te)
