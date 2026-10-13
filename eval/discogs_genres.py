"""Look up each catalogue track's genres and styles on Discogs (official API, personal token).
Reads the token from ~/.config/similarsounds/discogs_token (never stored in the project).
Resumable: results go to eval/results/discogs_genres.jsonl, one line per track.
    .venv/bin/python -m eval.discogs_genres            # whole catalogue (~60 lookups a minute)
    .venv/bin/python -m eval.discogs_genres --limit 50  # quick trial"""
import argparse, json, re, sqlite3, sys, time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "eval" / "results" / "discogs_genres.jsonl"
TOKEN_FILE = Path.home() / ".config" / "similarsounds" / "discogs_token"
API = "https://api.discogs.com/database/search"

MIX = re.compile(r"\s*[\(\[][^\)\]]*(mix|edit|remix|version|dub|rework|vip|extended|original|radio|mixed)[^\)\]]*[\)\]]", re.I)
FEAT = re.compile(r"\s*[\(\[]?\b(feat|ft|featuring)\b\.?.*$", re.I)


def clean_title(t: str) -> str:
    return FEAT.sub("", MIX.sub("", t)).strip()


def first_artist(a: str) -> str:
    return re.split(r",| & | x | feat\.? | ft\.? ", a, maxsplit=1, flags=re.I)[0].strip()


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--older", action="store_true", help="trial on releases over a year old"); args = ap.parse_args()
    if not TOKEN_FILE.exists():
        sys.exit("No Discogs token yet: save it to ~/.config/similarsounds/discogs_token first.")
    token = TOKEN_FILE.read_text().strip()
    client = httpx.Client(timeout=20, headers={"Authorization": f"Discogs token={token}",
                                                "User-Agent": "SimilarSounds/1.0 +https://www.similarsounds.com"})
    done = set()
    if OUT.exists():
        done = {json.loads(l)["id"] for l in OUT.read_text().splitlines() if l.strip()}
    rows = sqlite3.connect(ROOT / "data" / "catalogue.db").execute(
        "SELECT deezer_id, artist, title, label FROM tracks ORDER BY release_date DESC").fetchall()
    todo = [r for r in rows if r[0] not in done]
    if args.older:
        import random; old = {r[0] for r in sqlite3.connect(ROOT / "data" / "catalogue.db").execute(
            "SELECT deezer_id FROM tracks WHERE release_date < date('now','-365 day')")}
        todo = [r for r in todo if r[0] in old]; random.Random(7).shuffle(todo)
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(rows)} tracks, {len(done)} already looked up, {len(todo)} to go", flush=True)
    found = 0
    with OUT.open("a") as fh:
        for n, (did, artist, title, label) in enumerate(todo, 1):
            a, t = first_artist(artist), clean_title(title)
            rec = {"id": did, "genres": [], "styles": [], "match": None}
            r = None
            for attempt in range(4):
                try:
                    r = client.get(API, params={"type": "release", "artist": a, "track": t, "per_page": 5})
                except httpx.HTTPError:           # dropped connection: wait and try again
                    time.sleep(10 * (attempt + 1)); continue
                if r.status_code == 429:
                    time.sleep(20 * (attempt + 1)); continue
                break
            if r is None:
                continue                          # not saved, so it's retried on the next run
            if r.status_code == 200:
                hits = r.json().get("results", [])
                # prefer a hit on the same label, else the first one whose title mentions the artist
                # the release title must name the artist; prefer one on the same label
                named = [h for h in hits if norm(a)[:6] and norm(a)[:6] in norm(h.get("title", ""))]
                best = next((h for h in named if label and norm(label) in {norm(x) for x in h.get("label", [])}), None) \
                    or (named[0] if named else None)
                if best:
                    rec.update(genres=best.get("genre", []), styles=best.get("style", []),
                               match=best.get("title"), year=best.get("year"))
                    found += 1
            elif r.status_code == 401:
                sys.exit("Discogs rejected the token: check it's saved correctly.")
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            # Discogs allows 60 requests a minute with a token; the response headers say how many are left
            left = int(r.headers.get("X-Discogs-Ratelimit-Remaining", "5") or 5) if r is not None else 5
            time.sleep(1.05 if left > 3 else 5)
            if n % 100 == 0:
                print(f"  {n}/{len(todo)} looked up, {found} found on Discogs", flush=True)
    print(f"done: {found} of {len(todo)} found on Discogs", flush=True)


if __name__ == "__main__":
    main()
