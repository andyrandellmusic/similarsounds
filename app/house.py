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
THRESHOLD = 0.4   # cross-validated: keeps ~92% of house, catches ~82% of non-house

FEATURES = ["kick_pulse", "kick_bar", "kick_offbeat", "pulse", "low_share", "nn_sim",
            "dance_genre", "tempo_off"]


def house_features(feats: dict, index, genres: list[int]) -> dict:
    q = index.embed(feats["embedding"])
    sims = np.sort(index.emb @ q)[::-1]
    return {
        **feats["rhythm"],
        "nn_sim": float(sims[:10].mean()),
        "dance_genre": float(any(g in DANCE_GENRES for g in genres)),
    }


def feature_vector(f: dict) -> list[float]:
    t = f["tempo_free"]
    off = min(abs(x - 125) for x in (t, t * 2, t / 2))   # distance from house tempo
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
        if min(abs(x - 125) for x in (t, t * 2, t / 2)) > 10:
            bits.append(f"tempo around {round(t)} BPM")
        if not f["dance_genre"]:
            bits.append("not tagged as dance/electronic")
        reason = ", ".join(bits) or "doesn't sound like house"
    return {"is_house": p >= THRESHOLD, "confidence": round(p, 2), "reason": reason}
