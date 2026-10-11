"""Relabel sub-genres by listening: compare each track's CLAP fingerprint with text descriptions
of each style, and flag tracks that sound more like other genres than house.
Writes eval/results/labels.json (no changes to the live catalogue yet)."""
import json, sqlite3
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
STYLES = {
    "Tech House": ["tech house with a punchy groove and rolling bassline", "tech house club track"],
    "Deep House": ["deep house with warm chords and a smooth laid-back groove", "deep house track"],
    "Afro House": ["afro house with tribal percussion and African vocals", "afro house track"],
    "Melodic House": ["melodic house and techno with emotional synths and arpeggios", "melodic techno track"],
    "Organic House": ["organic house with acoustic instruments, slow and hypnotic", "organic downtempo house track"],
    "Soulful House": ["soulful house with gospel vocals and piano", "soulful vocal house track"],
    "Jackin House": ["jackin house with chopped vocal samples and a bouncy swing", "chicago jackin house track"],
    "Bass House": ["bass house with heavy distorted wobbling bass", "bass house track"],
    "Minimal / Deep Tech": ["minimal deep tech with sparse percussion and a deep rolling groove", "minimal house track"],
    "Funky / Disco House": ["disco house with funky guitar, strings and disco samples", "nu disco track"],
}
OTHER = {
    "pop": ["a pop song with a singer", "radio pop music"],
    "hip hop / r&b": ["hip hop rap song", "r&b slow jam"],
    "edm / big room": ["big room EDM festival anthem with a huge drop", "commercial dance pop"],
    "dubstep / dnb": ["dubstep with a heavy drop", "drum and bass"],
    "techno / trance": ["hard techno", "trance music"],
    "other": ["rock band", "ambient music without drums", "acoustic singer songwriter"],
}

import torch, laion_clap
m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))

def text_vecs(groups):
    names, vecs = [], []
    for name, prompts in groups.items():
        with torch.no_grad():
            e = m.get_text_embedding(prompts, use_tensor=False)
        e = e / np.linalg.norm(e, axis=1, keepdims=True)
        v = e.mean(0); names.append(name); vecs.append(v / np.linalg.norm(v))
    return names, np.array(vecs)

s_names, S = text_vecs(STYLES)
o_names, O = text_vecs(OTHER)
z = np.load(ROOT / "data" / "clap.npz")
A = z["emb"] / np.linalg.norm(z["emb"], axis=1, keepdims=True)
# Some descriptions match everything more strongly; judge each style against its average across the catalogue
zs = lambda M: (M - M.mean(0)) / (M.std(0) + 1e-9)
ss_raw, so_raw = A @ S.T, A @ O.T
ss, so = zs(ss_raw), zs(so_raw)
np.savez(ROOT / "eval" / "results" / "clap_text.npz", S=S, O=O, s_names=s_names, o_names=o_names)
rows = {r[0]: r for r in sqlite3.connect(ROOT / "data" / "catalogue.db").execute("SELECT deezer_id, artist, title, style FROM tracks")}
out = []
for i, did in enumerate(z["ids"].tolist()):
    best = int(ss[i].argmax()); ob = int(so[i].argmax())
    r = rows[did]
    out.append({"deezer_id": did, "artist": r[1], "title": r[2], "old": r[3], "new": s_names[best],
                "style_score": round(float(ss[i, best]), 3), "other": o_names[ob], "other_score": round(float(so[i, ob]), 3),
                "house_margin": round(float(ss[i].max() - so[i].max()), 3)})
json.dump(out, open(ROOT / "eval" / "results" / "labels.json", "w"))
from collections import Counter
print("new labels:", Counter(o["new"] for o in out).most_common())
print("changed:", sum(o["new"] != o["old"] for o in out), "of", len(out))
flag = [o for o in out if o["other_score"] > 2.0 and o["style_score"] < 0.5]
print("sounds clearly like another genre:", len(flag))
print(Counter(o["other"] for o in flag).most_common())
