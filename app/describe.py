"""'Describe a sound': typed words -> known phrases -> a CLAP text fingerprint -> the tracks that sound
most like it. The phrase fingerprints are made offline (scripts/describe_vocab.py), so no model runs here."""
import json, re
from datetime import date
from pathlib import Path

import numpy as np

DATA = Path(__file__).resolve().parent.parent / "data"
_z = np.load(DATA / "describe_vocab.npz")
PHRASES = [str(p) for p in _z["phrases"]]
EMB = _z["emb"]
_syn = json.load(open(DATA / "describe_vocab.json"))
# every way of saying a phrase (the phrase itself too), longest first so "deep sub bass" beats "deep"
LOOKUP = sorted({**{w.lower(): i for i, p in enumerate(PHRASES) for w in _syn.get(p, [])},
                 **{p.lower(): i for i, p in enumerate(PHRASES)}}.items(), key=lambda kv: -len(kv[0]))
EXAMPLES = ["warm sunset deep house with saxophone", "dark rolling minimal with vocal chops", "funky disco with strings",
            "dreamy melodic house with female vocals", "afro house with tribal percussion", "late night acid bassline"]


def understand(text: str) -> list[int]:
    """The phrases found in the text, in the order they appear."""
    t = " " + re.sub(r"[^a-z0-9'\- ]+", " ", (text or "").lower()) + " "
    found = []
    for words, i in LOOKUP:
        m = re.search(r"(?<![a-z0-9])" + re.escape(words) + r"(?![a-z0-9])", t)
        if m:
            found.append((m.start(), i))
            t = t[:m.start()] + " " * (m.end() - m.start()) + t[m.end():]     # don't count the same words twice
    return [i for _, i in sorted(found) if True][:8]


_aff = {}
def _affinity(index) -> np.ndarray:
    """How strongly each track matches each phrase, compared with other tracks (per phrase) and with the
    track's other phrases (so a few tracks that score high for everything don't win every search)."""
    key = (id(index), len(index.rows))
    if key not in _aff:
        S = index.clap_raw @ EMB.T
        have = index.has_clap
        S = (S - S[have].mean(0)) / (S[have].std(0) + 1e-9)
        S = S - S.mean(1, keepdims=True)
        _aff.clear(); _aff[key] = S.astype("float32")
    return _aff[key]


def search(index, text: str, limit: int = 24) -> dict:
    ids = list(dict.fromkeys(understand(text)))
    if not ids:
        return {"understood": [], "results": [], "examples": EXAMPLES}
    z = np.where(index.has_clap, _affinity(index)[:, ids].mean(1), -9)
    age = index.age_days
    score = z + np.where(age <= 60, 0.35, np.where(age <= 365, 0.15, 0))    # newer releases first when it's close
    today, out, per_artist, titles = date.today(), [], {}, set()
    for i in np.argsort(-score):
        r = index.rows[i]
        if not index.has_clap[i] or not r["cover"]:
            continue
        a, base = r["artist"], re.sub(r"\s*[\(\[].*$", "", r["title"]).lower()
        if per_artist.get(a, 0) >= 2 or (a, base) in titles:      # one version of each song, two songs per artist
            continue
        titles.add((a, base))
        per_artist[a] = per_artist.get(a, 0) + 1
        out.append({"deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"], "cover": r["cover"],
                    "style": r["style"], "camelot": r["camelot"], "bpm": r["bpm"], "key": r["key"], "energy": int(r["energy"]),
                    "age_days": (today - date.fromisoformat(r["release_date"])).days if r["release_date"] else None})
        if len(out) >= limit:
            break
    return {"understood": [PHRASES[i] for i in ids], "results": out}
