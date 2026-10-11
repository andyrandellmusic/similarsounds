"""Artists that sound alike, from the audio of their tracks in our catalogue.

Each artist gets one "sound fingerprint": the average of their tracks' sound fingerprints.
Artists are compared by how close those averages are."""

import re
from collections import defaultdict

import numpy as np

_SPLIT = re.compile(r"\s*(?:,|&| x | feat\.? | ft\.? | vs\.? )\s*", re.I)


def main_artist(name: str) -> str:
    return _SPLIT.split(name or "")[0].strip() or name


class Artists:
    def __init__(self, index):
        self.index = index
        self.rebuild()

    def rebuild(self):
        groups: dict[str, list[int]] = defaultdict(list)
        for i, r in enumerate(self.index.rows):
            groups[main_artist(r["artist"])].append(i)
        self.names = sorted(groups)
        self.rows_of = {n: groups[n] for n in self.names}
        self.by_key = {n.lower(): n for n in self.names}
        if not self.names:
            self.centroids = np.zeros((0, 1), dtype="float32")
            return
        c = np.stack([self.index.emb[groups[n]].mean(axis=0) for n in self.names])
        self.centroids = c / (np.linalg.norm(c, axis=1, keepdims=True) + 1e-9)
        self.pos = {n: i for i, n in enumerate(self.names)}

    def find(self, name: str) -> str | None:
        return self.by_key.get(main_artist(name).lower())

    def like_vector(self, vec: np.ndarray, exclude: str | None = None, k: int = 8) -> list[dict]:
        if not len(self.names):
            return []
        sims = self.centroids @ vec
        out = []
        for i in np.argsort(-sims):
            n = self.names[i]
            if exclude and n.lower() == exclude.lower():
                continue
            rows = self.rows_of[n]
            top = max(rows, key=lambda j: float(self.index.emb[j] @ vec))
            out.append({"name": n, "similarity": round(float((sims[i] + 1) / 2) * 100),
                        "tracks": len(rows), "example": self.index.rows[top]})
            if len(out) == k:
                break
        return out

    def like_artist(self, name: str, k: int = 12) -> list[dict]:
        n = self.find(name)
        if not n:
            return []
        return self.like_vector(self.centroids[self.pos[n]], exclude=n, k=k)
