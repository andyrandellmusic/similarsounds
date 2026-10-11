"""Written guides for DJs (/guides): evergreen pages that answer what house DJs search for, and link
into the tool and the similar-track pages. Each guide has an FAQ that Google can show as rich results."""

import json
from html import escape

from app.pages import SITE, page

UPDATED = "2026-10-12"
AUTHOR = "SimilarSounds"

# Camelot code -> musical key
CAMELOT = [
    ("1A", "A♭ minor", "1B", "B major"), ("2A", "E♭ minor", "2B", "F♯ major"), ("3A", "B♭ minor", "3B", "D♭ major"),
    ("4A", "F minor", "4B", "A♭ major"), ("5A", "C minor", "5B", "E♭ major"), ("6A", "G minor", "6B", "B♭ major"),
    ("7A", "D minor", "7B", "F major"), ("8A", "A minor", "8B", "C major"), ("9A", "E minor", "9B", "G major"),
    ("10A", "B minor", "10B", "D major"), ("11A", "F♯ minor", "11B", "A major"), ("12A", "D♭ minor", "12B", "E major"),
]

CTA = ('<p class="guide-cta"><a class="btn" href="/">Try it: paste a track and get house music that mixes with it</a></p>')


def camelot_table() -> str:
    rows = "".join(f"<tr><td><b>{a}</b></td><td>{ak}</td><td><b>{b}</b></td><td>{bk}</td></tr>" for a, ak, b, bk in CAMELOT)
    return ('<div class="tbl"><table><thead><tr><th>Camelot</th><th>Minor key</th><th>Camelot</th><th>Major key</th></tr></thead>'
            f"<tbody>{rows}</tbody></table></div>")


