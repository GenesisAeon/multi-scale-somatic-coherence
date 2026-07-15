"""HRV adapter for PhysioNet CAP Sleep Database and SHHS.

Downloads records via WFDB from PhysioNet. Falls back to STUB mode
when the network is unavailable — explicitly flagged, never silently
faking real data.

References
----------
Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, PhysioNet.
    Circulation 101(23), e215–e220.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# fmt: off
# CAP Sleep Database — healthy controls without neurological conditions
CAP_HEALTHY_RECORDS = [
    "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10",
    "n11", "n12", "n13", "n14", "n15", "n16",
]
# fmt: on

PHYSIONET_CAP_DB = "capslpdb"
PHYSIONET_SHHS_DB = "shhs"


@dataclass
class HRVRecord:
    """Container for a single subject's HRV data."""

    subject_id: str
    database: str
    rr_intervals_ms: np.ndarray
    sampling_info: dict[str, Any]
    is_stub: bool = False

    def __post_init__(self) -> None:
        if self.is_stub:
            logger.warning(
                "HRVRecord(%s) is a STUB — not real PhysioNet data. "
                "Do not use for statistical inference.",
                self.subject_id,
            )


def load_hrv_record(
    subject_id: str,
    database: str = PHYSIONET_CAP_DB,
    cache_dir: Path | None = None,
    allow_stub: bool = True,
) -> HRVRecord:
    """Load RR-interval time series for one subject from PhysioNet.

    Parameters
    ----------
    subject_id:
        Record name within the database (e.g. ``"n1"`` for CAP).
    database:
        PhysioNet database slug (``"capslpdb"`` or ``"shhs"``).
    cache_dir:
        Local directory for cached WFDB files. Defaults to
        ``~/.cache/mssc/physionet``.
    allow_stub:
        If ``True``, return a clearly flagged stub when download fails.
        If ``False``, raise on failure.

    Returns
    -------
    HRVRecord
        Contains RR intervals in milliseconds.

    Raises
    ------
    RuntimeError
        When the download fails and ``allow_stub=False``.
    """
    cache_dir = cache_dir or Path.home() / ".cache" / "mssc" / "physionet"
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        import wfdb  # type: ignore[import]

        record = wfdb.rdann(
            subject_id,
            "ecg",
            pn_dir=database,
            rd_segments=True,
        )
        rr_ms = _annotation_to_rr(record)
        logger.info("Loaded %d RR intervals for %s from %s", len(rr_ms), subject_id, database)
        return HRVRecord(
            subject_id=subject_id,
            database=database,
            rr_intervals_ms=rr_ms,
            sampling_info={"source": "physionet", "db": database},
            is_stub=False,
        )

    except ImportError:
        msg = "wfdb is not installed. Install with: pip install wfdb"
        if not allow_stub:
            raise RuntimeError(msg) from None
        logger.warning("%s — returning STUB for %s", msg, subject_id)

    except Exception as exc:
        msg = f"Failed to load {subject_id} from {database}: {exc}"
        if not allow_stub:
            raise RuntimeError(msg) from exc
        logger.warning("%s — returning STUB", msg)

    return _make_stub(subject_id, database)


def load_all_cap_healthy(
    cache_dir: Path | None = None,
    allow_stub: bool = True,
) -> list[HRVRecord]:
    """Load all 16 healthy CAP subjects.

    Statistical note
    ----------------
    n=16 is sufficient for per-subject time-series analysis (full-night
    recordings provide thousands of RR intervals per person), but group-level
    inference is underpowered. Report individual-level results primarily;
    flag group statistics with the small-n caveat in epistemic_status.md.
    """
    return [
        load_hrv_record(sid, PHYSIONET_CAP_DB, cache_dir=cache_dir, allow_stub=allow_stub)
        for sid in CAP_HEALTHY_RECORDS
    ]


def _annotation_to_rr(annotation: Any) -> np.ndarray:
    """Convert WFDB annotation sample indices to RR intervals in ms."""
    beat_samples = np.array(
        [s for s, sym in zip(annotation.sample, annotation.symbol) if sym in "NnLRBAaJSVrFejnE"]
    )
    if len(beat_samples) < 2:
        raise ValueError("Fewer than 2 beat annotations — cannot compute RR intervals.")
    fs = annotation.fs if hasattr(annotation, "fs") and annotation.fs else 1000.0
    rr_ms = np.diff(beat_samples) / fs * 1000.0
    # Physiological plausibility filter: 200–3000 ms
    rr_ms = rr_ms[(rr_ms >= 200) & (rr_ms <= 3000)]
    return rr_ms


def _make_stub(subject_id: str, database: str) -> HRVRecord:
    """Return a clearly labelled synthetic HRV stub."""
    rng = np.random.default_rng(seed=abs(hash(subject_id)) % (2**32))
    # Approximate healthy overnight HRV: mean ~850 ms, std ~80 ms, 7 hours
    n_beats = int(7 * 3600 * 1000 / 850)
    rr_ms = rng.normal(loc=850.0, scale=80.0, size=n_beats).clip(200, 3000)
    return HRVRecord(
        subject_id=subject_id,
        database=database,
        rr_intervals_ms=rr_ms,
        sampling_info={"source": "STUB — synthetic, not real PhysioNet data"},
        is_stub=True,
    )
