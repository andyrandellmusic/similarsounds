"""Generate the SimilarSounds logo concepts (v2: sharp, angular SS).

    ../.tools/uv run python make_logos.py      (from the brand folder)

Writes, for each concept:
  logo-NN.svg       the mark on a transparent background (pure vector, no fonts)
  logo-NN-icon.svg  the mark on a dark rounded tile (app icon / favicon / avatar)
and logos.html, a brand board showing every concept large, as a lockup with the
name, as an app icon, at favicon sizes, and in one-colour white.
Earlier rounded concepts are kept in brand/v1/.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent
WHITE, GREEN, INK = "#f2f2f5", "#c6ff3d", "#0b0b0f"

# The sharp S: top bar, a short left stem, one steep diagonal spine (the "Z" energy),
# a short right stem, bottom bar. Drawn as a single stroke with mitred (sharp) corners
# and square-cut ends. Box: W x H, stroke T.
W, H, T = 36, 56, 10
h = T / 2
SHAPES = {
    "steep": [(W, h), (h, h), (h, H * .30), (W - h, H * .70), (W - h, H - h), (0, H - h)],
    "spine": [(W, h), (h, h), (h, H * .40), (W - h, H * .60), (W - h, H - h), (0, H - h)],
}


def d(shape="steep"):
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in SHAPES[shape])


def s(x, y, color, t=T, scale=1.0, shape="steep", extra=""):
    return (f'<path d="{d(shape)}" transform="translate({x:.2f} {y:.2f}) scale({scale})" fill="none" '
            f'stroke="{color}" stroke-width="{t / scale:.2f}" stroke-linejoin="miter" '
            f'stroke-miterlimit="10" stroke-linecap="butt"{extra}/>')


def pair(x, y, c1=WHITE, c2=GREEN, gap=8, **kw):
    sc = kw.get("scale", 1.0)
    return s(x, y, c1, **kw) + s(x + (W + gap) * sc, y, c2, **kw)


def centred_pair(c1=WHITE, c2=GREEN, gap=8, scale=1.0, **kw):
    width = (2 * W + gap) * scale
    return pair((120 - width) / 2, (120 - H * scale) / 2, c1, c2, gap, scale=scale, **kw)


def bars_mask(mid):
    # Vertical "equaliser" bars, only visible inside the two S shapes
    bars = "".join(f'<rect x="{x}" y="0" width="3.2" height="120" fill="{WHITE if x < mid else GREEN}"/>'
                   for x in range(14, 108, 5))
    return bars


def build():
    ink_gap = INK
    m = {}

    m["Blade"] = ("The core idea: two razor-sharp S's with a steep, Z-like spine. Clean, confident, "
                  "reads instantly at any size.", centred_pair())

    m["Spine"] = ("Same construction with a gentler diagonal, so it reads more like a classic S while "
                  "staying angular.", centred_pair(shape="spine"))

    # Slipstream: the second S is dropped by exactly the spine's slope, so both diagonals sit on
    # one continuous line - a single "lightning" stroke running through the pair
    pts = SHAPES["steep"]
    slope = (pts[3][1] - pts[2][1]) / (pts[3][0] - pts[2][0])
    gap, sc = 6, 0.8
    dx = W + gap
    dy = dx * slope
    w_all, h_all = (dx + W) * sc, (dy + H) * sc
    x0, y0 = (120 - w_all) / 2, (120 - h_all) / 2
    m["Slipstream"] = ("The second S drops so both diagonals form one unbroken line, like a "
                       "lightning strike through the pair.",
                       s(x0, y0, WHITE, scale=sc) + s(x0 + dx * sc, y0 + dy * sc, GREEN, scale=sc))

    # Interlock: green S behind, white S in front with a thin dark cut-line so they read as linked
    m["Interlock"] = ("Two S's overlap with a precise cut-line between them: linked, layered, "
                      "two sounds locking together.",
                      s(51, 32, GREEN) + s(26, 32, ink_gap, t=T + 5) + s(26, 32, WHITE))

    m["Velocity"] = ("Both S's leaned forward 12°: the sharpness of the Z with a sense of speed "
                     "and movement.",
                     f'<g transform="translate(60 60) skewX(-12) translate(-60 -60)">{centred_pair()}</g>')

    m["Equaliser"] = ("The SS is made of thin vertical bars, like a spectrum analyser. Sound and "
                      "initials in one mark.",
                      f'<defs><mask id="eq"><rect width="120" height="120" fill="black"/>'
                      f'{centred_pair(WHITE, WHITE, gap=8, t=13)}</mask></defs>'
                      f'<g mask="url(#eq)">{bars_mask(60)}</g>')

    m["Outline"] = ("A hollow white S beside a solid green one: the original and its 'similar sound'. "
                    "Premium, fashion-label feel.",
                    s(20, 32, WHITE) + s(20, 32, INK, t=T - 4.4) + s(64, 32, GREEN))

    m["Step"] = ("The second S steps down, like a rhythm or a rising set. Simple, but with movement.",
                 s(22, 22, WHITE) + s(62, 42, GREEN))

    m["Stack"] = ("One S above the other: a tall, narrow monogram, strong as a vertical banner or "
                  "phone app icon.",
                  s(42, 6, WHITE, scale=0.95) + s(42, 61, GREEN, scale=0.95))

    m["Hex"] = ("The SS inside a sharp hexagon outline, like a record label stamp or club "
                "emblem.",
                f'<path d="M60 8 L105 34 L105 86 L60 112 L15 86 L15 34 Z" fill="none" stroke="{GREEN}" '
                f'stroke-width="3" stroke-linejoin="miter"/>' + centred_pair(scale=0.68, t=7.5))
    return m


def svg(body, tile=False):
    bg = f'<rect width="120" height="120" rx="24" fill="{INK}"/>' if tile else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">{bg}{body}</svg>'


def mono(body):
    # One-colour version: everything white (keeps the dark cut-lines so overlaps still read)
    return body.replace(GREEN, WHITE)


def wordmark(size):
    return (f'<span class="wm" style="font-size:{size}px">SIMILAR<b>SOUNDS</b></span>')


def main():
    marks = build()
    cards = []
    for i, (name, (blurb, body)) in enumerate(marks.items(), 1):
        n = f"{i:02d}"
        (OUT / f"logo-{n}.svg").write_text(svg(body))
        (OUT / f"logo-{n}-icon.svg").write_text(svg(body, tile=True))
        icon = svg(body, tile=True)
        cards.append(f"""
    <article class="card">
      <div class="hero">{svg(body)}</div>
      <div class="info">
        <div class="title"><span class="n">{n}</span>{name}</div>
        <p>{blurb}</p>
        <div class="lockup"><div class="lk">{svg(body)}</div>{wordmark(19)}</div>
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; background:#050507; color:{WHITE}; font:15px/1.5 Inter,system-ui,sans-serif; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:40px 16px 80px; }}
  h1 {{ margin:0; }}
  .sub {{ color:#8d8da0; margin:10px 0 30px; max-width:720px; }}
  .wm {{ font-weight:900; letter-spacing:.08em; color:{WHITE}; white-space:nowrap; }}
  .wm b {{ color:{GREEN}; font-weight:900; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:16px; }}
  .card {{ background:#101016; border:1px solid #23232e; border-radius:6px; overflow:hidden; }}
  .hero {{ background:{INK}; display:grid; place-items:center; height:230px; border-bottom:1px solid #23232e; }}
  .hero svg {{ width:190px; height:190px; }}
  .info {{ padding:16px 18px 18px; }}
  .title {{ font-weight:800; font-size:16px; letter-spacing:.02em; text-transform:uppercase; }}
  .n {{ color:{GREEN}; font:700 12px ui-monospace,monospace; margin-right:8px; }}
  p {{ color:#8d8da0; margin:4px 0 14px; font-size:14px; }}
  .lockup {{ display:flex; align-items:center; gap:10px; background:{INK}; border-radius:4px; padding:14px 16px; }}
  .lk svg {{ width:40px; height:40px; display:block; }}
  .row {{ display:flex; align-items:center; gap:12px; margin-top:12px; }}
  .icon svg {{ width:56px; height:56px; display:block; }}
  .fav.f32 svg {{ width:32px; height:32px; display:block; }}
  .fav.f16 svg {{ width:16px; height:16px; display:block; }}
  .mono {{ background:{INK}; border-radius:4px; padding:4px; }}
  .mono svg {{ width:48px; height:48px; display:block; }}
  .dl {{ margin-left:auto; display:flex; flex-direction:column; gap:2px; text-align:right; font-size:12px; }}
  .dl a {{ color:{GREEN}; font-weight:600; text-decoration:none; }}
  .legend {{ color:#8d8da0; font-size:12px; margin:-18px 0 24px; }}
</style></head>
<body><div class="wrap">
  <h1>{wordmark(34)}</h1>
  <p class="sub">10 logo concepts built on one sharp, angular S: mitred corners, square-cut ends and a steep Z-like spine.
    White and green on near-black, as on the site.</p>
  <p class="legend">Each card: the mark &middot; the lockup with the name &middot; app icon (56px) &middot; browser-tab icon at 32px and 16px &middot; one-colour white version.</p>
  <div class="grid">{''.join(cards)}
  </div>
</div></body></html>"""
    (OUT / "logos.html").write_text(html)
    print(f"wrote {len(marks)} concepts to {OUT}")


if __name__ == "__main__":
    main()
