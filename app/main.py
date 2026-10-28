"""SimilarSounds prototype API.

Run:  uv run uvicorn app.main:app --reload --port 8000
"""
import json
import os
import random
import re
import sqlite3
import threading
from datetime import date
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app import billing, guides, house, info_pages, pages, reviews, sources, tokens, tracklist, mixprev, describe, planner, fresh
from app.artists import Artists, main_artist
from app.analysis import analyse
from app.catalogue import DB_PATH, Index, energy_vector
from app.ranking import rank
from app.suggest import Suggester
from scripts.seed import STYLES

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="SimilarSounds")
if not DB_PATH.exists():                 # normally downloaded during the build; if not, get it now
    from scripts.catalogue_store import fetch
    fetch()
index = Index()
suggester = Suggester(index)
artists = Artists(index)
_query_cache: dict[int, dict] = {}
_analysis_lock = threading.Lock()

# CANONICAL_HOST (www.similarsounds.com on Render): every other
# address (e.g. similarsounds.onrender.com) permanently redirects to it.
CANONICAL_HOST = os.environ.get("CANONICAL_HOST", "").strip().lower()


_BLOCKED_UA = re.compile("|".join(re.escape(b) for b in pages.BLOCKED_BOTS), re.I)


@app.middleware("http")
async def redirect_to_canonical(request: Request, call_next):
    # SEO-tool crawlers that ignore robots.txt: a tiny "no" instead of the page (saves the bandwidth)
    if request.url.path != "/robots.txt" and _BLOCKED_UA.search(request.headers.get("user-agent", "")):
        return PlainTextResponse("Crawling not allowed. See /robots.txt", status_code=403)
    host = request.headers.get("host", "").split(":")[0].lower()
    if CANONICAL_HOST and host and host != CANONICAL_HOST and request.url.path != "/healthz":
        query = f"?{request.url.query}" if request.url.query else ""
        return RedirectResponse(f"https://{CANONICAL_HOST}{request.url.path}{query}", status_code=301)
    head = request.method == "HEAD"          # uptime checkers and crawlers use HEAD: answer it like GET, minus the body
    if head:
        request.scope["method"] = "GET"
    response = await call_next(request)
    if head:
        request.scope["method"] = "HEAD"    # the server then sends the headers only
    # Static files: ones linked with a ?v= version change name whenever they change, so browsers can keep
    # them for a year; the rest (e.g. images linked without a version) for a day.
    if request.url.path.startswith("/static/") and response.status_code == 200:
        response.headers["Cache-Control"] = ("public, max-age=31536000, immutable" if "v=" in request.url.query
                                             else "public, max-age=86400")
    # Pages: browsers must check for a newer version every time (a quick 304 when nothing changed),
    # so a new release shows up on the next visit instead of an old saved copy.
    elif "text/html" in response.headers.get("content-type", "") and "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-cache"
    return response


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


# Optional accounts (Supabase Auth). Both values are public by design: they go into the web page.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ggcohybfbbspoeccdkud.supabase.co").strip()
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "").strip()


@app.get("/api/config")
def config():
    return {"supabase_url": SUPABASE_URL if SUPABASE_ANON_KEY else "", "supabase_anon_key": SUPABASE_ANON_KEY,
            "subscriptions": billing.enabled()}


@app.post("/api/subscribe")
async def subscribe(request: Request):
    """SimilarSounds Unlimited: a Stripe Checkout page for the logged-in visitor (off until SUBSCRIPTIONS_ON=1)."""
    if not billing.enabled():
        raise HTTPException(503, "Subscriptions aren't open yet")
    user = await run_in_threadpool(billing.signed_in_user, request)
    if not user:
        raise HTTPException(401, "Log in first")
    try:
        return {"url": await run_in_threadpool(billing.checkout_url, user)}
    except Exception as e:
        print(f"billing: checkout failed: {e}", flush=True)
        raise HTTPException(502, "Couldn't open the payment page. Please try again.")


