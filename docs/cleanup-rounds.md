# SimilarSounds whole-site clean-up rounds (28 Oct 2026)

Each round: audit the live site, its data and its jobs; fix the worst problems; re-score; push only if the
score goes up. (The earlier UX rounds are in ux-rounds.md.)

## Rubric (each 0-10, overall = average)

| Area | 10/10 means |
|---|---|
| Bugs | No errors, broken links, 404s or dead buttons; the daily jobs all work |
| Content | Every bit of text and help matches what the site does |
| Catalogue | Only real house tracks, no junk or spam, right details |
| Search & SEO | Google can read every page; no blocked, missing or duplicate pages |
| Speed & bandwidth | Light pages, bots don't burn bandwidth |
| Reliability | No crashes or memory restarts; daily jobs safe and self-healing |
| Mobile & access | Works with thumbs and keyboards, readable |
| Tidiness & security | No leftover code or unused endpoints; nothing exposed or abusable |

## Log

### Baseline: 7.1
Bugs 8 · Content 8 · Catalogue 7.5 · SEO 6.5 · Speed 5 · Reliability 6.5 · Mobile 8.5 · Tidiness 7
- No browser errors in a full search / set / menu run; 40 random sitemap pages all load.
- Google: 848 pages indexed, 14,251 discovered-not-indexed, 10 × 404, 1 blocked by robots, 3 redirects.
- Bandwidth: 7.27 GB this month from ~110 real visitors. Home page is 375 KB uncompressed (98 KB compressed),
  track pages 37 KB (5.7 KB compressed); the request log is mostly SEO crawlers (Semrush) reading thousands
  of artist / track pages.
- Daily pull: Discogs returns nothing on GitHub; new sources were being cut off by the 2,000 limit (fixed
  earlier today: leftovers now carry over). Render restarts after running out of memory several times a week.
- Dead code: the old "Hear the mix" server endpoint (/api/mixinfo, CPU-heavy beat analysis) is unused.

### Round 1: 7.1 → 7.4 (kept)
- SEO-tool crawlers (Semrush, Ahrefs, Majestic, DotBot, BLEX, DataForSEO, Petal, Bytespider and others) are
  told to stay away in robots.txt, and the server answers them with a 37-byte "no" (403) instead of the page
  if they ignore it. Google, Bing, Apple and the AI search bots are still allowed. Tested: Semrush/Ahrefs 403,
  Googlebot/Bingbot/browsers 200.
Bugs 8 · Content 8 · Catalogue 7.5 · SEO 6.5 · Speed 7.5 · Reliability 6.5 · Mobile 8.5 · Tidiness 7

### Round 2: 7.4 → 7.6 (kept)
- Memory (Render restarts at 512 MB; the server sat at ~480 MB): each track's raw sound data is parsed once
  into arrays and the text copies dropped from the in-memory rows (index keeps 101 MB instead of 111 MB), and
  after loading the server hands freed memory back to the system (malloc_trim, Linux only). Preview-clip cache
  40 → 24 clips (~8 MB less).
- Dead code removed: the old "Hear the mix" endpoint /api/mixinfo and its CPU-heavy beat analysis (the decks
  find the beats in the browser now).
Bugs 8 · Content 8 · Catalogue 7.5 · SEO 6.5 · Speed 7.5 · Reliability 7 · Mobile 8.5 · Tidiness 7.5

### Round 3: 7.6 → 7.8 (kept)
- Memory: the server kept up to 2,000 rendered track pages (~37 KB each, ~74 MB) and crawlers filled it fast;
  now the 300 most recent (~11 MB).
- Old pages: tracks taken out by hand (data/removed_tracks.json) are now set aside as "removed by hand", so
  their old pages answer with the friendly "gone" page (410, Google drops them) instead of a bare 404.
  (The 404s in Search Console are tracks deleted by hand before this; they'll drop out on their own.)
Bugs 8.5 · Content 8 · Catalogue 7.5 · SEO 7 · Speed 7.5 · Reliability 7.5 · Mobile 8.5 · Tidiness 7.5
