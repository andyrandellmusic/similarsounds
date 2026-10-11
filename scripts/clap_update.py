"""Add CLAP sound fingerprints for catalogue tracks that don't have one yet (and drop ones for
tracks that have been removed). Runs in the daily GitHub job; needs laion-clap + torch and the
LAION music checkpoint (CC0 licence). Previews are analysed and thrown away; only the 512-number
fingerprint is kept, in data/clap.npz.

    python -m scripts.clap_update --ckpt /path/to/music_audioset_epoch_15_esc_90.14.pt
"""
import argparse, sqlite3, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import load_audio

OUT = ROOT / "data" / "clap.npz"


def fetch(did):
    for attempt in range(4):
        try:
            t = sources.deezer_track(did)
            return did, sources.fetch_preview(t["preview"]) if t.get("preview") else None
        except Exception:
            time.sleep(4 * (attempt + 1))
    return did, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    args = ap.parse_args()
    ids = [r[0] for r in sqlite3.connect(ROOT / "data" / "catalogue.db").execute("SELECT deezer_id FROM tracks")]
    keep = set(ids)
    done = {}
    if OUT.exists():
        z = np.load(OUT)
        done = {d: e for d, e in zip(z["ids"].tolist(), z["emb"]) if d in keep}
    todo = [i for i in ids if i not in done]
    print(f"{len(ids)} tracks, {len(done)} have CLAP, {len(todo)} to add", flush=True)
    if todo:
        import librosa, torch, laion_clap
        m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
        m.load_ckpt(args.ckpt)
        with ThreadPoolExecutor(3) as pool:
            for did, data in pool.map(fetch, todo):
                if not data:
                    continue
                try:
                    y = librosa.resample(load_audio(data), orig_sr=22050, target_sr=48000)[:480000]
                    with torch.no_grad():
                        done[did] = m.get_audio_embedding_from_data(x=y[None, :].astype("float32"), use_tensor=False)[0]
                except Exception as e:
                    print("  skip", did, e, flush=True)
    np.savez(OUT, ids=np.array(list(done), dtype="int64"), emb=np.array(list(done.values()), dtype="float32"))
    # Label the new tracks' sub-genre by sound, the same way the catalogue was relabelled
    st = np.load(ROOT / "data" / "clap_styles.npz")
    new = [d for d in todo if d in done]
    if new:
        E = np.array([done[d] for d in new]); E /= np.linalg.norm(E, axis=1, keepdims=True)
        best = (((E @ st["S"].T) - st["mu"]) / st["sd"]).argmax(1)
        conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
        conn.executemany("UPDATE tracks SET style = ? WHERE deezer_id = ?", [(str(st["names"][b]), d) for b, d in zip(best, new)])
        conn.commit()
        print("labelled", len(new), "new tracks", flush=True)
    print("CLAP fingerprints:", len(done), flush=True)


if __name__ == "__main__":
    main()
