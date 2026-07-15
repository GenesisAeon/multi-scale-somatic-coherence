# Stub Notice — MSSC Adapters

## Which adapters may return stubs

Both `physionet_hrv_adapter.py` and `physionet_eeg_adapter.py` include a
fallback stub mode. A stub is returned **only** when:

1. The `wfdb` package is not installed, **or**
2. A network/PhysioNet download fails.

Stubs are **always** flagged explicitly:
- `HRVRecord.is_stub == True` / `EEGRecord.is_stub == True`
- A `WARNING`-level log message names the subject and reason.
- The `sampling_info` / `metadata` dict contains the string
  `"STUB — synthetic, not real PhysioNet data"`.

## What stubs are for

Stubs exist **only** for:
- CI/CD pipelines without network access.
- Unit-test edge-case validation (known synthetic signals).
- Local development without PhysioNet credentials.

## What stubs must never be used for

- Statistical inference about coupling coefficients.
- p-value or effect-size computation reported as real results.
- Any output in `falsification_log.md`.

The analysis code in `coherence_metric.py`, `null_hypothesis_test.py`, and
`beta_fit.py` will refuse to process stub records for real inference — they
raise `ValueError` if `is_stub=True` and `allow_stubs=False` (the default).

## Installing WFDB for real data

```bash
pip install wfdb
```

PhysioNet records used in MSSC (both publicly available without login):

| Database | PhysioNet slug | Records used |
|---|---|---|
| CAP Sleep Database | `capslpdb` | `n1`–`n16` (healthy controls) |
| Sleep Heart Health Study | `shhs` | `shhs1-*` (independent replication set) |
