"""Build / top up the house catalogue from Deezer playlists (stand-in until Beatport access).

Run daily to keep the catalogue fresh:
    uv run python -m scripts.seed --per-style 120
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import date

from app import sources
from app.analysis import analyse
from app.catalogue import connect, release_date_ok, upsert

YEAR = date.today().year

# style -> playlist search queries (newest first)
STYLES = {
    "Tech House": [f"tech house {YEAR}", f"tech house {YEAR - 1}", "tech house new releases"],
    "Deep House": [f"deep house {YEAR}", f"deep house {YEAR - 1}", "deep house new"],
    "Afro House": [f"afro house {YEAR}", f"afro house {YEAR - 1}"],
    "Melodic House": [f"melodic house {YEAR}", f"melodic house techno {YEAR}", "progressive house melodic"],
    "Organic House": [f"organic house {YEAR}", "organic downtempo house"],
    "Soulful House": [f"soulful house {YEAR}", "soulful house"],
    "Jackin House": [f"jackin house {YEAR}", "disco house", "classic house groove"],
    "Bass House": [f"bass house {YEAR}", "uk bass house"],
    "Minimal / Deep Tech": [f"minimal deep tech {YEAR}", "minimal house", "uk minimal deep tech", "deep tech minimal groove",
                            "rominimal", "minimal tech house rollers"],
    "Funky / Disco House": [f"nu disco {YEAR}", "funky house"],
}

# Extra searches per style, so each run reaches beyond the same few playlists
for _style, _qs in STYLES.items():
    _name = _style.split(" / ")[0].lower()
    _qs += [f"best {_name} {YEAR}", f"new {_name} releases", f"{_name} {YEAR} mix"]
PLAYLISTS_PER_QUERY = 15

_albums: dict[int, dict] = {}


def candidates(style: str, queries: list[str], per_style: int, seen: set[int]) -> list[tuple[int, str]]:
    out = []
    for q in queries:
        for pl in sources.deezer("/search/playlist", q=q, limit=PLAYLISTS_PER_QUERY).get("data", []):
            tracks = sources.deezer(f"/playlist/{pl['id']}/tracks", limit=100).get("data", [])
            for t in tracks:
                if t["id"] in seen or not t.get("preview"):
                    continue
                seen.add(t["id"])
                out.append((t["id"], style))
                if len(out) >= per_style:
                    return out
    return out


def fetch(track_id: int, style: str) -> tuple[dict, bytes] | None:
    t = sources.deezer_track(track_id)
    if not t.get("preview") or not release_date_ok(t.get("release_date")):
        return None
    album_id = t["album"]["id"]
    if album_id not in _albums:
        try:
            _albums[album_id] = sources.deezer(f"/album/{album_id}")
        except Exception:
            _albums[album_id] = {}
    album = _albums[album_id]
    meta = {
        "deezer_id": t["id"], "isrc": t.get("isrc"), "title": t["title"],
        "artist": t["artist"]["name"], "album": t["album"]["title"], "label": album.get("label"),
        "cover": t["album"].get("cover_medium"), "release_date": t["release_date"], "style": style,
    }
    return meta, sources.fetch_preview(t["preview"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-style", type=int, default=100)
    ap.add_argument("--styles", nargs="*", help="limit to these style names")
    args = ap.parse_args()

    conn = connect()
    seen = {r[0] for r in conn.execute("SELECT deezer_id FROM tracks")}
    isrcs = {r[0] for r in conn.execute("SELECT isrc FROM tracks WHERE isrc IS NOT NULL")}
    print(f"Catalogue currently has {len(seen)} tracks")

    todo = []
    for style, queries in STYLES.items():
        if args.styles and style not in args.styles:
            continue
        c = candidates(style, queries, args.per_style, seen)
        print(f"  {style}: {len(c)} new candidates")
        todo += c

    added = 0
    with ThreadPoolExecutor(6) as io_pool, ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 1)) as cpu:
        fetches = [io_pool.submit(fetch, tid, style) for tid, style in todo]
        analyses = {}
        for f in as_completed(fetches):
            try:
                res = f.result()
            except Exception as e:
                print("  fetch failed:", e, file=sys.stderr)
                continue
            if not res:
                continue
            meta, audio = res
            if meta["isrc"] and meta["isrc"] in isrcs:
                continue
            isrcs.add(meta["isrc"])
            analyses[cpu.submit(analyse, audio)] = meta
        for f in as_completed(analyses):
            meta = analyses[f]
            try:
                upsert(conn, {**meta, **f.result()})
                added += 1
                if added % 25 == 0:
                    print(f"  analysed {added}/{len(analyses)}")
            except Exception as e:
                print(f"  analysis failed for {meta['title']}: {e}", file=sys.stderr)

    total = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    print(f"Added {added} tracks. Catalogue now has {total}.")


if __name__ == "__main__":
    main()
