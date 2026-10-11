"""SQLite catalogue plus the in-memory index used for matching.

Only metadata and computed features are stored - never audio.
(Swap for Postgres + pgvector when the catalogue grows past ~100k tracks.)
"""
import json
import sqlite3
import threading
from datetime import date
from pathlib import Path

import numpy as np

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "catalogue.db"
CLAP_PATH = DB_PATH.parent / "clap.npz"
CLAP_WEIGHT = 0.85

SCHEMA = """
CREATE TABLE IF NOT EXISTS tracks (
    deezer_id    INTEGER PRIMARY KEY,
    isrc         TEXT,
    title        TEXT NOT NULL,
    artist       TEXT NOT NULL,
    album        TEXT,
    label        TEXT,
    cover        TEXT,
    release_date TEXT,
    style        TEXT,
    key          TEXT,
    camelot      TEXT,
    bpm          REAL,
    energy_raw   TEXT,
    embedding    TEXT,
    added_at     TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_release ON tracks(release_date);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert(conn: sqlite3.Connection, t: dict) -> None:
    conn.execute(
        """INSERT OR REPLACE INTO tracks
           (deezer_id, isrc, title, artist, album, label, cover, release_date, style,
            key, camelot, bpm, energy_raw, embedding)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (t["deezer_id"], t.get("isrc"), t["title"], t["artist"], t.get("album"), t.get("label"),
         t.get("cover"), t.get("release_date"), t.get("style"), t["key"], t["camelot"], t["bpm"],
         json.dumps(t["energy_raw"]), json.dumps(t["embedding"])),
    )
    conn.commit()


def energy_vector(raw: dict) -> list[float]:
    return [raw["loudness"], raw["onset"], raw["brightness"]]


# Plain-word sound tags. Each axis: (feature, word when high, word when low), judged against the catalogue
SOUND_AXES = [("onset", "driving", "laid-back"), ("brightness", "bright", "dark"),
              ("bass", "bass-heavy", "airy"), ("flatness", "gritty", "smooth"), ("movement", "evolving", "steady")]


def sound_axes(raw: dict, emb) -> list[float]:
    # embedding layout: 20 MFCC means, 20 MFCC stds, 7 contrast means, 7 contrast stds, flatness, onset std, centroid std
    return [raw["onset"], raw["brightness"], float(emb[1]), float(emb[54]), float(emb[56])]


