"""Record the how-to demo on the local site as sharp screencast frames plus a timeline of where things are.

Usage: .venv/bin/python scripts/video/record.py OUTDIR
Writes OUTDIR/frames/*.jpg, OUTDIR/frames.json (timestamps) and OUTDIR/events.json (boxes in CSS px).
"""
import asyncio, base64, json, math, os, sys, time
from playwright.async_api import async_playwright

OUT = sys.argv[1]
W, H, DSF = 1600, 900, 2
ADD = ["Time To Connect", "Good Life", "Falling", "Down N Down"]   # after the two drags, one link is an orange "Workable"

CURSOR = """
addEventListener('DOMContentLoaded', () => {
  const c = document.createElement('div'); c.id = '__cur';
  c.innerHTML = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6-3.6 6.4z" fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>';
  Object.assign(c.style, {position:'fixed', left:'0', top:'0', zIndex:2147483647, pointerEvents:'none',
    transform:'translate(-100px,-100px)', filter:'drop-shadow(0 2px 4px rgba(0,0,0,.5))'});
  const r = document.createElement('div'); r.id = '__ring';
  Object.assign(r.style, {position:'fixed', left:'0', top:'0', width:'44px', height:'44px', margin:'-22px 0 0 -22px',
    borderRadius:'50%', border:'2px solid #c6ff3d', zIndex:2147483646, pointerEvents:'none', opacity:'0'});
  document.documentElement.append(c);   // no click ring
  addEventListener('pointermove', e => { c.style.transform = `translate(${e.clientX - 4}px,${e.clientY - 2}px)`; }, true);
  addEventListener('pointerdown', e => {
    r.style.transition = 'none'; r.style.opacity = '1'; r.style.transform = `translate(${e.clientX}px,${e.clientY}px) scale(.4)`;
    requestAnimationFrame(() => requestAnimationFrame(() => {
      r.style.transition = 'transform .45s ease-out, opacity .45s ease-out';
      r.style.transform = `translate(${e.clientX}px,${e.clientY}px) scale(1.3)`; r.style.opacity = '0'; }));
  }, true);
});
"""

events, frames, mlog = [], [], []

# filming only: a tidier set panel (hide the extra tools so the tracks and columns fit in one shot)
FILM_CSS = """addEventListener('DOMContentLoaded', () => { const st = document.createElement('style'); st.textContent = `
  .gap-btn, .gap-box, .last-next, .set-hint, #set-share, .set-tools { display: none !important; }
  .set-panel { width: 560px !important; max-width: 560px !important; }
  #scrim.open { background: rgba(4,4,7,.82) !important; backdrop-filter: blur(2px); }`;
  document.head.append(st); });"""
t0 = time.time()


def ev(kind, box=None, **kw):
    events.append({"t": time.time() - t0, "kind": kind, "box": box, **kw})
    print(f"{time.time() - t0:6.2f}s {kind} {box or ''}", flush=True)


