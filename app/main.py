"""SimilarSounds prototype API.

Run:  uv run uvicorn app.main:app --reload --port 8000
"""
import json
import os
import re
import threading
from datetime import date
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import house, sources
from app.analysis import analyse
from app.catalogue import Index, energy_vector
from app.ranking import rank
from app.suggest import Suggester
from scripts.seed import STYLES

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="SimilarSounds")
index = Index()
suggester = Suggester(index)
_query_cache: dict[int, dict] = {}
_analysis_lock = threading.Lock()

# CANONICAL_HOST (www.similarsounds.com on Render): every other
# address (e.g. similarsounds.onrender.com) permanently redirects to it.
CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "").strip().lower()


@app.middleware("http")
async def redirect_to_canonical(request: Request, call_next):
    host = request.headers.get("host", "").split(":")[0].lower()
    if CANONICAL_HOST and host and host != CANONICAL_HOST and request.url.path != "/healthz":
        query = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(f"https://{CANONICAL_HOST}{request.url.path}{query}", status_code=301)
    return await call_next(request)


@app.on_event("startup")
def warm_up():
    """Run one throwaway analysis in the background so librosa's JIT-compiled code is
    ready before the first real visitor (otherwise their first search takes ~25 s)."""
    import io

    import soundfile as sf

    def run():
        buf = io.BytesIO()
        sf.write(buf, (np.random.default_rng(0).standard_normal(22050 * 5) * 0.1).astype("float32"),
                 22050, format="WAV")
        analyse(buf.getvalue())

    threading.Thread(target=run, daemon=True).start()


@app.get("/healthz")
def healthz():
    return {"ok": True, "tracks": len(index.rows)}


def analyse_query(deezer_id: int) -> dict:
    """Features for the pasted track: from the catalogue if we have it, otherwise analyse its preview."""
    if deezer_id in index.ids:
        r = index.rows[index.ids[deezer_id]]
        return {"key": r["key"], "camelot": r["camelot"], "bpm": r["bpm"], "energy": float(r["energy"]),
                "embedding": json.loads(r["embedding"]), "title": r["title"], "artist": r["artist"],
                "label": r["label"], "cover": r["cover"], "release_date": r["release_date"],
                "deezer_id": deezer_id, "in_catalogue": True,
                # Everything in the catalogue was collected as house
                "house_check": {"is_house": True, "confidence": 1.0, "reason": None}}
    if deezer_id in _query_cache:
        return _query_cache[deezer_id]
    t = sources.deezer_track(deezer_id)
    if not t.get("preview"):
        raise HTTPException(404, "No preview available for this track, so it can't be analysed.")
    audio = sources.fetch_preview(t["preview"])
    with _analysis_lock:   # one analysis at a time keeps peak memory inside the free 512 MB plan
        feats = analyse(audio)
    energy = float(index.energy_scores(np.array([energy_vector(feats["energy_raw"])], dtype="float32"))[0])
    try:
        album = sources.deezer(f"/album/{t['album']['id']}")
    except Exception:
        album = {}
    genres = [g["id"] for g in album.get("genres", {}).get("data", [])]
    q = {**feats, "energy": energy, "title": t["title"], "artist": t["artist"]["name"],
         "label": album.get("label"), "cover": t["album"].get("cover_medium"),
         "release_date": t.get("release_date"), "deezer_id": deezer_id, "in_catalogue": False,
         "house_check": house.check(house.house_features(feats, index, genres))}
    _query_cache[deezer_id] = q
    return q


@app.get("/api/match")
async def match(
    url: str = Query(..., description="YouTube / SoundCloud / Beatport / Deezer link, or 'Artist - Title'"),
    max_age_days: int | None = None,
    strict_key: bool = False,
    bpm_range: float = 6.0,
    style: str | None = None,
    allow_non_house: bool = False,
    limit: int = Query(30, ge=1, le=90),
):
    if not index.rows:
        raise HTTPException(503, "The catalogue is empty - run the seed script first.")
    try:
        src = await run_in_threadpool(sources.resolve_link, url)
    except ValueError as e:
        raise HTTPException(400, str(e))

    deezer_id = src.get("deezer_id")
    if not deezer_id:
        hit = await run_in_threadpool(sources.find_on_deezer, src["title"], src["author"])
        if not hit:
            raise HTTPException(404, f"Couldn't find \"{sources.clean_title(src['title'])}\" in our preview "
                                     "source yet. Try typing 'Artist - Title'.")
        deezer_id = hit["id"]

    q = await run_in_threadpool(analyse_query, deezer_id)
    results, guessed_style = rank(index, q, exclude_id=deezer_id, max_age_days=max_age_days,
                                  strict_key=strict_key, bpm_range=bpm_range, style=style or None, limit=limit)
    query = {k: v for k, v in q.items() if k not in ("embedding", "energy_raw", "rhythm")}
    query["style"] = guessed_style if q["house_check"]["is_house"] else None
    query["energy"] = int(query["energy"])
    # Not house: hold results back unless the visitor chooses to see them anyway
    if not q["house_check"]["is_house"] and not allow_non_house:
        results = []
    return {"source": src, "query": query, "results": results}


@app.get("/api/tracks")
async def tracks(ids: str = Query(..., max_length=400)):
    """Key/BPM/energy for a list of Deezer ids (used to open a shared set)."""
    out = []
    for raw in ids.split(",")[:30]:
        if not raw.strip().isdigit():
            continue
        try:
            q = await run_in_threadpool(analyse_query, int(raw))
        except HTTPException:
            continue
        out.append({"deezer_id": q["deezer_id"], "title": q["title"], "artist": q["artist"], "cover": q["cover"],
                    "key": q["key"], "camelot": q["camelot"], "bpm": q["bpm"], "energy": int(q["energy"])})
    return {"tracks": out}


@app.get("/api/suggest")
def suggest(q: str = Query("", max_length=100)):
    """Search-as-you-type: artists from the first letter, tracks from 3 letters, or an artist's
    tracks once the box reads "Artist - "."""
    if q.lower().startswith(("http", "www.")) or "://" in q:
        return {"artists": [], "tracks": []}
    return suggester.suggest(q)


@app.get("/api/stats")
def stats():
    rows = index.rows
    today = date.today()
    recent = sum(1 for r in rows if r["release_date"] and (today - date.fromisoformat(r["release_date"])).days <= 365)
    # Example tracks for the start screen: the newest releases, one per artist and sub-genre
    examples, seen = [], set()
    explicit = re.compile(r"\b(pussy|fuck|shit|bitch|dick|cock|nigga|hoe|sex)\w*", re.I)
    for r in sorted(rows, key=lambda r: r["release_date"] or "", reverse=True):
        if not r["cover"] or explicit.search(r["title"]) or r["artist"] in seen or r["style"] in {e["style"] for e in examples}:
            continue
        seen.add(r["artist"])
        examples.append({"deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"],
                         "cover": r["cover"], "style": r["style"]})
        if len(examples) == 4:
            break
    return {"tracks": len(rows), "last_12_months": recent, "styles": list(STYLES), "examples": examples}


@app.post("/api/reload")
def reload():
    index.reload()
    suggester.rebuild()
    return {"tracks": len(index.rows)}


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
