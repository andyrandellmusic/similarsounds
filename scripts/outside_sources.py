"""More places to find new house releases for the daily pull, beyond Deezer's own playlists and labels:
    Discogs      the newest house releases added, by style (needs DISCOGS_TOKEN, or the token saved on the Mac)
    MusicBrainz  releases tagged house / deep house / tech house... from the last few weeks (open, no key)
    (and a daily back-catalogue batch: older Discogs and MusicBrainz releases, and every house / dance release Apple's
     iTunes catalogue has for the artists we already carry)
    Last.fm      the top tracks on each house tag (only when LASTFM_API_KEY is set; non-commercial use only)
    iTunes       Apple's House and Dance top-song charts in 8 countries (open, no key; popular tracks of any age)
Each find is then looked up on Deezer, which supplies the preview, artwork and release date, and has to pass the
same checks as the label pull: a dance album, released in the last few months. Releases already looked at are
remembered in data/outside_follow.json, so each day only opens new ones.
"""
import json
import os
import re
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import httpx

from app import sources

STATE = Path(__file__).resolve().parent.parent / "data" / "outside_follow.json"
UA = "SimilarSounds/1.0 ( management@similarsounds.com )"
DISCOGS_STYLES = ["House", "Deep House", "Tech House", "Minimal", "Nu-Disco", "Afro House"]
MB_TAGS = ["house", "deep house", "tech house", "minimal", "nu disco", "afro house"]
LASTFM_TAGS = ["deep house", "tech house", "house", "minimal house", "nu disco", "afro house"]
ITUNES_CHARTS = {"House": 1048, "Dance": 17}
ITUNES_COUNTRIES = ["gb", "us", "de", "nl", "fr", "es", "it", "au"]

_http = httpx.Client(timeout=30, headers={"User-Agent": UA})
_albums: dict[int, dict] = {}


def _discogs_token() -> str:
    tok = os.environ.get("DISCOGS_TOKEN", "").strip()
    f = Path.home() / ".config" / "similarsounds" / "discogs_token"
    return tok or (f.read_text().strip() if f.exists() else "")


def _clean(s: str) -> str:
    s = re.sub(r"\s*\(\d+\)", "", s or "")                  # Discogs' "Artist (2)" numbering
    s = re.sub(r"\s*[\(\[](original|extended|radio|club)[^\)\]]*[\)\]]", "", s, flags=re.I)
    return s.strip()


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", _clean(s).lower())


def _get(url: str, tries: int = 3, **kw) -> httpx.Response | None:
    for n in range(tries):
        try:
            r = _http.get(url, **kw)
            if r.status_code == 200:
                return r
            if r.status_code in (429, 503):
                time.sleep(2 + 3 * n); continue
            return None
        except httpx.HTTPError:
            time.sleep(2)
    return None


# ---------- where the releases come from: (key, artist, title) ----------
def discogs_releases(pages: int = 2) -> list[tuple[str, str, str]]:
    tok = _discogs_token()
    if not tok:
        print("  Discogs: no token, skipped (add DISCOGS_TOKEN)", flush=True)
        return []
    out, year = [], date.today().year
    for style in DISCOGS_STYLES:
        for page in range(1, pages + 1):
            r = _get("https://api.discogs.com/database/search", headers={"Authorization": f"Discogs token={tok}"},
                     params={"type": "release", "style": style, "year": year, "sort": "date_added", "sort_order": "desc",
                             "per_page": 100, "page": page})
            time.sleep(1.1)                                          # Discogs: 60 requests a minute
            for x in (r.json().get("results", []) if r else []):
                artist, _, title = (x.get("title") or "").partition(" - ")
                if title and not artist.lower().startswith("various"):
                    out.append((f"dg:{x.get('master_id') or x.get('id')}", artist, title))
    return out


def musicbrainz_releases(days: int = 45) -> list[tuple[str, str, str]]:
    since, today = (date.today() - timedelta(days=days)).isoformat(), date.today().isoformat()
    out = []
    for tag in MB_TAGS:
        r = _get("https://musicbrainz.org/ws/2/release/", headers={"Accept": "application/json"},
                 params={"query": f'tag:"{tag}" AND date:[{since} TO {today}]', "fmt": "json", "limit": 100})
        time.sleep(1.2)                                              # MusicBrainz: one request a second
        for x in (r.json().get("releases", []) if r else []):
            artist = "".join(a.get("name", "") + a.get("joinphrase", "") for a in x.get("artist-credit", []))
            if artist and x.get("title") and not artist.lower().startswith("various"):
                out.append((f"mb:{x.get('release-group', {}).get('id') or x['id']}", artist, x["title"]))
    return out


