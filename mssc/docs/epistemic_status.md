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
as CREP domain 18 when all four conditions are simultaneously satisfied:

| Condition | Current status |
|---|---|
| (a) Coupling statistically significant | PENDING |
| (b) Null hypothesis excluded (effect size) | PENDING |
| (c) β-fit stable across ≥2 datasets | PENDING |
| (d) Replication on SHHS cohort | PENDING |

**Current gate status: BLOCKED (no conditions satisfied yet)**
