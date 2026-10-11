"""Re-detect the musical key of every catalogue track with the current detect_key (previews are
fetched, analysed and thrown away). Writes key + camelot back to data/catalogue.db. Resumable via
eval/results/rekey_done.txt.  python -m scripts.rekey"""
import sqlite3, sys, time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import detect_key, load_audio

DONE = ROOT / "eval" / "results" / "rekey_done.txt"


def fetch(did):
    for a in range(4):
        try:
            t = sources.deezer_track(did)
            return did, sources.fetch_preview(t["preview"]) if t.get("preview") else None
        except Exception:
            time.sleep(4 * (a + 1))
    return did, None


def key_of(data):
    return detect_key(load_audio(data))


def main():
    conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
    ids = [r[0] for r in conn.execute("SELECT deezer_id FROM tracks")]
    done = set(int(x) for x in DONE.read_text().split()) if DONE.exists() else set()
    todo = [i for i in ids if i not in done]
    print(f"{len(ids)} tracks, {len(todo)} to re-key", flush=True)
    changed = 0
    with ThreadPoolExecutor(4) as io, ProcessPoolExecutor(6) as cpu, DONE.open("a") as log:
        pending = {}
        for n, (did, data) in enumerate(io.map(fetch, todo), 1):
            if data:
                pending[cpu.submit(key_of, data)] = did
            if len(pending) >= 24 or n == len(todo):
                for f, d in list(pending.items()):
                    try:
                        name, cam = f.result()
                        old = conn.execute("SELECT camelot FROM tracks WHERE deezer_id=?", (d,)).fetchone()[0]
                        changed += old != cam
                        conn.execute("UPDATE tracks SET key=?, camelot=? WHERE deezer_id=?", (name, cam, d))
                        log.write(f"{d}\n")
                    except Exception as e:
                        print("  skip", d, e, flush=True)
                conn.commit(); log.flush(); pending = {}
            if n % 500 == 0:
                print(f"  {n}/{len(todo)}  changed so far {changed}", flush=True)
    print("done, keys changed:", changed, flush=True)


if __name__ == "__main__":
    main()
