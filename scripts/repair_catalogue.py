"""Small repairs to the catalogue, run by the daily pull (and the publish workflow) before publishing:
    - tracks with no cover art get their album's cover from Deezer.
Usage: python -m scripts.repair_catalogue
"""
import sqlite3

from app import sources
from app.catalogue import DB_PATH


def main():
    conn = sqlite3.connect(DB_PATH)
    missing = conn.execute("SELECT deezer_id FROM tracks WHERE COALESCE(cover, '') = ''").fetchall()
    fixed = 0
    for (tid,) in missing:
        try:
            t = sources.deezer_track(tid)
            cover = (t.get("album") or {}).get("cover_medium") or (t.get("album") or {}).get("cover")
            if cover:
                conn.execute("UPDATE tracks SET cover = ? WHERE deezer_id = ?", (cover, tid)); fixed += 1
        except Exception as e:
            print(f"  cover for {tid}: {e}")
    conn.commit(); conn.close()
    print(f"covers: {fixed} of {len(missing)} missing covers filled in")


if __name__ == "__main__":
    main()
