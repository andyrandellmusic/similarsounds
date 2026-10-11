"""Your-tracks test: for each track you picked, the 5 closest-sounding catalogue tracks according
to CLAP and according to the site's current system, shown blind as List A / List B."""
import json, random, sqlite3, sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import analyse, load_audio

SEEDS = [4280292312, 2338469585, 3253824161, 395875972, 4265272552, 3604108432, 4234024562, 921009452, 1884719647]
CACHE = ROOT / "eval" / "cache"
conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
rows = {r[0]: r for r in conn.execute("SELECT deezer_id, artist, title, style, embedding FROM tracks")}

z = np.load(ROOT / "data" / "clap.npz")
c_ids = z["ids"].tolist(); C = z["emb"]
c_mu, c_sd = C.mean(0), C.std(0) + 1e-6
Cz = (C - c_mu) / c_sd; Cz /= np.linalg.norm(Cz, axis=1, keepdims=True)

o_ids = list(rows); O = np.array([json.loads(rows[i][4]) for i in o_ids], dtype="float32")
o_mu, o_sd = O.mean(0), O.std(0) + 1e-6
Oz = (O - o_mu) / o_sd; Oz /= np.linalg.norm(Oz, axis=1, keepdims=True)

import torch, librosa, laion_clap
m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))


def preview(did):
    f = CACHE / f"{did}.mp3"
    if not f.exists():
        f.write_bytes(sources.fetch_preview(sources.deezer_track(did)["preview"]))
    return f.read_bytes()


def top(scores, ids, seed, title, k=5):
    out, seen = [], {title.lower()}
    for i in np.argsort(-scores):
        did = ids[i]
        t = rows.get(did)
        if did == seed or not t or t[2].split(" (")[0].lower() in seen:
            continue
        seen.add(t[2].split(" (")[0].lower())
        out.append({"deezer_id": did, "artist": t[1], "title": t[2]})
        if len(out) == k:
            break
    return out


random.seed(11)
tests = []
for seed in SEEDS:
    info = sources.deezer_track(seed)
    data = preview(seed)
    y = load_audio(data)
    with torch.no_grad():
        ce = m.get_audio_embedding_from_data(x=librosa.resample(y, orig_sr=22050, target_sr=48000)[None, :480000].astype("float32"), use_tensor=False)[0]
    cz = (ce - c_mu) / c_sd; cz /= np.linalg.norm(cz)
    oe = np.array(analyse(data)["embedding"], dtype="float32")
    oz = (oe - o_mu) / o_sd; oz /= np.linalg.norm(oz)
    lists = [{"sys": "clap", "tracks": top(Cz @ cz, c_ids, seed, info["title"])},
             {"sys": "current", "tracks": top(Oz @ oz, o_ids, seed, info["title"])}]
    random.shuffle(lists)
    for l in lists:
        for t in l["tracks"]:
            preview(t["deezer_id"])
    tests.append({"seed": {"deezer_id": seed, "artist": info["artist"]["name"], "title": info["title"], "style": ""}, "lists": lists})
    print(info["artist"]["name"], "-", info["title"], flush=True)
json.dump(tests, open(ROOT / "eval" / "listen5.json", "w"))
print("ok")
