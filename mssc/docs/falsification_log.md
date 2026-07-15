# Falsification Log — MSSC Module

**Purpose:** Record every test result, positive and negative, with enough
detail to reconstruct or audit the analysis. A null result entered here
with full methodology is as scientifically valuable as a positive one.

**Format:** Each entry must include date, dataset, method, raw numbers,
and conclusion. No entry may be deleted — mark superseded entries
`[SUPERSEDED by ENTRY-NNN]`.

---

## Entry format template

```
### ENTRY-NNN — <YYYY-MM-DD>

**Dataset:** <CAP n1–n16 / SHHS subset / other>
**Stub mode:** <Yes / No — if Yes, this entry is INVALID for inference>
**Analysis script:** <script name + git commit hash>
**Method:** <brief method description with parameter values>

**Results:**
- Observed value: X.XXXX
- Surrogate mean: X.XXXX ± X.XXXX (N surrogates)
- p-value (uncorrected): X.XXXX
- p-value (Bonferroni-corrected, k=3): X.XXXX
- Effect size (z): X.XX
- Significant at α=0.05 (corrected): Yes / No

**Conclusion:** <what this result means for H1, in one sentence>
**Open questions raised:**
```

---

## Log entries

*(No entries yet — populated after first real-data run)*

---

## Aggregate summary table

| Entry | Date | Dataset | Metric | p_corrected | z | Significant |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

---

## Notes on record-keeping

- Entries are append-only. Do not edit or remove prior entries.
- If a bug is found in analysis code, add a new entry with the corrected
  result and reference the original entry as superseded.
- Stub-mode runs must be explicitly flagged and excluded from the
  aggregate summary.
- The first date on which all CREP gate conditions (a)–(d) are
  simultaneously met should be recorded here as a milestone entry.
