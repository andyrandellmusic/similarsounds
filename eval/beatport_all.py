"""For every Beatport chart track (eval/beatport_charts.tsv): find the exact track on Deezer, get its
CLAP fingerprint, and run our own key/BPM/energy analysis, so we can (1) teach the genre sorter and
(2) score our key + BPM detection against Beatport's published values. Resumable."""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import sources
from app.analysis import analyse, load_audio
import librosa, torch, laion_clap

OUT = ROOT / "eval" / "results" / "bp_all.jsonl"
done = set()
if OUT.exists():
    done = {json.loads(l)["row"] for l in OUT.open()}
rows = [l.rstrip("\n").split("\t") for l in open(ROOT / "eval" / "beatport_charts.tsv", encoding="utf-8")]
STOP = {"the", "a", "feat", "ft", "extended", "mix", "original", "remix", "edit", "version", "radio", "club"}
norm = lambda x: set(w for w in re.sub(r"[^a-z0-9 ]", " ", x.lower()).split() if w not in STOP)

def find(i):
    genre, artist, title, mix, bpm, key, src = rows[i]
    first = artist.split(",")[0].strip()
    remix = bool(re.search(r"remix|edit|rework|mix\b", mix, re.I)) and not re.search(r"^(original|extended|radio)", mix, re.I)
    q = f"{first} - {title}" + (f" ({mix})" if remix else "")
    for attempt in range(3):
        try:
            hit = sources.find_on_deezer(q, "")
            break
        except Exception:
            time.sleep(3)
    else:
        return i, None
    if not hit:
        return i, None
    want, have = norm(title.split(" (")[0]), norm(hit["title"])
    if not want or len(want & have) < max(1, len(want) // 2 + (len(want) > 1)):
        return i, None
    if remix:   # remix: the remixer's name should appear in Deezer's title
        rm = norm(re.sub(r"(extended|radio)?\s*(remix|edit|rework|mix|dub|vip)", "", mix, flags=re.I))
        if rm and not (rm & have):
            return i, None
    try:
        return i, (hit, sources.fetch_preview(hit["preview"]))
    except Exception:
        return i, None

m = laion_clap.CLAP_Module(enable_fusion=False, amodel="HTSAT-base")
m.load_ckpt(str(Path.home() / ".cache/laion_clap/music_audioset_epoch_15_esc_90.14.pt"))
todo = [i for i in range(len(rows)) if i not in done]
print(len(rows), "rows,", len(done), "done,", len(todo), "to go", flush=True)
found = 0
with ThreadPoolExecutor(3) as pool, OUT.open("a") as f:
    for n, (i, res) in enumerate(pool.map(find, todo), 1):
        rec = {"row": i, "genre": rows[i][0], "bp_artist": rows[i][1], "bp_title": rows[i][2], "bp_mix": rows[i][3],
               "bp_bpm": float(rows[i][4]) if rows[i][4] not in ("", "None") else None, "bp_key": rows[i][5], "src": rows[i][6]}
        if res:
            hit, audio = res
            try:
                a = analyse(audio)
                y = librosa.resample(load_audio(audio), orig_sr=22050, target_sr=48000)[:480000]
                with torch.no_grad():
                    ce = m.get_audio_embedding_from_data(x=y[None, :].astype("float32"), use_tensor=False)[0]
                rec.update({"deezer_id": hit["id"], "dz": f"{hit['artist']['name']} - {hit['title']}", "our_bpm": a["bpm"],
                            "our_key": a["camelot"], "energy_raw": a["energy_raw"], "clap": [round(float(v), 5) for v in ce]})
                found += 1
            except Exception as e:
                rec["error"] = str(e)
        f.write(json.dumps(rec) + "\n"); f.flush()
        if n % 50 == 0:
            print(f"  {n}/{len(todo)}  found {found}", flush=True)
print("done, found", found, flush=True)
