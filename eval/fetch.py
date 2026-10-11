"""Step 1 of the sound-model test: pick ~120 catalogue tracks per style and save their Deezer
previews locally (eval/cache, git-ignored) so every model analyses exactly the same audio.
The cache is only for this test and is deleted afterwards."""
import json, random, sqlite3, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import sources

PER_STYLE = 120
CACHE = Path(__file__).parent / "cache"
CACHE.mkdir(exist_ok=True)

conn = sqlite3.connect(Path(__file__).parent.parent / "data" / "catalogue.db")
rows = conn.execute("SELECT deezer_id, artist, title, style FROM tracks WHERE style IS NOT NULL").fetchall()
random.seed(42)
by_style = {}
for r in rows:
    by_style.setdefault(r[3], []).append(r)
sample = []
for style, rs in sorted(by_style.items()):
    random.shuffle(rs)
    sample += rs[:PER_STYLE]
print(len(sample), "tracks across", len(by_style), "styles")


def get(r):
    did = r[0]
    out = CACHE / f"{did}.mp3"
    if out.exists() and out.stat().st_size > 10000:
        return True
    for attempt in range(4):
        try:
            t = sources.deezer_track(did)
            if not t.get("preview"):
                return False
            out.write_bytes(sources.fetch_preview(t["preview"]))
            return True
        except Exception as e:
            time.sleep(3 * (attempt + 1))   # Deezer sometimes says "too many requests": wait and retry
    return False

with ThreadPoolExecutor(3) as pool:
    ok = list(pool.map(get, sample))
kept = [dict(zip(("deezer_id", "artist", "title", "style"), r)) for r, k in zip(sample, ok) if k]
json.dump(kept, open(Path(__file__).parent / "sample.json", "w"), indent=0)
print("saved", len(kept), "previews")
