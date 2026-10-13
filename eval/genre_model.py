"""Genre models from CLAP sound fingerprints, trained on Beatport's 629 chart tracks plus Boss's
listening-test answers. Reports honest (cross-validated) accuracy; --save writes data/genre_model.npz."""
import json, sys, collections
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FIVE = ["House", "Deep House", "Tech House", "Minimal / Deep Tech", "Funky / Disco House"]

def load():
    z = np.load(ROOT / "data" / "clap.npz"); cat = dict(zip(z["ids"].tolist(), z["emb"]))
    bp = [json.loads(l) for f in ("bp_all.jsonl", "usb_refs.jsonl") if (ROOT / "eval" / "results" / f).exists()
          for l in open(ROOT / "eval" / "results" / f)]          # Beatport charts + Boss's rekordbox USB tags
    bp = [(np.array(r["clap"], "float32"), r["genre"], "beatport", r["deezer_id"]) for r in bp if r.get("clap") and r["genre"] in FIVE]
    L = {int(k): v["genre"] for k, v in json.load(open(ROOT / "eval" / "results" / "genre_labels.json")).items()}
    me = [(cat[i], g, "boss", i) for i, g in L.items() if i in cat]
    return bp, me, cat

def fit(X, y, k, l2=1.0, iters=3000, lr=0.5):
    mu, sd = X.mean(0), X.std(0) + 1e-6
    Z = (X - mu) / sd; Z /= np.linalg.norm(Z, axis=1, keepdims=True)
    W = np.zeros((k, Z.shape[1])); b = np.zeros(k); Y = np.eye(k)[y]
    cw = len(y) / (k * np.maximum(np.bincount(y, minlength=k), 1))          # balance classes
    sw = cw[y][:, None]
    for _ in range(iters):
        P = np.exp(Z @ W.T + b); P /= P.sum(1, keepdims=True)
        G = (P - Y) * sw
        W -= lr * (G.T @ Z / len(y) + l2 * W / len(y)); b -= lr * G.mean(0)
    return {"mu": mu, "sd": sd, "W": W, "b": b}

def prob(m, X):
    Z = (X - m["mu"]) / m["sd"]; Z /= np.linalg.norm(Z, axis=1, keepdims=True)
    P = np.exp(Z @ m["W"].T + m["b"]); return P / P.sum(1, keepdims=True)

def cv(rows, classes, folds=10, seed=0):
    X = np.array([r[0] for r in rows]); y = np.array([classes.index(r[1]) for r in rows])
    f = np.random.default_rng(seed).permutation(len(y)) % folds; P = np.zeros((len(y), len(classes)))
    for k in range(folds):
        P[f == k] = prob(fit(X[f != k], y[f != k], len(classes)), X[f == k])
    return y, P

if __name__ == "__main__":
    bp, me, cat = load()
    # 1) ours vs not ours
    rows = [(x, "ours" if g in FIVE else "not", s, i) for x, g, s, i in bp + me]
    y, P = cv(rows, ["ours", "not"])
    src = np.array([r[2] for r in rows])
    for thr in (0.5, 0.6, 0.7):
        pred_not = P[:, 1] >= thr
        b = src == "boss"
        print(f"ours-vs-not @ {thr}: your 'not ours' caught {np.mean(pred_not[b & (y == 1)]):.0%} | your keepers kept {np.mean(~pred_not[b & (y == 0)]):.0%} | Beatport house kept {np.mean(~pred_not[src == 'beatport']):.0%}")
    # 2) the five sub-genres
    rows5 = [r for r in bp + me if r[1] in FIVE]
    y5, P5 = cv(rows5, FIVE)
    s5 = np.array([r[2] for r in rows5]); pred = P5.argmax(1)
    print(f"sub-genre accuracy: Beatport tracks {np.mean(pred[s5 == 'beatport'] == y5[s5 == 'beatport']):.0%}, your tracks {np.mean(pred[s5 == 'boss'] == y5[s5 == 'boss']):.0%} (site now: 52% on your tracks)")
    cm = collections.Counter((FIVE[a], FIVE[b]) for a, b in zip(y5, pred) if a != b)
    print("most common mix-ups (true -> predicted):", cm.most_common(6))
    if "--save" in sys.argv:
        X = np.array([r[0] for r in rows]); yy = np.array([0 if r[1] == "ours" else 1 for r in rows]); m1 = fit(X, yy, 2)
        X5 = np.array([r[0] for r in rows5]); m5 = fit(X5, np.array([FIVE.index(r[1]) for r in rows5]), 5)
        np.savez(ROOT / "data" / "genre_model.npz", ours_mu=m1["mu"], ours_sd=m1["sd"], ours_W=m1["W"], ours_b=m1["b"],
                 five_mu=m5["mu"], five_sd=m5["sd"], five_W=m5["W"], five_b=m5["b"], five=np.array(FIVE))
        print("saved data/genre_model.npz")
