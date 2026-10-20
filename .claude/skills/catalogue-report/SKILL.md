---
name: catalogue-report
description: Report what the SimilarSounds daily catalogue update has pulled into the site over the last few days (tracks added, non-house and duplicate versions removed, catalogue size, sub-genres, labels, newest releases, anything odd). Use when Boss asks what music/tracks the site has pulled in, what the daily update added, how the catalogue is growing, or to check the 6am track pull.
---

# Catalogue report

The daily GitHub Actions job (`.github/workflows/daily-catalogue.yml`) runs at 6am UK time, adds new house
releases to `data/catalogue.db`, removes non-house tracks and duplicate versions (kept in the `set_aside`
table), commits the database, and Render redeploys the site.

## Steps

1. Get the latest catalogue (the daily job commits it): `git pull --rebase --autostash`
2. Run the report for the window asked for (default 3 days):
   `python3 scripts/catalogue_report.py 3`
3. Tell Boss in plain English, short:
   - tracks added each day, and how many were removed as not house / duplicate versions
   - the catalogue size now and the growth over the window
   - the sub-genre split, how fresh the releases are, the top labels, and a few of the newest releases
   - anything under "Worth a look" (future release dates, slowed / sped-up / phonk edits that slipped in,
     missing keys, duplicates), saying whether it needs fixing
4. If no daily run shows up for a day, check the Actions runs:
   `curl -s "https://api.github.com/repos/andyrandellmusic/similarsounds/actions/workflows/daily-catalogue.yml/runs?per_page=5"`
   and say which run failed or didn't start.

Don't change the catalogue as part of the report; offer fixes (e.g. setting aside odd edits) and wait for Boss's go-ahead.
