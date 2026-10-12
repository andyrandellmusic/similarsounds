"""Tracklist import ("paste your set") and gap fillers ("bridge" tracks that mix with both neighbours)."""

import re
import unicodedata

from app.ranking import rank

MAX_LINES = 40

_NUM = re.compile(r"^\s*(?:\d{1,3}[\.\)\:\-]|#\d+|\d{1,3}\s+-\s)\s*")                 # "1." "2)" "#3" "04 - "
_TIME = re.compile(r"^\s*[\[\(]?\d{1,2}:\d{2}(?::\d{2})?[\]\)]?\s*[-–—]?\s*")        # "[00:00]" "1:02:33 -"
_LABEL = re.compile(r"\s*[\[\{][^\]\}]*[\]\}]\s*$")                                    # trailing "[Defected]"
_MIX = re.compile(r"\s*\((?:original|extended|radio|club)\s+(?:mix|edit|version)\)", re.I)


def parse(text: str) -> list[tuple[str, str]]:
    """Lines like '1. Artist - Title [Label]' -> [(artist, title)]. Lines without ' - ' are skipped."""
    out = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        for _ in range(2):
            line = _NUM.sub("", _TIME.sub("", line))
        line = _LABEL.sub("", line).strip(" -–—•*")
        line = re.sub(r"\s+[–—]\s+", " - ", line)
        if " - " not in line:
            continue
        artist, title = (s.strip() for s in line.split(" - ", 1))
        if artist and title and artist.lower() not in ("id", "unknown") and title.lower() not in ("id", "unknown"):
            out.append((artist, title))
        if len(out) >= MAX_LINES:
            break
    return out


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = _MIX.sub("", s)
    s = re.sub(r"\b(feat|ft)\.?\b.*$", "", s)
    return re.sub(r"[^a-z0-9]+", "", s)


_lookup: dict = {}


def find_in_catalogue(index, artist: str, title: str) -> int | None:
    """Exact-ish match on main artist + title (ignores 'Original Mix', punctuation, accents, feat.)."""
    if _lookup.get("_n") != len(index.rows):
        _lookup.clear()
        for r in index.rows:
            first = re.split(r"\s*(?:,|&| x | feat\.? | ft\.? )\s*", r["artist"] or "", flags=re.I)[0]
            for a in {r["artist"] or "", first}:
                _lookup.setdefault(_norm(a) + "|" + _norm(r["title"]), r["deezer_id"])
        _lookup["_n"] = len(index.rows)
    first = re.split(r"\s*(?:,|&| x | feat\.? | ft\.? )\s*", artist, flags=re.I)[0]
    for a in (artist, first):
        hit = _lookup.get(_norm(a) + "|" + _norm(title))
        if hit:
            return hit
    return None


def bridges(index, qa: dict, qb: dict, exclude: set[int], limit: int = 4) -> list[dict]:
    """Tracks that mix with BOTH qa (before) and qb (after): ranked on each side, then combined."""
    lo, hi = sorted((qa["bpm"], qb["bpm"]))
    span = max(4.0, (hi - lo) / 2 + 4)
    n = len(index.rows)
    ra, _ = rank(index, qa, limit=n, bpm_range=span + (hi - lo))
    rb, _ = rank(index, qb, limit=n, bpm_range=span + (hi - lo))
    sb = {r["deezer_id"]: r for r in rb}
    out, seen = [], set()
    for r in ra:
        o = sb.get(r["deezer_id"])
        if not o or r["deezer_id"] in exclude:
            continue
        base = _norm(re.sub(r"\s*[\(\[].*$", "", r["title"])) + "|" + _norm(r["artist"])
        if base in seen:                                # skip "(Extended Mix)" twins
            continue
        if not (lo - 3 <= r["bpm"] <= hi + 3):         # sits between the two tempos
            continue
        both = r["score"] * o["score"] * (1 + min(r["key_match"], o["key_match"]))
        out.append({**r, "similarity": round((r["similarity"] + o["similarity"]) / 2), "score": round(both, 5),
                    "fit_before": r["key_match"], "fit_after": o["key_match"], "_base": base})
    out.sort(key=lambda r: -r["score"])
    picked = []
    for r in out:
        if r["_base"] not in seen:
            seen.add(r["_base"]); picked.append({k: v for k, v in r.items() if k != "_base"})
        if len(picked) >= limit:
            break
    return picked
