"""Tests for CREPGateStatus enum and gate logic."""

from __future__ import annotations

from mssc.crep_gate import (
    GATE_CONDITIONS,
    RHO_SEM_FALSIFICATION_THRESHOLD,
    RHO_SEM_MIN_SAMPLE_SIZE,
    CREPGateStatus,
    current_gate_status,
)


class TestCREPGateStatus:
    def test_enum_values(self) -> None:
        assert CREPGateStatus.BLOCKED == "blocked"
        assert CREPGateStatus.PENDING_REVIEW == "pending_review"
        assert CREPGateStatus.PASSED == "passed"

    def test_current_status_is_blocked(self) -> None:
        assert current_gate_status() == CREPGateStatus.BLOCKED

    def test_five_conditions_present(self) -> None:
        expected = {
            "coupling_significant",
            "null_excluded",
            "beta_fit_stable",
            "replicated_shhs",
            "rho_sem_correlation_tested",
        }
        assert set(GATE_CONDITIONS.keys()) == expected

    def test_all_conditions_false(self) -> None:
        assert not any(GATE_CONDITIONS.values())

    def test_passed_when_all_true(self) -> None:
        original = dict(GATE_CONDITIONS)
        try:
            for k in GATE_CONDITIONS:
                GATE_CONDITIONS[k] = True
            assert current_gate_status() == CREPGateStatus.PASSED
        finally:
            GATE_CONDITIONS.update(original)

    def test_blocked_when_partial(self) -> None:
        original = dict(GATE_CONDITIONS)
        try:
            GATE_CONDITIONS["coupling_significant"] = True
            assert current_gate_status() == CREPGateStatus.BLOCKED
        finally:
            GATE_CONDITIONS.update(original)

    def test_falsification_threshold_preregistered(self) -> None:
        # These values must not change after the first TIP run against P41 data.
        assert RHO_SEM_FALSIFICATION_THRESHOLD == 0.3
        assert RHO_SEM_MIN_SAMPLE_SIZE == 30
