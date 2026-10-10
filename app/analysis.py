"""Audio analysis: key (Camelot), BPM, raw energy features and a timbre embedding.

Audio is analysed in memory and never written to disk.
"""
import io

import librosa
import numpy as np
import soundfile as sf

SR = 22050

# Krumhansl-Schmuckler key profiles
MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

# Camelot numbers indexed by pitch class (C=0)
CAMELOT_MAJOR = [8, 3, 10, 5, 12, 7, 2, 9, 4, 11, 6, 1]   # "B" side
CAMELOT_MINOR = [5, 12, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10]   # "A" side


def strip_id3(data: bytes) -> bytes:
    """libsndfile can't sniff MP3s that start with an ID3v2 tag, so drop the tag."""
    while data[:3] == b"ID3" and len(data) > 10:
        size = (data[6] & 0x7F) << 21 | (data[7] & 0x7F) << 14 | (data[8] & 0x7F) << 7 | (data[9] & 0x7F)
        footer = 10 if data[5] & 0x10 else 0
        data = data[10 + size + footer:]
    return data


def load_audio(data: bytes) -> np.ndarray:
    data = strip_id3(data)
    y, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y


def detect_key(y: np.ndarray) -> tuple[str, str]:
    """Return (musical key name, Camelot code) e.g. ("A minor", "8A")."""
    # Coarse STFT/CQT resolutions keep peak memory low enough for a 512 MB server;
    # we only need the track-wide average chroma, not fine timing.
    D = librosa.stft(y, n_fft=2048, hop_length=1024)
    H, _ = librosa.decompose.hpss(D)
    harmonic = librosa.istft(H, hop_length=1024, length=len(y))
    del D, H
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=SR, hop_length=4096).mean(axis=1)
    best = (-2.0, 0, "major")
    for tonic in range(12):
        for mode, profile in (("major", MAJOR), ("minor", MINOR)):
            r = np.corrcoef(chroma, np.roll(profile, tonic))[0, 1]
            if r > best[0]:
                best = (r, tonic, mode)
    _, tonic, mode = best
    if mode == "major":
        return f"{NOTES[tonic]} major", f"{CAMELOT_MAJOR[tonic]}B"
    return f"{NOTES[tonic]} minor", f"{CAMELOT_MINOR[tonic]}A"


def detect_bpm(y: np.ndarray, lo: float = 105, hi: float = 140) -> float:
    """Fine-grained tempo: autocorrelate a high-resolution onset envelope over the
    house tempo range and interpolate the peak (librosa's default grid is ~3 BPM wide)."""
    hop = 128
    fps = SR / hop
    onset = librosa.onset.onset_strength(y=y, sr=SR, hop_length=hop, n_fft=1024, aggregate=np.median)
    onset = onset - onset.mean()
    ac = librosa.autocorrelate(onset)
    bpms = np.arange(lo, hi, 0.05)
    lags = 60 * fps / bpms
    # Score each candidate tempo by its beat lag plus the 2- and 4-beat lags
    score = sum(w * np.interp(lags * m, np.arange(len(ac)), ac) for m, w in ((1, 1.0), (2, 0.6), (4, 0.4)))
    bpm = float(bpms[int(np.argmax(score))])
    # House is almost always produced at whole-number BPMs
    return float(round(bpm)) if abs(bpm - round(bpm)) < 0.3 else round(bpm, 1)


def analyse(data: bytes) -> dict:
    y = load_audio(data)
    key_name, camelot = detect_key(y)
    bpm = detect_bpm(y)

    rms = librosa.feature.rms(y=y)[0]
    onset = librosa.onset.onset_strength(y=y, sr=SR)
    centroid = librosa.feature.spectral_centroid(y=y, sr=SR)[0]
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20)
    contrast = librosa.feature.spectral_contrast(y=y, sr=SR)
    flatness = librosa.feature.spectral_flatness(y=y)[0]

    # Raw energy ingredients; converted to a 1-10 scale against the catalogue later
    energy_raw = {
        "loudness": float(20 * np.log10(rms.mean() + 1e-9)),
        "onset": float(onset.mean()),
        "brightness": float(centroid.mean()),
    }

    # Timbre/groove fingerprint (key-independent on purpose: key is scored separately)
    embedding = np.concatenate([
        mfcc.mean(axis=1), mfcc.std(axis=1),
        contrast.mean(axis=1), contrast.std(axis=1),
        [flatness.mean(), onset.std(), centroid.std()],
    ]).astype("float32")

    return {
        "key": key_name,
        "camelot": camelot,
        "bpm": bpm,
        "energy_raw": energy_raw,
        "embedding": embedding.tolist(),
    }
