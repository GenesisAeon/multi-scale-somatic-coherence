# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Fixed
- Editable install (`pip install -e .`) was broken: `[tool.hatch.build]
  dev-mode-dirs = ["src"]` pointed at the vendored scaffold copy instead of
  the repo root where `mssc/` actually lives, so `import mssc` failed
  outside of `pytest` (which happens to add the cwd to `sys.path` on its
  own). Removed the stale setting; hatchling's default now correctly
  resolves the root-layout `mssc` package.
- `scripts/validate_runtime.py` crashed with `UnicodeEncodeError` on
  Windows consoles due to the `✓`/`✗` markers and the default non-UTF-8
  codepage. Forced UTF-8 stdout/stderr at the top of the script.

### Removed
- Vendored `src/diamond_setup/` copy (unused local dev-mode leftover from
  the original diamond-setup scaffold; the real dependency is declared in
  `pyproject.toml`).
- `tests/test_cli.py`, `test_preset.py`, `test_protocol.py`,
  `test_validator.py` — these tested the vendored `diamond_setup` scaffold
  CLI/templates/protocol, not anything in `mssc`/`tip`. Never adapted after
  the initial scaffold commit. `tests/test_runtime_contract.py` (which
  tests this repo's own `contracts/runtime.schema.yaml` +
  `scripts/validate_runtime.py`) is unaffected and stays.
- `typer`/`rich` dev dependencies (only needed by the removed vendored CLI
  scaffold and its tests).

## [0.1.0] - 2026-07-16
### Added
- Initial `genesis-mssc` package (P49): MSSC (cross-scale EEG–HRV
  coherence: `compute_coherence`, `fit_scaling_exponent`, `run_null_test`)
  and TIP (Temporal Integrity Probe: `SessionRunner`, consistency
  scoring, context manipulations).
- `mssc.crep_gate` — `CREPGateStatus` three-state gate
  (`blocked` / `pending_review` / `passed`) with five pre-registered
  falsification conditions for domain-18 registration, including the
  Ρ_sem/TIP correlation hypothesis vs. `scope-resilience` (P41).
- `contracts/runtime.schema.yaml` — Q4 runtime contract schema +
  `scripts/validate_runtime.py` validator.
### Changed
- `tip/` merged into `mssc/tip/` as a proper subpackage (previously two
  unrelated top-level packages, neither matching the `genesis-mssc` PyPI
  name).

Note: this package has not been published to PyPI yet (still Pre-Alpha,
intentional — see `README.md`).
