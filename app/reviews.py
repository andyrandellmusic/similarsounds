"""Visitor star reviews.

Every review is appended to data/reviews.csv on the server straight away. Render's free plan
wipes that file on every restart, so when REVIEWS_TOKEN is set (a GitHub token that can write
to the private repo in REVIEWS_REPO) each review is also appended to reviews.csv in that repo,
which is where they're kept for good and where you read them.

Nothing personal is stored: just the time, the stars, the site language, the play count and any
comment typed into the "How can we improve?" box at the bottom of the page.
"""

import base64
import csv
import io
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

import httpx

LOCAL = Path(__file__).resolve().parent.parent / "data" / "reviews.csv"
REPO = os.environ.get("REVIEWS_REPO", "andyrandellmusic/similarsounds-reviews")
TOKEN = os.environ.get("REVIEWS_TOKEN", "").strip()
FILE = "reviews.csv"
HEADER = ["time_utc", "stars", "language", "tracks_played", "source", "comment"]

_lock = threading.Lock()


def _row(stars: int, lang: str, plays: int, comment: str = "", source: str = "popup") -> list[str]:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return [now, str(stars), lang, str(plays), source, comment]


def _csv_line(row: list[str]) -> str:
    buf = io.StringIO()
    csv.writer(buf).writerow(row)
    return buf.getvalue()


def _save_local(row: list[str]) -> None:
    LOCAL.parent.mkdir(exist_ok=True)
    new = not LOCAL.exists()
    with LOCAL.open("a", newline="") as f:
        if new:
            f.write(_csv_line(HEADER))
        f.write(_csv_line(row))


def _save_github(row: list[str]) -> bool:
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE}"
    headers = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
    with httpx.Client(timeout=15) as client:
        for _ in range(3):  # retry if two reviews land at the same moment
            r = client.get(url, headers=headers)
            if r.status_code == 200:
                sha = r.json()["sha"]
                text = base64.b64decode(r.json()["content"]).decode()
            elif r.status_code == 404:
                sha, text = None, _csv_line(HEADER)
            else:
                return False
            body = {
                "message": f"Review: {row[1]} stars",
                "content": base64.b64encode((text + _csv_line(row)).encode()).decode(),
            }
            if sha:
                body["sha"] = sha
            w = client.put(url, headers=headers, json=body)
            if w.status_code in (200, 201):
                return True
            if w.status_code not in (409, 422):
                return False
    return False


def save(stars: int, lang: str, plays: int, comment: str = "", source: str = "popup") -> None:
    row = _row(stars, lang, plays, comment, source)
    with _lock:
        _save_local(row)
        if TOKEN:
            try:
                _save_github(row)
            except httpx.HTTPError:
                pass
    _save_supabase(stars, lang, plays, comment, source)


def _save_supabase(stars: int, lang: str, plays: int, comment: str, source: str) -> None:
    """Also keep the review in Supabase, where the private stats page (/stats) reads it."""
    from app import tokens
    if not tokens.ENABLED:
        return
    try:
        tokens._client.post(f"{tokens.URL}/rest/v1/rpc/add_review",
                            headers={"apikey": tokens.KEY, "Content-Type": "application/json"},
                            json={"p_stars": stars, "p_lang": lang, "p_plays": plays,
                                  "p_comment": comment or None, "p_source": source})
    except httpx.HTTPError:
        pass
