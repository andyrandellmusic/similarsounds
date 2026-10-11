"""Find Beatport's chart tracks on Deezer, get CLAP to listen to 10 per genre, and build a
sound profile per genre (the average CLAP fingerprint of its 10 examples)."""
import json, re, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import load_audio
import librosa, torch, laion_clap

refs = json.load(open(ROOT / "eval" / "beatport_refs.json"))
m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))
out, used = {}, {}
for genre in refs["current"]:
  vecs, picked = [], []
  for part in ("current", "classics"):
    got = 0
    for n in refs[part][genre]:
        if got == 10:
            break
        artist, title = n.split(" - ", 1)
        hit = sources.find_on_deezer(f"{artist.split(',')[0]} - {title}", "")
        if not hit:
            continue
        # must be the same song, not just the same artist
        norm = lambda x: set(w for w in re.sub(r"[^a-z0-9 ]", " ", x.lower()).split() if w not in {"the", "a", "feat", "ft", "extended", "mix", "original", "remix", "edit"})
        want, have = norm(title.split(" (")[0]), norm(hit["title"])
        if not want or len(want & have) < max(1, len(want) // 2 + (len(want) > 1)):
            print("   skip (different song):", n, "->", hit["title"], flush=True)
            continue
        if "remix" in title.lower() and "remix" not in hit["title"].lower() and "mix" not in hit["title"].lower():
            print("   skip (not the remix):", n, "->", hit["title"], flush=True)
            continue
        y = librosa.resample(load_audio(sources.fetch_preview(hit["preview"])), orig_sr=22050, target_sr=48000)[:480000]
        with torch.no_grad():
            vecs.append(m.get_audio_embedding_from_data(x=y[None, :].astype("float32"), use_tensor=False)[0])
        picked.append(f"{part}: {hit['artist']['name']} - {hit['title']}  [{hit['id']}]")
        got += 1
  out[genre] = np.array(vecs); used[genre] = picked
  print(genre, len(vecs), flush=True)
np.savez(ROOT / "eval" / "results" / "beatport_refs.npz", **{g.replace(" / ", "_").replace(" ", "_"): v for g, v in out.items()}, names=np.array(list(out)))
json.dump(used, open(ROOT / "eval" / "beatport_refs_used.json", "w"), indent=1, ensure_ascii=False)
