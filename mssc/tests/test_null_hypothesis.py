"""Tests for null_hypothesis_test.py."""

from __future__ import annotations

import numpy as np

from mssc.analysis.null_hypothesis_test import phase_randomise, run_null_test


class TestPhaseRandomise:
    def test_same_length(self) -> None:
        rng = np.random.default_rng(0)
        x = rng.standard_normal(256)
        s = phase_randomise(x, rng)
        assert len(s) == len(x)

    def test_amplitude_spectrum_preserved(self) -> None:
        rng = np.random.default_rng(1)
        x = rng.standard_normal(256)
        s = phase_randomise(x, rng)
        assert np.allclose(np.abs(np.fft.rfft(x)), np.abs(np.fft.rfft(s)), atol=1e-8)

    def test_different_from_original(self) -> None:
        rng = np.random.default_rng(2)
        x = np.sin(np.linspace(0, 10 * np.pi, 512))
        s = phase_randomise(x, rng)
        assert not np.allclose(x, s)


class TestRunNullTest:
    def test_returns_three_metrics(self) -> None:
        rng = np.random.default_rng(42)
        x = rng.standard_normal(200)
        y = rng.standard_normal(200)
        results = run_null_test(x, y, n_surrogates=50, seed=0)
        assert len(results) == 3
        metrics = {r.metric for r in results}
        assert metrics == {"xcorr_peak", "te_hrv_to_eeg", "te_eeg_to_hrv"}

    def test_p_values_in_range(self) -> None:
        rng = np.random.default_rng(5)
        x = rng.standard_normal(150)
        y = rng.standard_normal(150)
        results = run_null_test(x, y, n_surrogates=50, seed=1)
        for r in results:
            assert 0.0 <= r.p_value <= 1.0
            assert 0.0 <= r.p_value_corrected <= 1.0

    def test_bonferroni_correction_applied(self) -> None:
        rng = np.random.default_rng(7)
        x = rng.standard_normal(200)
        y = rng.standard_normal(200)
        results = run_null_test(x, y, n_surrogates=50, seed=2)
        for r in results:
            assert r.n_corrections == 3
            assert r.p_value_corrected >= r.p_value

    def test_perfectly_coupled_is_significant(self) -> None:
        """Perfectly coupled series should yield significant xcorr."""
        t = np.linspace(0, 10 * np.pi, 300)
        x = np.sin(t) + 0.05 * np.random.default_rng(99).standard_normal(300)
        y = np.sin(t)
        results = run_null_test(x, y, n_surrogates=100, seed=3)
        xcorr_result = next(r for r in results if r.metric == "xcorr_peak")
        assert xcorr_result.is_significant(), (
            f"Expected significant xcorr for identical series, "
            f"got p={xcorr_result.p_value_corrected}"
        )