GUIDES = [
    {
        "slug": "camelot-wheel",
        "title": "The Camelot Wheel Explained: How to Mix in Key",
        "short": "The Camelot wheel explained",
        "description": "What the Camelot wheel is, how to read codes like 8A and 9B, and the four key changes that always sound good in a DJ mix. With a full key chart.",
        "intro": "Mixing in key is the difference between a blend that sounds like one record and one that clashes. The Camelot wheel makes it simple: every key gets a number and a letter, and the moves that work are just steps around the wheel.",
        "body": f"""
<h2>What the Camelot wheel is</h2>
<p>Music has 24 keys: 12 minor and 12 major. Remembering which ones sound good together is hard, so DJs use the <b>Camelot wheel</b>, a circle where every key gets a code from <b>1 to 12</b> plus a letter: <b>A for minor</b>, <b>B for major</b>. Keys that sit next to each other on the wheel share most of their notes, which is why they blend smoothly.</p>
<p>Most DJ software (Rekordbox, Serato, Traktor, Engine DJ) can show keys in Camelot, and so does SimilarSounds: every track has a coloured key chip like <b>8A</b>.</p>

<h2>The four moves that always work</h2>
<ul class="steps">
  <li><b>Same code</b> (8A → 8A). Identical key. The safest mix there is.</li>
  <li><b>One step around the wheel</b> (8A → 7A or 9A). Changes one note. Smooth, and the classic way to move a set along.</li>
  <li><b>Switch the letter</b> (8A → 8B). Same notes, but moves between minor and major. 8A to 8B lifts the mood; 8B to 8A darkens it.</li>
  <li><b>Energy boost</b> (8A → 10A, two steps). Riskier, but used on purpose it gives a noticeable lift. Best during a long, sparse blend or a drum-only intro.</li>
</ul>
<p>Anything further away (say 8A → 3A) is likely to clash if both melodies are playing at once. That doesn't mean you can never do it: it just means making the switch over drums, a breakdown or a quick cut instead of a long blend.</p>

<h2>Full Camelot key chart</h2>
<p>Use this to translate keys from Beatport, Spotify or your software into Camelot codes.</p>
{camelot_table()}

<h2>Do you always have to mix in key?</h2>
<p>No. House is drum-led, and plenty of great transitions happen over percussion where key barely matters. But when two tracks with chords, vocals or bass lines overlap for 16 bars or more, being in key is what makes it sound deliberate. Think of key as one of three things to line up, together with <a href="/guides/house-music-bpm">tempo</a> and <a href="/guides/dj-set-energy">energy</a>.</p>

<h2>Watch out for pitch</h2>
<p>Speeding a track up or down also changes its key unless <b>key lock</b> (also called Master Tempo) is on. A change of about <b>6% moves a track by one semitone</b>, which jumps it 7 places around the Camelot wheel. Small tempo changes of 1–2% are fine; for bigger ones, turn key lock on.</p>

<h2>Finding tracks in a compatible key</h2>
<p>Paste any track into <a href="/">SimilarSounds</a> and the matches come back already checked against its key: green means it mixes well, amber is workable, red will clash. The <b>key wheel</b> on the results page lets you tap a key to see only the tracks in it.</p>
""",
        "faq": [
            ("What does 8A mean in DJing?", "8A is a Camelot code. The number (1–12) is the position on the Camelot wheel and the letter shows the scale: A is minor, B is major. 8A is A minor."),
            ("Which keys mix with 8A?", "8A mixes with 8A (same key), 7A and 9A (one step either side) and 8B (its relative major). 10A works as an energy boost."),
            ("Do I have to mix in key?", "Not always. Drum-only blends and quick cuts work in any key. Key matters most when melodies, vocals or bass lines overlap for a long blend."),
            ("Does changing the tempo change the key?", "Yes, unless key lock (Master Tempo) is on. Around 6% faster or slower moves a track by a semitone, which is 7 places on the Camelot wheel."),
        ],
    },
    {
        "slug": "songs-that-mix-together",
        "title": "How to Find Songs That Mix Well Together",
        "short": "How to find songs that mix well together",
        "description": "The four things that make two tracks mix well (sound, key, tempo and energy) and a quick way to find house tracks that blend with the one you're playing.",
        "intro": "Two tracks mix well when they feel like they belong in the same moment. That comes down to four things you can check before you ever touch a fader.",
        "body": """
<h2>1. They sound alike</h2>
<p>The most important thing is the hardest to put in a tag: the <b>sound</b>. Similar drums, similar bass weight, similar groove and atmosphere. A rolling deep house track and a stabby tech house tool can share a key and a tempo and still feel wrong together. Listen for the kick, the bass line and how busy the hats are.</p>

<h2>2. Their keys are compatible</h2>
<p>When melodies overlap, keys need to agree. The easy rule: the same Camelot code, one step either side, or the same number with the other letter. The <a href="/guides/camelot-wheel">Camelot wheel guide</a> explains it in two minutes.</p>

<h2>3. Their tempos are close</h2>
<p>Within about <b>3 BPM</b> is easy to beat-match without anyone noticing. Bigger jumps work too, but you'll be stretching one track a lot, so use key lock and keep the blend short. See typical tempos in the <a href="/guides/house-music-bpm">house music BPM guide</a>.</p>

<h2>4. The energy goes where you want</h2>
<p>A track can match on everything above and still kill the room if it drops the energy at the wrong time. Decide whether the next track should hold the level, lift it or give people a breather. More on that in <a href="/guides/dj-set-energy">how to build a set that flows</a>.</p>

<h2>The quick way: let SimilarSounds check all four</h2>
<ol class="steps">
  <li>Go to <a href="/">SimilarSounds</a> and type an artist, or paste a YouTube, SoundCloud, Beatport, Bandcamp or Deezer link.</li>
  <li>You get the newest house tracks that <b>sound</b> closest to it, each with its key, BPM and energy.</li>
  <li>Every match is marked <b>green</b> (mixes well), <b>amber</b> (workable) or <b>red</b> (will clash), with the reason: "Same key · −2 BPM · energy +1".</li>
  <li>Add the ones you like to your set and press <b>Smart order</b> to put them in the order that mixes best.</li>
</ol>
<p>You can also browse ready-made lists: <a href="/similar-to/genre/deep-house">deep house</a>, <a href="/similar-to/genre/tech-house">tech house</a>, <a href="/similar-to/genre/minimal-deep-tech">minimal / deep tech</a>, <a href="/similar-to/genre/funky-disco-house">funky / disco house</a> and <a href="/similar-to/genre/house">house</a>.</p>

<h2>Train your ears too</h2>
<p>Tools get you a shortlist; your ears make the call. Before a gig, try each new track against the one before it on headphones. If the blend makes you want to keep it going, it's a keeper.</p>
""",
        "faq": [
            ("How do DJs know which songs go together?", "They check four things: whether the tracks sound alike, whether their keys are compatible, whether their tempos are close and whether the energy moves the way they want. Experience and listening do the rest."),
            ("How close does the BPM need to be?", "Within about 3 BPM is easy and unnoticeable. Bigger jumps are possible with key lock on and a shorter blend."),
            ("Is there a tool that finds songs that mix with a track?", "Yes. SimilarSounds finds new house tracks that sound like the track you paste and checks each one's key, BPM and energy against it, so you can see at a glance what will mix."),
        ],
    },
    {
        "slug": "house-music-bpm",
        "title": "House Music BPM Guide: Tempos for Every Style",
        "short": "House music BPM guide",
        "description": "What BPM house music is, with typical tempos for deep house, tech house, minimal / deep tech and disco house, taken from thousands of real releases.",
        "intro": "House music usually sits between 118 and 130 BPM. Each style has its own sweet spot, and knowing it helps you plan a set that builds instead of lurching.",
        "body": """
<h2>Typical tempos by style</h2>
<p>These ranges come from the <b>6,600+ house releases</b> in the SimilarSounds catalogue. The middle half of each style falls in the range shown, with the most common tempo in the last column.</p>
<div class="tbl"><table>
<thead><tr><th>Style</th><th>Most tracks</th><th>Typical</th></tr></thead>
<tbody>
<tr><td><a href="/similar-to/genre/deep-house">Deep House</a></td><td>120–125 BPM</td><td>123</td></tr>
<tr><td><a href="/similar-to/genre/funky-disco-house">Funky / Disco House</a></td><td>120–126 BPM</td><td>123</td></tr>
<tr><td><a href="/similar-to/genre/house">House</a></td><td>122–127 BPM</td><td>124</td></tr>
<tr><td><a href="/similar-to/genre/tech-house">Tech House</a></td><td>124–128 BPM</td><td>126</td></tr>
<tr><td><a href="/similar-to/genre/minimal-deep-tech">Minimal / Deep Tech</a></td><td>123–129 BPM</td><td>126</td></tr>
</tbody></table></div>

<h2>How DJs use tempo in a set</h2>
<p>Most house sets start slower and creep up. Opening at 120–122 with deeper records and finishing at 126–128 with tech house is a classic shape. Moving <b>1–2 BPM every few tracks</b> is unnoticeable to a crowd; jumping 6 BPM in one mix is not.</p>
<p>If you need a bigger change, do it over a breakdown, use a drum-only intro, or bring the tempo across gradually over several tracks.</p>

<h2>Half-time and double-time</h2>
<p>A 120 BPM track and a 60 or 240 BPM track line up beat for beat, which is how DJs sometimes slip in a downtempo or drum &amp; bass record. Within house you'll rarely need it, but it's handy for warm-up and after-hours sets.</p>

<h2>BPM and key go together</h2>
<p>Changing tempo by more than a couple of percent also shifts the key unless key lock is on: about 6% equals a full semitone. Read the <a href="/guides/camelot-wheel">Camelot wheel guide</a> to see why that matters.</p>

<h2>Browse house music by BPM</h2>
<p>Find tracks at the exact tempo you need: <a href="/similar-to/bpm/118-120">118–120</a>, <a href="/similar-to/bpm/120-122">120–122</a>, <a href="/similar-to/bpm/122-124">122–124</a>, <a href="/similar-to/bpm/124-126">124–126</a>, <a href="/similar-to/bpm/126-128">126–128</a>, <a href="/similar-to/bpm/128-130">128–130</a> BPM. Or paste a track into <a href="/">SimilarSounds</a> and set the BPM range filter to ±3 to get only matches close to its tempo.</p>
""",
        "faq": [
            ("What BPM is house music?", "Most house music is between 118 and 130 BPM, with 122–126 the most common."),
            ("What BPM is deep house?", "Deep house usually sits between 120 and 125 BPM, most often around 123."),
            ("What BPM is tech house?", "Tech house is usually 124–128 BPM, most often around 126."),
            ("How much can I change the BPM between tracks?", "1–2 BPM every few tracks is unnoticeable. For bigger jumps, use key lock and change over a breakdown or drum intro."),
        ],
    },
    {
        "slug": "house-music-styles",
        "title": "Deep House vs Tech House vs Minimal: What's the Difference?",
        "short": "Deep house vs tech house vs minimal",
        "description": "How to tell deep house, tech house, minimal / deep tech, funky / disco house and classic house apart: the sound, the tempo and when DJs play each one.",
        "intro": "House has a lot of labels, and they overlap. Here's what actually separates the main styles you'll find on Beatport and in a club, and when each one works best in a set.",
        "body": """
<h2>Deep House</h2>
<p><b>Sound:</b> warm chords, soft or jazzy keys, rounded bass and a relaxed groove. Often soulful vocals or spoken samples. <b>Tempo:</b> usually 120–125 BPM. <b>When:</b> warm-ups, rooftops, early evening and anywhere people are talking as much as dancing. <a href="/similar-to/genre/deep-house">Browse deep house</a>.</p>

<h2>Tech House</h2>
<p><b>Sound:</b> punchy kick, tight percussion, rolling or bouncy bass lines and short vocal hooks. Built for the dancefloor rather than for listening. <b>Tempo:</b> usually 124–128 BPM. <b>When:</b> peak time in most house clubs. <a href="/similar-to/genre/tech-house">Browse tech house</a>.</p>

<h2>Minimal / Deep Tech</h2>
<p><b>Sound:</b> stripped-back and hypnotic. Fewer elements, swung and shuffling drums, deep sub bass and small details that change slowly. Includes what many DJs call rominimal and UK minimal. <b>Tempo:</b> usually 123–129 BPM. <b>When:</b> late nights and after-hours, for crowds that want to lock in for hours. <a href="/similar-to/genre/minimal-deep-tech">Browse minimal / deep tech</a>.</p>

<h2>Funky / Disco House</h2>
<p><b>Sound:</b> live-sounding bass lines, chopped disco and funk samples, filter sweeps, horns and big uplifting vocals. Includes nu disco and French-touch style house. <b>Tempo:</b> usually 120–126 BPM. <b>When:</b> anytime the crowd wants to smile: parties, weddings, sunny day sets. <a href="/similar-to/genre/funky-disco-house">Browse funky / disco house</a>.</p>

<h2>House</h2>
<p><b>Sound:</b> the broad middle: classic four-to-the-floor grooves, piano and organ stabs, vocal house and anything that doesn't sit neatly in one of the styles above. <b>Tempo:</b> usually 122–127 BPM. <a href="/similar-to/genre/house">Browse house</a>.</p>

<h2>Can you mix styles together?</h2>
<p>Yes, and the best sets do. Deep house into tech house is the most natural journey in house music: the tempo creeps up from about 123 to 126 and the sound gets punchier. The trick is finding <b>bridge tracks</b> that sit between two styles. Paste one track into <a href="/">SimilarSounds</a> and you'll see matches from neighbouring styles that share its sound, with key and BPM checked.</p>

<h2>Why labels disagree</h2>
<p>Genre tags come from labels and stores, and they're often marketing choices. Two shops can file the same record differently. Use the tags to narrow things down, then trust the sound, which is why SimilarSounds matches on how tracks actually sound rather than on their label.</p>
""",
        "faq": [
            ("What is the difference between deep house and tech house?", "Deep house is warmer and more relaxed, with soft chords and rounded bass, usually at 120–125 BPM. Tech house is punchier and more percussive, built for peak time, usually at 124–128 BPM."),
            ("What is minimal deep tech?", "A stripped-back, hypnotic style of house with swung drums, deep sub bass and few elements, usually at 123–129 BPM and played late at night."),
            ("Is nu disco the same as disco house?", "They're close relatives. Both use disco and funk sounds; nu disco is often slower and more song-like, disco house is more loop-based and club-focused. SimilarSounds groups them as Funky / Disco House."),
        ],
    },
    {
        "slug": "dj-set-energy",
        "title": "How to Build a DJ Set That Flows",
        "short": "How to build a DJ set that flows",
        "description": "Plan a house DJ set that keeps the floor moving: shaping the energy, choosing transitions by key and tempo, and checking the order before you play.",
        "intro": "A set that flows isn't just good tracks in a row. It's a journey: each track leads naturally into the next, and the energy rises and falls on purpose.",
        "body": """
<h2>Start with the shape</h2>
<p>Before picking tracks, decide the shape of the night. A typical club set looks like this:</p>
<ul class="steps">
  <li><b>Warm-up:</b> lower energy, deeper sounds, slower tempos. Let people arrive.</li>
  <li><b>Build:</b> energy and tempo creep up. More percussion, more hooks.</li>
  <li><b>Peak:</b> your strongest records, highest energy.</li>
  <li><b>Breathers:</b> short dips between peaks so the peaks feel bigger.</li>
  <li><b>Close:</b> something memorable to end on.</li>
</ul>
<p>Playing the opening slot? Your job is the warm-up, not the peak. Don't play the headliner's records.</p>

<h2>Think in energy, not just genre</h2>
<p>SimilarSounds gives every track an <b>energy score from 1 to 10</b>, based on how driving and dense it sounds. A good rule: move the energy by <b>no more than 1–2 points per mix</b>, unless you're making a big moment on purpose. The <b>energy flow</b> line in the set builder shows your whole set at a glance, so dips and sudden jumps stand out.</p>

<h2>Make every transition easy</h2>
<p>For each pair of tracks, check three things:</p>
<ol class="steps">
  <li><b>Key:</b> same Camelot code, one step either side, or the other letter. See the <a href="/guides/camelot-wheel">Camelot wheel guide</a>.</li>
  <li><b>Tempo:</b> within about 3 BPM. See the <a href="/guides/house-music-bpm">BPM guide</a>.</li>
  <li><b>Sound:</b> do they feel like they belong together? See <a href="/guides/songs-that-mix-together">how to find songs that mix</a>.</li>
</ol>

<h2>Build it with the set builder</h2>
<p>The <a href="/">SimilarSounds set builder</a> is free and does the checking for you:</p>
<ol class="steps">
  <li>Search a track and tap <b>+ Set</b> on the matches you like.</li>
  <li>Open <b>Your set</b>. Every transition is coloured <b>green</b> (smooth), <b>amber</b> (workable) or <b>red</b> (clashes).</li>
  <li>Drag tracks into order, or press <b>Smart order</b> to have it arranged for the smoothest mixes.</li>
  <li>Stuck for the next track? Press <b>Find what mixes next</b> on the last one.</li>
  <li>Copy the tracklist or share the set with a link.</li>
</ol>

<h2>Leave room to read the crowd</h2>
<p>Plan more tracks than you'll play and group them into small "pockets" that mix well together. Then you can follow the room instead of a fixed list, without ever being stuck for a track that fits.</p>
""",
        "faq": [
            ("How do you plan a DJ set?", "Decide the shape of the night first (warm-up, build, peak, breathers, close), then choose tracks so each one mixes with the next on key, tempo and sound, and the energy moves the way you planned."),
            ("How many tracks do I need for a one-hour set?", "For house, usually 15–20 tracks for an hour, but bring 30–40 so you can follow the crowd."),
            ("Is there a free set builder for DJs?", "Yes. SimilarSounds has a free set builder that checks every transition for key and tempo, colours it green, amber or red, and can order the set for you."),
        ],
    },
    {
        "slug": "find-similar-songs",
        "title": "How to Find House Tracks Similar to a Song You Love",
        "short": "How to find tracks similar to a song",
        "description": "Five ways to find new house music that sounds like a track you love, from 'similar to' tools to labels, remixers and DJ charts.",
        "intro": "You've found a track you can't stop playing and you want ten more like it. Here are the fastest ways DJs dig for similar music.",
        "body": """
<h2>1. Use a "similar tracks" tool</h2>
<p>The quickest route. Paste the track into <a href="/">SimilarSounds</a> (a YouTube, SoundCloud, Beatport, Bandcamp or Deezer link, or just type the artist) and you'll get the newest house releases that <b>sound</b> closest to it. It listens to the music itself rather than relying on genre tags, and checks each match for key, BPM and energy, so the results are ready to mix.</p>
<p>Every track in the catalogue also has its own page, like the ones in <a href="/similar-to">all similar-track pages</a>, and every artist has an <a href="/artists-like">"artists like…"</a> page.</p>

<h2>2. Follow the label</h2>
<p>Labels have a sound. If you love a record, look at the label's other releases from the same year. You'll often find a whole run of tracks in the same style.</p>

<h2>3. Follow the remixer</h2>
<p>A remix tells you as much about the remixer as the original artist. Check what else they've remixed and released, and who they've collaborated with.</p>

<h2>4. Dig through DJ charts and sets</h2>
<p>Find DJs who play the track (search the title on tracklist sites or in mix descriptions) and look at what they play around it. The records before and after it in a set are often the best matches of all.</p>

<h2>5. Check the artist's influences</h2>
<p>Artists often name their influences in interviews, on their profiles and in the samples they use. Following those back can lead you to older records with the same feel.</p>

<h2>Keep a shortlist</h2>
<p>Whatever method you use, save the tracks you like in one place. In SimilarSounds, tap <b>+ Set</b> and they're saved on your device (or in your free account), with the transitions between them already checked. Then read <a href="/guides/dj-set-energy">how to build a set that flows</a>.</p>
""",
        "faq": [
            ("How can I find songs similar to a song I like?", "Use a similar-tracks tool like SimilarSounds, then dig through the same label, the remixer's other work and DJ sets that play the track."),
            ("Is there a free tool to find similar house music?", "Yes. SimilarSounds is free: paste a track and it finds new house releases that sound like it, with key, BPM and energy checked so you can mix them."),
            ("How does SimilarSounds decide which tracks are similar?", "It analyses the audio of every track to compare how they actually sound (drums, bass, groove and atmosphere), then checks key, tempo and energy against your track."),
        ],
    },
]