@app.post("/api/billing-portal")
async def billing_portal(request: Request):
    """Stripe's page to cancel SimilarSounds Unlimited or change the card."""
    user = await run_in_threadpool(billing.signed_in_user, request)
    if not user:
        raise HTTPException(401, "Log in first")
    try:
        url = await run_in_threadpool(billing.portal_url, user)
    except Exception as e:
        print(f"billing: portal failed: {e}", flush=True)
        url = None
    if not url:
        raise HTTPException(404, "No subscription found for this account")
    return {"url": url}


@app.post("/api/stripe/webhook", include_in_schema=False)
async def stripe_webhook(request: Request):
    """Stripe tells us about payments, renewals and cancellations; the account's searches follow."""
    payload = await request.body()
    if not billing.verify(payload, request.headers.get("stripe-signature", "")):
        raise HTTPException(400, "Bad signature")
    try:
        await run_in_threadpool(billing.handle, json.loads(payload))
    except Exception as e:                       # tell Stripe to try again later
        print(f"billing: webhook failed: {e}", flush=True)
        raise HTTPException(500, "Couldn't save that")
    return {"ok": True}


@app.get("/healthz")
def healthz():
    if not index.rows:                   # no catalogue: fail, so Render keeps the previous version running
        raise HTTPException(503, "No catalogue loaded")
    return {"ok": True, "tracks": len(index.rows)}


def analyse_query(deezer_id: int) -> dict:
    """Features for the pasted track: from the catalogue if we have it, otherwise analyse its preview."""
    if deezer_id in index.ids:
        r = index.rows[index.ids[deezer_id]]
        return {"key": r["key"], "camelot": r["camelot"], "bpm": r["bpm"], "energy": float(r["energy"]),
                "embedding": json.loads(r["embedding"]), "energy_raw": json.loads(r["energy_raw"]),
                "title": r["title"], "artist": r["artist"],
                "label": r["label"], "cover": r["cover"], "release_date": r["release_date"],
                "deezer_id": deezer_id, "in_catalogue": True, "row": index.ids[deezer_id],
                # Everything in the catalogue was collected as house
                "house_check": {"is_house": True, "confidence": 1.0, "reason": None}}
    if deezer_id in _query_cache:
        return _query_cache[deezer_id]
    # One analysis at a time (keeps peak memory inside the free 512 MB plan). Re-check the cache
    # once we hold the lock: a prefetch for the same track may have just finished it.
    with _analysis_lock:
        if deezer_id in _query_cache:
            return _query_cache[deezer_id]
        t = sources.deezer_track(deezer_id)
        if not t.get("preview"):
            raise HTTPException(404, "No preview available for this track, so it can't be analysed.")
        feats = analyse(sources.fetch_preview(t["preview"]))
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
    request: Request,
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
    # Each new track searched uses a token, once we know the search works (the same track again today is free)
    tk = await run_in_threadpool(tokens.check, request, int(deezer_id), True)
    if tk and not tk.get("allowed"):
        raise HTTPException(402, {"code": "no_tokens", "stage": tk.get("stage"), "signed_in": tk.get("signed_in"),
                                  "reset_at": tk.get("reset_at")})
    results, guessed_style = rank(index, q, exclude_id=deezer_id, max_age_days=max_age_days,
                                  strict_key=strict_key, bpm_range=bpm_range, style=style or None, limit=limit)
    query = {k: v for k, v in q.items() if k not in ("embedding", "energy_raw", "rhythm", "row")}
    query["style"] = guessed_style if q["house_check"]["is_house"] else None
    query["energy"] = int(query["energy"])
    query["sound"] = index.describe(q["energy_raw"], q["embedding"])
    # Not house: hold results back unless the visitor chooses to see them anyway
    if not q["house_check"]["is_house"] and not allow_non_house:
        results = []
    _, qv, space = index.query_vec(q)
    like = artists.like_vector(qv, exclude=main_artist(q["artist"]), k=6, space=space) if results else []
    similar_artists = [{"name": a["name"], "slug": pages.slugify(a["name"])} for a in like]
    return {"source": src, "query": query, "results": results, "similar_artists": similar_artists, "tokens": tk}


def _set_item(q: dict) -> dict:
    return {"deezer_id": q["deezer_id"], "title": q["title"], "artist": q["artist"], "cover": q["cover"],
            "key": q["key"], "camelot": q["camelot"], "bpm": q["bpm"], "energy": int(q["energy"])}


