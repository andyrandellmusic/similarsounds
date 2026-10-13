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
    # Drop new tracks that don't sound enough like Beatport's house charts (same test used on the catalogue)
    ref = np.load(ROOT / "data" / "beatport_house_refs.npz")
    norm = lambda X: (lambda Z: Z / np.linalg.norm(Z, axis=1, keepdims=True))((X - ref["mu"]) / ref["sd"])
    new_ids = [d for d in todo if d in done]
    if new_ids:
        closeness = np.sort(norm(np.array([done[d] for d in new_ids], dtype="float32")) @ norm(ref["emb"]).T, axis=1)[:, -10:].mean(1)
        weak = [d for d, c in zip(new_ids, closeness) if c < float(ref["cut"])]
        if weak:
            conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
            conn.executemany("DELETE FROM tracks WHERE deezer_id = ?", [(d,) for d in weak]); conn.commit()
            for d in weak:
                done.pop(d, None)
            np.savez(OUT, ids=np.array(list(done), dtype="int64"), emb=np.array(list(done.values()), dtype="float32"))
            print("removed", len(weak), "new tracks that don't sound like house", flush=True)
            todo = [d for d in todo if d not in set(weak)]

    # Genre check (the same rules as the big clean-up): new tracks that sound like trance / EDM / techno / pop,
    # or come from labels that aren't ours, are set aside - kept in the set_aside table, never shown
    gc_path = ROOT / "data" / "genre_check.npz"
    new = [d for d in todo if d in done]
    if new and gc_path.exists():
        gc = np.load(gc_path)
        E = np.array([done[d] for d in new], dtype="float32")
        Z = (E - gc["mu"]) / gc["sd"]; Z /= np.linalg.norm(Z, axis=1, keepdims=True)
        L = Z @ gc["W"].T + gc["b"]; P = np.exp(L - L.max(1, keepdims=True)); P /= P.sum(1, keepdims=True)
        p_not = P[:, 1]
        En = E / np.linalg.norm(E, axis=1, keepdims=True); S = En @ gc["text_emb"].T * 100
        T = np.exp(S - S.max(1, keepdims=True)); T /= T.sum(1, keepdims=True)
        hk = [k for k, n in enumerate(gc["text_names"]) if n in set(gc["house"].tolist())]
        house_text = T[:, hk].sum(1)
        bad_labels = set(gc["not_labels"].tolist())
        conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
        labels = dict(conn.execute(f"SELECT deezer_id, label FROM tracks WHERE deezer_id IN ({','.join('?' * len(new))})", new))
        out = [d for k, d in enumerate(new)
               if (labels.get(d) in bad_labels and p_not[k] >= 0.4) or p_not[k] >= 0.85 or (p_not[k] >= 0.6 and house_text[k] < 0.35)]
        if out:
            cols = [r[1] for r in conn.execute("PRAGMA table_info(tracks)")]
            conn.execute("CREATE TABLE IF NOT EXISTS set_aside AS SELECT * FROM tracks WHERE 0")
            have = {r[1] for r in conn.execute("PRAGMA table_info(set_aside)")}
            for c in ("aside_kind", "aside_why", "aside_at"):
                if c not in have:
                    conn.execute(f"ALTER TABLE set_aside ADD COLUMN {c} TEXT")
            cl = ", ".join(cols)
            for d in out:
                conn.execute(f"INSERT OR REPLACE INTO set_aside ({cl}, aside_kind, aside_why, aside_at) SELECT {cl}, 'not house', "
                             f"'daily genre check', datetime('now') FROM tracks WHERE deezer_id = ?", (d,))
                conn.execute("DELETE FROM tracks WHERE deezer_id = ?", (d,))
            conn.commit()
            print("set aside", len(out), "new tracks that aren't our genres", flush=True)
            todo = [d for d in todo if d not in set(out)]

    # Label the new tracks' sub-genre by sound: a classifier taught with 629 Beatport chart tracks
    # (Deep House / Tech House / Minimal / Deep Tech / Nu Disco). "House" when it isn't clearly one of them.
    st = np.load(ROOT / "data" / "clap_styles.npz")
    new = [d for d in todo if d in done]
    if new:
        E = np.array([done[d] for d in new], dtype="float32")
        Z = (E - st["mu"]) / st["sd"]; Z /= np.linalg.norm(Z, axis=1, keepdims=True)
        logits = Z @ st["W"].T + st["b"]
        p = np.exp(logits - logits.max(1, keepdims=True)); p /= p.sum(1, keepdims=True)
        labels = [str(st["names"][k]) if p[i, k] >= float(st["threshold"]) else str(st["fallback"])
                  for i, k in enumerate(p.argmax(1))]
        conn = sqlite3.connect(ROOT / "data" / "catalogue.db")
        conn.executemany("UPDATE tracks SET style = ? WHERE deezer_id = ?", list(zip(labels, new)))
        conn.commit()
        print("labelled", len(new), "new tracks", flush=True)
    print("CLAP fingerprints:", len(done), flush=True)


if __name__ == "__main__":
    main()
