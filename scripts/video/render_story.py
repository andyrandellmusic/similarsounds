"""Turn the recorded frames into a cinematic 1080p MP4: speed ramps, eased zooms/pans, logo end card.

Usage: .venv/bin/python scripts/video/render.py RECDIR OUT.mp4 [--preview]
"""
import bisect, json, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

REC, OUT = sys.argv[1], sys.argv[2]
PREVIEW = "--preview" in sys.argv
FPS, OW, OH = 30, 1920, 1080
CW, CH, SCALE = 1600, 900, 2          # page size in CSS px, and frame pixels per CSS px

frames = json.load(open(f"{REC}/frames.json"))
ft = [f["t"] for f in frames]

events = json.load(open(f"{REC}/events.json"))
def T(kind, n=0):
    return [e for e in events if e["kind"] == kind][n]["t"]
def B(kind, n=0):
    return [e for e in events if e["kind"] == kind][n]["box"]

# raw recording time -> output time: anchor (raw, output-seconds-after-previous)
st = T("start")
rows = [e for e in events if e["kind"] == "row"]
adds = [e for e in events if e["kind"] == "add"]
F = lambda n: T("flow", n)
S = lambda n: T("summary", n)

# ---- time: (raw moment, seconds of video since the previous moment) ----
ANCH = [(st - 0.35, 0), (st + 1.2, 1.4),                                           # full screen
        (T("search"), 1.0), (T("type"), 0.2), (T("type") + 0.9, 0.9),          # into the search bar, typing
        (T("suggest"), 0.6), (T("pick_artist"), 0.8), (T("suggest2"), 0.6), (T("pick_track"), 0.7),
        (T("pick_track") + 0.4, 0.45), (T("results"), 0.25), (T("results") + 0.05, 1.3)]   # lock onto the searched track
for i, (r, a) in enumerate(zip(rows, adds)):
    ANCH += [(r["t"], 1.6 if i == 0 else 1.4), (a["t"], 0.8), (a["t"] + 1.0, 0.6)]
ANCH += [(T("open_set") - 1.6, 1.4), (T("open_set"), 1.3), (T("panel"), 0.9),   # out to 100%, into the SET tab
         (T("list"), 0.6), (T("grab", 0), 0.9), (T("drop", 0), 1.6), (T("grab", 1), 1.1), (T("drop", 1), 1.6),
         (S(3), 0.6), (T("line"), 1.3), (T("line") + 0.9, 0.9), (T("gap_btn"), 0.9), (T("gap_box"), 1.0), (T("insert"), 1.4), (S(4), 0.8),
         (F(1), 1.0), (T("smart"), 1.5), (T("smart") + 0.25, 0.3)]                # click Smart order, then straight to the logo
TIME, acc = [], 0.0
SLOW = 1.1                                       # 10% slower than the last version
for r, d in ANCH:
    acc += d * SLOW; TIME.append((r, acc))

# ---- camera keyframes: (raw time, centre x, centre y, zoom) in CSS px; zoom 1 = whole page (100%) ----
sb = B("search")
LIST_Z = 1.45                                    # just wide enough for a whole track box (1008px)
LY = 310                                         # list view: the searched track shows at the top, Add buttons stay in frame
gb, ib, fb, lb = B("gap_btn"), B("insert"), B("open_set"), B("line")
CAM = [(st - 0.35, 800, 450, 1.0), (st + 1.2, 800, 450, 1.0),
       (T("search"), sb[0] + 330, sb[1] + 24, 2.3), (T("type"), sb[0] + 290, sb[1] + 24, 2.5),
       (T("type") + 0.9, sb[0] + 300, sb[1] + 24, 2.6),
       (T("suggest"), 800, 600, 1.5), (T("pick_artist"), 720, B("pick_artist")[1] + 30, 1.8),
       (T("suggest2"), 790, 590, 1.5), (T("pick_track"), 690, B("pick_track")[1] + 20, 1.8),
       (T("pick_track") + 0.4, 800, LY, LIST_Z), (T("results"), 800, LY, LIST_Z), (T("results") + 0.05, 800, LY, LIST_Z)]
for r, a in zip(rows, adds):
    ab = a["box"]; ax, ay = ab[0] + ab[2] / 2, ab[1] + ab[3] / 2
    CAM += [(r["t"], 800, LY, LIST_Z), (a["t"] - 0.15, ax, ay, 2.7),         # into Add to set, click
            (a["t"] + 0.9, 800, LY, LIST_Z)]                                  # back out, keep scrolling
CAM += [(T("open_set") - 1.6, 800, 450, 1.0), (T("open_set") - 1.0, 800, 450, 1.0),   # 100%
        (T("open_set"), fb[0] + fb[2] / 2, fb[1] + fb[3] / 2, 3.0),                   # into the SET tab
        ]
