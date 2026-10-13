"""Add the released tracks from Boss's rekordbox USB to the catalogue, using his rekordbox genre tag
as the sub-genre. Reads eval/results/usb_refs.jsonl (tracks already matched on Deezer by
eval/beatport_all.py). Unlike the daily update there's no age limit: these are tracks he plays.
    .venv/bin/python -m scripts.add_usb            # report only
    .venv/bin/python -m scripts.add_usb --apply"""
import argparse, json, sys
from pathlib import Path

from app import sources
from app.analysis import analyse
from app.catalogue import connect, upsert

ROOT = Path(__file__).resolve().parent.parent
FIVE = {"House", "Deep House", "Tech House", "Minimal / Deep Tech", "Funky / Disco House"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); args = ap.parse_args()
    conn = connect()
    have = {r[0] for r in conn.execute("SELECT deezer_id FROM tracks")}
    try:                                   # never re-add a track the genre clean-up set aside
        have |= {r[0] for r in conn.execute("SELECT deezer_id FROM set_aside")}
    except Exception:
        pass
    isrcs = {r[0] for r in conn.execute("SELECT isrc FROM tracks WHERE isrc IS NOT NULL")}
    rows = [json.loads(l) for l in open(ROOT / "eval" / "results" / "usb_refs.jsonl")]
    rows = [r for r in rows if r.get("deezer_id") and r["genre"] in FIVE and r["deezer_id"] not in have
            and not r["dz"].startswith("Chez Damier - Can You Feel It")]     # Deezer matched a different (1992) track
    print(f"{len(rows)} USB tracks to add", flush=True)
    added = 0
    for r in rows:
        try:
            t = sources.deezer_track(r["deezer_id"])
            if not t.get("preview") or (t.get("isrc") and t["isrc"] in isrcs):
                continue
            album = sources.deezer(f"/album/{t['album']['id']}")
            meta = {"deezer_id": t["id"], "isrc": t.get("isrc"), "title": t["title"], "artist": t["artist"]["name"],
                    "album": t["album"]["title"], "label": album.get("label"), "cover": t["album"].get("cover_medium"),
                    "release_date": t["release_date"], "style": r["genre"]}
            print(f"  {meta['artist']} - {meta['title']} ({meta['release_date']}, {meta['label']}) -> {r['genre']}", flush=True)
            if args.apply:
                upsert(conn, {**meta, **analyse(sources.fetch_preview(t["preview"]))})
                isrcs.add(t.get("isrc")); added += 1
        except Exception as e:
            print(f"  failed for {r['dz']}: {e}", file=sys.stderr)
    print(f"added {added}" if args.apply else "report only: run with --apply to add them")


if __name__ == "__main__":
    main()
