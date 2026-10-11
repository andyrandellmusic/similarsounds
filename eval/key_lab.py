"""Key-detection lab: for each Beatport track we found on Deezer, compute several kinds of
'which notes are playing' summaries (chroma), then test key-finding methods against Beatport's key.
Step 1 (this script): fetch previews again and save the chroma summaries to eval/results/key_chroma.npz."""
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np, librosa
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import load_audio, SR

R = [json.loads(l) for l in open(ROOT / "eval" / "results" / "bp_all.jsonl")]
R = [r for r in R if r.get("deezer_id") and r.get("bp_key") and r["bp_key"] not in ("None", "")]

def fetch(r):
    for a in range(3):
        try:
            return r, sources.fetch_preview(sources.deezer_track(r["deezer_id"])["preview"])
        except Exception:
            time.sleep(3)
    return r, None

def feats(y):
    D = librosa.stft(y, n_fft=2048, hop_length=1024)
    H, _ = librosa.decompose.hpss(D)
    h = librosa.istft(H, hop_length=1024, length=len(y))
    cur = librosa.feature.chroma_cqt(y=h, sr=SR, hop_length=4096).mean(1)                     # what the site uses now
    fine = librosa.feature.chroma_cqt(y=h, sr=SR, hop_length=2048, bins_per_octave=36)
    fine_log = np.log1p(10 * fine).mean(1)
    bass = librosa.feature.chroma_cqt(y=h, sr=SR, hop_length=2048, fmin=librosa.note_to_hz("C1"), n_octaves=3).mean(1)
    mids = librosa.feature.chroma_cqt(y=h, sr=SR, hop_length=2048, fmin=librosa.note_to_hz("C3"), n_octaves=4).mean(1)
    cens = librosa.feature.chroma_cens(y=h, sr=SR, hop_length=2048).mean(1)
    return np.stack([cur, fine_log, bass, mids, cens])

out_ids, out_keys, out_genres, out_feats = [], [], [], []
with ThreadPoolExecutor(3) as pool:
    for n, (r, data) in enumerate(pool.map(fetch, R), 1):
        if not data:
            continue
        try:
            out_feats.append(feats(load_audio(data))); out_ids.append(r["deezer_id"]); out_keys.append(r["bp_key"]); out_genres.append(r["genre"])
        except Exception as e:
            print("skip", r["deezer_id"], e)
        if n % 100 == 0:
            print(f"  {n}/{len(R)}", flush=True)
np.savez(ROOT / "eval" / "results" / "key_chroma.npz", ids=np.array(out_ids), keys=np.array(out_keys), genres=np.array(out_genres),
         X=np.array(out_feats), kinds=np.array(["current", "fine_log", "bass", "mids", "cens"]))
print("saved", len(out_ids))
