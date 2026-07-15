"""Surrogate-data null hypothesis test for cross-scale coupling.

Generates phase-randomised surrogates (Theiler et al. 1992) to test whether
the observed coupling strength exceeds what chance would produce.

All results are reported as p-values AND effect sizes. A p-value alone is
insufficient — see the MSSC specification for why.

References
----------
Theiler J et al. (1992). Testing for nonlinearity in time series.
    Physica D 58(1–4), 77–94. [Phase-randomisation surrogates]
Cohen J (1988). Statistical Power Analysis for the Behavioral Sciences.
    [Effect size conventions]
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from mssc.analysis.coherence_metric import compute_coherence

logger = logging.getLogger(__name__)


@dataclass
class NullTestResult:
    """Outcome of one surrogate null hypothesis test."""

    subject_id: str
    metric: str  # "xcorr_peak" | "te_hrv_to_eeg" | "te_eeg_to_hrv"
    observed_value: float
    surrogate_mean: float
    surrogate_std: float
    n_surrogates: int
    p_value: float
    effect_size_z: float  # (observed - surrogate_mean) / surrogate_std
    # Two-tailed p-value with Bonferroni correction if multiple metrics tested
    p_value_corrected: float | None = None
    n_corrections: int | None = None

    def is_significant(self, alpha: float = 0.05, use_corrected: bool = True) -> bool:
        use_p = (
            self.p_value_corrected
            if (use_corrected and self.p_value_corrected is not None)
            else self.p_value
        )
        return use_p < alpha

    def summary(self) -> str:
        corrected = (
            f", p_corrected={self.p_value_corrected:.4f}"
            if self.p_value_corrected is not None
            else ""
        )
        sig = "SIGNIFICANT" if self.is_significant() else "not significant"
        return (
            f"{self.subject_id} | {self.metric}: observed={self.observed_value:.4f}, "
            f"surrogate_mean={self.surrogate_mean:.4f}±{self.surrogate_std:.4f}, "
            f"z={self.effect_size_z:.2f}, p={self.p_value:.4f}{corrected} [{sig}]"
        )


def phase_randomise(series: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Generate one phase-randomised surrogate of a 1D time series.

    Preserves the amplitude spectrum while destroying temporal structure.
    Valid for testing against linear-correlation null hypotheses.
    (Theiler et al. 1992)
    """
    fft = np.fft.rfft(series)
    n = len(series)
    n_freqs = len(fft)
    phases = rng.uniform(0, 2 * np.pi, size=n_freqs)
    # Keep DC and Nyquist phase unchanged
    phases[0] = 0.0
    if n % 2 == 0:
        phases[-1] = 0.0
    fft_shuffled = np.abs(fft) * np.exp(1j * phases)
    surrogate = np.fft.irfft(fft_shuffled, n=n)
    return surrogate.astype(series.dtype)


def run_null_test(
    hrv_series: np.ndarray,
    eeg_series: np.ndarray,
    subject_id: str = "unknown",
    n_surrogates: int = 500,
    alpha: float = 0.05,
    seed: int | None = None,
) -> list[NullTestResult]:
    """Test coupling significance against phase-randomised surrogates.

    Three metrics are tested with Bonferroni correction:
    - xcorr_peak
    - te_hrv_to_eeg
    - te_eeg_to_hrv

    Parameters
    ----------
    hrv_series, eeg_series:
        Real HRV and EEG time series.
    n_surrogates:
        Number of surrogate samples. 500 gives ~0.002 p-value resolution.
    alpha:
        Family-wise error rate for Bonferroni correction.
    seed:
        RNG seed for reproducibility.

    Returns
    -------
    List of NullTestResult, one per metric. Always three items.
    """
    rng = np.random.default_rng(seed)

    observed = compute_coherence(hrv_series, eeg_series, subject_id=subject_id)
    observed_values = {
        "xcorr_peak": observed.xcorr_peak,
        "te_hrv_to_eeg": observed.te_hrv_to_eeg,
        "te_eeg_to_hrv": observed.te_eeg_to_hrv,
    }

    surrogate_distributions: dict[str, list[float]] = {m: [] for m in observed_values}

    for i in range(n_surrogates):
        hrv_surr = phase_randomise(hrv_series, rng)
        eeg_surr = phase_randomise(eeg_series, rng)
        try:
            surr_result = compute_coherence(hrv_surr, eeg_surr, subject_id=f"{subject_id}_surr{i}")
        except ValueError:
            logger.debug("Surrogate %d failed coherence computation — skipping", i)
            continue
        surrogate_distributions["xcorr_peak"].append(surr_result.xcorr_peak)
        surrogate_distributions["te_hrv_to_eeg"].append(surr_result.te_hrv_to_eeg)
        surrogate_distributions["te_eeg_to_hrv"].append(surr_result.te_eeg_to_hrv)

    results: list[NullTestResult] = []
    n_metrics = len(observed_values)

    for metric, obs_val in observed_values.items():
        dist = np.array(surrogate_distributions[metric])
        if len(dist) < 10:
            logger.warning(
                "Too few valid surrogates for %s (%d) — p-value unreliable", metric, len(dist)
            )

        surr_mean = float(np.mean(dist))
        surr_std = float(np.std(dist, ddof=1)) if len(dist) > 1 else float("nan")
        effect_z = (obs_val - surr_mean) / surr_std if surr_std > 0 else float("nan")

        # Two-tailed p-value: fraction of surrogates with |value| >= |observed|
        p_val = float(np.mean(np.abs(dist) >= abs(obs_val))) if len(dist) > 0 else float("nan")
        # Bonferroni correction
        p_corrected = min(1.0, p_val * n_metrics)

        results.append(
            NullTestResult(
                subject_id=subject_id,
                metric=metric,
                observed_value=obs_val,
                surrogate_mean=surr_mean,
                surrogate_std=surr_std,
                n_surrogates=len(dist),
                p_value=p_val,
                effect_size_z=effect_z,
                p_value_corrected=p_corrected,
                n_corrections=n_metrics,
            )
        )
        logger.info("%s", results[-1].summary())

    return results
