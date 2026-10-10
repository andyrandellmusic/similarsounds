"""Generate the SimilarSounds logo concepts (v3: SS built from squares that also form an object).

    ../.tools/uv run python make_logos.py      (from the brand folder)

For each concept writes logo-NN.svg (transparent) and logo-NN-icon.svg (on a dark tile),
plus logos.html, a brand board. Earlier rounds: brand/v1 (rounded), brand/v2 (sharp S).
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
WHITE, GREEN, INK = "#f2f2f5", "#c6ff3d", "#0b0b0f"
DIM = "#1d1d27"          # unlit pad / cell

# One S on a 5 x 7 grid of squares. The cut corners (open top-right / bottom-left
# diagonals) are what make it read as an S rather than the digit 5.
S_GRID = [".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."]
# SS = two S's with one empty column between: 11 x 7 cells
SS = [(c, r) for r, row in enumerate(S_GRID) for c, v in enumerate(row) if v == "#"]
SS = [(c, r, WHITE) for c, r in SS] + [(c + 6, r, GREEN) for c, r in SS]


def sq(x, y, size, fill, rx=0.6):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" rx="{rx}" fill="{fill}"/>'


def grid(cells, cols, rows, cell, gap, fill_fn=None, rx=0.6):
    """Draw cells [(col,row,colour)] centred in the 120 box."""
    pitch = cell + gap
    w, h = cols * pitch - gap, rows * pitch - gap
    x0, y0 = (120 - w) / 2, (120 - h) / 2
    out = []
    if fill_fn:   # background cells (e.g. unlit pads)
        lit = {(c, r) for c, r, _ in cells}
        out += [sq(x0 + c * pitch, y0 + r * pitch, cell, fill_fn(c, r), rx)
                for r in range(rows) for c in range(cols) if (c, r) not in lit and fill_fn(c, r)]
    out += [sq(x0 + c * pitch, y0 + r * pitch, cell, col, rx) for c, r, col in cells]
    return "".join(out)


def shift(cells, dc=0, dr=0, colour=None):
    return [(c + dc, r + dr, colour or col) for c, r, col in cells]


def build():
    m = {}

    m["Pixel"] = ("The base mark: two squared-off S's built from a grid of squares. Crisp, "
                  "digital, and sharp even as a 16px tab icon.",
                  grid(SS, 11, 7, 7.6, 1.6))

    # Pad controller: an 11 x 9 grid of pads where the lit ones spell SS
    m["Launchpad"] = ("A DJ pad controller: a grid of pads where the lit ones spell SS. The object "
                      "every producer recognises.",
                      grid(shift(SS, 0, 1), 11, 9, 7.4, 1.6, fill_fn=lambda c, r: DIM, rx=1.0))

    # House: a stepped green roof over the SS - "house" music
    roof = [(c, r, GREEN) for r, (a, b) in enumerate([(4, 6), (3, 7), (2, 8), (1, 9), (0, 10)])
            for c in range(a, b + 1)]
    m["House"] = ("A stepped roof of green squares sits on the SS, which becomes the house: "
                  "a literal nod to house music.",
                  grid(roof + shift(SS, 0, 6, WHITE), 11, 13, 6.4, 1.4))

    # Headphones: a square-built headband over the two S's (the ear cups)
    band = ([(0, r, WHITE) for r in (2, 3)] + [(10, r, WHITE) for r in (2, 3)] +
            [(1, 1, WHITE), (9, 1, WHITE)] + [(c, 0, WHITE) for c in range(2, 9)])
    m["Headphones"] = ("A headband of squares turns the two S's into the ear cups of a pair of "
                       "headphones.",
                       grid(band + shift(SS, 0, 5), 11, 12, 6.6, 1.4))

    # Record: a ring of squares (a pixel vinyl) around the SS label
    ring = []
    for r in range(17):
        for c in range(17):
            dist = math.hypot(c - 8, r - 8)
            if 7.55 <= dist <= 8.5:
                ring.append((c, r, WHITE))
    m["Record"] = ("A vinyl record drawn in squares, with SS as its centre label. Made for "
                   "DJs and crate-diggers.",
                   grid(ring + shift(SS, 3, 5), 17, 17, 5.4, 1.2))

    # Blocks: every square extruded into a solid block - SS as a physical object
    m["Blocks"] = ("Each square becomes a solid 3D block, so the SS reads like a physical object "
                   "or speaker stack.", blocks())
    return m


def blocks():
    cell, gap, depth = 6.8, 1.4, 3.6
    pitch = cell + gap
    w, h = 11 * pitch - gap + depth, 7 * pitch - gap + depth
    x0, y0 = (120 - w) / 2, (120 - h) / 2 + depth
    shades = {WHITE: ("#ffffff", "#9a9aa8"), GREEN: ("#e4ff9e", "#6f9418")}
    backs, fronts = [], []
    for c, r, col in SS:
        x, y = x0 + c * pitch, y0 + r * pitch
        top, side = shades[col]
        backs.append(f'<path d="M{x:.2f} {y:.2f} L{x + cell:.2f} {y:.2f} L{x + cell + depth:.2f} {y - depth:.2f} '
                     f'L{x + depth:.2f} {y - depth:.2f} Z" fill="{top}"/>')
        backs.append(f'<path d="M{x + cell:.2f} {y:.2f} L{x + cell:.2f} {y + cell:.2f} '
                     f'L{x + cell + depth:.2f} {y + cell - depth:.2f} L{x + cell + depth:.2f} {y - depth:.2f} Z" '
                     f'fill="{side}"/>')
        fronts.append(sq(x, y, cell, col, rx=0))
    return "".join(backs + fronts)


def svg(body, tile=False):
    bg = f'<rect width="120" height="120" rx="22" fill="{INK}"/>' if tile else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">{bg}{body}</svg>'


def mono(body):
    for c in (GREEN, "#e4ff9e", "#6f9418"):
        body = body.replace(c, WHITE if c == GREEN else ("#ffffff" if c == "#e4ff9e" else "#9a9aa8"))
    return body


def wordmark(size):
    return f'<span class="wm" style="font-size:{size}px">SIMILAR<b>SOUNDS</b></span>'


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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Space+Grotesk:wght@700&display=swap" rel="stylesheet">
<style>
  body {{ margin:0; background:#050507; color:{WHITE}; font:15px/1.5 Inter,system-ui,sans-serif; }}
  .wrap {{ max-width:1180px; margin:0 auto; padding:40px 16px 80px; }}
  h1 {{ margin:0; }}
  .sub {{ color:#8d8da0; margin:10px 0 30px; max-width:720px; }}
  .wm {{ font-family:"Space Grotesk",Inter,sans-serif; font-weight:700; letter-spacing:.12em; color:{WHITE}; white-space:nowrap; }}
  .wm b {{ color:{GREEN}; font-weight:700; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:16px; }}
  .card {{ background:#101016; border:1px solid #23232e; border-radius:6px; overflow:hidden; }}
  .hero {{ background:{INK}; display:grid; place-items:center; height:240px; border-bottom:1px solid #23232e; }}
  .hero svg {{ width:200px; height:200px; }}
  .info {{ padding:16px 18px 18px; }}
  .title {{ font-weight:800; font-size:15px; letter-spacing:.08em; text-transform:uppercase; }}
  .n {{ color:{GREEN}; font:700 12px ui-monospace,monospace; margin-right:8px; }}
  p {{ color:#8d8da0; margin:4px 0 14px; font-size:14px; }}
  .lockup {{ display:flex; align-items:center; gap:12px; background:{INK}; border-radius:4px; padding:14px 16px; }}
  .lk svg {{ width:44px; height:44px; display:block; }}
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
  <h1>{wordmark(32)}</h1>
  <p class="sub">SS built from squares, where the squares also form a music object. White and green on near-black, as on the site.</p>
  <p class="legend">Each card: the mark &middot; the lockup with the name &middot; app icon (56px) &middot; browser-tab icon at 32px and 16px &middot; one-colour version.</p>
  <div class="grid">{''.join(cards)}
  </div>
</div></body></html>"""
    (OUT / "logos.html").write_text(html)
    print(f"wrote {len(marks)} concepts to {OUT}")


if __name__ == "__main__":
    main()
