"""Public, crawlable pages: one per catalogue track ("Tracks similar to X by Y"), plus browse
pages by sub-genre and BPM, a sitemap and robots.txt. Plain server-rendered HTML so search
engines can read them; the interactive app stays at /."""

import re
import unicodedata
from collections import Counter
from datetime import date
from html import escape

from app.artists import main_artist

SITE = "https://www.similarsounds.com"
BPM_WINDOWS = [(lo, lo + 2) for lo in range(110, 136, 2)]   # 110-112 … 134-136

LOGO = ('<svg viewBox="16 39 64 42" aria-hidden="true"><path d="M37 39 L58 60 L37 81 L16 60 Z" fill="#f2f2f5"/>'
        '<path d="M59 43.95 L75.05 60 L59 76.05 L42.95 60 Z" fill="none" stroke="#0b0b0f" stroke-width="12"/>'
        '<path d="M59 43.95 L75.05 60 L59 76.05 L42.95 60 Z" fill="none" stroke="#c6ff3d" stroke-width="7"/></svg>')


def slugify(text: str, limit: int = 70) -> str:
    s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:limit].rstrip("-") or "track"


def track_path(r: dict) -> str:
    return f"/similar-to/{slugify(r['artist'] + ' ' + r['title'])}-{r['deezer_id']}"


def style_path(style: str) -> str:
    return f"/similar-to/genre/{slugify(style)}"


# ---------- mixing rules (same as the app)
def key_mix(a: str, b: str) -> tuple[int, str]:
    na, la, nb, lb = int(a[:-1]), a[-1], int(b[:-1]), b[-1]
    up = (nb - na) % 12
    step = min(up, 12 - up)
    if la == lb and step == 0: return 2, "same key"
    if la == lb and step == 1: return 2, "adjacent key"
    if la != lb and step == 0: return 2, "relative major/minor"
    if la == lb and step == 2: return 1, "energy-boost key change (+2)" if up == 2 else "key change (−2)"
    if la != lb and step == 1: return 1, "diagonal key change"
    return 0, "key clash"


def mix(q: dict, t: dict) -> tuple[str, str]:
    k = key_mix(q["camelot"], t["camelot"])
    d = abs(t["bpm"] - q["bpm"])
    b = 2 if d <= 3 else 1 if d <= 6 else 0
    e = abs(int(t["energy"]) - int(q["energy"]))
    en = 2 if e <= 2 else 1 if e == 3 else 0
    score = min(k[0], b, en)
    return ["bad", "ok", "good"][score], ["Will clash", "Workable", "Mixes well"][score]


def camelot_color(code: str) -> str:
    n, minor = int(code[:-1]), code.endswith("A")
    return f"hsl({(n - 1) * 30} 90% {74 if minor else 82}%)"


def ago(days: int) -> str:
    if days < 1: return "today"
    if days < 31: return f"{days}d ago"
    if days < 365: return f"{round(days / 30)}mo ago"
    return f"{days / 365:.1f}y ago"


def summary(q: dict, rs: list[dict]) -> str:
    n = len(rs)
    if not n:
        return ""
    out = [f'We compared the sound of "{q["title"]}" by {q["artist"]} with every track in our house catalogue.']
    out.append(f"The closest match sounds {max(t['similarity'] for t in rs)}% like it.")
    bpms = sorted(t["bpm"] for t in rs)
    lo, hi = round(bpms[int(n * 0.1)]), round(bpms[min(n - 1, int(n * 0.9))])
    out.append(f"Most sit around {lo} BPM." if lo == hi else f"Most sit between {lo} and {hi} BPM.")
    in_key = sum(1 for t in rs if key_mix(q["camelot"], t["camelot"])[0] == 2)
    if in_key:
        out.append(f"{in_key} of {n} are in a key that mixes with {q['camelot']}.")
    styles = [s for s, _ in Counter(t["style"] for t in rs if t["style"]).most_common(2)]
    if styles:
        out.append(f"The sound leans {' and '.join(styles)}.")
    labels = [l for l, c in Counter(t["label"] for t in rs if t["label"]).most_common(3) if c >= 2]
    if labels:
        out.append(f"Releases on {', '.join(labels)} come up more than once.")
    return " ".join(out)


