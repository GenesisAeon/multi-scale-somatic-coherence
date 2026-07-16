# genesis-mssc

**P49 · GenesisAeon genesis-os ecosystem**

> ⚠️ **Pre-Alpha / Exploratory** — results are not ready for clinical, policy, or production use.
> The MSSC CREP integration gate is currently **BLOCKED** (all four conditions pending).
> See [`mssc/docs/epistemic_status.md`](mssc/docs/epistemic_status.md) for the full falsification-first status.

[![CI](https://github.com/GenesisAeon/multi-scale-somatic-coherence/actions/workflows/ci.yml/badge.svg)](https://github.com/GenesisAeon/multi-scale-somatic-coherence/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/genesis-mssc)](https://pypi.org/project/genesis-mssc/)

---

## What this is

`genesis-mssc` bundles two exploratory research submodules:

| Submodule | Full name | Status |
|-----------|-----------|--------|
| `mssc` | Multi-Scale Somatic Coherence Framework | Pre-Alpha · CREP gate BLOCKED |
| `tip` | Temporal Integrity Probe | Pre-Alpha · future P50 candidate |

Both ship together in one wheel at v0.1.0 and will be split into separate packages once each satisfies its own Diamond Interface and CREP criteria.

---

## MSSC — Multi-Scale Somatic Coherence Framework

Measures cross-scale coupling between cardiac (HRV) and neural (EEG) signals from publicly available PhysioNet datasets:

- **CAP Sleep Database** (`capslpdb`) — 16 healthy controls (n1–n16); rich per-subject, underpowered for group inference (min detectable d ≈ 0.72)
- **SHHS** (Sleep Heart Health Study) — larger cohort for replication

Three coupling metrics with phase-randomised surrogate null tests (Theiler 1992, Bonferroni k=3):
- `xcorr_peak` — cross-correlation peak
- `te_hrv_to_eeg` — transfer entropy HRV → EEG
- `te_eeg_to_hrv` — transfer entropy EEG → HRV

β-scaling exponent fitting tested for overlap with UTAC clusters (CI overlap only, not membership claim).

**CREP integration gate** — MSSC qualifies as GenesisAeon domain 18 only when all four conditions hold simultaneously:
1. Coupling significance (p_corrected < 0.05 across ≥ 80% subjects)
2. Surrogate null exclusion (effect_size_z ≥ 2.0)
3. Stable β-fit (R² ≥ 0.90 in ≥ 75% subjects)
4. Independent replication on SHHS cohort

Current status: **all four PENDING → gate BLOCKED**.

---

## TIP — Temporal Integrity Probe

A context-manipulation harness that measures text-behaviour consistency in AI agents under three session modes:

- `dense` — full chronological history
- `sparse` — final states only
- `fragmented` — history with injected manipulations

Three manipulation types: `temporal_shuffle`, `contradiction_injection`, `gap_injection`.

Consistency scoring uses behavioural language only — no mental-state attribution.
See [`mssc/tip/docs/epistemic_boundaries.md`](mssc/tip/docs/epistemic_boundaries.md) for what TIP does and does not measure.

TIP is a future P50 candidate (somatische Entsprechung von `theta-resonance` P27) once it produces Γ_somatic via a full Diamond Interface.

**Open falsifiable hypothesis:** TIP consistency scores are predicted to rank-correlate (Spearman ρ) with Ρ_sem values computed via P41 (scope-resilience). This makes TIP the first behavioural, externally-observable test of the Ρ_sem hallucination-resilience framework — no access to model internals required. *This is a testable prediction, not a confirmed result.* Confirmation requires: (1) computing Ρ_sem for matched model/prompt pairs via P41, (2) running TIP on the same pairs, (3) logging the correlation in `mssc/docs/falsification_log.md`.

---

## Installation

```bash
pip install genesis-mssc
```

Requires Python 3.11+. PhysioNet data is fetched at runtime via `wfdb` — no login required for CAP Sleep DB or SHHS.

## Quick start

```python
from mssc.adapters.physionet_hrv_adapter import load_cap_healthy_subject
from mssc.adapters.physionet_eeg_adapter import load_cap_eeg_subject
from mssc.analysis.coherence_metric import compute_coherence
from mssc.analysis.null_hypothesis_test import run_null_test

hrv = load_cap_healthy_subject("n1")
eeg = load_cap_eeg_subject("n1")

# Coupling strength
result = compute_coherence(hrv.rr_intervals_ms / 1000.0, eeg.epochs.mean(axis=(0, 1)))

# Significance against surrogates
null_results = run_null_test(hrv.rr_intervals_ms / 1000.0, eeg.epochs.mean(axis=(0, 1)),
                             subject_id="n1", n_surrogates=500, seed=42)
for r in null_results:
    print(r.summary())
```

## Development

```bash
git clone https://github.com/GenesisAeon/multi-scale-somatic-coherence
cd multi-scale-somatic-coherence
pip install -e ".[dev]"
pytest
```

---

## Role in the GenesisAeon Ecosystem

`genesis-mssc` is **P49** in the GenesisAeon genesis-os ecosystem registry — somatic coherence / temporal integrity. It is explicitly exploratory and subject to the standard GenesisAeon falsification-first protocol.

The `diamond-setup` scaffold tool (P-INFRA-1) is a separate package with its own PyPI entry and Zenodo DOI.

## Citation

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.PLACEHOLDER.svg)](https://doi.org/10.5281/zenodo.PLACEHOLDER)

DOI will be assigned on first GitHub Release once Zenodo–GitHub integration is enabled.

---

Built within the [GenesisAeon](https://github.com/GenesisAeon) ecosystem · [uv](https://docs.astral.sh/uv/) · [hatchling](https://hatch.pypa.io/)
