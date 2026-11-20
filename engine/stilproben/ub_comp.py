"""Unterbau-Mischform, Schritt 2: 2,5D-Kamerafahrt durch die Miniaturwelt + animierte Ebenen (Regen, Lichter gehen aus, Countdown).
python3 ub_comp.py STILLDIR OUT.mp4"""
import sys, math, subprocess, numpy as np, cv2, OpenEXR
from PIL import Image, ImageDraw, ImageFont
D_IN, OUT = sys.argv[1], sys.argv[2]
W, H, FPS, DUR = 1920, 1080, 30, 15.0
on = cv2.cvtColor(cv2.imread(D_IN + "/on.png"), cv2.COLOR_BGR2RGB).astype(np.float32)
off = cv2.cvtColor(cv2.imread(D_IN + "/off.png"), cv2.COLOR_BGR2RGB).astype(np.float32)
ex = OpenEXR.File(D_IN + "/depth.exr")
ch = {k: v for part in ex.parts for k, v in part.channels.items()}
zk = [k for k in ch if k.endswith("Depth.Z") or k.endswith(".Z") or k == "Z"][0]
Z = np.array(ch[zk].pixels, np.float32)
Z = np.clip(Z, 0, np.percentile(Z, 99)); near = 1 - (Z - Z.min()) / (Z.max() - Z.min() + 1e-6)   # 1 = nah
near = cv2.GaussianBlur(near, (0, 0), 3)
off = off * 0.55                                   # ohne Fensterlicht wirkt die Stadt dunkler

# Fenster-Maske (was beim Ausschalten dunkel wird) und "dein Haus" = ein Fenster vorne Mitte
lum = lambda a: a.mean(axis=2)
win = (((lum(on) - lum(off)) > 50) & (lum(off) < 45)).astype(np.float32)
win = cv2.dilate(win, np.ones((3, 3), np.uint8)); win = cv2.GaussianBlur(win, (0, 0), 1.2)
_Y, _X = np.mgrid[:H, :W]
cand = ((win > 0.6) * (_Y > H * 0.55) * (_Y < H * 0.7) * (np.abs(_X - W * 0.55) < W * 0.2)).astype(np.float32)
yy, xx = np.unravel_index(np.argmax(cv2.GaussianBlur(cand, (0, 0), 6)), cand.shape)
MY = np.zeros((H, W), np.float32); cv2.circle(MY, (int(xx), int(yy)), 34, 1.0, -1); MY = cv2.GaussianBlur(MY, (0, 0), 4)
# Ausschalt-Reihenfolge: Strasse fuer Strasse (Blöcke) von hinten links nach vorne rechts, mit Zufall
rng = np.random.default_rng(2)
blocks = cv2.resize(rng.random((9, 16)).astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST)
order = 0.55 * (np.mgrid[:H, :W][1] / W) + 0.25 * (1 - np.mgrid[:H, :W][0] / H) + 0.2 * blocks   # 0..1

def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)
def eo(u): u = min(max(u, 0), 1); return 1 - (1 - u) ** 3
YY, XX = np.mgrid[:H, :W].astype(np.float32)
TS = np.clip((np.abs(YY - H * 0.52) - H * 0.16) / (H * 0.22), 0, 1)

def warp(img, t):
    """2,5D: Zoom + seitliche Fahrt, nahe Teile bewegen sich staerker."""
    u = ease(t / DUR)
    z = 1.04 + 0.16 * u; px = -60 + 140 * u; py = 20 - 40 * u
    cx, cy = W / 2, H / 2
    k = 0.35 + 0.65 * near
    mx = cx + (XX - cx) / (1 + (z - 1) * k) - px * k
    my = cy + (YY - cy) / (1 + (z - 1) * k) - py * k
    return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

