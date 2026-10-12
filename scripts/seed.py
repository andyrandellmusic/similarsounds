"""Build / top up the house catalogue from Deezer playlists (stand-in until Beatport access).

Run daily to keep the catalogue fresh:
    uv run python -m scripts.seed --per-style 120
"""
import argparse
import multiprocessing
from pathlib import Path
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from datetime import date

from app import sources
from app.analysis import analyse
from app.catalogue import connect, release_date_ok, upsert

YEAR = date.today().year

# style -> playlist search queries (newest first)
STYLES = {
    "House": [f"house music {YEAR}", f"new house {YEAR}", f"vocal house {YEAR}", f"jackin house {YEAR}", f"soulful house {YEAR}"],
    "Deep House": [f"deep house {YEAR}", f"deep house {YEAR - 1}", "deep house new"],
    "Tech House": [f"tech house {YEAR}", f"tech house {YEAR - 1}", "tech house new releases"],
    "Minimal / Deep Tech": [f"minimal deep tech {YEAR}", "minimal house", "uk minimal deep tech", "deep tech minimal groove",
                            "rominimal", "minimal tech house rollers"],
    "Funky / Disco House": [f"nu disco {YEAR}", f"funky house {YEAR}", f"disco house {YEAR}", "nu disco new releases"],
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


MAX_AGE_DAYS = 730   # only add releases from the last 2 years: newer music matters most


def fetch(track_id: int, style: str) -> tuple[dict, bytes] | None:
    from datetime import timedelta
    t = sources.deezer_track(track_id)
    if not t.get("preview") or not release_date_ok(t.get("release_date")):
        return None
    if t["release_date"] < (date.today() - timedelta(days=MAX_AGE_DAYS)).isoformat():
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


ARTIST_STATE = Path(__file__).resolve().parent.parent / "data" / "artist_follow.json"


def artist_candidates(conn, n_artists: int, seen: set[int], max_age_days: int = 120) -> list[tuple[int, str]]:
    """New releases from house artists already in the catalogue. Rotates through the artists a few
    hundred a day, so every artist gets checked regularly. (Each track's style is set later by sound.)"""
    import json
    from datetime import date, timedelta
    state = json.loads(ARTIST_STATE.read_text()) if ARTIST_STATE.exists() else {"ids": {}, "next": 0}
    names = sorted({r[0].split(",")[0].split(" & ")[0].strip() for r in conn.execute("SELECT artist FROM tracks")})
    start = state.get("next", 0) % max(1, len(names))
    batch = (names[start:] + names[:start])[:n_artists]
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()
    out = []
    for name in batch:
        aid = state["ids"].get(name)
        try:
            if aid is None:
                hits = [a for a in sources.deezer("/search/artist", q=name, limit=5).get("data", [])
                        if a["name"].lower() == name.lower()]
                aid = max(hits, key=lambda a: a.get("nb_fan", 0))["id"] if hits else 0
                state["ids"][name] = aid
            if not aid:
                continue
            for al in sources.deezer(f"/artist/{aid}/albums", limit=15).get("data", []):
                if (al.get("release_date") or "") < cutoff:
                    continue
                for t in sources.deezer(f"/album/{al['id']}/tracks", limit=30).get("data", []):
                    if t["id"] not in seen and t.get("preview"):
                        seen.add(t["id"]); out.append((t["id"], "House"))
        except Exception as e:
            print("  artist skipped:", name, e, file=sys.stderr)
    state["next"] = (start + n_artists) % max(1, len(names))
    ARTIST_STATE.write_text(json.dumps(state))
    return out


LABEL_STATE = Path(__file__).resolve().parent.parent / "data" / "label_follow.json"

# Well-known house labels (deep, tech, minimal / deep tech, disco / funky and classic house). Labels
# already in the catalogue with a few tracks are added to these automatically.
HOUSE_LABELS = [
    # house / vocal / classic
    "Defected", "Defected Records", "Toolroom", "Toolroom Records", "Strictly Rhythm", "Nervous Records", "Large Music",
    "Glasgow Underground", "Classic Music Company", "Hot Creations", "Sweat It Out", "Ministry of Sound Recordings",
    "Big Love", "Moda Black", "Of Unsound Mind", "Shall Not Fade", "Lobster Theremin", "Nothing Else Matters",
    "Repopulate Mars", "Kaluki", "Club Sweat", "Perfect Driver Music", "Higher Ground", "Hottrax", "Solid Grooves Records",
    "Solid Grooves Raw", "CUFFED", "Rawsome Recordings", "Trick", "Saved Records", "Cajual Records", "Relief",
    "Simma Black", "Glitterbox Recordings", "Glitterbox", "Sondela Recordings", "Black Book Records", "Dirtybird",
    "DFTD", "Origins Recordings", "Moon Harbour Recordings", "Get Physical Music", "Snatch! Records",
    "Elrow Music", "Cuttin' Headz", "Hellbent Records", "Hot Since 82", "Knee Deep In Sound", "Catch & Release",
    "Ultra Music", "Spinnin' Deep", "Sola", "Insomniac Records", "Truesoul", "Drumcode", "Hood Politics Records",
    "Experts Only", "Do Not Sleep", "Elrow", "Kitball", "Sink or Swim", "Night Service Only", "Box Of Cats",
    "Insane Records", "Mood Child", "Dear Deer", "Masquerade Music", "Sandwichez", "Material", "Chaos",
    # deep house
    "Anjunadeep", "Freerange Records", "Lost & Found", "Rebirth", "Get Physical", "Crosstown Rebels", "Innervisions",
    "Diynamic", "Watergate Records", "Selected.", "Stil vor Talent", "Sounds Of Sirin", "Bar 25 Music", "Kompakt",
    "Purified Records", "All Day I Dream", "Exploited", "Lazy Days", "Locus", "Kaleidoscope", "Atjazz Record Company",
    "Ninja Tune", "Futureboogie Recordings", "Heist Recordings", "Dirt Crew Recordings", "Razor-N-Tape",
    "Local Talk", "Rhythm Section International", "Lumberjacks in Hell", "Shanghai Spaceport", "Fryhide",
    "Sole Channel Music", "Tokyo Dawn Records", "Delusions of Grandeur", "Spinnin' Records",
    # minimal / deep tech
    "Fuse London", "Rawax", "Taping Tapes", "Desolat", "Rekids", "Cocoon Recordings", "Minus", "Ovum Recordings",
    "Trapez", "Perlon", "Circus Recordings", "Moscow Records", "Meander", "Nervmusic Records", "Cyclic Records",
    "Phonica Records", "Unknown To The Unknown", "Hotflush Recordings", "Body Movements", "Housewax", "TBX Records",
    "Superfreq", "Cuttin' Headz", "Mood Swings", "Cinematique", "WeMe Records", "Hommage", "Unplugged Records",
    # disco / funky / nu disco
    "Purple Disco Machine", "Roche Musique", "Kitsuné Musique", "Ed Banger Records", "Nu Groove", "Disco Galactic",
    "Midnight Riot", "Toy Tonics", "Razor-N-Tape Reserve", "Hot Biscuits", "Glitterbox Recordings", "Bombstrikes",
    "Faded Records", "Classic Disco", "Z Records", "Soul Clap Records", "Rocafort Records", "Cr2 Records", "Big Beat Records",
]
DANCE_GENRES = {106, 113}   # Deezer: Electro, Dance


def label_candidates(conn, n_labels: int, seen: set[int], max_age_days: int = 120) -> list[tuple[int, str]]:
    """New releases from house labels. Checks a rotating batch of labels each day; albums already
    looked at are remembered so each run only opens new ones. (Style is set later by sound.)"""
    import json
    from datetime import date, timedelta
    state = json.loads(LABEL_STATE.read_text()) if LABEL_STATE.exists() else {"next": 0, "done": []}
    done = set(state.get("done", []))
    in_cat = [l for l, n in conn.execute(
        "SELECT label, COUNT(*) n FROM tracks WHERE label IS NOT NULL AND label != '' GROUP BY label HAVING n >= 3")]
    names = list(dict.fromkeys(HOUSE_LABELS + sorted(in_cat)))
    start = state.get("next", 0) % max(1, len(names))
    batch = (names[start:] + names[:start])[:n_labels]
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()
    out = []
    for name in batch:
        try:
            albums = sources.deezer("/search/album", q=f'label:"{name}"', limit=100).get("data", [])
            for a in albums:
                if a["id"] in done:
                    continue
                al = sources.deezer(f"/album/{a['id']}")
                genres = {g["id"] for g in (al.get("genres") or {}).get("data", [])}
                old = (al.get("release_date") or "") < cutoff
                if old or (genres and not genres & DANCE_GENRES):
                    done.add(a["id"])      # never worth opening again
                    continue
                for t in (al.get("tracks") or {}).get("data", []):
                    if t["id"] not in seen and t.get("preview"):
                        seen.add(t["id"]); out.append((t["id"], "House"))
        except Exception as e:
            print("  label skipped:", name, e, file=sys.stderr)
    state["next"] = (start + n_labels) % max(1, len(names))
    state["done"] = sorted(done)[-60000:]
    LABEL_STATE.write_text(json.dumps(state))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--artists", type=int, default=0, help="also check this many catalogue artists for new releases")
    ap.add_argument("--labels", type=int, default=0, help="also check this many house labels for new releases")
    ap.add_argument("--max-new", type=int, default=1500, help="most new tracks to fetch and analyse in one run")
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
    if args.artists:
        c = artist_candidates(conn, args.artists, seen)
        print(f"  new releases from {args.artists} catalogue artists: {len(c)} candidates")
        todo += c
    if args.labels:
        c = label_candidates(conn, args.labels, seen)
        print(f"  new releases from {args.labels} house labels: {len(c)} candidates")
        todo += c

    # Keep each daily run inside its time limit; whatever's left is picked up the next day
    if len(todo) > args.max_new:
        print(f"  {len(todo)} candidates: taking the first {args.max_new} this run", flush=True)
        todo = todo[:args.max_new]
    print(f"  fetching {len(todo)} previews…", flush=True)

    # 1) download previews (network), 2) analyse them in worker processes (CPU).
    # A track whose audio crashes a worker is skipped and the workers are restarted,
    # so one bad file can't stop the whole daily update.
    fetched = []
    with ThreadPoolExecutor(3) as io_pool:
        for f in as_completed([io_pool.submit(fetch, tid, style) for tid, style in todo]):
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
            fetched.append((meta, audio))

    added, pending = 0, list(range(len(fetched)))
    while pending:
        retry = []
        # "spawn" workers: on Linux the default ("fork" while download threads exist) can freeze the job
        with ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 1), mp_context=multiprocessing.get_context("spawn")) as cpu:
            futs = {cpu.submit(analyse, fetched[k][1]): k for k in pending}
            for f in as_completed(futs):
                k = futs[f]
                meta = fetched[k][0]
                try:
                    upsert(conn, {**meta, **f.result()})
                    added += 1
                    if added % 25 == 0:
                        print(f"  analysed {added}/{len(fetched)}", flush=True)
                except BrokenProcessPool:
                    retry.append(k)      # the pool died; try these again with fresh workers
                except Exception as e:
                    print(f"  analysis failed for {meta['title']}: {e}", file=sys.stderr)
        if retry and len(retry) == len(pending):   # nothing got through: drop the first one and carry on
            print(f"  skipped {fetched[retry[0]][0]['title']} (crashed the analyser)", file=sys.stderr)
            retry = retry[1:]
        pending = retry

    total = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    print(f"Added {added} tracks. Catalogue now has {total}.")


if __name__ == "__main__":
    main()
