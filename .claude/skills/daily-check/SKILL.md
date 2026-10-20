---
name: daily-check
description: Boss's SimilarSounds daily check in one go - is the site up and on the latest version, did the 6am track pull run, what music it pulled in over the last few days (added, removed, sub-genres, labels, newest, anything odd), and what's new in his Gmail that matters. Use when Boss asks to check the site, check the music/tracks pulled in, check his emails, "do the daily check", or anything like "what's happened since yesterday".
---

# Daily check (keep it cheap: one script, one inbox read)

## 1. Site + 6am track pull + music pulled in — one command

```
python3 scripts/daily_check.py 3
```
(Use another number of days if Boss asks, e.g. `7` for a week. The script does its own `git pull`.)

It prints: site up / speed / latest version live; the last few 6am runs and whether they succeeded;
then the catalogue report (added / not house / duplicate versions per day, total, sub-genres, release
freshness, top labels, newest releases, and "Worth a look" warnings).

Don't re-check any of this by hand or in the browser unless the script reports a problem.

## 2. Emails — read the inbox list once (Claude in Chrome)

- Load the Chrome tools in one ToolSearch call (tabs_context_mcp, navigate, get_page_text).
- Find the Gmail tab with tabs_context_mcp (or open a new tab) and navigate it to
  `https://mail.google.com/mail/u/0/#inbox`, then `get_page_text` with `max_chars: 5000`. That one read is enough.
- Only open an email if it's a real reply from a person or company Boss is dealing with (Traxsource, Bandcamp,
  Beatport, YouTube, Discogs, Render, GitHub failures, Google Search Console problems) and the preview doesn't
  say enough.
- Ignore promotions, newsletters and routine Google security / sign-in notices (mention only if unexpected).
- Never reply, send, delete or change anything in Gmail without Boss saying so; draft replies and show him first.

## 3. Report to Boss — short, plain English

1. **Site:** up / on latest version (one line; detail only if something's wrong).
2. **6am track pull:** ran each day? (one line)
3. **Music pulled in:** a small table per day (added, removed not house, removed duplicates, total), then
   sub-genres, how fresh, top labels, 3-4 newest tracks.
4. **Worth a look:** anything from the script's warnings, with a yes/no offer to fix it.
5. **Emails:** only the ones that matter, one line each, with any action needed.

Then stop. Don't fix anything as part of the check; offer the fix and wait for Boss's go-ahead.
