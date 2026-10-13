"""Render the logo images from the SVG mark: static/apple-touch-icon.png (180), static/icon-512.png and
the link-preview card static/og.png (1200x630).   .venv/bin/python -m scripts.brand_images"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
W1 = "M0 70A70 70 0 0 1 70 0V35A35 35 0 0 0 35 70Z M140 0A70 70 0 0 1 70 70V35A35 35 0 0 0 105 0Z"
W2 = "M0 140A70 70 0 0 1 70 70V105A35 35 0 0 0 35 140Z M140 70A70 70 0 0 1 70 140V105A35 35 0 0 0 105 70Z"
MARK = f'<svg viewBox="0 0 140 140"><path d="{W1}" fill="#f2f2f5"/><path d="{W2}" fill="#c6ff3d"/></svg>'
FONT = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;800&display=swap" rel="stylesheet">'
ICON = f"""<html><head>{FONT}<style>html,body{{margin:0;background:#111116}}
  body{{width:100vw;height:100vh;display:grid;place-items:center}} svg{{width:56%;height:56%}}</style></head><body>{MARK}</body></html>"""
OG = f"""<html><head>{FONT}<style>html,body{{margin:0}}
  body{{width:1200px;height:630px;background:#0b0b0f;color:#f2f2f5;font-family:Inter,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;
    background-image:radial-gradient(rgba(255,255,255,.05) 1px,transparent 1px);background-size:32px 32px}}
  .wm{{display:flex;align-items:center;font-weight:800;font-size:112px;letter-spacing:-.035em;line-height:1}}
  .wm svg{{width:.82em;height:.82em;margin-right:.18em}} .wm span{{color:#c6ff3d}}
  .line{{width:860px;height:2px;background:#c6ff3d;margin:34px 0 30px}}
  h1{{margin:0;font-size:46px;font-weight:800;letter-spacing:-.02em}} h1 em{{font-style:normal;color:#c6ff3d}}
  p{{margin:18px 0 0;color:#9a9aac;font-size:24px;font-weight:600}}</style></head>
  <body><div class="wm">{MARK}Similar<span>Sounds</span></div><div class="line"></div>
  <h1>Paste a track. Get <em>the perfect mix</em>.</h1><p>Matched on key, BPM, energy and sound &nbsp;·&nbsp; www.similarsounds.com</p></body></html>"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome")
        for name, html, size in (("apple-touch-icon.png", ICON, 180), ("icon-512.png", ICON, 512), ("og.png", OG, (1200, 630))):
            w, h = size if isinstance(size, tuple) else (size, size)
            pg = await b.new_page(viewport={"width": w, "height": h})
            await pg.set_content(html, wait_until="networkidle"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(ROOT / "static" / name))
            await pg.close()
        await b.close()

asyncio.run(main())
