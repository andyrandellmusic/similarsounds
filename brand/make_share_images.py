"""Draw the social share image and app icons (PNG) from the diamond logo.

    ./.tools/uv run python brand/make_share_images.py      (from the project folder)

Writes static/og.png (1200x630), static/apple-touch-icon.png (180) and static/icon-512.png.
Uses the macOS Arial fonts; drawn at 3x and scaled down for smooth edges.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
WHITE, GREEN, INK, MUTED = (242, 242, 245), (198, 255, 61), (11, 11, 15), (141, 141, 160)
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
SS = 3  # supersampling


def diamond(cx, cy, half):
    return [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)]


def ring(img, cx, cy, outer, inner, color):
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    d.polygon(diamond(cx, cy, outer), fill=255)
    d.polygon(diamond(cx, cy, inner), fill=0)
    img.paste(Image.new("RGB", img.size, color), (0, 0), mask)


def draw_mark(img, x, y, height):
    """The site logo: solid white diamond overlapped by a green outline diamond with a dark cut.
    Geometry from the site's SVG (viewBox 16 39 64 42): white centre 37, green centre 59, half 21."""
    u = height / 42                      # px per SVG unit
    X = lambda v: x + (v - 16) * u
    cy = y + 21 * u
    d = ImageDraw.Draw(img)
    d.polygon(diamond(X(37), cy, 21 * u), fill=WHITE)
    ring(img, X(59), cy, (16.05 + 4.95 + 3.54) * u, (16.05 - 4.95 - 3.54) * u, INK)   # dark cut
    ring(img, X(59), cy, (16.05 + 4.95) * u, (16.05 - 4.95) * u, GREEN)            # green outline
    return 64 * u                          # drawn width


def og():
    W, H = 1200 * SS, 630 * SS
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)
    # faint grid of dots for texture
    for gx in range(0, W, 48 * SS):
        for gy in range(0, H, 48 * SS):
            d.ellipse([gx, gy, gx + 2 * SS, gy + 2 * SS], fill=(28, 28, 36))
    big = ImageFont.truetype(BOLD, 112 * SS)
    cap = big.getbbox("S")                 # capital height for sizing the mark
    cap_h = cap[3] - cap[1]
    mark_h = cap_h * 1.18
    sim_w = d.textlength("Similar", font=big)
    snd_w = d.textlength("Sounds", font=big)
    gap = 0.07 * 112 * SS
    total = mark_h * 64 / 42 + gap + sim_w + snd_w
    x0 = (W - total) / 2
    base_y = 250 * SS                      # top of the capitals
    draw_mark(img, x0, base_y + cap_h / 2 - mark_h / 2, mark_h)
    tx = x0 + mark_h * 64 / 42 + gap
    d.text((tx, base_y - cap[1]), "Similar", font=big, fill=WHITE)
    d.text((tx + sim_w, base_y - cap[1]), "Sounds", font=big, fill=GREEN)
    tag = ImageFont.truetype(BOLD, 38 * SS)
    line = "Paste a track. Get the latest house music, with the perfect mix."
    tw = d.textlength(line, font=tag)
    d.text(((W - tw) / 2, 420 * SS), line, font=tag, fill=WHITE)
    small = ImageFont.truetype(REG, 26 * SS)
    sub = "Matched on key, BPM, energy and sound  ·  www.similarsounds.com"
    sw = d.textlength(sub, font=small)
    d.text(((W - sw) / 2, 484 * SS), sub, font=small, fill=MUTED)
    img.resize((1200, 630), Image.LANCZOS).save(ROOT / "static" / "og.png", optimize=True)


def icon(size, name):
    S = size * SS
    img = Image.new("RGB", (S, S), INK)
    mark_h = S * 0.42
    draw_mark(img, (S - mark_h * 64 / 42) / 2, (S - mark_h) / 2, mark_h)
    img.resize((size, size), Image.LANCZOS).save(ROOT / "static" / name, optimize=True)


if __name__ == "__main__":
    og()
    icon(180, "apple-touch-icon.png")
    icon(512, "icon-512.png")
    print("wrote static/og.png, static/apple-touch-icon.png, static/icon-512.png")
