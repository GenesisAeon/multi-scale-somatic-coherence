"""CREP integration gate status for MSSC.

Three-state enum matches the planned genesis-os Three-Tier classification
(Core / Scientific / Experimental):

  blocked        — one or more gate conditions unmet; results not registrable
  pending_review — all five conditions met, awaiting independent review
  passed         — conditions met and independently reviewed; domain 18 active

Current status: blocked (all five conditions pending).

P41 ↔ P49 validation loop
--------------------------
P41 (scope-resilience) provides the theoretical Ρ_sem framework.
P49 (genesis-mssc / TIP) provides the only external behavioural test
of that framework. Neither is independently validated until condition (e)
below is satisfied. This is a validation loop, not a circular dependency:
the arrow P41 → P49 is conceptual (theory → instrument); the arrow
P49 → P41 is empirical (falsification result → theory status).
"""

from __future__ import annotations

from enum import StrEnum


class CREPGateStatus(StrEnum):
    BLOCKED = "blocked"
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"


# Five simultaneous conditions required for domain-18 registration.
# Update each entry (False → True) only when the corresponding evidence
# is logged in mssc/docs/falsification_log.md with a run timestamp.
#
# Pre-registered falsification threshold for condition (e):
#   Spearman ρ < 0.3 at n ≥ 30 path-perturbation pairs refutes the
#   Ρ_sem/TIP correlation hypothesis. This threshold is fixed here
#   BEFORE the test is run; post-hoc adjustment invalidates the test.
GATE_CONDITIONS: dict[str, bool] = {
    "coupling_significant": False,        # (a) p_corrected < 0.05, ≥80% subjects
    "null_excluded": False,               # (b) effect_size_z ≥ 2.0
    "beta_fit_stable": False,             # (c) R² ≥ 0.90, ≥75% subjects, ≥2 datasets
    "replicated_shhs": False,             # (d) independent SHHS cohort replication
    "rho_sem_correlation_tested": False,  # (e) Spearman ρ ≥ 0.3, n ≥ 30, vs P41 Ρ_sem
}

# Pre-registered rejection threshold — do not modify after first TIP run.
RHO_SEM_FALSIFICATION_THRESHOLD = 0.3
RHO_SEM_MIN_SAMPLE_SIZE = 30


def current_gate_status() -> CREPGateStatus:
    """Return the current CREP gate status derived from GATE_CONDITIONS."""
    if all(GATE_CONDITIONS.values()):
        return CREPGateStatus.PASSED
    return CREPGateStatus.BLOCKED
