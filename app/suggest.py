"""Search-as-you-type suggestions for the search box.

- "c", "ch", "chris l"  -> artists whose name (or any word in it) starts with what's typed,
                           plus matching track titles once there are 3+ characters
- "Chris Lake - "       -> that artist's tracks, narrowed by whatever follows the dash

The house catalogue answers instantly; Deezer fills in everyone else (cached, and only
from 2 characters on so a single letter never hits the API).
"""
import re
import threading
import time
import unicodedata
from collections import defaultdict

from app import sources

_cache: dict[tuple, tuple[float, object]] = {}
_cache_lock = threading.Lock()
CACHE_SECONDS = 600


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()


def starts(name: str, q: str) -> int:
    """2 = whole name starts with q, 1 = a later word does, 0 = no match."""
    n = norm(name)
    if n.startswith(q):
        return 2
    return 1 if any(w.startswith(q) for w in n.split()[1:]) or f" {q}" in f" {n}" else 0


def _cached(key, fn):
    now = time.time()
    with _cache_lock:
        hit = _cache.get(key)
        if hit and now - hit[0] < CACHE_SECONDS:
            return hit[1]
    try:
        value = fn()
    except Exception:
        value = []
    with _cache_lock:
        if len(_cache) > 2000:
            _cache.clear()
        _cache[key] = (now, value)
    return value


def _track_out(t: dict, row: dict | None = None) -> dict:
    out = {"deezer_id": t["deezer_id"] if "deezer_id" in t else t["id"],
           "title": t["title"],
           "artist": t["artist"] if isinstance(t["artist"], str) else t["artist"]["name"],
           "cover": t.get("cover") or (t.get("album") or {}).get("cover_small"),
           "in_catalogue": row is not None}
    if row:
        out.update(camelot=row["camelot"], bpm=row["bpm"], release_date=row["release_date"])
    return out


class Suggester:
    def __init__(self, index):
        self.index = index
        self.rebuild()

    def rebuild(self):
        """Group catalogue tracks by artist for instant prefix lookups."""
        by_artist = defaultdict(list)
        for r in self.index.rows:
            by_artist[r["artist"]].append(r)
        self.artists = []
        for name, rows in by_artist.items():
            rows.sort(key=lambda r: r["release_date"] or "", reverse=True)
            self.artists.append({"name": name, "norm": norm(name), "tracks": rows,
                                 "latest": rows[0]["release_date"] or "", "cover": rows[0]["cover"]})

    # ---------------------------------------------------------------- text mode
    def suggest(self, text: str, limit: int = 8) -> dict:
        text = text.strip()
        if " - " in text or text.endswith(" -"):
            artist, _, title = text.partition(" -")
            return self.artist_tracks(artist.strip(), title.strip(" -"), limit)
        q = norm(text)
        if not q:
            return {"artists": [], "tracks": []}

        # Catalogue artists: full-name prefix first, then most tracks, then newest
        cat = [(s, a) for a in self.artists if (s := starts(a["name"], q))]
        cat.sort(key=lambda x: x[1]["latest"], reverse=True)          # newest first...
        cat.sort(key=lambda x: (-x[0], -len(x[1]["tracks"])))         # ...within best match / most tracks
        artists = [{"name": a["name"], "picture": a["cover"], "in_catalogue": len(a["tracks"])}
                   for _, a in cat[:limit]]

        if len(q) >= 2 and len(artists) < limit:
            seen = {norm(a["name"]) for a in artists}
            found = _cached(("artist", q), lambda: sources.deezer("/search/artist", q=text, limit=15)["data"])
            extra = sorted((a for a in found if starts(a["name"], q)),
                           key=lambda a: (-starts(a["name"], q), -a.get("nb_fan", 0)))
            for a in extra:
                if len(artists) >= limit:
                    break
                if norm(a["name"]) in seen:   # same name, fewer fans: skip the duplicate
                    continue
                seen.add(norm(a["name"]))
                artists.append({"name": a["name"], "picture": a.get("picture_small"), "in_catalogue": 0})

        tracks = []
        if len(q) >= 3:
            rows = [r for r in self.index.rows if starts(r["title"], q)]
            rows.sort(key=lambda r: r["release_date"] or "", reverse=True)
            tracks = [_track_out(r, r) for r in rows[:4]]
            # Outside the catalogue, only suggest tracks once the query is specific enough
            # (4+ letters), and only when the title itself or the artist's full name starts with it
            if len(tracks) < 5 and len(q) >= 4:
                ids = {t["deezer_id"] for t in tracks}
                found = _cached(("track", q), lambda: sources.deezer("/search", q=text, limit=15)["data"])
                for t in found:
                    if t["id"] in ids or not t.get("preview"):
                        continue
                    if starts(t["title"], q) == 2 or norm(t["artist"]["name"]).startswith(q):
                        tracks.append(_track_out(t, self._row(t["id"])))
                        ids.add(t["id"])
                    if len(tracks) >= 5:
                        break
        return {"artists": artists, "tracks": tracks}

    # -------------------------------------------------------------- artist mode
    def artist_tracks(self, artist: str, title: str = "", limit: int = 12) -> dict:
        a_norm, t_norm = norm(artist), norm(title)
        tracks, ids = [], set()
        for a in self.artists:
            if a["norm"] == a_norm:
                for r in a["tracks"]:
                    if not t_norm or starts(r["title"], t_norm):
                        tracks.append(_track_out(r, r))
                        ids.add(r["deezer_id"])

        def deezer_top():
            hits = sources.deezer("/search/artist", q=artist, limit=10)["data"]
            same_name = [h for h in hits if norm(h["name"]) == a_norm]
            if not same_name:
                return []
            # Several Deezer artists can share a name; the real one has by far the most fans
            exact = max(same_name, key=lambda h: h.get("nb_fan", 0))
            return sources.deezer(f"/artist/{exact['id']}/top", limit=50)["data"]

        if len(tracks) < limit:
            for t in _cached(("top", a_norm), deezer_top):
                if t["id"] in ids or not t.get("preview"):
                    continue
                if t_norm and not starts(t["title"], t_norm):
                    continue
                tracks.append(_track_out(t, self._row(t["id"])))
                ids.add(t["id"])
                if len(tracks) >= limit:
                    break
        return {"artists": [], "tracks": tracks[:limit], "artist": artist}

    def _row(self, deezer_id):
        i = self.index.ids.get(deezer_id)
        return self.index.rows[i] if i is not None else None
