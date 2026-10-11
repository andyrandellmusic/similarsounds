"""Give every catalogue track a CLAP sound fingerprint (512 numbers), computed on this Mac.
Previews are fetched, analysed and thrown away (only the fingerprint is kept).
Writes data/clap.npz: ids + embeddings. Safe to stop and restart: it resumes."""
import sqlite3, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import load_audio

OUT = ROOT / "data" / "clap.npz"
CACHE = ROOT / "eval" / "cache"
ids = [r[0] for r in sqlite3.connect(ROOT / "data" / "catalogue.db").execute("SELECT deezer_id FROM tracks")]
done = {}
if OUT.exists():
    z = np.load(OUT)
    done = dict(zip(z["ids"].tolist(), z["emb"]))
todo = [i for i in ids if i not in done]
print(f"{len(ids)} tracks, {len(done)} already done, {len(todo)} to go", flush=True)


def fetch(did):
    cached = CACHE / f"{did}.mp3"
    if cached.exists():
        return did, cached.read_bytes()
    for attempt in range(4):
        try:
            t = sources.deezer_track(did)
            return did, sources.fetch_preview(t["preview"]) if t.get("preview") else None
        except Exception:
            time.sleep(4 * (attempt + 1))
    return did, None


import torch, librosa, laion_clap
torch.set_num_threads(6)
m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))


def save():
    np.savez(OUT, ids=np.array(list(done), dtype="int64"), emb=np.array(list(done.values()), dtype="float32"))


t0 = time.time()
with ThreadPoolExecutor(3) as pool:
    for n, (did, data) in enumerate(pool.map(fetch, todo), 1):
        if data:
            try:
                y = librosa.resample(load_audio(data), orig_sr=22050, target_sr=48000)[:480000]
                with torch.no_grad():
                    done[did] = m.get_audio_embedding_from_data(x=y[None, :].astype("float32"), use_tensor=False)[0]
            except Exception as e:
                print("  skip", did, e, flush=True)
        if n % 200 == 0:
            save()
            print(f"  {n}/{len(todo)}  {time.time() - t0:.0f}s", flush=True)
save()
print("done", len(done), flush=True)