@app.post("/api/tracklist")
async def import_tracklist(request: Request):
    """Paste a set's tracklist: each line is found in the catalogue (free) or looked up and analysed
    (uses a search credit each, like a normal search). Returns set-builder items in order."""
    try:
        body = await request.json()
        text = str(body.get("text") or "")[:8000]
        rows = body.get("tracks") or []
    except (ValueError, AttributeError):
        raise HTTPException(400, "Bad tracklist")
    if isinstance(rows, list) and rows:                 # artist and title typed in separate boxes
        lines = [(str(r.get("artist") or "").strip()[:200], str(r.get("title") or "").strip()[:200])
                 for r in rows[:tracklist.MAX_LINES] if isinstance(r, dict)]
        lines = [(a, t) for a, t in lines if a and t]
    else:
        lines = tracklist.parse(text)
    if not lines:
        raise HTTPException(400, "Couldn't read any tracks. Put one track per line, like 'Artist - Title'.")
    out, looked_up = [], 0
    for artist, title in lines:
        label = f"{artist} - {title}"
        did = tracklist.find_in_catalogue(index, artist, title)
        try:
            if did is None:
                if looked_up >= 20:
                    out.append({"line": label, "status": "skipped"}); continue
                hit = await run_in_threadpool(sources.find_on_deezer, label, "")
                if not hit:
                    out.append({"line": label, "status": "not_found"}); continue
                did = hit["id"]
                if did not in index.ids:
                    tk = await run_in_threadpool(tokens.check, request, int(did), True)
                    if tk and not tk.get("allowed"):
                        out.append({"line": label, "status": "no_credits"}); continue
                    looked_up += 1
            q = await run_in_threadpool(analyse_query, did)
            out.append({"line": label, "status": "found", "track": _set_item(q)})
        except HTTPException:
            out.append({"line": label, "status": "not_found"})
        except Exception:
            out.append({"line": label, "status": "not_found"})
    return {"items": out, "tokens": await run_in_threadpool(tokens.check, request, None, False)}


@app.post("/api/fresh")
async def fresh_for_set(request: Request):
    """'Fresh for your set': the newest releases that mix with what's already in the visitor's set."""
    try:
        ids = [int(x) for x in (await request.json()).get("ids", [])][:60]
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(400, "Bad set")
    return await run_in_threadpool(fresh.fresh, index, ids)


@app.post("/api/plan")
async def plan_gig(request: Request):
    """'Plan my gig': a whole set for a slot (warm-up, peak time, closing, all night), every track mixing into the next."""
    try:
        body = await request.json()
        minutes = int(body.get("minutes") or 60)
        slot = str(body.get("slot") or "peak")
        style = str(body.get("style") or "")
        seed = int(body["seed"]) if str(body.get("seed") or "").isdigit() else None
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(400, "Bad plan")
    if slot not in planner.SLOTS or not 30 <= minutes <= 240 or (style and style not in STYLES):
        raise HTTPException(400, "Bad plan")
    tracks = await run_in_threadpool(planner.plan, index, minutes, slot, style, seed)
    if not tracks:
        raise HTTPException(404, "Not enough tracks for that yet. Try another vibe.")
    return {"tracks": tracks}


@app.get("/api/describe/words")
def describe_words():
    """The sounds "Describe a sound" understands, for the drop-down while typing."""
    return {"words": [[p, describe._syn.get(p, [])] for p in describe.PHRASES], "examples": describe.EXAMPLES}


@app.get("/api/describe")
def describe_sound(q: str = Query("", max_length=200)):
    """'Describe a sound': tracks that sound like the words typed (e.g. "warm sunset deep house with sax")."""
    return describe.search(index, q)


