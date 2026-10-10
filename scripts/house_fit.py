"""Fit the house check on data/house_eval.json and write data/house_model.json.

    uv run python -m scripts.house_eval   # collect labelled examples (slow)
    uv run python -m scripts.house_fit    # fit + cross-validate (instant)
"""
import collections
import json

import numpy as np

from app.house import FEATURES, feature_vector


def fit(X, y, l2=1.0, iters=4000, lr=0.1):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    w, b = np.zeros(Z.shape[1]), 0.0
    sw = np.where(y == 1, (y == 0).sum() / max((y == 1).sum(), 1), 1.0)   # balance classes
    for _ in range(iters):
        g = (1 / (1 + np.exp(-(Z @ w + b))) - y) * sw
        w -= lr * (Z.T @ g / len(y) + l2 * w / len(y))
        b -= lr * g.mean()
    return {"features": FEATURES, "mu": mu.tolist(), "sd": sd.tolist(), "w": w.tolist(), "b": float(b)}


def predict(m, X):
    Z = (X - np.array(m["mu"])) / np.array(m["sd"])
    return 1 / (1 + np.exp(-(Z @ np.array(m["w"]) + m["b"])))


def main():
    rows = json.load(open("data/house_eval.json"))
    X = np.array([feature_vector(r) for r in rows])
    y = np.array([r["label"] for r in rows])

    folds = np.random.default_rng(0).permutation(len(y)) % 10
    P = np.zeros(len(y))
    for f in range(10):
        P[folds == f] = predict(fit(X[folds != f], y[folds != f]), X[folds == f])

    for thr in (0.3, 0.4, 0.5, 0.6):
        ok = P >= thr
        print(f"threshold {thr}: house kept {ok[y == 1].mean():.0%}, non-house caught {(~ok[y == 0]).mean():.0%}")
    per = collections.defaultdict(list)
    for r, p in zip(rows, P):
        per[r["kind"]].append(p >= 0.5)
    print("passed as house (threshold 0.5):", {k: f"{sum(v)}/{len(v)}" for k, v in sorted(per.items())})
    print("house wrongly flagged:", [(r["name"], round(float(p), 2)) for r, p in zip(rows, P)
                                     if r["label"] == 1 and p < 0.5])

    model = fit(X, y)
    print("weights:", {n: round(w, 2) for n, w in zip(FEATURES, model["w"])}, "bias", round(model["b"], 2))
    json.dump(model, open("data/house_model.json", "w"), indent=1)


if __name__ == "__main__":
    main()
