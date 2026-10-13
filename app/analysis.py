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


def decode(data: bytes) -> tuple[np.ndarray, int]:
    """Mono audio at the file's own sample rate."""
    y, sr = sf.read(io.BytesIO(strip_id3(data)), dtype="float32", always_2d=False)
    if y.ndim > 1:
        y = y.mean(axis=1)
    return y, int(sr)


def load_audio(data: bytes) -> np.ndarray:
    y, sr = decode(data)
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return y


# Key profiles tuned for dance music (strong tonic and fifth). Chosen by testing against the keys
# Beatport publishes for 629 house tracks: 47% exact / 66% mixable, vs 31% / 53% for the classical
# Krumhansl profiles on whole-range chroma (see eval/key_lab.py).
EDM_MAJOR = np.array([0.16, 0.08, 0.08, 0.06, 0.10, 0.09, 0.05, 0.13, 0.06, 0.08, 0.05, 0.06])
EDM_MINOR = np.array([0.17, 0.06, 0.08, 0.12, 0.05, 0.09, 0.05, 0.13, 0.08, 0.05, 0.07, 0.05])
MINOR_LEAN = 0.04          # most house is in a minor key (68% of the Beatport test set)


try:
    import essentia
    essentia.log.infoActive = essentia.log.warningActive = False
    import essentia.standard as _es
except ImportError:                                  # fall back to the chroma method below
    _es = None
ESS_NOTES = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
             "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def detect_key(y: np.ndarray, sr: int = SR) -> tuple[str, str]:
    """Return (musical key name, Camelot code) e.g. ("A minor", "8A").

    Uses Essentia's key extractor with the Sha'ath profile, best of every free method we tested against
    the keys Beatport publishes for 629 house tracks: 56% exact / 70% mixable, vs 47% / 66% for our own
    chroma method (eval: scratch keybpm tests, Oct 2026). Give it audio at the file's own sample rate."""
    if _es is not None:
        k, scale, _ = _es.KeyExtractor(profileType="shaath", sampleRate=sr)(np.ascontiguousarray(y, dtype="float32"))
        tonic = ESS_NOTES[k]
        if scale == "major":
            return f"{NOTES[tonic]} major", f"{CAMELOT_MAJOR[tonic]}B"
        return f"{NOTES[tonic]} minor", f"{CAMELOT_MINOR[tonic]}A"
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    return detect_key_chroma(y)


def detect_key_chroma(y: np.ndarray) -> tuple[str, str]:
    """Our own key finder (no Essentia): returns (musical key name, Camelot code) e.g. ("A minor", "8A").

    Listens to the harmonic part (drums removed) and mainly to the chord/melody range
    (C3 upwards), because in a 30-second house preview the kick drum smears the bass notes."""
    D = librosa.stft(y, n_fft=2048, hop_length=1024)
    H, _ = librosa.decompose.hpss(D)
    harmonic = librosa.istft(H, hop_length=1024, length=len(y))
    del D, H
    fine = np.log1p(10 * librosa.feature.chroma_cqt(y=harmonic, sr=SR, hop_length=2048, bins_per_octave=36)).mean(axis=1)
    mids = librosa.feature.chroma_cqt(y=harmonic, sr=SR, hop_length=2048,
                                      fmin=librosa.note_to_hz("C3"), n_octaves=4).mean(axis=1)
    chroma = mids / (mids.sum() + 1e-9) + 0.5 * fine / (fine.sum() + 1e-9)
    best = (-2.0, 0, "major")
    for tonic in range(12):
        for mode, profile in (("major", EDM_MAJOR), ("minor", EDM_MINOR)):
            r = np.corrcoef(chroma, np.roll(profile, tonic))[0, 1] + (MINOR_LEAN if mode == "minor" else 0)
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


def _ac_at(ac: np.ndarray, lag: float) -> float:
    return float(np.interp(lag, np.arange(len(ac)), ac))


def rhythm_features(y: np.ndarray, bpm: float) -> dict:
    """Signals for "is this house?": a steady four-on-the-floor kick at the detected tempo."""
    hop = 256
    fps = SR / hop
    lag = 60 * fps / bpm

    # One power spectrogram, reused for every measurement below (keeps peak memory low)
    power = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)) ** 2

    # Kick band only (< 150 Hz), so hi-hats and vocals don't count
    S = librosa.feature.melspectrogram(S=power, sr=SR, n_mels=12, fmax=150)
    kick = librosa.onset.onset_strength(S=librosa.power_to_db(S, ref=np.max), sr=SR, hop_length=hop)
    k = kick - kick.mean()
    kac = librosa.autocorrelate(k)
    kac = kac / (kac[0] + 1e-9)

    mel = librosa.feature.melspectrogram(S=power, sr=SR, n_mels=64)
    del power
    onset = librosa.onset.onset_strength(S=librosa.power_to_db(mel, ref=np.max), sr=SR, hop_length=hop)
    o = onset - onset.mean()
    oac = librosa.autocorrelate(o)
    oac = oac / (oac[0] + 1e-9)
    # Unrestricted tempo (60-200 BPM), weighted towards ~120 like librosa's estimator.
    # (librosa.feature.tempo pulls in scipy.stats, which costs ~110 MB on a 512 MB server.)
    cand = np.arange(60.0, 200.0, 0.5)
    prior = np.exp(-0.5 * np.log2(cand / 120) ** 2)
    strength = np.interp(60 * fps / cand, np.arange(len(oac)), oac)
    tempo_free = float(cand[int(np.argmax(np.clip(strength, 0, None) * prior))])

    # Share of energy in the kick band (house is bass-heavy and kick-driven)
    low_share = float(mel[:6].sum() / (mel.sum() + 1e-9))
    return {
        "kick_pulse": _ac_at(kac, lag),             # kick repeats on every beat
        "kick_bar": _ac_at(kac, lag * 4),           # ...and keeps going bar after bar
        "kick_offbeat": _ac_at(kac, lag * 0.5),     # low for 4x4, high for breakbeats/DnB
        "pulse": _ac_at(oac, lag),
        "tempo_free": round(tempo_free, 1),
        "low_share": low_share,
    }


def analyse(data: bytes) -> dict:
    raw, sr = decode(data)
    key_name, camelot = detect_key(raw, sr)
    y = librosa.resample(raw, orig_sr=sr, target_sr=SR) if sr != SR else raw
    del raw
    bpm = detect_bpm(y)
    rhythm = rhythm_features(y, bpm)

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
        "rhythm": rhythm,
    }
