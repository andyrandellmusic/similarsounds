"""What the daily catalogue update has pulled in over the last few days.

Usage: python3 scripts/catalogue_report.py [DAYS]     (default 3; get the latest catalogue first:
       git pull, then python -m scripts.catalogue_store fetch - scripts/daily_check.py does both)

Prints, for each daily run in the window: tracks added, removed (not house / duplicate versions) and the
catalogue size; then the new tracks by sub-genre, release age and label, the newest releases, and any
warnings worth a look (future release dates, titles that suggest non-house edits, missing keys).
"""
import json, sqlite3, sys, os
from datetime import date, timedelta

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
DB = os.path.join(os.path.dirname(__file__), "..", "data", "catalogue.db")
since = (date.today() - timedelta(days=DAYS - 1)).isoformat()
db = sqlite3.connect(DB)
q = lambda sql, *a: db.execute(sql, a).fetchall()


print(f"Catalogue now: {q('select count(*) from tracks')[0][0]:,} tracks\n")
# catalogue size after each published run (written by scripts/catalogue_store.py publish)
from datetime import datetime
from zoneinfo import ZoneInfo
log_file = os.path.join(os.path.dirname(__file__), "..", "data", "catalogue_runs.json")
log = json.load(open(log_file)) if os.path.exists(log_file) else []
runs = [(log[i - 1]["tracks"] if i else None, e) for i, e in enumerate(log) if e["at"][:10] >= since]
print("Daily runs (UK time):")
for before, e in runs:
    after = e["tracks"]
    t = datetime.fromisoformat(e["at"].replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/London"))
    when, day = t.strftime("%a %d %b %H:%M"), e["at"][:10]
    added = q("select count(*) from tracks where substr(added_at,1,10)=?", day)[0][0]
    gone = dict(q("select aside_kind, count(*) from set_aside where substr(aside_at,1,10)=? group by aside_kind", day))
    net = f"{after - before:+,}" if before is not None and after is not None else "?"
    print(f"  {when}: +{added} added, -{gone.get('not house', 0)} not house, -{gone.get('duplicate version', 0)} duplicate versions"
          f" -> {after:,} tracks ({net})")
if not runs:
    print("  none found - check the Actions tab on GitHub")

new = f"added_at >= '{since}'"
print(f"\nNew tracks since {since}: {q(f'select count(*) from tracks where {new}')[0][0]:,}"
      f" from {q(f'select count(distinct artist) from tracks where {new}')[0][0]} artists,"
      f" {q(f'select count(distinct label) from tracks where {new}')[0][0]} labels")
print("By sub-genre:  " + ", ".join(f"{s} {n}" for s, n in q(f"select style, count(*) n from tracks where {new} group by style order by n desc")))
ages = q(f"""select case when release_date > date('now') then 'not out yet'
                         when release_date >= date('now','-7 day') then 'this week'
                         when release_date >= date('now','-30 day') then 'this month'
                         when release_date >= date('now','-90 day') then '1-3 months' else 'older' end a, count(*)
             from tracks where {new} group by a order by 2 desc""")
print("By release:    " + ", ".join(f"{a} {n}" for a, n in ages))
print("Top labels:    " + ", ".join(f"{l} {n}" for l, n in q(f"select label, count(*) n from tracks where {new} group by label order by n desc limit 6")))

print("\nNewest releases:")
for t, a, s, c, b, d in q(f"select title, artist, style, camelot, round(bpm), release_date from tracks where {new} and release_date <= date('now') order by release_date desc limit 8"):
    print(f"  {d}  {a} - {t}  ({s}, {c}, {int(b or 0)} BPM)")

warn = []
fut = q(f"select count(*) from tracks where {new} and release_date > date('now')")[0][0]
if fut: warn.append(f"{fut} tracks have a release date in the future (pre-orders)")
odd = q(f"""select artist || ' - ' || title from tracks where {new} and (lower(title) like '%slowed%' or lower(title) like '%sped up%'
            or lower(title) like '%nightcore%' or lower(title) like '%phonk%' or lower(title) like '%brazilian funk%')""")
if odd: warn.append(f"{len(odd)} titles look like non-house edits: " + "; ".join(r[0] for r in odd[:5]))
nokey = q(f"select count(*) from tracks where {new} and (key is null or key = '')")[0][0]
if nokey: warn.append(f"{nokey} new tracks have no key")
dups = q("""select count(*) from (select lower(artist), lower(replace(replace(title,' (Extended Mix)',''),' (Original Mix)','')), count(*) c
            from tracks group by 1, 2 having c > 1)""")[0][0]
if dups: warn.append(f"{dups} songs appear more than once")
print("\nWorth a look:" if warn else "\nNothing odd spotted.")
for w in warn:
    print("  - " + w)