@app.get("/api/clip/{deezer_id}")
async def mix_clip(deezer_id: int, request: Request):
    """A track's preview clip, for "Hear the mix" and one-tap previews. Answers byte-range requests,
    so the player's drag bar can jump to any point in the track."""
    try:
        data = await run_in_threadpool(mixprev.clip, deezer_id)
    except Exception:
        raise HTTPException(404, "No preview for this track")
    headers = {"Cache-Control": "private, max-age=900", "Accept-Ranges": "bytes"}
    m = re.match(r"bytes=(\d*)-(\d*)$", request.headers.get("range", "").strip())
    if m and (m.group(1) or m.group(2)):
        size = len(data)
        if m.group(1):
            start, end = int(m.group(1)), min(int(m.group(2)) if m.group(2) else size - 1, size - 1)
        else:                                   # "bytes=-500": the last 500 bytes
            start, end = max(0, size - int(m.group(2))), size - 1
        if start >= size or start > end:
            return Response(status_code=416, headers={"Content-Range": f"bytes */{size}"})
        headers["Content-Range"] = f"bytes {start}-{end}/{size}"
        return Response(data[start:end + 1], status_code=206, media_type="audio/mpeg", headers=headers)
    return Response(data, media_type="audio/mpeg", headers=headers)


@app.get("/api/mixinfo")
async def mix_info(a: int, b: int):
    """Tempo and beat positions for both tracks of a "Hear the mix" preview."""
    try:
        qa = await run_in_threadpool(analyse_query, a)
        qb = await run_in_threadpool(analyse_query, b)
        ga = await run_in_threadpool(mixprev.beat_grid, a, float(qa["bpm"]))
        gb = await run_in_threadpool(mixprev.beat_grid, b, float(qb["bpm"]))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(404, "Couldn't prepare that mix")
    return {"a": ga, "b": gb}


@app.get("/api/bridge")
async def bridge(a: int, b: int, exclude: str = Query("", max_length=2000)):
    """Tracks to put between two set tracks so the transition works: they mix with both."""
    try:
        qa = await run_in_threadpool(analyse_query, a)
        qb = await run_in_threadpool(analyse_query, b)
    except HTTPException:
        raise HTTPException(404, "Couldn't analyse one of those tracks")
    skip = {int(x) for x in exclude.split(",") if x.strip().isdigit()} | {a, b}
    return {"results": tracklist.bridges(index, qa, qb, skip, limit=12)}


@app.post("/api/vote")
async def vote(request: Request):
    """Thumbs up / down on a match (helps us measure and improve matching)."""
    try:
        b = await request.json()
        seed, match, value = int(b["seed"]), int(b["match"]), int(b["vote"])
    except (ValueError, TypeError, KeyError):
        raise HTTPException(400, "Bad vote")
    if value not in (-1, 0, 1):
        raise HTTPException(400, "Bad vote")
    ok = await run_in_threadpool(tokens.vote, request, seed, match, value, b.get("rank"), b.get("similarity"), str(b.get("mix") or "")[:16])
    return {"ok": ok}


@app.get("/api/tokens")
async def tokens_left(request: Request):
    """How many free searches this visitor has left (doesn't use one)."""
    return await run_in_threadpool(tokens.check, request, None, False) or {"metered": False}


@app.post("/api/prefetch/{deezer_id}")
async def prefetch(deezer_id: int):
    """Start analysing a track the visitor is about to pick, so the real search is instant."""
    if deezer_id not in index.ids and deezer_id not in _query_cache:
        threading.Thread(target=lambda: _safe(analyse_query, deezer_id), daemon=True).start()
    return {"ok": True}


def _safe(fn, *a):
    try:
        fn(*a)
    except Exception:
        pass


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
    # "Try a fresh release": four recent releases, one per artist and sub-genre, a different set each day
    # (picked at random from the last 14 days, widening to 30 / 60 if there aren't enough)
    examples, seen = [], set()
    explicit = re.compile(r"\b(pussy|fuck|shit|bitch|dick|cock|nigga|hoe|sex)\w*", re.I)
    ok = [r for r in rows if r["cover"] and r["release_date"] and not explicit.search(r["title"])]
    for days in (14, 30, 60, 100000):
        pool = [r for r in ok if (today - date.fromisoformat(r["release_date"])).days <= days]
        if len({r["style"] for r in pool}) >= 4 and len(pool) >= 60:
            break
    random.Random(today.toordinal()).shuffle(pool)
    # up to five sets of eight (the home page rotates through them), each set at most two per sub-genre,
    # and no artist twice across all of them
    sets: list[list[dict]] = []
    for _ in range(5):
        group = []
        for r in pool:
            if r["artist"] in seen or sum(e["style"] == r["style"] for e in group) >= 2:
                continue
            seen.add(r["artist"])
            group.append({"deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"],
                          "cover": r["cover"], "style": r["style"], "camelot": r["camelot"], "bpm": r["bpm"],
                          "age_days": (today - date.fromisoformat(r["release_date"])).days if r["release_date"] else None})
            if len(group) == 8:
                break
        if len(group) < 8:
            break
        sets.append(group)
    examples = sets[0] if sets else examples
    return {"tracks": len(rows), "last_12_months": recent, "styles": list(STYLES), "examples": examples,
            "fresh_sets": sets, "most_played": most_played(12)}


