"""Public "What's in the database" page (/database) and honest comparison pages (/vs/...)."""

import json
from collections import Counter
from datetime import date, timedelta
from html import escape
from statistics import median

from app.pages import SITE, camelot_color, page, style_path

CHECKED = "October 2026"   # when the competitor details below were last checked


# ---------- /database
def database_page(index) -> str:
    rows = index.rows
    today = date.today()
    total = len(rows)

    def age(r):
        try:
            return (today - date.fromisoformat((r["release_date"] or "")[:10])).days
        except ValueError:
            return None

    ages = [a for a in (age(r) for r in rows) if a is not None]
    fresh = {d: sum(1 for a in ages if a <= d) for d in (7, 30, 90, 365)}
    styles = Counter(r["style"] for r in rows if r["style"])
    labels = {r["label"] for r in rows if r.get("label")}
    artists = {(r["artist"] or "").split(",")[0].strip().lower() for r in rows if r.get("artist")}
    top = max(styles.values()) if styles else 1

    style_rows = []
    for s, n in styles.most_common():
        bpms = [r["bpm"] for r in rows if r["style"] == s and r["bpm"]]
        new = sum(1 for r in rows if r["style"] == s and (age(r) or 9999) <= 90)
        style_rows.append(
            f'<tr><td><a href="{style_path(s)}">{escape(s)}</a></td>'
            f'<td class="bar-cell"><span class="bar" style="width:{n / top * 100:.0f}%"></span></td>'
            f'<td class="num">{n:,}</td><td class="num">{new:,}</td><td class="num">{round(median(bpms)) if bpms else "–"}</td></tr>')

    keys = Counter(r["camelot"] for r in rows if r.get("camelot"))
    key_chips = "".join(
        f'<span class="kchip" style="background:{camelot_color(k)}" title="{n:,} tracks">{escape(k)} <b>{n:,}</b></span>'
        for k, n in sorted(keys.items(), key=lambda kv: (int(kv[0][:-1]), kv[0][-1])))
    top_labels = Counter(r["label"] for r in rows if r.get("label")).most_common(15)
    label_list = "".join(f"<li>{escape(l)} <span>{n}</span></li>" for l, n in top_labels)

    body = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> / Database</nav>
  <h1>What's in the database</h1>
  <p class="lead">SimilarSounds covers house music only, and it's built for new releases. Here's exactly what you're
  searching, so you know what's well covered. Updated every day.</p>
  <div class="stat-grid">
    <div><b>{total:,}</b><span>house tracks</span></div>
    <div><b>{fresh[7]:,}</b><span>released in the last 7 days</span></div>
    <div><b>{fresh[30]:,}</b><span>in the last 30 days</span></div>
    <div><b>{fresh[365]:,}</b><span>in the last 12 months</span></div>
    <div><b>{len(labels):,}</b><span>record labels</span></div>
    <div><b>{len(artists):,}</b><span>artists</span></div>
  </div>
  <h2>Tracks by style</h2>
  <div class="tbl"><table class="db">
    <thead><tr><th>Style</th><th></th><th class="num">Tracks</th><th class="num">Last 3 months</th><th class="num">Typical BPM</th></tr></thead>
    <tbody>{"".join(style_rows)}</tbody></table></div>
  <h2>Tracks by key</h2>
  <p class="muted">Every track is analysed for its key, shown in <a href="/guides/camelot-wheel">Camelot</a>.</p>
  <div class="kchips">{key_chips}</div>
  <h2>Labels that come up most</h2>
  <ul class="labels">{label_list}</ul>
  <h2>How it's built</h2>
  <ul class="steps">
    <li>New house releases are added every morning, from about 200 house labels, the artists already in the catalogue and genre playlists.</li>
    <li>Every track is analysed from its 30-second preview for its sound, key, BPM and energy.</li>
    <li>Anything that doesn't sound like house (or isn't at house tempo) is removed automatically.</li>
    <li>We don't host or store any audio: previews play from Deezer, and every track links to Beatport, SoundCloud and YouTube.</li>
  </ul>
  <p class="guide-cta"><a class="btn" href="/">Search it: paste a track and get house music that mixes with it</a></p>"""
    return page(f"What's in the SimilarSounds database: {total:,} house tracks | SimilarSounds",
                f"{total:,} house tracks, {fresh[30]:,} released in the last 30 days. See the catalogue by style, key and label, updated daily.",
                "/database", body)


# ---------- /vs comparison pages
YES, NO, PART = '<span class="y">✓</span>', '<span class="n">✗</span>', '<span class="p">~</span>'

COMPARISONS = {
    "digdeeper": {
        "name": "DigDeeper",
        "url": "https://digdeeper.fm",
        "title": "SimilarSounds vs DigDeeper: which is better for DJs?",
        "description": "SimilarSounds vs DigDeeper compared: sound matching, key and BPM mixing, set building, music coverage and price.",
        "intro": "DigDeeper and SimilarSounds both find tracks by how they actually sound, not by genre tags. The difference is what happens next: SimilarSounds also checks whether each match will mix with your track, and helps you build the set.",
        "rows": [
            ("Finds tracks that sound like yours", YES, YES),
            ("Checks key compatibility for every match (Camelot)", YES, NO),
            ("Shows BPM and energy for every match", YES, PART),
            ("Green / amber / red \"will it mix\" for every match", YES, NO),
            ("Set builder that checks every transition and orders the set", YES, NO),
            ("Focused on new releases (newest first)", YES, PART),
            ("Genres covered", "House only (deep, tech, minimal, disco)", "Dozens of genres"),
            ("Catalogue size", "Thousands of house tracks, growing daily", "Millions of tracks"),
            ("Paste YouTube, SoundCloud or Bandcamp links", YES, YES),
            ("Price", "Free (free account adds more searches)", "Free tier, Pro from €5.49/month"),
        ],
        "pick_us": "You play house and want to know what will actually mix: key, tempo and energy checked for every match, and a set builder that flags clashes before you play.",
        "pick_them": "You dig across many genres beyond house, or want the biggest possible catalogue to search.",
        "faq": [
            ("Is SimilarSounds a DigDeeper alternative?", "Yes. Both find tracks by sound. SimilarSounds is free, focuses on house music and new releases, and checks key, BPM and energy so you can see what will mix."),
            ("Does DigDeeper check if tracks are in key?", f"As of {CHECKED}, DigDeeper ranks tracks by how similar they sound. SimilarSounds also checks every match's key against your track using the Camelot wheel."),
        ],
    },
    "tunebat": {
        "name": "Tunebat",
        "url": "https://tunebat.com",
        "title": "SimilarSounds vs Tunebat: finding tracks that mix",
        "description": "SimilarSounds vs Tunebat compared: key and BPM data, finding tracks that sound alike, house music focus and set building.",
        "intro": "Tunebat is a huge key and BPM database for almost any song, plus audio tools. SimilarSounds is built for one job: finding new house tracks that sound like yours and mix with it.",
        "rows": [
            ("Key and BPM for tracks", YES, YES),
            ("Finds tracks that sound like yours (listens to the audio)", YES, PART),
            ("Green / amber / red \"will it mix\" for every match", YES, NO),
            ("Energy score for every track", YES, PART),
            ("Set builder that checks every transition and orders the set", YES, NO),
            ("Newest house releases first", YES, NO),
            ("Genres covered", "House only", "All music"),
            ("Extra audio tools (vocal remover, mastering…)", NO, YES),
            ("Price", "Free (free account adds more searches)", "Free, with paid tools"),
        ],
        "pick_us": "You're a house DJ looking for new tracks that sound like the one you're playing and mix with it, ready to drop into a set.",
        "pick_them": "You need the key and BPM of any song in any genre, or audio tools like a vocal remover.",
        "faq": [
            ("Is SimilarSounds like Tunebat?", "Both show key and BPM. SimilarSounds goes further for house DJs: it listens to the audio to find tracks that sound alike, and checks key, tempo and energy so you can see what will mix."),
            ("Which is better for finding songs that mix?", "For house music, SimilarSounds: every match is marked green, amber or red for how well it mixes with your track, and the set builder checks every transition."),
        ],
    },
    "mixed-in-key": {
        "name": "Mixed In Key",
        "url": "https://mixedinkey.com",
        "title": "SimilarSounds vs Mixed In Key: discovering vs analysing",
        "description": "SimilarSounds vs Mixed In Key compared: finding new music versus analysing the music you own, key and energy, and price.",
        "intro": "Mixed In Key is paid desktop software that analyses the music you already own: key, energy and mixing suggestions inside your collection. SimilarSounds helps you find new music to add to it. Many DJs will use both.",
        "rows": [
            ("Analyses the key and energy of tracks", YES, YES),
            ("Finds new music you don't own yet", YES, NO),
            ("Finds tracks that sound like yours", YES, NO),
            ("Mixing suggestions in key", YES, YES),
            ("Works with your own music files", NO, YES),
            ("Set builder that checks every transition", YES, PART),
            ("Runs in the browser, nothing to install", YES, NO),
            ("Price", "Free", "Paid software"),
        ],
        "pick_us": "You want to discover new house releases that fit your sound and see straight away whether they'll mix.",
        "pick_them": "You want to analyse and organise the files already in your collection, inside your DJ software.",
        "faq": [
            ("Is SimilarSounds a free Mixed In Key alternative?", "For discovering music, yes: it's free and shows key, BPM and energy for every match. Mixed In Key analyses files you already own, which SimilarSounds doesn't do."),
            ("Can I use SimilarSounds with Mixed In Key?", "Yes. Find new tracks on SimilarSounds, buy them, then analyse them in Mixed In Key alongside the rest of your collection."),
        ],
    },
}


def _cell(v):
    return v if v.startswith("<span") else escape(v)


def vs_page(slug: str) -> str | None:
    c = COMPARISONS.get(slug)
    if not c:
        return None
    rows = "".join(f"<tr><td>{escape(f)}</td><td>{_cell(a)}</td><td>{_cell(b)}</td></tr>" for f, a, b in c["rows"])
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in c["faq"])
    others = "".join(f'<li><a href="/vs/{s}">SimilarSounds vs {escape(o["name"])}</a></li>' for s, o in COMPARISONS.items() if s != slug)
    jsonld = '<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in c["faq"]]},
        ensure_ascii=False) + "</script>"
    body = f"""<article class="guide">
  <div class="crumbs"><a href="/vs">Comparisons</a> / {escape(c["name"])}</div>
  <h1>{escape(c["title"])}</h1>
  <p class="lead">{escape(c["intro"])}</p>
  <div class="tbl"><table class="vs">
    <thead><tr><th></th><th>SimilarSounds</th><th>{escape(c["name"])}</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
  <p class="muted">✓ yes &nbsp; ~ partly &nbsp; ✗ no. {escape(c["name"])} details checked on <a href="{c["url"]}" rel="nofollow noopener" target="_blank">their website</a> in {CHECKED}; things change, so check there for the latest.</p>
  <h2>Choose SimilarSounds if…</h2><p>{escape(c["pick_us"])}</p>
  <h2>Choose {escape(c["name"])} if…</h2><p>{escape(c["pick_them"])}</p>
  <p class="guide-cta"><a class="btn" href="/">Try SimilarSounds free: paste a track</a></p>
  <h2>Questions</h2><div class="faq">{faq}</div>
  <h2>More comparisons</h2><ul class="more">{others}</ul>
</article>"""
    return page(f"{c['title']} | SimilarSounds", c["description"], f"/vs/{slug}", body, jsonld=jsonld)


def vs_hub() -> str:
    items = "".join(f'<li><a class="guide-card" href="/vs/{s}"><b>SimilarSounds vs {escape(c["name"])}</b>'
                    f'<span>{escape(c["description"])}</span></a></li>' for s, c in COMPARISONS.items())
    body = f"""<div class="crumbs">Comparisons</div>
<h1>How SimilarSounds compares</h1>
<p class="lead">Honest side-by-side comparisons with other tools DJs use to find and mix music.</p>
<ul class="guide-list">{items}</ul>"""
    return page("SimilarSounds compared: DigDeeper, Tunebat, Mixed In Key | SimilarSounds",
                "How SimilarSounds compares with DigDeeper, Tunebat and Mixed In Key for finding house tracks that mix.",
                "/vs", body)


def sitemap_urls() -> list[str]:
    return [f"{SITE}/database", f"{SITE}/vs"] + [f"{SITE}/vs/{s}" for s in COMPARISONS]