def lastfm_tracks() -> list[tuple[str, str, str]]:
    key = os.environ.get("LASTFM_API_KEY", "").strip()
    if not key:
        return []
    out = []
    for tag in LASTFM_TAGS:
        r = _get("https://ws.audioscrobbler.com/2.0/", params={"method": "tag.gettoptracks", "tag": tag, "limit": 100,
                                                              "api_key": key, "format": "json"})
        time.sleep(0.3)
        for t in ((r.json().get("tracks") or {}).get("track", []) if r else []):
            artist, title = (t.get("artist") or {}).get("name", ""), t.get("name", "")
            if artist and title:
                out.append((f"lf:{_norm(artist)}|{_norm(title)}", artist, title))
    return out


def itunes_charts() -> list[tuple[str, str, str]]:
    out = []
    for country in ITUNES_COUNTRIES:
        for genre in ITUNES_CHARTS.values():
            r = _get(f"https://itunes.apple.com/{country}/rss/topsongs/limit=200/genre={genre}/json")
            time.sleep(0.5)
            for e in ((r.json().get("feed") or {}).get("entry", []) if r else []):
                artist, title = e.get("im:artist", {}).get("label", ""), e.get("im:name", {}).get("label", "")
                if artist and title:
                    out.append((f"it:{_norm(artist)}|{_norm(title)}", artist, title))
    return out


# ---------- finding them on Deezer ----------
def _album(aid: int) -> dict:
    if aid not in _albums:
        _albums[aid] = sources.deezer(f"/album/{aid}")
    return _albums[aid]


def _ok_album(al: dict, cutoff: str, dance_genres: set[int]) -> bool:
    genres = {g["id"] for g in (al.get("genres") or {}).get("data", [])}
    return (al.get("release_date") or "") >= cutoff and (not genres or bool(genres & dance_genres))


def deezer_release(artist: str, title: str) -> dict | None:
    """The Deezer album for this release, if the names match."""
    a, t = _clean(artist).split(",")[0].split(" & ")[0], _clean(title)
    hits = sources.deezer("/search/album", q=f'artist:"{a}" album:"{t}"', limit=10).get("data", []) \
        or sources.deezer("/search/album", q=f"{a} {t}", limit=10).get("data", [])
    for h in hits:
        if _norm(h.get("title", "")).startswith(_norm(t)[:24]) and _norm(a) in _norm(h.get("artist", {}).get("name", "")):
            return _album(h["id"])
    return None


def deezer_track(artist: str, title: str) -> dict | None:
    a, t = _clean(artist).split(",")[0].split(" & ")[0], _clean(title)
    # a plain search, checked by name below (Deezer's artist:/track: search syntax no longer finds tracks reliably)
    hits = sources.deezer("/search", q=f"{a} {t}", limit=15).get("data", [])
    return next((h for h in hits if h.get("preview") and _norm(h.get("title", "")).startswith(_norm(t)[:20])
                 and _norm(a) in _norm(h.get("artist", {}).get("name", ""))), None)


