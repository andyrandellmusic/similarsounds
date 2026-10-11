"""Step 2: turn every test preview into a "sound fingerprint" with one model.
Usage: python eval/embed.py <current|yamnet|openl3|panns|clap>
Writes eval/results/<model>.npy (one row per track, same order as eval/sample.json)."""
import json, sys, time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
model = sys.argv[1]
sample = json.load(open(ROOT / "eval" / "sample.json"))
CACHE = ROOT / "eval" / "cache"


def audio(did, sr):
    import librosa
    y = np.load(CACHE / f"{did}.npy").astype("float32")   # 22,050 Hz mono, decoded exactly as the site does
    return y if sr == 22050 else librosa.resample(y, orig_sr=22050, target_sr=sr)


def run(fn, sr):
    out, t0 = [], time.time()
    for i, s in enumerate(sample):
        out.append(fn(audio(s["deezer_id"], sr)))
        if i % 100 == 0:
            print(f"  {i}/{len(sample)}  {time.time() - t0:.0f}s", flush=True)
    return np.array(out, dtype="float32")


if model == "current":
    import sqlite3
    conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
    emb = {d: json.loads(e) for d, e in conn.execute("SELECT deezer_id, embedding FROM tracks")}
    X = np.array([emb[s["deezer_id"]] for s in sample], dtype="float32")

elif model == "yamnet":
    import tensorflow_hub as hub
    m = hub.load("https://tfhub.dev/google/yamnet/1")
    def f(y):
        _, emb, _ = m(y.astype("float32"))
        e = emb.numpy()
        return np.concatenate([e.mean(0), e.std(0)])
    X = run(f, 16000)

elif model == "openl3":
    import torch, torchopenl3
    m = torchopenl3.core.load_audio_embedding_model(input_repr="mel256", content_type="music", embedding_size=512)
    def f(y):
        with torch.no_grad():
            e, _ = torchopenl3.get_audio_embedding(y, 48000, model=m, hop_size=0.5, verbose=False)
        e = np.asarray(e).reshape(-1, 512)
        return np.concatenate([e.mean(0), e.std(0)])
    X = run(f, 48000)

elif model == "panns":
    import torch
    from panns_inference import AudioTagging
    m = AudioTagging(checkpoint_path=None, device="cpu")
    def f(y):
        _, e = m.inference(y[None, :].astype("float32"))
        return e[0]
    X = run(f, 32000)

elif model == "clap":
    import torch, laion_clap
    m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
    m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))   # LAION's music checkpoint
    def f(y):
        with torch.no_grad():
            e = m.get_audio_embedding_from_data(x=y[None, :480000].astype("float32"), use_tensor=False)
        return e[0]
    X = run(f, 48000)

np.save(ROOT / "eval" / "results" / f"{model}.npy", X)
print(model, X.shape)
