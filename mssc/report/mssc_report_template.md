# MSSC Analysis Report

**Generated:** {{timestamp}}
**Module version:** {{module_version}}
**Git commit:** {{git_commit}}
**Stub mode:** {{stub_mode}} — if Yes, all results below are INVALID for inference

---

## Datasets used

| Role | Database | Records | n subjects | Real data |
|---|---|---|---|---|
| Primary | CAP Sleep Database (capslpdb) | n1–n16 | 16 | {{cap_real}} |
| Replication | Sleep Heart Health Study (shhs) | {{shhs_records}} | {{shhs_n}} | {{shhs_real}} |

---

## Cross-correlation results

### Per-subject (CAP)

| Subject | xcorr_peak | peak_lag | p (uncorr) | p (Bonferroni) | z | Significant |
|---|---|---|---|---|---|---|
{{xcorr_rows}}

**Group summary (n={{n_subjects}}):** {{xcorr_group_summary}}

> ⚠️ n=16 group statistics are underpowered (minimum detectable d≈0.72 at 80% power).
> Report individual-level results as primary; treat group statistics as exploratory.

---

## Transfer entropy results

### HRV → EEG

| Subject | TE (observed) | Surrogate mean±std | p (corr) | z |
|---|---|---|---|---|
{{te_hrv_to_eeg_rows}}

### EEG → HRV

| Subject | TE (observed) | Surrogate mean±std | p (corr) | z |
|---|---|---|---|---|
{{te_eeg_to_hrv_rows}}

---

## Scaling exponent (β-fit) — only populated if coupling is significant

| Subject | β | CI low | CI high | R² | Compatible clusters |
|---|---|---|---|---|---|
{{beta_rows}}

**Note on cluster compatibility:** CI overlap with a UTAC cluster indicates
statistical compatibility only. It is not proof of cluster membership or of
renormalisation-group dynamics in biological systems.

---

## CREP integration gate

| Condition | Met | Evidence |
|---|---|---|
| (a) Coupling significant (p_corrected < 0.05) | {{gate_a}} | `falsification_log.md` |
| (b) Effect size outside surrogate dist. | {{gate_b}} | `falsification_log.md` |
| (c) β-fit stable (CI overlap, ≥2 datasets) | {{gate_c}} | beta_fit output |
| (d) Replication on SHHS | {{gate_d}} | `epistemic_status.md` |

**Gate status:** {{gate_overall}}

---

## Open questions for next iteration

{{open_questions}}

---

## References

- Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, PhysioNet. *Circulation* 101(23), e215–e220.
- Schreiber T (2000). Measuring information transfer. *Phys Rev Lett* 85(2), 461–464.
- Theiler J et al. (1992). Testing for nonlinearity in time series. *Physica D* 58, 77–94.
- Terzano MG et al. (2001). Atlas, rules and recording techniques for the scoring of CAP in human sleep. *Sleep Medicine* 2(6), 537–553.
- Cohen J (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.).
