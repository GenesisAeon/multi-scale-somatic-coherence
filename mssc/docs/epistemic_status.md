# Epistemic Status — MSSC Module

**Last updated:** 2026-07-15
**Module version:** 0.1.0-exploratory

---

## A. What follows directly from the data

The following statements are only entered here once the corresponding
analysis code has been run on real PhysioNet data and results logged in
`falsification_log.md`. Until then, each item is marked **(pending)**.

| Claim | Status | Evidence location |
|---|---|---|
| Statistically significant cross-correlation between HRV and EEG-coherence in CAP healthy subjects | **(pending)** | `falsification_log.md` → CAP xcorr test |
| Transfer entropy (HRV→EEG) significantly exceeds phase-randomised surrogate baseline | **(pending)** | `falsification_log.md` → CAP TE test |
| Result replicates in SHHS independent cohort | **(pending)** | `falsification_log.md` → SHHS replication |

---

## B. What is interpretation within the UTAC framework

The following claims go beyond raw data and assume the UTAC formalisation
maps onto biological reality. They are interpretations, not results:

- "The coupling coefficient falls within a known UTAC β-cluster" — this
  is a CI-overlap comparison, not proof that biological systems follow
  renormalisation-group dynamics.
- "HRV and EEG co-vary as coupled attractors" — language borrowed from
  dynamical systems theory; validity depends on the quality of the
  scaling fit (R² threshold) and on conditions (A) and (B) above both
  holding.

---

## C. What remains open hypothesis

- **H1 (core):** Multi-scale physiological coherence follows the same
  β-cluster structure as other UTAC domains. This is untested.
  It may be confirmed, refuted, or found to require a new cluster category.
- Whether the coupling direction (HRV→EEG vs. EEG→HRV) is consistent
  across subjects and sleep stages — highly variable individual differences
  expected.
- Whether the coupling changes systematically across NREM/REM/wake
  (third falsifiable sub-question from the spec) — requires sleep-staging
  labels from CAP annotations.

---

## D. Known limitations — must not be omitted from publications

### Sample size (n=16, CAP healthy controls)

Per-subject time-series analysis is statistically sound: a full-night
recording (~7 hours) yields thousands of RR intervals and hundreds of
30-second EEG epochs. Transfer-entropy estimation is feasible at this
resolution.

**Group-level inference is underpowered.** With n=16 and a typical
two-tailed test (α=0.05, power=0.80), the minimum detectable effect size
is approximately d≈0.72 (medium-to-large by Cohen's conventions). Null
results at this n do not rule out small-to-medium coupling effects.
Any group-level p-value must be reported alongside effect size and CI;
"no significant group effect" must not be interpreted as "no coupling exists."

### Estimator bias

Histogram-based transfer entropy is positively biased for small samples.
The surrogate comparison in `null_hypothesis_test.py` controls for this
bias at the individual level, but does not eliminate it. For group-level
TE comparisons, consider a bias-corrected estimator (e.g. KSG, Kraskov
et al. 2004) in future iterations.

### Stub data

If any adapter returned stubs due to network/library unavailability,
the corresponding results are excluded from this document entirely.
See `falsification_log.md` for flags on each run.

---

## CREP Integration Gate status

Per the MSSC specification, Section 6.1, results may only be registered
as CREP domain 18 when all five conditions are simultaneously satisfied.
Gate status is a three-state enum: `blocked` → `pending_review` → `passed`
(see `mssc/crep_gate.py`). The five-condition requirement reflects the
P41 ↔ P49 validation loop: condition (e) is the empirical bridge between
the Ρ_sem theory (P41) and the TIP instrument (P49).

| Condition | Key | Criterion | Current status |
|---|---|---|---|
| (a) Coupling statistically significant | `coupling_significant` | p_corrected < 0.05, ≥80% subjects | `False` |
| (b) Null hypothesis excluded | `null_excluded` | effect_size_z ≥ 2.0 | `False` |
| (c) β-fit stable | `beta_fit_stable` | R² ≥ 0.90, ≥75% subjects, ≥2 datasets | `False` |
| (d) Replication on SHHS cohort | `replicated_shhs` | independent cohort | `False` |
| (e) Ρ_sem/TIP correlation tested | `rho_sem_correlation_tested` | Spearman ρ ≥ 0.3, n ≥ 30 pairs | `False` |

**Current gate status: `blocked`** (no conditions satisfied yet)

---

## Connection to Ρ_sem (scope-resilience, P41)

### P41 ↔ P49 validation loop

P41 (scope-resilience) provides the theoretical Ρ_sem framework.
P49 (genesis-mssc / TIP) provides the only external behavioural test of
that framework without access to model internals. This is a validation
loop, not a circular dependency:

- **P41 → P49 (conceptual):** the Ρ_sem formula generates a testable
  prediction about observable TIP scores.
- **P49 → P41 (empirical):** TIP results either support or falsify the
  prediction, updating the evidential status of the Ρ_sem framework.

Neither package is independently validated until condition (e) is satisfied.

### Pre-registered falsification criterion

**Hypothesis:** A model on a high-resilience semantic path (high Ρ_sem)
produces more consistent outputs under temporal perturbation (higher TIP
consistency score) than a model on a low-resilience path.

**Rejection criterion (pre-registered):**
Spearman ρ < 0.3 at n ≥ 30 path-perturbation pairs refutes the hypothesis.

This threshold is fixed in `mssc/crep_gate.py` as
`RHO_SEM_FALSIFICATION_THRESHOLD = 0.3` and `RHO_SEM_MIN_SAMPLE_SIZE = 30`
**before any TIP runs against P41 data.** Post-hoc adjustment of this
threshold invalidates the test and must be treated as a protocol deviation,
logged separately in `falsification_log.md`.

**This is a testable prediction, not a confirmed result.**

### Falsification protocol (three steps)

1. Compute Ρ_sem for ≥ 30 model/prompt pairs via P41.
2. Run TIP on the same pairs under matched temporal perturbations
   (at least one of: `temporal_shuffle`, `contradiction_injection`,
   `gap_injection`).
3. Compute Spearman ρ between TIP consistency scores and Ρ_sem values.
   Log the result in `falsification_log.md` with run timestamp, n,
   observed ρ, and verdict (supported / refuted / inconclusive if n < 30).

Until step 3 is executed, condition (e) remains `False` and gate status
remains `blocked`.
