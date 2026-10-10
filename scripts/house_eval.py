"""Collect labelled examples to calibrate the house-music check.

    uv run python -m scripts.house_eval        # writes data/house_eval.json

Positives: house tracks from playlists, excluding anything already in the catalogue.
Negatives: Deezer genre charts (pop, rap, rock...) plus close relatives (techno, trance, DnB...).
"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor

from app import sources
from app.analysis import analyse
from app.catalogue import Index
from app.house import house_features

POSITIVE_QUERIES = ["house music new 2026", "defected records", "toolroom house", "hot creations",
                    "afro house hits", "deep house sessions", "tech house club", "melodic house 2026"]
NEGATIVE_CHARTS = {132: "pop", 116: "rap", 152: "rock", 165: "rnb", 129: "jazz", 98: "classical",
                   197: "latin", 464: "metal", 84: "country", 144: "reggae", 169: "soul"}
NEGATIVE_QUERIES = {"techno 2026": "techno", "drum and bass 2026": "dnb", "trance 2026": "trance",
                    "dubstep": "dubstep", "hardstyle": "hardstyle", "ambient chill": "ambient",
                    "big room edm": "edm", "uk garage 2026": "ukg"}


def from_playlists(query, n, skip):
    out = []
    for pl in sources.deezer("/search/playlist", q=query, limit=2).get("data", []):
        for t in sources.deezer(f"/playlist/{pl['id']}/tracks", limit=60).get("data", []):
            if t.get("preview") and t["id"] not in skip:
                skip.add(t["id"])
                out.append(t)
                if len(out) >= n:
                    return out
    return out


def main():
    index = Index()
    skip = set(index.ids)
    jobs = []
    for q in POSITIVE_QUERIES:
        jobs += [(t, 1, "house") for t in from_playlists(q, 9, skip)]
    for gid, name in NEGATIVE_CHARTS.items():
        tracks = [t for t in sources.deezer(f"/chart/{gid}/tracks", limit=12).get("data", [])
                  if t.get("preview") and t["id"] not in skip]
        skip.update(t["id"] for t in tracks)
        jobs += [(t, 0, name) for t in tracks[:8]]
    for q, name in NEGATIVE_QUERIES.items():
        jobs += [(t, 0, name) for t in from_playlists(q, 6, skip)]
    print(f"{len(jobs)} tracks to analyse", file=sys.stderr)

    def run(job):
        t, label, kind = job
        try:
            full = sources.deezer_track(t["id"])
            album = sources.deezer(f"/album/{full['album']['id']}")
            genres = [g["id"] for g in album.get("genres", {}).get("data", [])]
            feats = analyse(sources.fetch_preview(full["preview"]))
            return {"id": t["id"], "label": label, "kind": kind,
                    "name": f"{t['artist']['name']} - {t['title']}", "genres": genres,
                    **house_features(feats, index, genres)}
        except Exception as e:
            print("skip", t["id"], e, file=sys.stderr)

    with ThreadPoolExecutor(4) as pool:
        rows = [r for r in pool.map(run, jobs) if r]
    with open("data/house_eval.json", "w") as f:
        json.dump(rows, f, indent=1)
    print(f"wrote {len(rows)} rows", file=sys.stderr)


if __name__ == "__main__":
    main()
