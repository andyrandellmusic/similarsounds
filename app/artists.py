"""Artists that sound alike, from the audio of their tracks in our catalogue.

Each artist gets one "sound fingerprint": the average of their tracks' sound fingerprints.
Artists are compared by how close those averages are."""

import re
from collections import Counter, defaultdict

import numpy as np

_SPLIT = re.compile(r"\s*(?:,|&| x | feat\.? | ft\.? | vs\.? )\s*", re.I)


def main_artist(name: str) -> str:
    return _SPLIT.split(name or "")[0].strip() or name


class Artists:
    def __init__(self, index):
        self.index = index
        self.rebuild()

    def rebuild(self):
        from app.pages import artist_slug
        # one artist per page address: spellings that share an address ("ZHU" / "Zhu", "Ultra Nate" / "Ultra
        # Naté") are one artist, shown under the spelling used on most of their tracks
        by_slug: dict[str, list[int]] = defaultdict(list)
        spellings: dict[str, Counter] = defaultdict(Counter)
        for i, r in enumerate(self.index.rows):
            n = main_artist(r["artist"])
            s = artist_slug(n)
            by_slug[s].append(i)
            spellings[s][n] += 1
        display = {s: min(c, key=lambda n: (-c[n], n)) for s, c in spellings.items()}
        groups = {display[s]: rows for s, rows in by_slug.items()}
        self.names = sorted(groups)
        self.rows_of = {n: groups[n] for n in self.names}
        self.by_slug = {s: display[s] for s in by_slug}
        self.by_key = {v.lower(): display[s] for s, c in spellings.items() for v in c}
        if not self.names:
            self.centroids = np.zeros((0, 1), dtype="float32")
            return
        def cents(M):
            c = np.stack([M[groups[n]].mean(axis=0) for n in self.names])
            return c / (np.linalg.norm(c, axis=1, keepdims=True) + 1e-9)
        self.spaces = {"emb": (self.index.emb, cents(self.index.emb)),
                       "sound": (self.index.sound, cents(self.index.sound))}
        self.centroids = self.spaces["sound"][1]
        self.pos = {n: i for i, n in enumerate(self.names)}

    def find(self, name: str) -> str | None:
        return self.by_key.get(main_artist(name).lower())

    def like_vector(self, vec: np.ndarray, exclude: str | None = None, k: int = 8, space: str = "sound") -> list[dict]:
        if not len(self.names):
            return []
        M, cents = self.spaces[space]
        sims = cents @ vec
        out = []
        for i in np.argsort(-sims):
            n = self.names[i]
            if exclude and n.lower() == exclude.lower():
                continue
            rows = self.rows_of[n]
            top = max(rows, key=lambda j: float(M[j] @ vec))
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