def outside_candidates(seen: set[int], dance_genres: set[int], max_age_days: int = 120, limit: int = 700,
                       until: float = float("inf")) -> list[tuple[int, str]]:
    """Up to `limit` new tracks a day (anything beyond waits for tomorrow, as it isn't marked as looked at)."""
    state = json.loads(STATE.read_text()) if STATE.exists() else {"done": []}
    done = set(state.get("done", []))
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()
    out, counts = [], {}
    for name, finder, kind in (("Discogs", discogs_releases, "album"), ("MusicBrainz", musicbrainz_releases, "album"),
                               ("Last.fm", lastfm_tracks, "track"), ("iTunes charts", itunes_charts, "any-age track")):
        if time.time() > until:
            break
        try:
            found = [f for f in dict.fromkeys(finder()) if f[0] not in done]
        except Exception as e:
            print(f"  {name} skipped: {e}", file=sys.stderr); continue
        before = len(out)
        for key, artist, title in found:
            if time.time() > until or len(out) >= limit:
                break
            try:
                if kind == "album":
                    al = deezer_release(artist, title)
                    if al and _ok_album(al, cutoff, dance_genres):
                        for t in (al.get("tracks") or {}).get("data", []):
                            if t["id"] not in seen and t.get("preview"):
                                seen.add(t["id"]); out.append((t["id"], "House"))
                else:                               # chart hits are popular whatever their age
                    t = deezer_track(artist, title)
                    if t and t["id"] not in seen and _ok_album(_album(t["album"]["id"]),
                                                               "0000" if kind == "any-age track" else cutoff, dance_genres):
                        seen.add(t["id"]); out.append((t["id"], "House"))
                done.add(key)                       # looked at: don't open it again
            except Exception as e:
                print(f"  {name}: {artist} - {title} skipped: {e}", file=sys.stderr)
        counts[name] = (len(found), len(out) - before)
    for name, (looked, new) in counts.items():
        print(f"    {name}: {looked} releases looked up, {new} new tracks", flush=True)
    state["done"] = sorted(done)[-80000:]
    STATE.write_text(json.dumps(state))
    return out


# ---------- the back catalogue: older house releases we don't have yet, a batch each day ----------
def _discogs_page(style: str, year: int, page: int) -> list[tuple[str, str, str]]:
    tok = _discogs_token()
    if not tok:
        return []
    r = _get("https://api.discogs.com/database/search", headers={"Authorization": f"Discogs token={tok}"},
             params={"type": "release", "style": style, "year": year, "sort": "have", "sort_order": "desc",
                     "per_page": 100, "page": page})                 # the records most people own, first
    time.sleep(1.1)
    out = []
    for x in (r.json().get("results", []) if r else []):
        artist, _, title = (x.get("title") or "").partition(" - ")
        if title and not artist.lower().startswith("various"):
            out.append((f"dg:{x.get('master_id') or x.get('id')}", artist, title))
    return out


def _mb_page(tag: str, start: str, end: str, offset: int) -> list[tuple[str, str, str]]:
    r = _get("https://musicbrainz.org/ws/2/release/", headers={"Accept": "application/json"},
             params={"query": f'tag:"{tag}" AND date:[{start} TO {end}]', "fmt": "json", "limit": 100, "offset": offset})
    time.sleep(1.2)
    out = []
    for x in (r.json().get("releases", []) if r else []):
        artist = "".join(a.get("name", "") + a.get("joinphrase", "") for a in x.get("artist-credit", []))
        if artist and x.get("title") and not artist.lower().startswith("various"):
            out.append((f"mb:{x.get('release-group', {}).get('id') or x['id']}", artist, x["title"]))
    return out


def _itunes_artist_releases(artist: str) -> list[tuple[str, str, str]]:
    """Every house / dance / electronic release Apple has for this artist (the iTunes catalogue)."""
    r = _get("https://itunes.apple.com/search", params={"term": artist, "entity": "musicArtist", "limit": 5})
    time.sleep(3)                                                    # iTunes: about 20 requests a minute
    hit = next((a for a in (r.json().get("results", []) if r else []) if _norm(a.get("artistName", "")) == _norm(artist)), None)
    if not hit:
        return []
    r = _get("https://itunes.apple.com/lookup", params={"id": hit["artistId"], "entity": "album", "limit": 200})
    time.sleep(3)
    rel = [x for x in (r.json().get("results", []) if r else [])
           if x.get("wrapperType") == "collection" and x.get("primaryGenreName") in ITUNES_GENRES]
    rel.sort(key=lambda x: x.get("releaseDate", ""), reverse=True)  # the newest few, so no one artist floods it
    return [(f"ia:{x['collectionId']}", artist, x["collectionName"]) for x in rel[:ITUNES_RELEASES_PER_ARTIST]]


ITUNES_GENRES = {"House", "Dance", "Electronic", "Deep House", "Techno", "Disco"}
ITUNES_ARTISTS_PER_DAY = 120
ITUNES_RELEASES_PER_ARTIST = 10
DISCOGS_PAGES_PER_YEAR = 5          # per style: the 500 most-owned releases of each year
OLDEST_YEAR = 2000


