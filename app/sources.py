"""Turning pasted links into tracks, and fetching stand-in previews from Deezer.

YouTube and SoundCloud are only used for metadata (oEmbed) and embedded players; Bandcamp only for the page title.
Their audio is never downloaded, per their terms.
"""
import html
import re
import threading
import time
from urllib.parse import urlparse

import httpx

DEEZER = "https://api.deezer.com"
client = httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "similarsounds/0.1"})

# Deezer allows ~50 requests / 5 seconds; stay well under it
_lock = threading.Lock()
_last = [0.0]


def deezer(path: str, **params) -> dict:
    with _lock:
        wait = 0.12 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
    r = client.get(f"{DEEZER}{path}", params=params)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Deezer error: {data['error']}")
    return data


def deezer_track(track_id: int) -> dict:
    return deezer(f"/track/{track_id}")


def fetch_preview(preview_url: str) -> bytes:
    r = client.get(preview_url)
    r.raise_for_status()
    return r.content


NOISE = re.compile(
    r"[\(\[][^\)\]]*(official|video|audio|visuali[sz]er|lyric|hq|hd|4k|premiere|out now|free download|"
    r"original mix|extended mix|extended)[^\)\]]*[\)\]]",
    re.I,
)


def clean_title(title: str) -> str:
    t = NOISE.sub("", title)
    t = re.sub(r"\[[^\]]*\]", "", t)          # [Label] tags
    t = re.sub(r"\b(premiere|out now)\b\s*[:|-]?", "", t, flags=re.I)
    t = re.sub(r"\s*\|.*$", "", t)            # "Title | Channel"
    t = re.sub(r"\b(4k|hd|hq|official (music )?video|official audio|lyrics?)\b", "", t, flags=re.I)
    t = t.replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", t).strip(" -")


def resolve_link(url: str) -> dict:
    """Return {source, title, author, embed_html, deezer_id?} for a pasted link or text."""
    url = url.strip()
    host = urlparse(url).netloc.lower()

    if "deezer.com" in host or "deezer.page.link" in host:
        r = client.get(url)
        m = re.search(r"/track/(\d+)", str(r.url))
        if not m:
            raise ValueError("Please paste a Deezer *track* link.")
        t = deezer_track(int(m.group(1)))
        return {"source": "deezer", "title": t["title"], "author": t["artist"]["name"],
                "embed_html": None, "deezer_id": t["id"]}

    if "youtube.com" in host or "youtu.be" in host:
        r = client.get("https://www.youtube.com/oembed", params={"url": url, "format": "json"})
        if r.status_code != 200:
            raise ValueError("Couldn't read that YouTube link (is the video public?).")
        d = r.json()
        return {"source": "youtube", "title": d["title"], "author": d.get("author_name", ""),
                "author_url": d.get("author_url"), "url": url, "embed_html": d.get("html")}

    if "soundcloud.com" in host:
        r = client.get("https://soundcloud.com/oembed", params={"url": url, "format": "json", "maxheight": 166})
        if r.status_code != 200:
            raise ValueError("Couldn't read that SoundCloud link (is the track public?).")
        d = r.json()
        # SoundCloud oEmbed titles look like "Track Name by Artist"
        title = re.sub(rf"\s+by\s+{re.escape(d.get('author_name', ''))}$", "", d["title"])
        return {"source": "soundcloud", "title": title, "author": d.get("author_name", ""),
                "author_url": d.get("author_url"), "url": url, "embed_html": d.get("html")}

    if "beatport.com" in host:
        m = re.search(r"/track/([^/]+)/\d+", url)
        if not m:
            raise ValueError("Please paste a Beatport *track* link.")
        return {"source": "beatport", "title": m.group(1).replace("-", " "), "author": "",
                "embed_html": None}

    if host.endswith("bandcamp.com"):
        m = re.search(r"/track/([^/?#]+)", url)
        if not m:
            raise ValueError("Please paste a Bandcamp *track* link.")
        # Read only the page's title ("Track, by Artist"); Bandcamp audio is never downloaded
        title, author = m.group(1).replace("-", " "), ""
        try:
            r = client.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; similarsounds/0.1)"})
            og = re.search(r'<meta property="og:title" content="([^"]+)"', r.text)
            if og:
                t, _, a = html.unescape(og.group(1)).rpartition(", by ")
                title, author = (t, a) if t else (a, "")
        except httpx.HTTPError:
            pass
        return {"source": "bandcamp", "title": title, "author": author, "url": url, "embed_html": None}

    if host:
        raise ValueError("Supported links: YouTube, SoundCloud, Beatport, Bandcamp, Deezer - or type 'Artist - Title'.")
    return {"source": "text", "title": url, "author": "", "embed_html": None}


def find_on_deezer(title: str, author: str) -> dict | None:
    """Find the best-matching Deezer track (with a preview) for a title from another platform."""
    cleaned = clean_title(title)
    queries = []
    if " - " in cleaned:
        artist, track = (s.strip() for s in cleaned.split(" - ", 1))
        queries.append(f'artist:"{artist}" track:"{track}"')
        queries.append(f"{artist} {track}")
        first = re.split(r"\s*(?:&|,| x | feat\.? | ft\.? | vs\.? | and )\s*", artist, flags=re.I)[0]
        if first != artist:
            queries += [f'artist:"{first}" track:"{track}"', f"{first} {track}"]
    else:
        artist, track = author, cleaned
        if author:
            queries.append(f'artist:"{author}" track:"{cleaned}"')
        queries.append(f"{author} {cleaned}".strip())
        queries.append(cleaned)

    best, best_score = None, 0.0
    for q in queries:
        res = [t for t in deezer("/search", q=q, limit=15).get("data", []) if t.get("preview")]
        for t in res:
            s = match_score(artist, track, t)
            if s > best_score:
                best, best_score = t, s
        if best_score >= 2.5:   # exact artist + title: stop searching
            break
    return best if best_score >= 1.0 else None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", re.sub(r"\(.*?\)|\[.*?\]", "", s.lower())).strip()


def _words(s: str) -> set[str]:
    return set(_norm(s).split())


def match_score(artist: str, track: str, t: dict) -> float:
    """How well a Deezer search hit matches the wanted artist/title (0 to ~3.2)."""
    hit_artist, hit_title = t["artist"]["name"], t["title"]
    score = 0.0
    if artist:
        a, ha = _norm(artist), _norm(hit_artist)
        if a == ha:
            score += 1.5
        elif ha and set(ha.split()) <= set(a.split()):
            score += 1.0    # main artist of a collab ("Chris Lake & Fisher" -> "Chris Lake")
        else:
            return 0.0      # different artist ("FISHER" is not "Amiran Fisher")
    want, got = _words(track), _words(hit_title)
    if want:
        score += len(want & got) / len(want | got)
        if _norm(track) == _norm(hit_title):
            score += 0.5
    # Keep remix versions apart: "X (Y Remix)" shouldn't match the original, and vice versa
    if ("remix" in track.lower()) == ("remix" in hit_title.lower()):
        score += 0.2
    return score + min(t.get("rank", 0), 1_000_000) / 5_000_000   # popularity tie-break
