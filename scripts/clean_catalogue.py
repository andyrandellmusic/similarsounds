"""Remove tracks that slipped into the catalogue but aren't house.

A track is removed when its Deezer album genres include no dance/electronic genre (e.g. pure
Pop), when it's tagged as a clearly different genre (Dubstep, Drum & Bass) without a house tag,
or when its tempo is outside house range. Usage:
    python -m scripts.clean_catalogue            # report only
    python -m scripts.clean_catalogue --apply    # actually delete
    python -m scripts.clean_catalogue --since "2026-10-11 02:28:10"   # only tracks added since
"""
import argparse
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from app import sources
from app.catalogue import DB_PATH

DANCE = {"Dance", "Electro", "Techno/House"}
OTHER = {"Dubstep", "Drum & Bass"}
BPM_MIN, BPM_MAX = 108, 135

_albums: dict[int, list[str]] = {}


def genres(deezer_id: int) -> list[str] | None:
    try:
        t = sources.deezer_track(deezer_id)
        aid = t["album"]["id"]
        if aid not in _albums:
            al = sources.deezer(f"/album/{aid}")
            _albums[aid] = [g["name"] for g in al.get("genres", {}).get("data", [])]
        return _albums[aid]
    except Exception:
        return None   # couldn't check: keep it


def verdict(bpm: float, g: list[str] | None) -> str | None:
    if not BPM_MIN <= bpm <= BPM_MAX:
        return f"tempo {round(bpm)} BPM"
    if g is None or not g:
        return None
    if not DANCE & set(g):
        return "genres: " + ", ".join(g)
    if OTHER & set(g) and "Techno/House" not in g:
        return "genres: " + ", ".join(g)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--since", default=None)
    args = ap.parse_args()
    conn = sqlite3.connect(DB_PATH)
    sql = "SELECT deezer_id, artist, title, bpm FROM tracks"
    rows = conn.execute(sql + (" WHERE added_at > ?" if args.since else ""), (args.since,) if args.since else ()).fetchall()
    print(f"Checking {len(rows)} tracks")
    with ThreadPoolExecutor(4) as pool:
        gs = list(pool.map(lambda r: genres(r[0]) if BPM_MIN <= r[3] <= BPM_MAX else [], rows))
    drop = []
    for (did, artist, title, bpm), g in zip(rows, gs):
        why = verdict(bpm, g)
        if why:
            drop.append(did)
            print(f"  remove: {artist} - {title} ({why})")
    print(f"{len(drop)} of {len(rows)} would be removed")
    if args.apply and drop:
        conn.executemany("DELETE FROM tracks WHERE deezer_id = ?", [(d,) for d in drop])
        conn.commit()
        print("Removed. Catalogue now has", conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0])


if __name__ == "__main__":
    main()