class Rain:
    def __init__(s, n=900):
        r = np.random.default_rng(5); s.x = r.uniform(0, W, n); s.y = r.uniform(0, H, n); s.v = r.uniform(900, 1500, n); s.l = r.uniform(10, 24, n)
    def draw(s, img, t):
        ov = np.zeros((H, W), np.float32); y = (s.y + s.v * t) % H; x = (s.x + 0.12 * s.v * t) % W
        for xi, yi, li in zip(x.astype(int), y.astype(int), s.l.astype(int)):
            cv2.line(ov, (xi, yi), (int(xi + li * 0.12), yi + li), 0.5, 1, cv2.LINE_AA)
        return img + ov[..., None] * np.array([150, 170, 210], np.float32) * 0.35
RAIN = Rain()

F = lambda s: ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", s)
def label(fr, text, x, y, size=58, sub=None, alpha=1.0, orange=False):
    im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    f = F(size); w = d.textlength(text, font=f)
    d.rounded_rectangle([x, y, x + w + 70, y + size + 44], 10, fill=(8, 14, 28, int(200 * alpha)))
    d.rectangle([x, y, x + 8, y + size + 44], fill=(255, 110, 20, int(255 * alpha)))
    d.text((x + 36, y + 18), text, font=f, fill=((255, 140, 50) if orange else (235, 238, 245)) + (int(255 * alpha),))
    if sub: d.text((x + 36, y + size + 52), sub, font=F(34), fill=(170, 180, 200, int(255 * alpha)))
    im.alpha_composite(ov); return np.array(im.convert("RGB")).astype(np.float32)

def frame(t):
    # Lichter: 6.0-10.5 s Strasse fuer Strasse aus, dein Haus bleibt bis 12.2 s an
    sweep = (t - 6.0) / 4.5
    m_off = np.clip((sweep * 1.15 - order) * 8, 0, 1) * win
    mine = MY * (1 - eo((t - 12.2) / 0.5))
    m_off = np.maximum(m_off - mine * win * 3, 0) if t < 12.7 else m_off
    flick = 1.0 if not (6.0 < t < 10.5) else (0.92 + 0.08 * math.sin(t * 37))
    g = np.clip(sweep, 0, 1) * (1 - 0.0)
    base = on * (1 - 0.45 * g)                               # Stadt wird insgesamt dunkler
    img = base * (1 - m_off[..., None]) * flick + off * m_off[..., None]
    keep = (MY * win)[..., None] * (1 - eo((t - 12.2) / 0.5))
    img = img * (1 - keep) + on * keep
    if False: img = img * (1 - MY[..., None] * eo((t - 12.2) / 0.5)) + off * (MY[..., None] * eo((t - 12.2) / 0.5))
    fr = warp(img.astype(np.float32), t)
    bl = cv2.GaussianBlur(fr, (0, 0), 7)                     # Tilt-Shift: oben und unten unscharf
    fr = fr * (1 - TS[..., None]) + bl * TS[..., None]
    fr = RAIN.draw(fr, t)
    vig = 1 - 0.35 * (((XX - W / 2) / (W / 2)) ** 2 + ((YY - H / 2) / (H / 2)) ** 2)
    fr = fr * vig[..., None]
    # Countdown in der Welt (Uhr springt), dann "Dein Haus"
    mins = 17 * 60 + 56 + int(min(t, 6.0) / 6.0 * 4)
    fr = label(fr, f"Tag 2 · {mins // 60:02d}:{mins % 60:02d} Uhr", 90, 80, 58, "Countdown", orange=t >= 6.0)
    if 10.6 < t < 14.6:
        al = min(1, (t - 10.6) / 0.3, (14.6 - t) / 0.3)
        u = ease(t / DUR); z = 1.04 + 0.16 * u; px = -60 + 140 * u; py = 20 - 40 * u; k = 0.35 + 0.65 * near[yy, xx]
        sx = W / 2 + (xx - W / 2 + px * k) * (1 + (z - 1) * k); sy = H / 2 + (yy - H / 2 + py * k) * (1 + (z - 1) * k)
        fr = label(fr, "Dein Haus", int(sx) - 110, int(sy) - 150, 46, None, al)
    return np.clip(fr, 0, 255).astype(np.uint8)

p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("ok")