BY_SLUG = {g["slug"]: g for g in GUIDES}


def _jsonld(g: dict) -> str:
    url = f"{SITE}/guides/{g['slug']}"
    data = [
        {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["description"],
         "dateModified": UPDATED, "datePublished": UPDATED, "mainEntityOfPage": url,
         "author": {"@type": "Organization", "name": AUTHOR, "url": SITE},
         "publisher": {"@type": "Organization", "name": AUTHOR, "url": SITE}},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in g["faq"]]},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Guides", "item": f"{SITE}/guides"},
            {"@type": "ListItem", "position": 2, "name": g["short"], "item": url}]},
    ]
    return "".join(f'<script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>' for d in data)


def guide_page(slug: str) -> str | None:
    g = BY_SLUG.get(slug)
    if not g:
        return None
    faq = "".join(f"<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in g["faq"])
    more = "".join(f'<li><a href="/guides/{o["slug"]}">{escape(o["title"])}</a></li>' for o in GUIDES if o["slug"] != slug)
    body = f"""<article class="guide">
  <div class="crumbs"><a href="/guides">Guides</a> / {escape(g["short"])}</div>
  <h1>{escape(g["title"])}</h1>
  <p class="lead">{escape(g["intro"])}</p>
  {g["body"]}
  {CTA}
  <h2>Questions</h2>
  <div class="faq">{faq}</div>
  <h2>More guides</h2>
  <ul class="more">{more}</ul>
</article>"""
    return page(f"{g['title']} | SimilarSounds", g["description"], f"/guides/{slug}", body, jsonld=_jsonld(g))


def guides_hub() -> str:
    items = "".join(f'<li><a class="guide-card" href="/guides/{g["slug"]}"><b>{escape(g["title"])}</b>'
                    f'<span>{escape(g["description"])}</span></a></li>' for g in GUIDES)
    body = f"""<div class="crumbs">Guides</div>
<h1>Guides for house DJs</h1>
<p class="lead">Short, practical guides to mixing in key, tempo, energy and finding music that fits your set.</p>
<ul class="guide-list">{items}</ul>
{CTA}"""
    return page("Guides for House DJs: Mixing in Key, BPM and Set Building | SimilarSounds",
                "Practical guides for house DJs: the Camelot wheel, house music BPM, deep house vs tech house, building a set that flows and finding similar tracks.",
                "/guides", body)


def sitemap_urls() -> list[str]:
    return [f"{SITE}/guides"] + [f"{SITE}/guides/{g['slug']}" for g in GUIDES]
