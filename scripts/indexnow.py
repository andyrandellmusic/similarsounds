"""Tell Bing (and through it ChatGPT search, Copilot, DuckDuckGo, Yandex…) about new or changed pages
straight away, using IndexNow (free, no account needed). The key below is public by design: the site
serves it at /79c46b4c89c7be3d8ddd6e1941d2af93.txt to prove the pages are ours.

  python -m scripts.indexnow --all            # every page in the sitemap (first time)
  python -m scripts.indexnow --since 2026-10-12  # tracks added since a date, plus the hub pages
"""

import argparse
import sqlite3
import sys
import xml.etree.ElementTree as ET

import httpx

SITE = "https://www.similarsounds.com"
HOST = "www.similarsounds.com"
KEY = "79c46b4c89c7be3d8ddd6e1941d2af93"
DB = "data/catalogue.db"


def all_urls() -> list[str]:
    xml = httpx.get(f"{SITE}/sitemap.xml", timeout=60).text
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [e.text for e in ET.fromstring(xml).findall("s:url/s:loc", ns)]


def new_urls(since: str) -> list[str]:
    from app.pages import track_path   # same slugs as the live site
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("select * from tracks where added_at >= ?", (since,)).fetchall()
    hubs = [f"{SITE}/", f"{SITE}/similar-to"]
    return hubs + [SITE + track_path(dict(r)) for r in rows]


def submit(urls: list[str]) -> None:
    for i in range(0, len(urls), 10000):
        batch = urls[i:i + 10000]
        r = httpx.post("https://api.indexnow.org/indexnow", timeout=60,
                       json={"host": HOST, "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": batch})
        print(f"IndexNow: sent {len(batch)} URLs -> HTTP {r.status_code} {r.text[:200]}")
        if r.status_code >= 400:
            sys.exit(1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--all", action="store_true")
    g.add_argument("--since")
    a = ap.parse_args()
    urls = all_urls() if a.all else new_urls(a.since)
    submit(urls)
