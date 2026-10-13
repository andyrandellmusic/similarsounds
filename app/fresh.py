"""'Fresh for your set': the newest releases that mix with tracks already in someone's set (key, BPM and
sound), each tagged with the set track it goes best with."""
import re
from datetime import date

import numpy as np

from app.planner import EXPLICIT, key_fit


def fresh(index, ids: list[int], limit: int = 12) -> dict:
    mine = [index.ids[i] for i in ids if i in index.ids]
    if not mine:
        return {"days": 0, "results": []}
    taken = set(mine)
    for days in (14, 30, 60):
        pool = np.array([i for i in np.where(index.age_days <= days)[0]
                         if i not in taken and index.rows[i]["cover"] and not EXPLICIT.search(index.rows[i]["title"])])
        if len(pool) >= 40:
            break
    if not len(pool):
        return {"days": days, "results": []}
    cams = [index.camelot[i] for i in pool]
    best, partner = np.full(len(pool), -9.0), np.zeros(len(pool), dtype=int)
    for s in mine:
        score = (index.sound[pool] @ index.sound[s]
                 + np.where(key_fit(index.camelot[s], cams) == 2, 0.35, np.where(key_fit(index.camelot[s], cams) == 1, 0.05, -0.6))
                 - np.where(np.abs(index.bpm[pool] - index.bpm[s]) > 6, 0.8, 0))
        better = score > best
        best[better], partner[better] = score[better], s
    today, out, per_artist, titles = date.today(), [], {}, set()
    for j in np.argsort(-best):
        r = index.rows[pool[j]]
        base = re.sub(r"\s*[\(\[].*$", "", r["title"]).lower()
        if per_artist.get(r["artist"], 0) >= 2 or (r["artist"], base) in titles:
            continue
        per_artist[r["artist"]] = per_artist.get(r["artist"], 0) + 1
        titles.add((r["artist"], base))
        w = index.rows[partner[j]]
        out.append({"deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"], "cover": r["cover"],
                    "style": r["style"], "camelot": r["camelot"], "bpm": r["bpm"], "key": r["key"], "energy": int(r["energy"]),
                    "age_days": (today - date.fromisoformat(r["release_date"])).days if r["release_date"] else None,
                    "with": {"title": w["title"], "artist": w["artist"]}})
        if len(out) >= limit:
            break
    return {"days": days, "results": out}
