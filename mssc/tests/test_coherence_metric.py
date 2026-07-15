"""Tests for coherence_metric.py using synthetic edge-case signals."""

from __future__ import annotations

import numpy as np
import pytest

from mssc.analysis.coherence_metric import compute_coherence, _zscore, _transfer_entropy


def _sine(n: int, freq: float = 0.1) -> np.ndarray:
    t = np.linspace(0, 2 * np.pi * freq * n, n)
    return np.sin(t)


class TestPerfectCoupling:
    """Identical signals should yield xcorr_peak ≈ 1.0 at lag 0."""

    def test_xcorr_peak_near_one(self) -> None:
        s = _sine(500)
        result = compute_coherence(s, s, subject_id="test_identical")
        assert abs(result.xcorr_peak) > 0.99
        assert result.xcorr_peak_lag == 0

    def test_te_non_negative(self) -> None:
        # Histogram TE is max(0, ...) — must always be non-negative
        s = _sine(500)
        result = compute_coherence(s, s)
        assert result.te_hrv_to_eeg >= 0.0
        assert result.te_eeg_to_hrv >= 0.0


class TestNoCoupling:
    """Independent random signals should have xcorr near 0."""

    def test_xcorr_near_zero(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.standard_normal(1000)
        y = rng.standard_normal(1000)
        result = compute_coherence(x, y)
        assert abs(result.xcorr_peak) < 0.3

    def test_te_near_zero(self) -> None:
        rng = np.random.default_rng(99)
        x = rng.standard_normal(500)
        y = rng.standard_normal(500)
        result = compute_coherence(x, y)
        assert result.te_hrv_to_eeg >= 0.0
        assert result.te_eeg_to_hrv >= 0.0


class TestPureNoise:
    """White noise baseline: xcorr and TE should be near zero."""

    def test_returns_result(self) -> None:
        rng = np.random.default_rng(7)
        x = rng.standard_normal(300)
        y = rng.standard_normal(300)
        result = compute_coherence(x, y, subject_id="noise_test")
        assert result.subject_id == "noise_test"
        assert np.isfinite(result.xcorr_peak)
        assert np.isfinite(result.te_hrv_to_eeg)


class TestInputValidation:
    def test_too_short_raises(self) -> None:
        x = np.array([1.0, 2.0, 3.0])
        y = np.array([1.0, 2.0, 3.0])
        with pytest.raises(ValueError, match="too short"):
            compute_coherence(x, y)

    def test_nan_raises(self) -> None:
        x = np.array([1.0, np.nan] + [1.0] * 20)
        y = np.ones(22)
        with pytest.raises(ValueError, match="NaN or Inf"):
            compute_coherence(x, y)

    def test_different_lengths_ok(self) -> None:
        rng = np.random.default_rng(0)
        x = rng.standard_normal(300)
        y = rng.standard_normal(400)
        result = compute_coherence(x, y)
        assert result.n_samples_hrv == 300
        assert result.n_samples_eeg == 400


class TestZscore:
    def test_constant_returns_zeros(self) -> None:
        x = np.ones(50) * 3.14
        assert np.allclose(_zscore(x), 0.0)

    def test_mean_zero_std_one(self) -> None:
        rng = np.random.default_rng(1)
        x = rng.standard_normal(200) * 5 + 10
        z = _zscore(x)
        assert abs(np.mean(z)) < 1e-10
        assert abs(np.std(z) - 1.0) < 1e-6
