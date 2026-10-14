"""'Plan my gig': a whole set for a time slot. Each slot has an energy and BPM curve (a warm-up climbs gently,
peak time stays high, a closing set winds down); the planner walks the catalogue picking the next track that
mixes with the last one (key, BPM, sound) and sits closest to where the curve should be at that point."""
import re

import numpy as np

SLOTS = {"warmup": "Warm-up", "peak": "Peak time", "closing": "Closing", "allnight": "All night"}
EXPLICIT = re.compile(r"\b(pussy|fuck|shit|bitch|dick|cock|nigga|hoe|sex)\w*", re.I)


def curve(slot: str, x: float) -> tuple[float, float]:
    """(energy 1-10, BPM) the set should be at, x from 0 (first track) to 1 (last)."""
    if slot == "warmup":
        return 3.5 + 2.7 * x, 118 + 5 * x
    if slot == "peak":
        rise = min(1.0, x / 0.4)
        return 6.2 + 2.3 * rise - 0.6 * max(0.0, x - 0.85) / 0.15, 124 + 4 * rise
    if slot == "closing":
        return 7.6 - 3.6 * x ** 1.2, 127 - 6 * x
    bump = x / 0.7 if x < 0.7 else 1 - 0.55 * (x - 0.7) / 0.3            # all night: build to a peak, then ease off
    return 3.5 + 5 * bump, 118 + 9 * bump


def _camelot(c: str) -> tuple[int, str]:
    return int(c[:-1]), c[-1]


def key_fit(a: str, others: list[str]) -> np.ndarray:
    """2 = mixes in key, 1 = workable key change, 0 = clash (same rules as the set builder)."""
    na, la = _camelot(a)
    out = np.zeros(len(others), dtype="float32")
    for j, b in enumerate(others):
        nb, lb = _camelot(b)
        step = min((nb - na) % 12, (na - nb) % 12)
        if (la == lb and step <= 1) or (la != lb and step == 0):
            out[j] = 2
        elif (la == lb and step == 2) or (la != lb and step == 1):
            out[j] = 1
    return out


def plan(index, minutes: int, slot: str, style: str = "", seed: int | None = None) -> list[dict]:
    n = int(min(30, max(6, round(minutes / 6))))           # about 6 minutes a track in a house set
    rows = index.rows
    base = np.array([bool(r["cover"]) and not EXPLICIT.search(r["title"]) for r in rows])
    if style:
        base &= np.array([r["style"] == style for r in rows])
    recent = base & (index.age_days <= 365)
    pool = np.where(recent if recent.sum() >= n * 8 else base)[0]
    if len(pool) < n:
        return []
    rec = np.where(index.age_days[pool] <= 60, 1.0, np.where(index.age_days[pool] <= 365, 0.5, 0.0))
    bpm, energy, snd = index.bpm[pool], index.energy[pool], index.sound[pool]
    cams = [index.camelot[i] for i in pool]
    used, chosen, artists, titles = np.zeros(len(pool), bool), [], [], set()

    def pick(score):
        order = np.argsort(-score)
        for j in order[:400]:
            r = rows[pool[j]]
            t = re.sub(r"\s*[\(\[].*$", "", r["title"]).lower()
            if used[j] or r["artist"] in artists[-4:] or artists.count(r["artist"]) >= 2 or (r["artist"], t) in titles:   # at most twice per set
                continue
            return j
        return None

    e0, b0 = curve(slot, 0)
    if seed is not None and seed in index.ids and index.ids[seed] in set(pool.tolist()):
        j = int(np.where(pool == index.ids[seed])[0][0])
    else:
        j = pick(-np.abs(energy - e0) * 0.5 - np.abs(bpm - b0) * 0.25 + rec * 0.6 + np.random.default_rng().random(len(pool)) * 0.4)
    for k in range(n):
        if k:
            e_t, b_t = curve(slot, k / (n - 1))
            p = chosen[-1]
            sim = snd @ snd[p]
            kf = key_fit(cams[p], cams)
            jump = np.abs(bpm - bpm[p])
            score = (1.3 * sim + np.where(kf == 2, 0.9, np.where(kf == 1, 0.25, -1.6))
                     - 0.32 * np.abs(energy - e_t) - 0.12 * np.abs(bpm - b_t) - np.where(jump > 4, 0.8, 0)
                     - np.where(np.abs(energy - energy[p]) > 2, 0.6, 0) + 0.35 * rec)
            j = pick(score)
            if j is None:
                break
        used[j] = True
        chosen.append(j)
        r = rows[pool[j]]
        artists.append(r["artist"]); titles.add((r["artist"], re.sub(r"\s*[\(\[].*$", "", r["title"]).lower()))
    return [{"deezer_id": rows[pool[j]]["deezer_id"], "title": rows[pool[j]]["title"], "artist": rows[pool[j]]["artist"],
             "cover": rows[pool[j]]["cover"], "key": rows[pool[j]]["key"], "camelot": rows[pool[j]]["camelot"],
             "bpm": rows[pool[j]]["bpm"], "energy": int(rows[pool[j]]["energy"])} for j in chosen]