def backfill_candidates(seen: set[int], dance_genres: set[int], limit: int,
                        until: float = float("inf")) -> list[tuple[int, str]]:
    """Up to `limit` older house tracks we don't have, found on Discogs (year by year, back from last year) and
    MusicBrainz (a month at a time, going back). Where it got to is saved, so tomorrow carries on from there."""
    state = json.loads(STATE.read_text()) if STATE.exists() else {"done": []}
    done = set(state.get("done", []))
    back = state.setdefault("back", {})
    dg = back.setdefault("discogs", {"year": date.today().year - 1, "style": 0, "page": 1})
    mb = back.setdefault("musicbrainz", {"end": (date.today() - timedelta(days=45)).isoformat(), "tag": 0, "offset": 0})
    it = back.setdefault("itunes", {"next": 0})
    from app.catalogue import connect                                 # artists already in the catalogue, biggest first
    blocked_file = Path(__file__).resolve().parent.parent / "data" / "blocked_artists.json"
    blocked = {_norm(a) for a in (json.loads(blocked_file.read_text()).get("artists", []) if blocked_file.exists() else [])}
    artists = [a for (a,) in connect().execute(
        "SELECT artist FROM tracks GROUP BY artist ORDER BY COUNT(*) DESC, artist") if _norm(a) not in blocked]
    it_today = 0
    out, looked = [], {"Discogs": 0, "MusicBrainz": 0, "iTunes": 0}

    def take(found, name):
        for key, artist, title in found:
            if len(out) >= limit or time.time() > until:
                return False
            if key in done:
                continue
            looked[name] += 1
            try:
                al = deezer_release(artist, title)
                if al and _ok_album(al, "0000", dance_genres):
                    for t in (al.get("tracks") or {}).get("data", []):
                        if t["id"] not in seen and t.get("preview"):
                            seen.add(t["id"]); out.append((t["id"], "House"))
                done.add(key)
            except Exception as e:
                print(f"  back catalogue: {artist} - {title} skipped: {e}", file=sys.stderr)
        return True

    # take turns: a page from Discogs, then a page from MusicBrainz, until today's share is found
    while len(out) < limit and time.time() < until:
        progressed = False
        if dg["year"] >= OLDEST_YEAR and _discogs_token():
            if take(_discogs_page(DISCOGS_STYLES[dg["style"]], dg["year"], dg["page"]), "Discogs"):
                dg["page"] += 1
                if dg["page"] > DISCOGS_PAGES_PER_YEAR:
                    dg["page"], dg["style"] = 1, dg["style"] + 1
                    if dg["style"] >= len(DISCOGS_STYLES):
                        dg["style"], dg["year"] = 0, dg["year"] - 1
            progressed = True
        if len(out) < limit and time.time() < until and mb["end"] >= f"{OLDEST_YEAR}-01-01":
            end = date.fromisoformat(mb["end"]); start = (end - timedelta(days=30)).isoformat()
            page = _mb_page(MB_TAGS[mb["tag"]], start, mb["end"], mb["offset"])
            if take(page, "MusicBrainz"):
                if len(page) < 50 or mb["offset"] >= 300:          # this tag is done for this month
                    mb["offset"], mb["tag"] = 0, mb["tag"] + 1
                    if mb["tag"] >= len(MB_TAGS):
                        mb["tag"], mb["end"] = 0, (end - timedelta(days=31)).isoformat()
                else:
                    mb["offset"] += 100
            progressed = True
        if len(out) < limit and time.time() < until and it_today < ITUNES_ARTISTS_PER_DAY and artists:
            name = artists[it["next"] % len(artists)]
            if take(_itunes_artist_releases(_clean(name).split(",")[0].split(" & ")[0]), "iTunes"):
                it["next"] = (it["next"] + 1) % len(artists); it_today += 1
            progressed = True
        if not progressed:
            break                                                    # gone all the way back
    print(f"    back catalogue: {looked['Discogs']} Discogs + {looked['MusicBrainz']} MusicBrainz + {looked['iTunes']} iTunes "
          f"releases looked up, {len(out)} new tracks (Discogs now at {dg['year']}, MusicBrainz at {mb['end']}, "
          f"iTunes at artist {it['next']} of {len(artists)})", flush=True)
    state["done"] = sorted(done)[-150000:]
    STATE.write_text(json.dumps(state))
    return out
