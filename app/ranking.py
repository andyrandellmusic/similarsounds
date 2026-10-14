"""Scoring: sound similarity x key x BPM x energy x recency."""
import re
from collections import Counter

import numpy as np

RECENCY_HALF_LIFE_DAYS = 90   # house moves fast: the boost halves every 3 months
RECENCY_MAX_BOOST = 1.0       # brand-new release scores up to 2x


def parse_camelot(code: str) -> tuple[int, str]:
    return int(code[:-1]), code[-1]


def key_score(a: str, b: str) -> float:
    """Harmonic-mixing compatibility on the Camelot wheel."""
    na, la = parse_camelot(a)
    nb, lb = parse_camelot(b)
    step = min((na - nb) % 12, (nb - na) % 12)
    if la == lb and step == 0:
        return 1.0     # same key
    if la == lb and step == 1:
        return 0.9     # +/-1: perfect mix
    if la != lb and step == 0:
        return 0.85    # relative major/minor
    if la == lb and step == 2:
        return 0.6     # energy boost
    return 0.35


def bpm_score(query_bpm: float, bpms: np.ndarray) -> np.ndarray:
    diff = np.abs(bpms - query_bpm)
    return np.exp(-((diff / 4.0) ** 2))


def energy_score(query_energy: float, energies: np.ndarray) -> np.ndarray:
    return np.exp(-((np.abs(energies - query_energy) / 3.0) ** 2))


def recency_boost(age_days: np.ndarray) -> np.ndarray:
    age = np.clip(age_days, 0, None)
    return 1 + RECENCY_MAX_BOOST * 0.5 ** (age / RECENCY_HALF_LIFE_DAYS)


MAX_PER_ARTIST = 2


def rank(index, query: dict, *, exclude_id=None, max_age_days=None, strict_key=False,
         bpm_range=6.0, style=None, limit=30) -> tuple[list[dict], str | None]:
    if not index.rows:
        return [], None

    M, q_vec, space = index.query_vec(query)
    cos = M @ q_vec
    sim = index.match(cos, space)           # 0..1

    # Guess the query's sub-genre from its nearest neighbours
    nearest = np.argsort(-cos)[:15]
    styles = Counter(index.rows[i]["style"] for i in nearest if index.rows[i]["style"])
    guessed_style = styles.most_common(1)[0][0] if styles else None

    keys = np.array([key_score(query["camelot"], c) for c in index.camelot])
    score = (sim ** 3) * keys * bpm_score(query["bpm"], index.bpm) \
        * energy_score(query["energy"], index.energy) * recency_boost(index.age_days)

    mask = np.abs(index.bpm - query["bpm"]) <= bpm_range
    if strict_key:
        mask &= keys >= 0.85
    if max_age_days:
        mask &= index.age_days <= max_age_days
    if style:
        mask &= np.array([r["style"] == style for r in index.rows])
    if exclude_id is not None and exclude_id in index.ids:
        mask[index.ids[exclude_id]] = False

    score = np.where(mask, score, -1)
    order = np.argsort(-score)[:limit * 10]
    results = []
    per_artist, songs = Counter(), set()
    for i in order:
        if score[i] < 0 or len(results) >= limit:
            break
        r = index.rows[i]
        # variety: at most MAX_PER_ARTIST tracks by one artist, and one version of each song
        artist = re.split(r",| & | feat\.? | x ", (r["artist"] or "").lower())[0].strip()
        song = (artist, re.sub(r"\s*[\(\[].*$", "", (r["title"] or "").lower()).strip())
        if per_artist[artist] >= MAX_PER_ARTIST or song in songs:
            continue
        per_artist[artist] += 1; songs.add(song)
        results.append({
            "deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"],
            "label": r["label"], "cover": r["cover"], "release_date": r["release_date"],
            "style": r["style"], "key": r["key"], "camelot": r["camelot"], "bpm": r["bpm"],
            "energy": int(r["energy"]), "age_days": int(index.age_days[i]),
            "similarity": round(float(sim[i]) * 100), "key_match": float(keys[i]),
            "score": round(float(score[i]), 4),
        })
    return results, guessed_style