async def main():
    os.makedirs(f"{OUT}/frames", exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(channel="chrome", headless=True, args=["--force-device-scale-factor=2"])
        ctx = await b.new_context(viewport={"width": W, "height": H}, device_scale_factor=DSF)
        await ctx.route("**/*supabase.co/**", lambda r: r.abort())
        await ctx.add_init_script(CURSOR)
        # filming: the page's own scrolls jump instantly (so the camera locks straight onto your track)
        await ctx.add_init_script("{ const st = window.scrollTo.bind(window); window.scrollTo = (a, b) => (a && typeof a === 'object') ? st({ ...a, behavior: 'instant' }) : st(a, b); }")
        # filming: no player bars (the mix plays silently in the video), no phone tips
        await ctx.add_init_script("addEventListener('DOMContentLoaded', () => { const st = document.createElement('style'); st.textContent = '#how-video, .set-hint, #mixbar, .mixbar, #nowbar, .rotate-tip { display: none !important; } .wrap { max-width: 1040px !important; padding-left: 16px !important; padding-right: 16px !important; }'; document.head.append(st); });")
        pg = await ctx.new_page()
        await pg.goto("http://localhost:8001/", wait_until="networkidle")
        await pg.evaluate("localStorage.clear(); sessionStorage.clear()")
        await pg.reload(wait_until="networkidle")
        await pg.wait_for_timeout(800)

        cdp = await ctx.new_cdp_session(pg)
        n = [0]

        async def on_frame(f):
            i = n[0]; n[0] += 1
            with open(f"{OUT}/frames/{i:05d}.jpg", "wb") as fh:
                fh.write(base64.b64decode(f["data"]))
            frames.append({"i": i, "t": f["metadata"]["timestamp"] - t0})
            try:
                await cdp.send("Page.screencastFrameAck", {"sessionId": f["sessionId"]})
            except Exception:
                pass
        cdp.on("Page.screencastFrame", lambda f: asyncio.ensure_future(on_frame(f)))
        await cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92,
                                                 "maxWidth": W * DSF, "maxHeight": H * DSF, "everyNthFrame": 1})
        mouse = {"x": W * 0.55, "y": H * 0.75}
        _move, _down, _up = pg.mouse.move, pg.mouse.down, pg.mouse.up
        async def lmove(x, y, **kw):
            await _move(x, y, **kw); mlog.append([time.time() - t0, x, y, 0])
        async def ldown(**kw):
            await _down(**kw); mlog.append([time.time() - t0, mlog[-1][1], mlog[-1][2], 1])
        async def lup(**kw):
            await _up(**kw); mlog.append([time.time() - t0, mlog[-1][1], mlog[-1][2], 2])
        pg.mouse.move, pg.mouse.down, pg.mouse.up = lmove, ldown, lup

        async def move(x, y, ms=600):
            sx, sy = mouse["x"], mouse["y"]
            steps = max(8, ms // 16)
            for s in range(1, steps + 1):
                k = s / steps; k = k * k * (3 - 2 * k)
                await pg.mouse.move(sx + (x - sx) * k, sy + (y - sy) * k)
                await asyncio.sleep(ms / 1000 / steps)
            mouse.update(x=x, y=y)

        async def box(sel_or_handle):
            h = await pg.query_selector(sel_or_handle) if isinstance(sel_or_handle, str) else sel_or_handle
            bb = h and await h.bounding_box()
            return bb and [bb["x"], bb["y"], bb["width"], bb["height"]]

        async def click(h, ms=650, kind="click"):
            bx = await box(h)
            await move(bx[0] + bx[2] / 2, bx[1] + bx[3] / 2, ms)
            ev(kind, bx)
            await pg.mouse.down(); await asyncio.sleep(0.07); await pg.mouse.up()

        async def wheel(dy, ms=900):
            steps = max(10, ms // 16)
            for s in range(steps):
                k = math.sin(math.pi * (s + .5) / steps)
                await pg.mouse.wheel(0, dy * k * math.pi / 2 / steps)
                await asyncio.sleep(ms / 1000 / steps)

        await pg.mouse.move(mouse["x"], mouse["y"])
        await asyncio.sleep(0.6)
        ev("start", [0, 0, W, H])
        await asyncio.sleep(0.8)

        # 1. type the artist into the search bar
        await click("#url", 800, "search")
        await asyncio.sleep(0.3)
        ev("type", await box("#url"))
        await pg.keyboard.type("Rossi", delay=140)
        await asyncio.sleep(1.0)
        ev("suggest", await box("#suggest"))
        await click(await pg.locator("#suggest >> text=Rossi.").first.element_handle(), 700, "pick_artist")
        await asyncio.sleep(1.2)
        ev("suggest2", await box("#suggest"))
        await click(await pg.locator("#suggest >> text=On Your Mind").first.element_handle(), 700, "pick_track")
        await pg.wait_for_selector("[data-add]", timeout=30000)
        await asyncio.sleep(1.2)
        qcard = """() => { const b = document.querySelector('[data-add]'); let e = b; while (e && e.getBoundingClientRect().width < 700) e = e.parentElement;
            const r = e.getBoundingClientRect(); return [r.x, r.y, r.width, r.height] }"""
        await asyncio.sleep(0.8)                         # let the page finish its own scroll
        qb = await pg.evaluate(qcard)
        if qb[1] < -5:                                   # bring the searched track back into view
            await wheel(qb[1] - 70, 700); await asyncio.sleep(0.5)
            qb = await pg.evaluate(qcard)
        ev("results", qb)

        # 2. scroll down and add tracks
        for title in ADD:
            btn = await pg.evaluate_handle("""t => [...document.querySelectorAll('[data-add]')].find(b => {
                const row = b.closest('.rrow, article, li') || b.parentElement.parentElement.parentElement;
                return row && row.innerText.includes(t) && !row.innerText.includes('YOUR TRACK'); })""", title)
            h = btn.as_element()
            bb = await h.bounding_box()
            target = H * 0.5
            if abs(bb["y"] - target) > 120:
                ev("scroll")
                await wheel(bb["y"] - target, 1100)
                await asyncio.sleep(0.35)
            row = await h.evaluate_handle("b => b.closest('.rrow, article, li') || b.parentElement.parentElement.parentElement")
            ev("row", await box(row.as_element()), title=title)
            await click(h, 600, "add")
            await asyncio.sleep(0.9)
            print("  set:", await pg.evaluate("JSON.parse(localStorage.getItem('ss_set')||'[]').length"),
                  await pg.evaluate("document.querySelector('#set-fab').outerHTML.slice(0,120)"), await h.inner_text())
            ev("fab", await box("#fab-open"))

        # 3. open the set builder (a whole page now)
        await asyncio.sleep(0.4)
        for _ in range(4):
            await pg.mouse.wheel(0, -40); await asyncio.sleep(0.06)
        await asyncio.sleep(0.5)
        fb = await box("#fab-open")
        await move(W - 9, fb[1] + fb[3] / 2, 1000)
        await asyncio.sleep(0.12)
        fb = await box("#fab-open")
        ev("open_set", fb)
        await pg.mouse.down(); await asyncio.sleep(0.07); await pg.mouse.up()
        await pg.wait_for_selector("#set-panel.open", timeout=5000)
        await asyncio.sleep(1.6)
        ev("panel", [0, 0, W, H])
        ev("summary", await box("#set-summary"), text=await pg.inner_text("#set-summary"))

        order = lambda: pg.evaluate("[...document.querySelectorAll('#set-list .set-item .t')].map(e=>e.textContent).join(' | ')")

        async def drag(frm, to):
            """Grab a track by its grip and slide it sideways into another slot: the cards glide aside, it snaps in."""
            items = await pg.query_selector_all("#set-list .set-item")
            g = await items[frm].query_selector(".grip")
            gb = await g.bounding_box()
            sx, sy = gb["x"] + gb["width"] / 2, gb["y"] + gb["height"] / 2
            await move(sx, sy, 700)
            ev("grab", await box(await items[frm].query_selector(".set-card")))
            await pg.mouse.down(); await asyncio.sleep(0.25)
            dirn = 1 if to > frm else -1
            x, v = sx, 0.0
            for k in range(600):             # ease up to a steady glide until the dashed slot is where we want it
                v = min(5.0, v + 0.14); x += dirn * v
                await pg.mouse.move(x, sy); mouse.update(x=x, y=sy)
                await asyncio.sleep(0.016)
                if await pg.evaluate("drag ? drag.to : -1") == to:
                    break
            # steer the floating card onto the dashed slot, closing part of the gap each frame
            # (aim at where the slot ends up, not where it is mid-slide)
            gapjs = """() => { const g = document.querySelector('.drag-ghost'); if (!g || !drag) return [0, 0];
                const st = document.querySelector('#set-stage'), sr = st.getBoundingClientRect(), s = drag.slots[drag.to], r = g.getBoundingClientRect();
                return [sr.left - st.scrollLeft + s.x - r.left, sr.top - st.scrollTop + s.y - r.top] }"""
            y, calm = sy, 0
            for k in range(240):
                dx, dy = await pg.evaluate(gapjs)
                if abs(dx) < 0.8 and abs(dy) < 0.8:
                    calm += 1
                    if calm >= 6: break
                else:
                    calm = 0
                x += max(-6.0, min(6.0, dx * 0.16)); y += max(-6.0, min(6.0, dy * 0.16))
                await pg.mouse.move(x, y); mouse.update(x=x, y=y)
                await asyncio.sleep(0.016)
            await asyncio.sleep(0.25)
            await pg.mouse.up()
            ev("drop", [x - 80, y - 120, 160, 300])
            await asyncio.sleep(0.6)
            print("   ", await order())

        await move(W * 0.5, H * 0.62, 500)
        ev("list", await box("#set-stage"))
        await asyncio.sleep(0.5)
        await drag(3, 2)          # move a couple of tracks around
        await asyncio.sleep(0.9)
        await drag(0, 1)
        await asyncio.sleep(0.9)
        ev("summary", await box("#set-summary"), text=await pg.inner_text("#set-summary"))

        # tap the coloured play button between two tracks that don't quite mix: it plays the transition
        # (no player bar in the video) and the details for that pair open under the set
        hb = await pg.query_selector("#set-list .link-dot.ok .st-hear") or await pg.query_selector("#set-list .link-dot.bad .st-hear")
        print("    play button:", await hb.evaluate("e => e.closest('.link-dot').className"))
        await click(hb, 900, "hear")
        await asyncio.sleep(2.2)
        await pg.evaluate("stopMix && stopMix()")
        ev("detail", await box("#set-detail"))
        await asyncio.sleep(0.6)

        # Fix this gap, then pick a track to fill it
        gap = await pg.query_selector("#set-detail [data-gap]")
        await click(gap, 900, "gap_btn")
        await pg.wait_for_selector("#set-detail .gap-box:not([hidden]) .gap-item", timeout=60000)
        await asyncio.sleep(1.0)
        ev("gap_box", await box("#set-detail .gap-box"))
        ins = await pg.query_selector("#set-detail .gap-item .ins")
        await asyncio.sleep(0.6)
        await click(ins, 800, "insert")
        await asyncio.sleep(1.4)
        ev("summary", await box("#set-summary"), text=await pg.inner_text("#set-summary"))
        print("    after insert:", await order())

        # Smart order
        await asyncio.sleep(0.6)
        await click("#set-smart", 1000, "smart")
        await asyncio.sleep(1.8)
        print("    smart:", await order())
        await asyncio.sleep(1.2)
        ev("end", [0, 0, W, H])
        await asyncio.sleep(0.5)
        await cdp.send("Page.stopScreencast")
        await asyncio.sleep(0.5)
        await pg.screenshot(path=f"{OUT}/last.png")
        await b.close()
    json.dump(frames, open(f"{OUT}/frames.json", "w")); json.dump(mlog, open(f"{OUT}/mouse.json", "w"))
    json.dump(events, open(f"{OUT}/events.json", "w"), indent=1)
    print("frames", len(frames))

asyncio.run(main())