pn = B("panel"); PZ = 1.3; PX = 1600 - 1600 / PZ / 2          # zoomed onto the set builder, right edge to right edge
g0, g1 = B("grab", 0), B("grab", 1)
CAM += [(T("panel"), PX, 346, PZ), (T("list"), PX, 346, PZ),                                  # top: columns + first tracks
        (T("grab", 0) - 0.4, PX, 554, PZ), (T("drop", 0) + 0.6, PX, 554, PZ),                  # follow the first move
        (T("grab", 1) - 0.4, PX, 400, PZ), (S(3), PX, 420, PZ),                                # and the second
        (T("line") - 0.1, lb[0] + lb[2] / 2, lb[1] + 20, 2.6),                                 # onto the orange "Workable" line
        (T("line") + 0.9, (lb[0] + gb[0] + gb[2]) / 2, lb[1] + 20, 2.4),                        # its details open
        (T("gap_btn") - 0.1, gb[0] + gb[2] / 2, gb[1] + gb[3] / 2, 2.8),                       # into "Fix this gap"
        (T("gap_box") - 0.2, PX, 470, PZ), (S(4), PX, 470, PZ),                                # back out, pick a track
        (F(1), 1600 - 340, 192, 2.35), (F(2) + 1.6, 1600 - 340, 192, 2.35)]                    # top half: columns + Smart order
CAM.sort()

END_VIDEO = TIME[-1][1]
FADE_OUT, CARD_IN, CARD_HOLD, CARD_OUT = 0.7, 0.7, 3.0, 0.7
TOTAL = END_VIDEO + FADE_OUT + CARD_IN + CARD_HOLD + CARD_OUT
LOGO_AT = END_VIDEO + FADE_OUT + CARD_IN          # the moment the logo has landed
print(f"logo lands at {LOGO_AT:.2f}s of {TOTAL:.2f}s", flush=True)
BG = (11, 11, 15)


def out_to_raw(t):
    outs = [o for _, o in TIME]
    if t <= outs[0]: return TIME[0][0]
    if t >= outs[-1]: return TIME[-1][0] + (t - outs[-1]) * 0.6
    i = bisect.bisect_right(outs, t) - 1
    (r0, o0), (r1, o1) = TIME[i], TIME[i + 1]
    return r0 + (r1 - r0) * (t - o0) / (o1 - o0)


def ease(k):  # smooth in-out
    return k * k * k * (k * (6 * k - 15) + 10)


def camera(r):
    if r <= CAM[0][0]: return CAM[0][1:]
    if r >= CAM[-1][0]: return CAM[-1][1:]
    i = bisect.bisect_right([c[0] for c in CAM], r) - 1
    a, b = CAM[i], CAM[i + 1]
    k = ease((r - a[0]) / (b[0] - a[0]))
    z = math.exp(math.log(a[3]) + (math.log(b[3]) - math.log(a[3])) * k)
    return a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, z


_cache = {}
def frame_at(r):
    i = max(0, bisect.bisect_right(ft, r) - 1)
    if i not in _cache:
        _cache.clear()
        _cache[i] = Image.open(f"{REC}/frames/{frames[i]['i']:05d}.jpg").convert("RGB")
    return _cache[i]


vig = Image.new("L", (OW, OH), 0)
d = ImageDraw.Draw(vig)
d.ellipse((-OW * 0.25, -OH * 0.35, OW * 1.25, OH * 1.35), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(220))
dark = Image.new("RGB", (OW, OH), (0, 0, 0))
bg = Image.new("RGB", (OW, OH), BG)
card = Image.open(f"{REC}/endcard.png").convert("RGB").resize((OW, OH))


def video_frame(t):
    r = out_to_raw(t)
    cx, cy, z = camera(r)
    w, h = CW / z, CH / z
    cx = min(max(cx, w / 2), CW - w / 2); cy = min(max(cy, h / 2), CH - h / 2)
    box = tuple(round(v * SCALE) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    img = frame_at(r).crop(box).resize((OW, OH), Image.LANCZOS)
    img = Image.composite(img, Image.blend(img, dark, 0.45), vig)
    return img


def render(t):
    if t < END_VIDEO:
        img = video_frame(t)
        if t < 0.5: img = Image.blend(bg, img, ease(t / 0.5))
        return img
    t2 = t - END_VIDEO
    if t2 < FADE_OUT:
        return Image.blend(video_frame(t), bg, ease(t2 / FADE_OUT))
    t3 = t2 - FADE_OUT
    s = 1.06 - 0.06 * ease(min(1, (t3) / (CARD_IN + CARD_HOLD)))
    cw, ch = round(OW * s), round(OH * s)
    c = card.resize((cw, ch), Image.LANCZOS).crop(((cw - OW) // 2, (ch - OH) // 2, (cw - OW) // 2 + OW, (ch - OH) // 2 + OH))
    if t3 < CARD_IN: return Image.blend(bg, c, ease(t3 / CARD_IN))
    if t3 < CARD_IN + CARD_HOLD: return c
    return Image.blend(c, bg, ease(min(1, (t3 - CARD_IN - CARD_HOLD) / CARD_OUT)))


if PREVIEW:
    for t in [float(a) for a in sys.argv[3:] if a[0].isdigit()]:
        render(t).save(f"{OUT}_{t:05.1f}.jpg", quality=85)
    sys.exit()

n = int(TOTAL * FPS)
ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo",
                       "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                       "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for k in range(n):
    ff.stdin.write(render(k / FPS).tobytes())
    if k % 150 == 0: print(f"{k}/{n}", flush=True)
ff.stdin.close(); ff.wait()
print("done", OUT, f"{TOTAL:.1f}s")