_top_cache = {"at": 0.0, "rows": []}


def most_played(n: int = 4) -> list[dict]:
    """The tracks played most on the site in the last 7 days (refreshed every 5 minutes), one per artist."""
    import time
    if time.time() - _top_cache["at"] > 300:
        _top_cache["rows"] = tokens.top_played(7, 40); _top_cache["at"] = time.time()
    today = date.today(); out, artists_seen = [], set()
    for did, plays in _top_cache["rows"]:
        if did not in index.ids:
            continue
        r = index.rows[index.ids[did]]
        if r["artist"] in artists_seen:
            continue
        artists_seen.add(r["artist"])
        out.append({"deezer_id": r["deezer_id"], "title": r["title"], "artist": r["artist"], "cover": r["cover"],
                    "style": r["style"], "camelot": r["camelot"], "key": r["key"], "bpm": r["bpm"], "plays": plays,
                    "age_days": (today - date.fromisoformat(r["release_date"])).days if r["release_date"] else None})
        if len(out) == n:
            break
    return out


@app.post("/api/play")
async def play(request: Request):
    """Count one preview play for the "Most played" list (only tracks in the catalogue)."""
    try:
        did = int((await request.json()).get("id"))
    except (ValueError, TypeError):
        raise HTTPException(400, "Bad track id")
    if did not in index.ids:
        return {"ok": False}
    return {"ok": await run_in_threadpool(tokens.count_play, did)}


LANG_CODES = {"en", "es", "fr", "de", "it", "pt", "nl"}


@app.post("/api/review")
async def review(request: Request):
    try:
        body = await request.json()
        stars = int(body.get("stars"))
        plays = max(0, min(int(body.get("plays") or 0), 1_000_000))
    except (ValueError, TypeError, AttributeError):
        raise HTTPException(400, "Bad review")
    if not 1 <= stars <= 5:
        raise HTTPException(400, "Stars must be 1-5")
    lang = body.get("lang") if body.get("lang") in LANG_CODES else "en"
    comment = str(body.get("comment") or "").strip()[:1000]
    source = "page" if body.get("source") == "page" else "popup"
    await run_in_threadpool(reviews.save, stars, lang, plays, comment, source)
    return {"ok": True}


@app.post("/api/reload")
def reload():
    index.reload()
    artists.rebuild()
    _page_cache.clear()
    suggester.rebuild()
    return {"tracks": len(index.rows)}


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


# ---------- public pages for search engines (one per catalogue track, plus browse pages)
_page_cache: dict[int, str] = {}
_style_by_slug = lambda: {pages.slugify(s): s for s in {r["style"] for r in index.rows if r["style"]}}


@app.get("/similar-to", response_class=HTMLResponse)
def similar_hub():
    return pages.hub_page(index)


@app.get("/similar-to/genre/{slug}", response_class=HTMLResponse)
def similar_genre(slug: str, page: int = 1):
    style = _style_by_slug().get(slug)
    if not style:   # a sub-genre we no longer use (e.g. afro-house): send people to the browse page
        return RedirectResponse("/similar-to", status_code=301)
    return pages.style_page(index, style, page)


@app.get("/similar-to/bpm/{lo}-{hi}", response_class=HTMLResponse)
def similar_bpm(lo: int, hi: int, page: int = 1):
    if (lo, hi) not in pages.BPM_WINDOWS:
        raise HTTPException(404, "No such BPM range")
    return pages.bpm_page(index, lo, hi, page)