# ---------- page shell
def page(title: str, description: str, path: str, body: str, *, jsonld: str = "") -> str:
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/static/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/static/apple-touch-icon.png">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/pages.css?v=4">
{jsonld}
</head>
<body>
<div class="wrap">
  <header class="top">
    <a class="brand" href="/" aria-label="SimilarSounds - home">{LOGO}Similar<span>Sounds</span></a>
    <a class="cta" href="/">Find matches for any track</a>
  </header>
  <main>
{body}
  </main>
  <footer>
    <nav aria-label="Browse"><a href="/">Home</a><a href="/guides">DJ guides</a><a href="/similar-to">All similar-track pages</a><a href="/artists-like">Artists like…</a><a href="/privacy">Privacy</a><a href="/cookies">Cookies</a><a href="/terms">Terms</a></nav>
    <p>Previews and track details by Deezer. Key, BPM and energy are estimates from 30-second previews. Not affiliated with Deezer, SoundCloud, YouTube or Beatport.</p>
  </footer>
</div>
</body>
</html>"""


def chips(t: dict, match: int | None = None) -> str:
    return (f'<span class="chip cam" style="background:{camelot_color(t["camelot"])}" title="{escape(t["key"] or "")}">{escape(t["camelot"])}</span>'
            + (f'<span class="chip match">{match}% match</span>' if match is not None else '')
            + f'<span class="chip">{round(t["bpm"])} BPM</span>'
            f'<span class="chip">Energy {int(t["energy"])}/10</span>')


def track_list(rows: list[dict], today: date) -> str:
    items = []
    for r in rows:
        age = (today - date.fromisoformat(r["release_date"])).days if r["release_date"] else None
        meta = " · ".join(escape(x) for x in [r["artist"], r["label"] or "", r["style"] or ""] if x)
        items.append(f"""<li><a class="row" href="{track_path(r)}">
      <img src="{escape(r['cover'] or '')}" alt="" loading="lazy" width="56" height="56">
      <span class="meta"><span class="t">{escape(r['title'])}</span><span class="a">{meta}</span>
      <span class="chips">{chips(r)}{f'<span class="chip">{ago(age)}</span>' if age is not None else ''}</span></span>
    </a></li>""")
    return f'<ol class="list plain">{"".join(items)}</ol>'


# ---------- pages
def track_page(index, q: dict, results: list[dict], style: str | None) -> str:
    sound = index.describe(q["energy_raw"], q["embedding"])
    today = date.today()
    r = q
    path = track_path(r)
    rows = []
    for i, t in enumerate(results, 1):
        cls, label = mix(q, t)
        age = t["age_days"]
        meta = " · ".join(escape(x) for x in [t["artist"], t["label"] or "", t["style"] or ""] if x)
        rows.append(f"""<li><a class="row" href="{track_path(t)}">
      <span class="n">{i}</span>
      <img src="{escape(t['cover'] or '')}" alt="" loading="lazy" width="56" height="56">
      <span class="meta"><span class="t">{escape(t['title'])}</span><span class="a">{meta}</span>
      <span class="chips">{chips(t, t['similarity'])}<span class="chip">{ago(age)}</span></span>
      <span class="mix {cls}"><i></i>{label}</span></span>
    </a></li>""")
    title = f"Tracks similar to {r['title']} by {r['artist']} | SimilarSounds"
    desc = (f"{len(results)} new house tracks that sound like {r['title']} by {r['artist']} "
            f"({r['camelot']}, {round(r['bpm'])} BPM), with key, BPM and energy for mixing.")
    crumbs = f'<a href="/">Home</a> / <a href="/similar-to">Similar tracks</a>'
    if style:
        crumbs += f' / <a href="{style_path(style)}">{escape(style)}</a>'
    related = "".join(f'<li><a href="{track_path(t)}">Tracks similar to {escape(t["title"])} by {escape(t["artist"])}</a></li>'
                      for t in results[:10])
    meta = " · ".join(escape(x) for x in [r["label"] or "", style or "", (r["release_date"] or "")[:4]] if x)
    body = f"""<nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav>
  <h1>Tracks similar to {escape(r['title'])} <span>by {escape(r['artist'])}</span></h1>
  <section class="ref">
    <img src="{escape(r['cover'] or '')}" alt="" width="96" height="96">
    <div><div class="label">Reference track</div>
      <div class="t">{escape(r['title'])}</div><div class="a">{escape(r['artist'])}{' · ' + meta if meta else ''}</div>
      <div class="chips">{chips(r)}</div>
      {f'<div class="sound"><span>Sound</span> {" · ".join(escape(w) for w in sound)}</div>' if sound else ''}
      <a class="btn" href="/?t={r['deezer_id']}">▶ Play previews &amp; build a set</a>
    </div>
  </section>
  <p class="summary">{escape(summary(q, results))}</p>
  <h2>{len(results)} closest matches</h2>
  <ol class="list">{"".join(rows)}</ol>
  <p class="more"><a class="btn ghost" href="/?t={r['deezer_id']}">Open in SimilarSounds: filters, previews and more matches <i class="g-arr">›</i></a></p>
  <p class="more"><a class="btn ghost" href="{artist_path(main_artist(r['artist']))}">Artists that sound like {escape(main_artist(r['artist']))} <i class="g-arr">›</i></a></p>
  <h2>Related pages</h2>
  <ul class="related">{related}</ul>
  <p class="note">Matched on sound, key, BPM and energy from 30-second previews on {today.strftime('%-d %B %Y')}. Rankings update as new releases are added.</p>"""
    return page(title, desc, path, body)


def hub_page(index) -> str:
    rows = index.rows
    styles = Counter(r["style"] for r in rows if r["style"])
    today = date.today()
    newest = sorted(rows, key=lambda r: r["release_date"] or "", reverse=True)[:60]
    bpm_counts = [(lo, hi, int(((index.bpm >= lo) & (index.bpm < hi)).sum())) for lo, hi in BPM_WINDOWS]
    style_links = "".join(f'<a class="pill" href="{style_path(s)}">{escape(s)} <b>{c}</b></a>' for s, c in sorted(styles.items()))
    bpm_links = "".join(f'<a class="pill" href="/similar-to/bpm/{lo}-{hi}">{lo}-{hi} BPM <b>{c}</b></a>' for lo, hi, c in bpm_counts if c)
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Similar tracks</nav>
  <h1>Similar house tracks</h1>
  <p class="summary">Every page below starts from one house track and lists the tracks that sound closest to it, with key, BPM and energy so you can see what mixes. {len(rows):,} tracks, newest releases first.</p>
  <h2>By sub-genre</h2><div class="pills">{style_links}</div>
  <h2>By BPM</h2><div class="pills">{bpm_links}</div>
  <h2>Newest releases</h2>{track_list(newest, today)}"""
    return page("Similar house tracks by sub-genre and BPM | SimilarSounds",
                "Find house tracks that sound alike: browse by sub-genre or BPM, with key, BPM and energy for mixing.",
                "/similar-to", body)


