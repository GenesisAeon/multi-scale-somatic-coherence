"""CREP integration gate status for MSSC.

Three-state enum matches the planned genesis-os Three-Tier classification
(Core / Scientific / Experimental):

  blocked       — one or more gate conditions unmet; results not registrable
  pending_review — all four conditions met, awaiting independent review
  passed        — conditions met and independently reviewed; domain 18 active

Current status: blocked (all four conditions pending).
"""

from __future__ import annotations

from enum import StrEnum


class CREPGateStatus(StrEnum):
    BLOCKED = "blocked"
    PENDING_REVIEW = "pending_review"
    PASSED = "passed"


# Four simultaneous conditions required for domain-18 registration.
# Update each entry when evidence is logged in falsification_log.md.
GATE_CONDITIONS: dict[str, bool] = {
    "coupling_significant": False,       # (a) p_corrected < 0.05, ≥80% subjects
    "null_excluded": False,              # (b) effect_size_z ≥ 2.0
    "beta_fit_stable": False,            # (c) R² ≥ 0.90, ≥75% subjects, ≥2 datasets
    "replicated_shhs": False,            # (d) independent SHHS cohort replication
}


def current_gate_status() -> CREPGateStatus:
    """Return the current CREP gate status from GATE_CONDITIONS."""
    if all(GATE_CONDITIONS.values()):
        return CREPGateStatus.PASSED
    return CREPGateStatus.BLOCKED