@app.get("/similar-to/{slug}", response_class=HTMLResponse)
def similar_track(slug: str):
    m = re.search(r"-(\d+)$", slug) or re.fullmatch(r"(\d+)", slug)
    deezer_id = int(m.group(1)) if m else None
    if deezer_id not in index.ids:
        return removed_track(deezer_id)
    r = index.rows[index.ids[deezer_id]]
    if pages.track_path(r) != f"/similar-to/{slug}":
        return RedirectResponse(pages.track_path(r), status_code=301)
    if deezer_id not in _page_cache:
        q = analyse_query(deezer_id)
        results, guessed = rank(index, q, exclude_id=deezer_id, limit=30)
        if len(_page_cache) > 2000:
            _page_cache.clear()
        _page_cache[deezer_id] = pages.track_page(index, q, results, r["style"] or guessed)
    return _page_cache[deezer_id]


_kept_versions: dict = {}


def removed_track(deezer_id):
    """A track page Google may still have, for a track that's left the catalogue. Duplicate versions go
    to the version we kept (301); tracks set aside as not our genres get a friendly 410 'gone' page."""
    from scripts.dedupe_versions import key as version_key
    row = None
    if deezer_id:
        with sqlite3.connect(DB_PATH) as conn:
            try:
                row = conn.execute("SELECT deezer_id, artist, title, aside_kind FROM set_aside WHERE deezer_id = ?",
                                   (deezer_id,)).fetchone()
            except sqlite3.OperationalError:
                row = None
    if not row:
        raise HTTPException(404, "We don't have a page for that track yet")
    if row[3] == "duplicate version":
        if _kept_versions.get("n") != len(index.rows):
            _kept_versions.clear(); _kept_versions["n"] = len(index.rows)
            for r in index.rows:
                _kept_versions.setdefault(version_key(r["artist"] or "", r["title"] or "")[:2], r)
        kept = _kept_versions.get(version_key(row[1] or "", row[2] or "")[:2])
        if kept:
            return RedirectResponse(pages.track_path(kept), status_code=301)
    return HTMLResponse(pages.gone_page(row[0], row[1], row[2]), status_code=410)


@app.get("/artists-like", response_class=HTMLResponse)
def artists_hub():
    return pages.artists_hub(artists)


@app.get("/artists-like/{slug}", response_class=HTMLResponse)
def artists_like(slug: str):
    name = next((n for n in artists.names if pages.slugify(n) == slug), None)
    if not name:
        raise HTTPException(404, "We don't have that artist yet")
    return pages.artist_page(artists, name)


@app.get("/database", response_class=HTMLResponse)
def database():
    return info_pages.database_page(index)


@app.get("/vs", response_class=HTMLResponse)
def vs_hub():
    return info_pages.vs_hub()


@app.get("/vs/{slug}", response_class=HTMLResponse)
def vs(slug: str):
    html = info_pages.vs_page(slug)
    if html is None:
        return RedirectResponse("/vs", status_code=301)
    return html


@app.get("/guides", response_class=HTMLResponse)
def guides_hub():
    return guides.guides_hub()


@app.get("/guides/{slug}", response_class=HTMLResponse)
def guide(slug: str):
    html = guides.guide_page(slug)
    if html is None:
        return RedirectResponse("/guides", status_code=301)
    return html


@app.get("/sitemap.xml")
def sitemap():
    return Response(pages.sitemap(index, artists), media_type="application/xml")


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    return pages.ROBOTS


@app.get("/llms.txt", response_class=PlainTextResponse)
def llms():
    return pages.LLMS


@app.get(f"/{pages.INDEXNOW_KEY}.txt", response_class=PlainTextResponse, include_in_schema=False)
def indexnow_key():
    return pages.INDEXNOW_KEY


@app.get("/stats", include_in_schema=False)
def stats_page():
    """Private dashboard: visitors and reviews. The page is public but the numbers only load for
    the owner account (checked inside Supabase)."""
    return FileResponse(STATIC / "stats.html", headers={"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store"})


@app.get("/privacy")
def privacy():
    return FileResponse(STATIC / "legal" / "privacy.html")


@app.get("/cookies")
def cookies():
    return FileResponse(STATIC / "legal" / "cookies.html")


@app.get("/terms")
def terms():
    return FileResponse(STATIC / "legal" / "terms.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
