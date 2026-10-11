"""Step 3: score each model's fingerprints. For every test track, look at its 10 closest
matches and ask: do they share its style? Is another track by the same artist among them?
Higher is better. 'random' shows what pure chance scores."""
import json, sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sample = json.load(open(ROOT / "eval" / "sample.json"))
styles = np.array([s["style"] for s in sample])
artists = np.array([s["artist"].split(",")[0].split(" & ")[0].strip().lower() for s in sample])
multi = np.array([c > 1 for c in (Counter(artists)[a] for a in artists)])


def prep(X):
    X = (X - X.mean(0)) / (X.std(0) + 1e-6)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-9)


def score(X, k=10):
    Z = prep(X)
    S = Z @ Z.T
    np.fill_diagonal(S, -np.inf)
    nn = np.argsort(-S, axis=1)[:, :k]
    style_p = (styles[nn] == styles[:, None]).mean()
    artist_hit = (artists[nn] == artists[:, None]).any(1)[multi].mean()
    return style_p, artist_hit


rows = []
rng = np.random.default_rng(0)
rows.append(("random (chance)",) + score(rng.standard_normal((len(sample), 64))))
for f in sorted((ROOT / "eval" / "results").glob("*.npy")):
    rows.append((f.stem,) + score(np.load(f)))
print(f"{'model':18s} {'same style in top 10':>22s} {'same artist found':>18s}")
for name, sp, ah in sorted(rows, key=lambda r: -r[1]):
    print(f"{name:18s} {sp*100:21.1f}% {ah*100:17.1f}%")
print(f"\n{len(sample)} tracks, {multi.sum()} have another track by the same artist in the test set")
