"""Generate the SimilarSounds logo concepts (v4: minimal symbols, no letters).

    ../.tools/uv run python make_logos.py      (from the brand folder)

For each concept writes logo-NN.svg (transparent) and logo-NN-icon.svg (on a dark tile),
plus logos.html, a brand board. Earlier rounds: v1 rounded SS, v2 sharp SS, v3 square-built SS.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent
WHITE, GREEN, INK = "#f2f2f5", "#c6ff3d", "#0b0b0f"


def build():
    m = {}
    m["Approx"] = ("The ≈ sign means 'similar to', and its two lines are sound waves. One white, "
                   "one green: two tracks that sound alike.",
                   '<path d="M22 50 C34 36 46 36 60 50 S 86 64 98 50" fill="none" stroke="#f2f2f5" '
                   'stroke-width="9" stroke-linecap="round"/>'
                   '<path d="M22 74 C34 60 46 60 60 74 S 86 88 98 74" fill="none" stroke="#c6ff3d" '
                   'stroke-width="9" stroke-linecap="round"/>')

    m["Echo"] = ("A solid circle and its echo: the track you paste, and the one we find that's "
                 "just like it.",
                 f'<circle cx="37" cy="60" r="21" fill="{WHITE}"/>'
                 f'<circle cx="84" cy="60" r="17.5" fill="none" stroke="{GREEN}" stroke-width="7"/>')

    m["Overlap"] = ("Two circles overlap, and the shared part glows green: what two tracks have "
                    "in common.",
                    '<defs><clipPath id="ov"><circle cx="48" cy="60" r="26"/></clipPath></defs>'
                    f'<circle cx="72" cy="60" r="26" fill="{GREEN}" clip-path="url(#ov)"/>'
                    f'<circle cx="48" cy="60" r="26" fill="none" stroke="{WHITE}" stroke-width="5"/>'
                    f'<circle cx="72" cy="60" r="26" fill="none" stroke="{WHITE}" stroke-width="5"/>')

    m["Pulse"] = ("A flat line with a single sharp peak, like a waveform: the moment a track "
                  "hits.",
                  f'<path d="M16 64 L44 64 L54 40 L66 84 L76 64 L104 64" fill="none" stroke="{WHITE}" '
                  f'stroke-width="7" stroke-linejoin="round" stroke-linecap="round"/>'
                  f'<path d="M44 64 L54 40 L66 84 L76 64" fill="none" stroke="{GREEN}" stroke-width="7" '
                  f'stroke-linejoin="round" stroke-linecap="round"/>')

    m["Bars"] = ("Three level bars rising, like a signal or EQ: the green one is the match.",
                 f'<rect x="28" y="62" width="14" height="28" fill="{WHITE}"/>'
                 f'<rect x="53" y="46" width="14" height="44" fill="{WHITE}"/>'
                 f'<rect x="78" y="30" width="14" height="60" fill="{GREEN}"/>')

    m["Ripple"] = ("A green dot with sound rippling out from it: one sound reaching others.",
                   f'<circle cx="38" cy="60" r="10" fill="{GREEN}"/>'
                   f'<path d="M58 40 A28 28 0 0 1 58 80" fill="none" stroke="{WHITE}" stroke-width="7" stroke-linecap="round"/>'
                   f'<path d="M74 28 A44 44 0 0 1 74 92" fill="none" stroke="{WHITE}" stroke-width="7" stroke-linecap="round"/>')
    return m


def svg(body, tile=False):
    bg = f'<rect width="120" height="120" rx="26" fill="{INK}"/>' if tile else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">{bg}{body}</svg>'


def mono(body):
    return body.replace(GREEN, WHITE)


def wordmark(size):
    return f'<span class="wm" style="font-size:{size}px">Similar<b>Sounds</b></span>'


def main():
    marks = build()
    cards, thumbs = [], []
    for i, (name, (blurb, body)) in enumerate(marks.items(), 1):
        thumbs.append(f'<a class="thumb" href="#c{i:02d}">{svg(body)}<span><b>{i:02d}</b> {name}</span></a>')
        n = f"{i:02d}"
        (OUT / f"logo-{n}.svg").write_text(svg(body))
        (OUT / f"logo-{n}-icon.svg").write_text(svg(body, tile=True))
        icon = svg(body, tile=True)
        cards.append(f"""
    <article class="card" id="c{n}">
      <div class="hero">{svg(body)}</div>
      <div class="info">
        <div class="title"><span class="n">{n}</span>{name}</div>
        <p>{blurb}</p>
        <div class="lockup"><div class="lk">{svg(body)}</div>{wordmark(22)}</div>
        <div class="row">
          <div class="icon">{icon}</div>
          <div class="fav f32">{icon}</div>
          <div class="fav f16">{icon}</div>
          <div class="mono">{svg(mono(body))}</div>
          <div class="dl"><a href="logo-{n}.svg" download>Mark SVG</a><a href="logo-{n}-icon.svg" download>Icon SVG</a></div>
        </div>
      </div>
    </article>""")

    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SimilarSounds logos</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; background:#050507; color:{WHITE}; font:15px/1.5 Inter,system-ui,sans-serif; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:40px 16px 80px; }}
  h1 {{ margin:0; }}
  .sub {{ color:#8d8da0; margin:10px 0 30px; max-width:720px; }}
  .wm {{ font-weight:800; letter-spacing:-.02em; color:{WHITE}; white-space:nowrap; }}
  .wm b {{ color:{GREEN}; font-weight:800; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:16px; }}
  .card {{ background:#101016; border:1px solid #23232e; border-radius:8px; overflow:hidden; }}
  .hero {{ background:{INK}; display:grid; place-items:center; height:240px; border-bottom:1px solid #23232e; }}
  .hero svg {{ width:180px; height:180px; }}
  .info {{ padding:16px 18px 18px; }}
  .title {{ font-weight:800; font-size:16px; }}
  .n {{ color:{GREEN}; font:700 12px ui-monospace,monospace; margin-right:8px; }}
  p {{ color:#8d8da0; margin:4px 0 14px; font-size:14px; }}
  .lockup {{ display:flex; align-items:center; gap:10px; background:{INK}; border-radius:6px; padding:14px 16px; }}
  .lk svg {{ width:40px; height:40px; display:block; }}
  .row {{ display:flex; align-items:center; gap:12px; margin-top:12px; }}
  .icon svg {{ width:56px; height:56px; display:block; }}
  .fav.f32 svg {{ width:32px; height:32px; display:block; }}
  .fav.f16 svg {{ width:16px; height:16px; display:block; }}
  .mono {{ background:{INK}; border-radius:6px; padding:4px; }}
  .mono svg {{ width:48px; height:48px; display:block; }}
  .dl {{ margin-left:auto; display:flex; flex-direction:column; gap:2px; text-align:right; font-size:12px; }}
  .dl a {{ color:{GREEN}; font-weight:600; text-decoration:none; }}
  .legend {{ color:#8d8da0; font-size:12px; margin:24px 0 16px; }}
  .overview {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }}
  .thumb {{ background:{INK}; border:1px solid #23232e; border-radius:8px; padding:10px 8px 8px; text-align:center;
            color:{WHITE}; text-decoration:none; font-size:13px; }}
  .thumb svg {{ width:100%; max-width:120px; height:auto; display:block; margin:0 auto 4px; }}
  .thumb b {{ color:{GREEN}; font-family:ui-monospace,monospace; font-size:11px; }}
  .thumb:hover {{ border-color:{GREEN}; }}
</style></head>
<body><div class="wrap">
  <h1>{wordmark(32)}</h1>
  <p class="sub">Minimal symbols, no letters. Each one is a single idea: similarity, or sound. White and green on near-black, as on the site.</p>
  <div class="overview">{''.join(thumbs)}</div>
  <p class="legend">Below, each one in detail. Each card: the mark &middot; with the name &middot; app icon (56px) &middot; browser-tab icon at 32px and 16px &middot; one-colour version.</p>
  <div class="grid">{''.join(cards)}
  </div>
</div></body></html>"""
    (OUT / "logos.html").write_text(html)
    print(f"wrote {len(marks)} concepts to {OUT}")


if __name__ == "__main__":
    main()
