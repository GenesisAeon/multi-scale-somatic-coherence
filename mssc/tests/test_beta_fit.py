"""Tests for beta_fit.py."""

from __future__ import annotations

import numpy as np
import pytest

from mssc.analysis.beta_fit import fit_scaling_exponent


class TestFitScalingExponent:
    def test_known_power_law(self) -> None:
        """Perfect power law x^(-2) should recover exponent ≈ -2."""
        x = np.arange(1, 101, dtype=float)
        values = x ** (-2.0)
        result = fit_scaling_exponent(values, seed=0, n_bootstrap=200)
        assert abs(result.exponent - (-2.0)) < 0.15
        assert result.r_squared > 0.95

    def test_ci_contains_true_exponent(self) -> None:
        """Bootstrap CI should contain the true exponent at 95% level."""
        x = np.arange(1, 51, dtype=float)
        values = x ** (-3.5)
        result = fit_scaling_exponent(values, seed=1, n_bootstrap=500)
        assert result.exponent_ci_low <= -3.5 <= result.exponent_ci_high

    def test_pure_noise_low_r_squared(self) -> None:
        rng = np.random.default_rng(42)
        values = np.abs(rng.standard_normal(50)) + 0.01
        result = fit_scaling_exponent(values, seed=2, n_bootstrap=100)
        assert result.r_squared < 0.5

    def test_cluster_overlap_detected(self) -> None:
        """An exponent near the 'biological' cluster centre should overlap."""
        x = np.arange(1, 100, dtype=float)
        # biological cluster centre ≈ 7.4 → exponent 7.4 in log-log space
        values = np.exp(7.4 * np.log(x))
        result = fit_scaling_exponent(values, seed=3, n_bootstrap=200)
        assert result.cluster_overlap.get("biological", False), (
            f"Expected biological cluster overlap, got exponent={result.exponent:.2f}, "
            f"CI=[{result.exponent_ci_low:.2f}, {result.exponent_ci_high:.2f}]"
        )

    def test_too_few_points_raises(self) -> None:
        with pytest.raises(ValueError, match="at least 5"):
            fit_scaling_exponent(np.array([1.0, 2.0, 3.0]))

    def test_nonpositive_values_raises(self) -> None:
        values = np.array([-1.0] + [1.0] * 20)
        with pytest.raises(ValueError, match="strictly positive"):
            fit_scaling_exponent(values)
