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
            self.emb_mean = emb.mean(axis=0)
            self.emb_std = emb.std(axis=0) + 1e-6
            z = (emb - self.emb_mean) / self.emb_std
            self.emb = z / (np.linalg.norm(z, axis=1, keepdims=True) + 1e-9)

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
        ref = self.energy_feats
        pct = np.stack([(ref[None, :, j] <= feats[:, None, j]).mean(axis=1) for j in range(ref.shape[1])], axis=1)
        combined = pct @ np.array([0.45, 0.35, 0.20])
        return np.clip(np.round(1 + combined * 9), 1, 10)

    def embed(self, embedding: list[float]) -> np.ndarray:
        z = (np.array(embedding, dtype="float32") - self.emb_mean) / self.emb_std
        return z / (np.linalg.norm(z) + 1e-9)


def release_date_ok(d: str | None) -> bool:
    try:
        date.fromisoformat(d)
        return True
    except (TypeError, ValueError):
        return False