class Index:
    """All catalogue tracks held in numpy arrays for fast scoring."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reload()

    def reload(self):
        conn = connect()
        rows = [dict(r) for r in conn.execute("SELECT * FROM tracks")]
        conn.close()
        with self._lock:
            self.rows = rows
            self.ids = {r["deezer_id"]: i for i, r in enumerate(rows)}
            if not rows:
                return
            emb = np.array([json.loads(r["embedding"]) for r in rows], dtype="float32")
            self.sound_ref = np.sort(np.array([sound_axes(json.loads(r["energy_raw"]), e)
                                               for r, e in zip(rows, emb)], dtype="float32"), axis=0)
            self.emb_mean = emb.mean(axis=0)
            self.emb_std = emb.std(axis=0) + 1e-6
            z = (emb - self.emb_mean) / self.emb_std
            self.emb = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-9)
            self._load_clap()
            self.scale = {name: self._cos_scale(M) for name, M in (("emb", self.emb), ("sound", self.sound))}

            self.energy_feats = np.array(
                [energy_vector(json.loads(r["energy_raw"])) for r in rows], dtype="float32")
            for r, e in zip(rows, self.energy_scores(self.energy_feats)):
                r["energy"] = e
            self.energy = np.array([r["energy"] for r in rows], dtype="float32")

            self.bpm = np.array([r["bpm"] for r in rows], dtype="float32")
            self.camelot = [r["camelot"] for r in rows]
            today = date.today()
            self.age_days = np.array(
                [(today - date.fromisoformat(r["release_date"])).days if r["release_date"] else 3650
                 for r in rows], dtype="float32")

    def energy_scores(self, feats: np.ndarray) -> np.ndarray:
        """Map raw energy features to a 1-10 scale by percentile against the catalogue."""
        # share of catalogue tracks at or below each value (sorted lookup: memory stays linear in size)
        ref = np.sort(self.energy_feats, axis=0)
        n = len(ref)
        pct = np.stack([np.searchsorted(ref[:, j], feats[:, j], side="right") / n for j in range(ref.shape[1])], axis=1)
        combined = pct @ np.array([0.45, 0.35, 0.20])
        return np.clip(np.round(1 + combined * 9), 1, 10)

    def _load_clap(self):
        """CLAP sound fingerprints (computed offline, data/clap.npz). Matching uses a blend:
        85% CLAP (how it sounds overall) + 15% our own groove features. Tracks added since the
        last CLAP run fall back to the groove features alone until the next daily update."""
        n = len(self.rows)
        self.has_clap = np.zeros(n, dtype=bool)
        self.sound = self.emb
        if not CLAP_PATH.exists():
            return
        z = np.load(CLAP_PATH)
        C = np.zeros((n, z["emb"].shape[1]), dtype="float32")
        for did, e in zip(z["ids"].tolist(), z["emb"]):
            i = self.ids.get(did)
            if i is not None:
                C[i] = e
                self.has_clap[i] = True
        if not self.has_clap.any():
            return
        mu, sd = C[self.has_clap].mean(0), C[self.has_clap].std(0) + 1e-6
        Cz = np.where(self.has_clap[:, None], (C - mu) / sd, 0)
        Cz /= np.linalg.norm(Cz, axis=1, keepdims=True) + 1e-9
        self.sound = np.hstack([np.sqrt(CLAP_WEIGHT) * Cz, np.sqrt(1 - CLAP_WEIGHT) * self.emb]).astype("float32")

    @staticmethod
    def _cos_scale(M: np.ndarray) -> tuple[float, float]:
        """Typical and near-identical similarity between two catalogue tracks (from random pairs)."""
        rng = np.random.default_rng(0)
        a, b = rng.integers(0, len(M), 4000), rng.integers(0, len(M), 4000)
        cos = np.einsum("ij,ij->i", M[a], M[b])
        return float(np.median(cos)), float(np.quantile(cos, 0.999))

    def match(self, cos: np.ndarray, space: str) -> np.ndarray:
        """Turn raw similarity into a 0-1 match score on the same scale whichever fingerprint is used:
        a typical pair of house tracks scores 0.5, the closest 0.1% of pairs about 0.95."""
        mid, top = self.scale[space]
        return np.clip(0.5 + 0.45 * (cos - mid) / (top - mid + 1e-9), 0.01, 0.99)

    def query_vec(self, query: dict) -> tuple[np.ndarray, np.ndarray, str]:
        """The matrix and query vector to compare with: the CLAP blend when the track is in the
        catalogue and has CLAP, otherwise our own sound features."""
        row = query.get("row")
        if row is not None and self.has_clap[row]:
            return self.sound, self.sound[row], "sound"
        return self.emb, self.embed(query["embedding"]), "emb"

    def describe(self, raw: dict, embedding: list[float], n: int = 3) -> list[str]:
        """Up to n words for how a track sounds compared with the rest of the catalogue."""
        vals = sound_axes(raw, embedding)
        pct = [np.searchsorted(self.sound_ref[:, j], v) / len(self.sound_ref) for j, v in enumerate(vals)]
        picks = sorted(((abs(p - 0.5), hi if p > 0.5 else lo) for p, (_, hi, lo) in zip(pct, SOUND_AXES)), reverse=True)
        return [w for d, w in picks if d >= 0.25][:n]

    def embed(self, embedding: list[float]) -> np.ndarray:
        z = (np.array(embedding, dtype="float32") - self.emb_mean) / self.emb_std
        return z / (np.linalg.norm(z) + 1e-9)


def release_date_ok(d: str | None) -> bool:
    try:
        date.fromisoformat(d)
        return True
    except (TypeError, ValueError):
        return False