def list_page(index, rows: list[dict], heading: str, intro: str, path: str, crumb: str, page_no: int) -> str:
    per = 60
    total = len(rows)
    pages = max(1, -(-total // per))
    page_no = min(max(1, page_no), pages)
    chunk = rows[(page_no - 1) * per: page_no * per]
    nav = ""
    if pages > 1:
        links = "".join(f'<a class="pill{" on" if p == page_no else ""}" href="{path}{"" if p == 1 else f"?page={p}"}">{p}</a>'
                        for p in range(1, pages + 1))
        nav = f'<nav class="pills pager" aria-label="Pages">{links}</nav>'
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/similar-to">Similar tracks</a> / {escape(crumb)}</nav>
  <h1>{escape(heading)}</h1>
  <p class="summary">{escape(intro)}</p>
  {track_list(chunk, date.today())}{nav}"""
    suffix = f" (page {page_no})" if page_no > 1 else ""
    return page(f"{heading}{suffix} | SimilarSounds", intro, path + (f"?page={page_no}" if page_no > 1 else ""), body)


def style_page(index, style: str, page_no: int) -> str:
    rows = sorted((r for r in index.rows if r["style"] == style), key=lambda r: r["release_date"] or "", reverse=True)
    return list_page(index, rows, f"Similar {style} tracks",
                     f"{len(rows):,} {style} tracks, newest first. Open any track to see what sounds like it and what mixes with it.",
                     style_path(style), style, page_no)


def bpm_page(index, lo: int, hi: int, page_no: int) -> str:
    rows = sorted((r for r in index.rows if lo <= r["bpm"] < hi), key=lambda r: r["release_date"] or "", reverse=True)
    return list_page(index, rows, f"House tracks at {lo}-{hi} BPM",
                     f"{len(rows):,} house tracks between {lo} and {hi} BPM, newest first. Open any track to find similar tracks that mix with it.",
                     f"/similar-to/bpm/{lo}-{hi}", f"{lo}-{hi} BPM", page_no)


def artist_path(name: str) -> str:
    return f"/artists-like/{slugify(name)}"


def artist_page(artists, name: str) -> str:
    like = artists.like_artist(name, k=12)
    own = sorted((artists.index.rows[i] for i in artists.rows_of[name]), key=lambda r: r["release_date"] or "", reverse=True)
    items = []
    for a in like:
        ex = a["example"]
        items.append(f"""<li><a class="row" href="{artist_path(a['name'])}">
      <img src="{escape(ex['cover'] or '')}" alt="" loading="lazy" width="56" height="56">
      <span class="meta"><span class="t">{escape(a['name'])}</span>
      <span class="a">For example: {escape(ex['title'])}{' · ' + escape(ex['style']) if ex['style'] else ''}</span>
      <span class="chips"><span class="chip match">{a['similarity']}% alike</span><span class="chip">{a['tracks']} track{'s' if a['tracks'] != 1 else ''}</span></span></span>
    </a></li>""")
    names = ", ".join(a["name"] for a in like[:3])
    desc = f"House artists who sound like {name}" + (f", such as {names}" if names else "") + ", measured from the music itself."
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/artists-like">Artists like…</a> / {escape(name)}</nav>
  <h1>Artists that sound like {escape(name)}</h1>
  <p class="summary">We averaged the sound of {name}'s tracks in our catalogue and compared it with every other house artist. These sound closest. Tap an artist to see who sounds like them, or open a track below to find tracks that mix with it.</p>
  <ol class="list">{"".join(items)}</ol>
  <h2>{escape(name)} tracks in our catalogue</h2>{track_list(own[:30], date.today())}"""
    return page(f"Artists like {name} | SimilarSounds", desc, artist_path(name), body)


def artists_hub(artists) -> str:
    links = "".join(f'<a class="pill" href="{artist_path(n)}">{escape(n)}</a>' for n in artists.names)
    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Artists like…</nav>
  <h1>Artists that sound alike</h1>
  <p class="summary">Pick an artist to see the house artists who sound most like them, measured from the music itself rather than tags or listener stats. {len(artists.names):,} artists.</p>
  <div class="pills">{links}</div>"""
    return page("House artists that sound alike | SimilarSounds",
                "Find house artists who sound like the ones you love, measured from the music itself.", "/artists-like", body)


def sitemap(index, artists=None) -> str:
    today = date.today().isoformat()
    urls = [f"{SITE}/", f"{SITE}/similar-to"]
    urls += [SITE + style_path(s) for s in sorted({r["style"] for r in index.rows if r["style"]})]
    urls += [f"{SITE}/similar-to/bpm/{lo}-{hi}" for lo, hi in BPM_WINDOWS]
    urls += [SITE + track_path(r) for r in index.rows]
    if artists:
        urls += [f"{SITE}/artists-like"] + [SITE + artist_path(n) for n in artists.names]
    from app import guides
    urls += guides.sitemap_urls()
    body = "".join(f"<url><loc>{escape(u)}</loc><lastmod>{today}</lastmod></url>" for u in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>'


# AI search and assistant crawlers are welcome too (ChatGPT, Claude, Perplexity, Google's AI, Bing/Copilot)
ROBOTS = (
    "User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /stats\n\n"
    + "".join(f"User-agent: {b}\nAllow: /\nDisallow: /api/\nDisallow: /stats\n\n" for b in
              ["OAI-SearchBot", "ChatGPT-User", "GPTBot", "ClaudeBot", "Claude-SearchBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Google-Extended", "Bingbot", "Applebot", "Applebot-Extended"])
    + f"Sitemap: {SITE}/sitemap.xml\n"
)

LLMS = f"""# SimilarSounds

> Free tool for house music DJs: paste any track and get brand-new house releases that sound like it and
> mix with it, matched on sound, musical key (Camelot), BPM and energy, newest releases first.

SimilarSounds ({SITE}) covers house music only: House, Deep House, Tech House, Minimal / Deep Tech and
Funky / Disco House. Around 6,600 releases, updated daily. Every match is marked green (mixes well),
amber (workable) or red (will clash). It also has a free set builder that checks every transition and can
order a set for the smoothest mixes. Free to use; a free account adds more searches.

## Use it
- [Find house tracks that mix with any track]({SITE}/): paste a YouTube, SoundCloud, Beatport, Bandcamp or Deezer link, or type an artist
- [Browse similar-track pages by genre and BPM]({SITE}/similar-to)
- [Artists that sound like…]({SITE}/artists-like)

## Guides
- [The Camelot wheel explained: how to mix in key]({SITE}/guides/camelot-wheel)
- [How to find songs that mix well together]({SITE}/guides/songs-that-mix-together)
- [House music BPM guide]({SITE}/guides/house-music-bpm)
- [Deep house vs tech house vs minimal]({SITE}/guides/house-music-styles)
- [How to build a DJ set that flows]({SITE}/guides/dj-set-energy)
- [How to find house tracks similar to a song]({SITE}/guides/find-similar-songs)

## Genres
- [Deep House]({SITE}/similar-to/genre/deep-house)
- [Tech House]({SITE}/similar-to/genre/tech-house)
- [Minimal / Deep Tech]({SITE}/similar-to/genre/minimal-deep-tech)
- [Funky / Disco House]({SITE}/similar-to/genre/funky-disco-house)
- [House]({SITE}/similar-to/genre/house)
"""

INDEXNOW_KEY = "79c46b4c89c7be3d8ddd6e1941d2af93"   # public by design: proves the site's IndexNow submissions
