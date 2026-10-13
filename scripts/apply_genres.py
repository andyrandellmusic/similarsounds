"""Apply eval/results/auto_genres.json to the catalogue: tracks marked 'set aside' move to the
set_aside table (kept, not deleted, never shown on the site, never re-added by the daily update);
kept tracks take their new sub-genre.   .venv/bin/python -m scripts.apply_genres [--dry-run]"""
import json, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def ensure_table(con):
    cols = [r[1] for r in con.execute("PRAGMA table_info(tracks)")]
    con.execute(f"CREATE TABLE IF NOT EXISTS set_aside AS SELECT * FROM tracks WHERE 0")
    have = {r[1] for r in con.execute("PRAGMA table_info(set_aside)")}
    for c, t in (("aside_kind", "TEXT"), ("aside_why", "TEXT"), ("aside_at", "TEXT")):
        if c not in have:
            con.execute(f"ALTER TABLE set_aside ADD COLUMN {c} {t}")
    return cols


def main():
    plan = json.load(open(ROOT / "eval" / "results" / "auto_genres.json"))
    con = sqlite3.connect(ROOT / "data" / "catalogue.db")
    cols = ensure_table(con)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    aside = [p for p in plan if p["action"] == "set aside"]
    moves = [p for p in plan if p["action"] == "keep" and p["style"] != p["site_style"]]
    print(f"setting aside {len(aside)} tracks, changing the sub-genre of {len(moves)}")
    if "--dry-run" in sys.argv:
        return
    cl = ", ".join(cols)
    for p in aside:
        con.execute(f"INSERT OR REPLACE INTO set_aside ({cl}, aside_kind, aside_why, aside_at) "
                    f"SELECT {cl}, ?, ?, ? FROM tracks WHERE deezer_id = ?", (p["kind"], p.get("why"), now, p["id"]))
        con.execute("DELETE FROM tracks WHERE deezer_id = ?", (p["id"],))
    con.executemany("UPDATE tracks SET style = ? WHERE deezer_id = ?", [(p["style"], p["id"]) for p in moves])
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    s = con.execute("SELECT COUNT(*) FROM set_aside").fetchone()[0]
    print(f"done: {n} tracks on the site, {s} set aside")


if __name__ == "__main__":
    main()
