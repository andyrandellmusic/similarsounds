"""Is the pasted track house music?

Combines rhythm (a steady four-on-the-floor kick near house tempo), sound (closeness to
the house catalogue) and Deezer's genre tags in a small logistic model. Calibrate with
scripts/house_eval.py + scripts/house_fit.py, which write data/house_model.json.
"""
import json
from pathlib import Path

import numpy as np

DANCE_GENRES = {106, 113}   # Deezer "Electro", "Dance"
MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "house_model.json"
THRESHOLD = 0.4   # cross-validated: keeps ~94% of house (96% of a DJ's own library), catches ~83% of non-house

FEATURES = ["kick_pulse", "kick_bar", "kick_offbeat", "pulse", "low_share", "nn_sim",
            "dance_genre", "tempo_off"]


def house_features(feats: dict, index, genres: list[int]) -> dict:
    q = index.embed(feats["embedding"])
    sims = np.sort(index.emb @ q)[::-1]
    return {
        **feats["rhythm"],
        "nn_sim": float(sims[:10].mean()),
        # 1 = Deezer tags it dance, 0 = tagged something else, 0.5 = no tags at all (common for small
        # labels and self-releases, so it mustn't count against the track)
        "dance_genre": float(any(g in DANCE_GENRES for g in genres)) if genres else 0.5,
    }


def _tempo_off(t: float) -> float:
    """Distance from house tempo, allowing for the beat being heard at half, double or 2/3 speed."""
    return min(abs(t * m - 125) for m in (1, 2, 0.5, 1.5, 2 / 3))


def feature_vector(f: dict) -> list[float]:
    t = f["tempo_free"]
    off = _tempo_off(t)
    vals = {**f, "tempo_off": min(off, 25) / 25}
    return [float(vals[name]) for name in FEATURES]


def _load_model():
    try:
        return json.loads(MODEL_PATH.read_text())
    except FileNotFoundError:
        return None


_model = _load_model()


def check(f: dict) -> dict:
    """Return {is_house, confidence, reason} for a track's house features."""
    if _model is None:
        return {"is_house": True, "confidence": None, "reason": None}
    z = (np.array(feature_vector(f)) - np.array(_model["mu"])) / np.array(_model["sd"])
    p = float(1 / (1 + np.exp(-(z @ np.array(_model["w"]) + _model["b"]))))
    reason = None
    if p < THRESHOLD:
        bits = []
        if f["kick_pulse"] < 0.2:
            bits.append("no steady four-on-the-floor kick")
        t = f["tempo_free"]
        if _tempo_off(t) > 10:
            bits.append(f"tempo around {round(t)} BPM")
        if f["dance_genre"] == 0:
            bits.append("not tagged as dance/electronic")
        reason = ", ".join(bits) or "doesn't sound like house"
    return {"is_house": p >= THRESHOLD, "confidence": round(p, 2), "reason": reason}
