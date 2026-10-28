"""Where the big data files live: a GitHub release, not the git history.

data/catalogue.db and data/clap.npz grow every day, and GitHub refuses files over 100 MB (and every daily copy
in git made the repository bigger). So they're kept as assets of the release "catalogue-data" instead, which
holds only the latest copy (up to 2 GB a file). Git keeps just data/catalogue_version.json: each file's size
and checksum, so a download can be checked.

    python -m scripts.catalogue_store fetch      # get the latest files (Render build, daily pull, the Mac)
    python -m scripts.catalogue_store publish    # compact, upload, write the version file (daily pull only)

Tracks taken out by hand are listed in data/removed_tracks.json: fetch takes them out of the downloaded
catalogue, and the next daily pull publishes the cleaned catalogue and empties the list.
"""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

REPO = os.environ.get("GITHUB_REPOSITORY", "andyrandellmusic/similarsounds")
TAG = "catalogue-data"
DATA = Path(__file__).resolve().parent.parent / "data"
FILES = ["catalogue.db", "clap.npz"]
VERSION = DATA / "catalogue_version.json"
REMOVED = DATA / "removed_tracks.json"
RUNS = DATA / "catalogue_runs.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _version() -> dict:
    return json.loads(VERSION.read_text()) if VERSION.exists() else {}


def apply_removals() -> int:
    """Take the tracks listed in data/removed_tracks.json out of the local catalogue."""
    ids = json.loads(REMOVED.read_text()).get("ids", []) if REMOVED.exists() else []
    db = DATA / "catalogue.db"
    if not ids or not db.exists():
        return 0
    conn = sqlite3.connect(db)
    q = ",".join("?" * len(ids)); args = [int(i) for i in ids]
    # set aside (not just deleted), so the track's old page says "gone" (410) instead of a bare 404
    cols = [c[1] for c in conn.execute("PRAGMA table_info(tracks)")]
    try:
        conn.execute(f"INSERT INTO set_aside ({','.join(cols)}, aside_kind, aside_why, aside_at) "
                     f"SELECT {','.join(cols)}, 'removed by hand', 'taken out by hand', datetime('now') "
                     f"FROM tracks WHERE deezer_id IN ({q})", args)
    except sqlite3.OperationalError:
        pass                                   # no set_aside table: just delete
    n = conn.execute(f"DELETE FROM tracks WHERE deezer_id IN ({q})", args).rowcount
    conn.commit(); conn.close()
    return n


def fetch() -> None:
    want = _version()
    for name in FILES:
        path, expect = DATA / name, (want.get(name) or {}).get("sha256")
        if path.exists() and (not expect or sha256(path) == expect):     # no version yet: the copy here is it
            print(f"{name}: already the latest", flush=True); continue
        url = f"https://github.com/{REPO}/releases/download/{TAG}/{name}"
        tmp, got = path.with_suffix(path.suffix + ".part"), False
        for attempt in range(6):
            try:
                with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(tmp, "wb") as f:
                        for chunk in r.iter_bytes(1 << 20):
                            f.write(chunk)
                got = True
                if not expect or sha256(tmp) == expect:
                    break
                print(f"{name}: download doesn't match the version file yet, trying again", flush=True)
            except httpx.HTTPError as e:
                print(f"{name}: download failed ({e}), trying again", flush=True)
            time.sleep(5 * (attempt + 1))
        if got:
            tmp.replace(path)          # a checksum mismatch after six tries means the release is newer: keep it
            print(f"{name}: downloaded ({path.stat().st_size / 1048576:.1f} MB)", flush=True)
        elif not path.exists():
            sys.exit(f"{name}: couldn't download it from {url}, and there's no local copy")
        else:
            print(f"{name}: couldn't download it, keeping the copy already here", flush=True)
    n = apply_removals()
    if n:
        print(f"took {n} hand-removed tracks out of the catalogue", flush=True)


def publish() -> None:
    """Compact the catalogue, upload both files to the release, and record their checksums."""
    db = DATA / "catalogue.db"
    apply_removals()
    conn = sqlite3.connect(db)
    total = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    conn.execute("VACUUM"); conn.close()                # drop the space left by removed tracks
    gh = lambda *a: subprocess.run(["gh", *a, "--repo", REPO], check=False, capture_output=True, text=True)
    if gh("release", "view", TAG).returncode != 0:
        r = gh("release", "create", TAG, "--title", "Catalogue data (latest)", "--latest=false",
               "--notes", "The latest catalogue.db and clap.npz, replaced by the daily pull. Don't delete.")
        if r.returncode != 0:
            sys.exit(f"couldn't create the release: {r.stderr}")
    r = gh("release", "upload", TAG, *[str(DATA / n) for n in FILES], "--clobber")
    if r.returncode != 0:
        sys.exit(f"upload failed: {r.stderr}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    VERSION.write_text(json.dumps({**{n: {"sha256": sha256(DATA / n), "bytes": (DATA / n).stat().st_size} for n in FILES},
                                   "updated": now, "tracks": total}, indent=1) + "\n")
    runs = json.loads(RUNS.read_text()) if RUNS.exists() else []
    runs = (runs + [{"at": now, "tracks": total}])[-400:]   # for the daily report: catalogue size after each run
    RUNS.write_text(json.dumps(runs, indent=0) + "\n")
    if REMOVED.exists():
        REMOVED.write_text(json.dumps({"ids": [], "why": "Tracks taken out by hand; applied and emptied by the daily pull."}, indent=1) + "\n")
    print(f"published {total:,} tracks ({(DATA / 'catalogue.db').stat().st_size / 1048576:.1f} MB catalogue)", flush=True)


if __name__ == "__main__":
    {"fetch": fetch, "publish": publish}[sys.argv[1] if len(sys.argv) > 1 else "fetch"]()
