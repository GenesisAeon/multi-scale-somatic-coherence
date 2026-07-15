"""EEG adapter for PhysioNet CAP Sleep Database and SHHS.

Loads EEG channels from WFDB recordings and computes per-epoch
spectral coherence. Falls back to STUB mode when network is unavailable.

References
----------
Goldberger AL et al. (2000). PhysioBank, PhysioToolkit, PhysioNet.
    Circulation 101(23), e215–e220.
Terzano MG et al. (2001). Atlas, rules, and recording techniques for
    scoring CAP in human sleep. Sleep Medicine 2(6), 537–553.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# CAP EEG channel labels (typical; actual names vary by record)
CAP_EEG_CHANNELS = ["C3-A2", "C4-A1", "F3-A2", "F4-A1", "O1-A2", "O2-A1"]

PHYSIONET_CAP_DB = "capslpdb"
PHYSIONET_SHHS_DB = "shhs"

EPOCH_DURATION_S = 30.0


@dataclass
class EEGRecord:
    """EEG data for one subject: per-epoch spectral coherence + raw signal."""

    subject_id: str
    database: str
    channels: list[str]
    sampling_rate_hz: float
    # shape: (n_epochs, n_channels, n_samples_per_epoch)
    epochs: np.ndarray
    # shape: (n_epochs,) — mean intra-channel spectral coherence per epoch
    spectral_coherence: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)
    is_stub: bool = False

    def __post_init__(self) -> None:
        if self.is_stub:
            logger.warning(
                "EEGRecord(%s) is a STUB — not real PhysioNet data. "
                "Do not use for statistical inference.",
                self.subject_id,
            )


def load_eeg_record(
    subject_id: str,
    database: str = PHYSIONET_CAP_DB,
    cache_dir: Path | None = None,
    epoch_duration_s: float = EPOCH_DURATION_S,
    allow_stub: bool = True,
) -> EEGRecord:
    """Load EEG recording from PhysioNet, segment into epochs, compute coherence.

    Parameters
    ----------
    subject_id:
        Record name within the database (e.g. ``"n1"``).
    database:
        PhysioNet database slug.
    cache_dir:
        Local directory for cached WFDB files.
    epoch_duration_s:
        Length of each analysis epoch in seconds (default 30 s, matching
        standard sleep scoring windows).
    allow_stub:
        If ``True``, return a clearly flagged stub when download fails.

    Returns
    -------
    EEGRecord
    """
    cache_dir = cache_dir or Path.home() / ".cache" / "mssc" / "physionet"
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        import wfdb  # type: ignore[import]

        record = wfdb.rdrecord(subject_id, pn_dir=database)
        fs = float(record.fs)
        sig = record.p_signal  # shape: (n_samples, n_channels)
        channels = list(record.sig_name)

        eeg_idx = _find_eeg_channels(channels)
        if not eeg_idx:
            raise ValueError(f"No EEG channels found in {subject_id}. Available: {channels}")

        eeg_sig = sig[:, eeg_idx]
        eeg_channels = [channels[i] for i in eeg_idx]
        epochs = _segment_epochs(eeg_sig, fs, epoch_duration_s)
        coherence = _compute_spectral_coherence(epochs, fs)

        logger.info(
            "Loaded %d epochs, %d EEG channels for %s from %s",
            len(epochs),
            len(eeg_channels),
            subject_id,
            database,
        )
        return EEGRecord(
            subject_id=subject_id,
            database=database,
            channels=eeg_channels,
            sampling_rate_hz=fs,
            epochs=epochs,
            spectral_coherence=coherence,
            metadata={"source": "physionet", "db": database},
            is_stub=False,
        )

    except ImportError:
        msg = "wfdb is not installed. Install with: pip install wfdb"
        if not allow_stub:
            raise RuntimeError(msg) from None
        logger.warning("%s — returning STUB for %s", msg, subject_id)

    except Exception as exc:
        msg = f"Failed to load EEG for {subject_id} from {database}: {exc}"
        if not allow_stub:
            raise RuntimeError(msg) from exc
        logger.warning("%s — returning STUB", msg)

    return _make_eeg_stub(subject_id, database, epoch_duration_s)


def _find_eeg_channels(channel_names: list[str]) -> list[int]:
    """Return indices of channels that look like EEG derivations."""
    eeg_patterns = ["C3", "C4", "F3", "F4", "O1", "O2", "Cz", "Pz", "EEG"]
    return [
        i
        for i, name in enumerate(channel_names)
        if any(pat in name.upper() for pat in eeg_patterns)
    ]


def _segment_epochs(
    signal: np.ndarray, fs: float, epoch_s: float
) -> np.ndarray:
    """Split multi-channel signal into fixed-length epochs.

    Returns shape (n_epochs, n_channels, samples_per_epoch).
    Trailing samples shorter than one epoch are discarded.
    """
    samples_per_epoch = int(fs * epoch_s)
    n_epochs = len(signal) // samples_per_epoch
    trimmed = signal[: n_epochs * samples_per_epoch]
    return trimmed.reshape(n_epochs, samples_per_epoch, signal.shape[1]).transpose(0, 2, 1)


def _compute_spectral_coherence(epochs: np.ndarray, fs: float) -> np.ndarray:
    """Compute mean intra-channel spectral coherence per epoch.

    Uses Welch's method in the delta+theta+alpha+beta bands (0.5–30 Hz).
    Returns one scalar per epoch: mean magnitude-squared coherence across
    all channel pairs.

    Reference
    ---------
    Welch PD (1967). The use of fast Fourier transform for the estimation
    of power spectra. IEEE Trans Audio Electroacoust 15(2), 70–73.
    """
    try:
        from scipy import signal as sp_signal  # type: ignore[import]
    except ImportError:
        logger.warning("scipy not available — returning NaN coherence array")
        return np.full(len(epochs), np.nan)

    n_epochs, n_channels, n_samples = epochs.shape
    coherence_per_epoch = np.zeros(n_epochs)

    for e_idx, epoch in enumerate(epochs):
        pair_coherences: list[float] = []
        for ch_a in range(n_channels):
            for ch_b in range(ch_a + 1, n_channels):
                f, cxy = sp_signal.coherence(epoch[ch_a], epoch[ch_b], fs=fs, nperseg=256)
                band_mask = (f >= 0.5) & (f <= 30.0)
                if band_mask.any():
                    pair_coherences.append(float(np.mean(cxy[band_mask])))
        coherence_per_epoch[e_idx] = float(np.mean(pair_coherences)) if pair_coherences else np.nan

    return coherence_per_epoch


def _make_eeg_stub(subject_id: str, database: str, epoch_s: float) -> EEGRecord:
    """Return a clearly labelled synthetic EEG stub."""
    rng = np.random.default_rng(seed=abs(hash(subject_id + "eeg")) % (2**32))
    fs = 256.0
    n_epochs = int(7 * 3600 / epoch_s)  # 7 hours
    n_channels = 3
    samples_per_epoch = int(fs * epoch_s)
    epochs = rng.standard_normal((n_epochs, n_channels, samples_per_epoch)).astype(np.float32)
    coherence = rng.uniform(0.2, 0.8, size=n_epochs)
    return EEGRecord(
        subject_id=subject_id,
        database=database,
        channels=["C3-A2", "C4-A1", "F3-A2"],
        sampling_rate_hz=fs,
        epochs=epochs,
        spectral_coherence=coherence,
        metadata={"source": "STUB — synthetic, not real PhysioNet data"},
        is_stub=True,
    )
