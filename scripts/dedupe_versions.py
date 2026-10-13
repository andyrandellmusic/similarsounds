"""Remove duplicate versions of the same track (e.g. "Song" and "Song (Extended Mix)"), keeping one:
the extended version if there is one (what DJs play), then the original, club mix, then radio edits. Remixes are different
tracks and are never merged. Removed tracks go to the set_aside table, so nothing is lost.
    .venv/bin/python -m scripts.dedupe_versions            # report only
    .venv/bin/python -m scripts.dedupe_versions --apply"""
import argparse, collections, re, sqlite3, time
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "catalogue.db"
# plain versions of one track: no remixer named
VERSION = re.compile(r"\s*[\(\[-]\s*(extended|original|radio|club|single|album)?\s*(mix|edit|version|cut|vocal mix)?\s*[\)\]]?\s*$", re.I)
PLAIN = re.compile(r"^(extended|original|radio|club|single|album)?\s*(mix|edit|version|cut)?$|^extended$", re.I)


def base(title: str):
    """(base title, version rank: 0 extended, 1 original, 2 club, 3 radio/edit) or None when the bracket names a remix/remixer."""
    m = re.match(r"^(.*?)\s*(?:[\(\[]([^\)\]]*)[\)\]]|-\s+([^-]*))\s*$", title)
    if not m:
        return title.strip().lower(), 1
    tag = (m.group(2) or m.group(3) or "").strip()
    if not PLAIN.match(tag):
        # a remix is its own track, but its edit / shortcut / extended cut is the same remix:
        # "(MK Remix Edit)" and "(MK Remix)" are one track, "(MK Remix)" and "(Dom Remix)" are two
        r = re.match(r"^(.*?\b(?:remix|rework|dub|mix|vip))\s+(extended|short|shortcut|radio edit|edit|cut|club mix|version)$", tag, re.I)
        if r:
            v = r.group(2).lower()
            return f"{m.group(1).strip().lower()} ({r.group(1).strip().lower()})", 0 if v.startswith("extended") else 3
        return title.strip().lower(), 1               # e.g. "(MK Remix)": its own track
    t = tag.lower()
    rank = 0 if t.startswith("extended") else 2 if t.startswith("club") else 3 if ("radio" in t or "edit" in t) else 1
    return m.group(1).strip().lower(), rank


def key(artist: str, title: str):
    b, rank = base(title)
    return re.sub(r"[^a-z0-9]", "", artist.lower().split(",")[0]), re.sub(r"[^a-z0-9]", "", b), rank


def existing_keys(conn) -> set:
    return {key(a, t)[:2] for a, t in conn.execute("SELECT artist, title FROM tracks")}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true"); args = ap.parse_args()
    conn = sqlite3.connect(DB)
    groups = collections.defaultdict(list)
    for did, artist, title, added in conn.execute("SELECT deezer_id, artist, title, added_at FROM tracks"):
        a, b, rank = key(artist, title)
        if b:
            groups[(a, b)].append((rank, added or "", did, f"{artist} - {title}"))
    drop = []
    for g in groups.values():
        if len(g) > 1:
            g.sort()
            print(f"  keep {g[0][3]}   |   remove " + "; ".join(x[3] for x in g[1:]))
            drop += [x[2] for x in g[1:]]
    print(f"{len(drop)} duplicate versions to remove")
    if args.apply and drop:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tracks)")]
        have = {r[1] for r in conn.execute("PRAGMA table_info(set_aside)")}
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        for did in drop:
            row = dict(zip(cols, conn.execute("SELECT * FROM tracks WHERE deezer_id=?", (did,)).fetchone()))
            row.update(aside_kind="duplicate version", aside_why="same track as another version on the site", aside_at=now)
            row = {k: v for k, v in row.items() if k in have}
            conn.execute(f"INSERT OR REPLACE INTO set_aside ({','.join(row)}) VALUES ({','.join('?' * len(row))})", list(row.values()))
            conn.execute("DELETE FROM tracks WHERE deezer_id=?", (did,))
        conn.commit(); print("removed", len(drop))


if __name__ == "__main__":
    main()
