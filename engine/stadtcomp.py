"""Compositing für die Unterbau-Modellstadt: aus den Blender-Standbildern (A/B/Tiefe, engine/stadt.py) bewegte Einstellungen.
2,5D-Kamerafahrt mit echter Tiefe, Übergang A→B (Lichter aus, Regal leert sich, Tor öffnet), Lichter auf Pfaden (Warenstrom),
Uhr/Fallblatt/Schilder perspektivisch IN der Welt, Tilt-Shift, Korn, Vignette.

python3 engine/stadtcomp.py plan.json RENDERDIR OUT.mp4 [--from i --to j]
plan.json: [{"id", "dur", "move": "push|flight|pan|still", "trans": "diff|lights|wipe_down|wipe_lr|none", "t_trans": [0.2, 0.85],
             "fx": [{"type": "dots", "path": "route_autobahn", "n": 40, "speed": 0.06, "stop": 0.5},
                    {"type": "clock", "anchor": "uhr", "from": 0, "to": 360},                # Minuten
                    {"type": "tafel", "anchor": "tafel", "texts": ["TAG 1", "TAG 2"]},
                    {"type": "label", "text": "Dein Haus", "anchor": "haus"},
                    {"type": "lines", "pairs": ["de_HHH", …], "fade": [0.3, 0.8]},
                    {"type": "frame", "anchor": "milchfach"}]}]
"""
import sys, os, json, math, subprocess, argparse
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

OW, OH, FPS = 1920, 1080, 25
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
ORANGE = np.array([255, 120, 30], np.float32); WARM = np.array([255, 190, 120], np.float32)

def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def eo(u): u = min(max(u, 0.0), 1.0); return 1 - (1 - u) ** 3

def load_rgb(p): return cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32)

def load_depth(p, W, H):
    try:
        import OpenEXR
        ex = OpenEXR.File(p); ch = {k: v for part in ex.parts for k, v in part.channels.items()}
        zk = [k for k in ch if k.endswith("Depth.Z") or k.endswith(".Z") or k == "Z"][0]
        Z = np.array(ch[zk].pixels, np.float32)
    except Exception:
        Z = cv2.imread(p, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_ANYCOLOR)
        Z = (Z[..., 0] if Z is not None and Z.ndim == 3 else Z)
        if Z is None: return np.full((H, W), 0.5, np.float32)
        Z = Z.astype(np.float32)
    Z = np.where(np.isfinite(Z), Z, np.nan); hi = np.nanpercentile(Z, 98); Z = np.nan_to_num(Z, nan=hi); Z = np.clip(Z, 0, hi)
    near = 1 - (Z - Z.min()) / (Z.max() - Z.min() + 1e-6)
    return cv2.GaussianBlur(near.astype(np.float32), (0, 0), 3)

def font(sz, bold=True): return ImageFont.truetype(FB if bold else FM, sz)

def quad_overlay(img, quad, tex_rgba):
    """RGBA-Textur perspektivisch auf ein 4-Eck (oben-links, oben-rechts, unten-rechts, unten-links) legen."""
    th, tw = tex_rgba.shape[:2]
    src = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]); dst = np.float32([q[:2] for q in quad])
    Hm = cv2.getPerspectiveTransform(src, dst)
    H, W = img.shape[:2]
    warped = cv2.warpPerspective(tex_rgba, Hm, (W, H), flags=cv2.INTER_LINEAR)
    a = warped[..., 3:4] / 255.0
    return img * (1 - a) + warped[..., :3] * a

def tex_text(text, w=1024, h=290, fg=(245, 230, 200), bg=(8, 10, 14, 255), size=170):
    im = Image.new("RGBA", (w, h), bg); d = ImageDraw.Draw(im); f = font(size)
    # Fallblatt-Raster: Kacheln mit Trennfuge
    n = max(1, len(text)); cw = w / max(n, 8)
    tw = d.textlength(text, font=f)
    if tw > w * 0.92:
        f = font(int(size * w * 0.92 / tw)); tw = d.textlength(text, font=f)
    d.text(((w - tw) / 2, h / 2), text, font=f, fill=fg, anchor="lm")
    d.line([(0, h / 2), (w, h / 2)], fill=(0, 0, 0, 255), width=4)
    return np.array(im)

def tex_clock(minutes, size=512):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    d.ellipse([8, 8, size - 8, size - 8], fill=(236, 228, 210, 255), outline=(40, 40, 46, 255), width=10)
    for k in range(12):
        a = k / 12 * 2 * math.pi; r1, r2 = c * 0.78, c * 0.9
        d.line([(c + r1 * math.sin(a), c - r1 * math.cos(a)), (c + r2 * math.sin(a), c - r2 * math.cos(a))], fill=(30, 30, 36, 255), width=12 if k % 3 == 0 else 6)
    h = (minutes / 60.0) % 12; m = minutes % 60
    for ang, ln, wd, col in ((h / 12 * 2 * math.pi, 0.5, 18, (20, 20, 26, 255)), (m / 60 * 2 * math.pi, 0.74, 10, (20, 20, 26, 255))):
        d.line([(c, c), (c + c * ln * math.sin(ang), c - c * ln * math.cos(ang))], fill=col, width=wd)
    d.ellipse([c - 16, c - 16, c + 16, c + 16], fill=(255, 110, 20, 255))
    return np.array(im)

def label(img, text, x, y, alpha=1.0, size=44, sub=None):
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    f = font(size); w = d.textlength(text, font=f); x = int(min(max(x - w / 2 - 30, 20), im.width - w - 90)); y = int(min(max(y, 20), im.height - 120))
    d.rounded_rectangle([x, y, x + w + 60, y + size + 34], 8, fill=(8, 14, 28, int(205 * alpha)))
    d.rectangle([x, y, x + 7, y + size + 34], fill=(255, 110, 20, int(255 * alpha)))
    d.text((x + 30, y + 14), text, font=f, fill=(238, 240, 246, int(255 * alpha)))
    if sub: d.text((x + 30, y + size + 40), sub, font=font(28, False), fill=(175, 185, 205, int(255 * alpha)))
    im.alpha_composite(ov); return np.array(im.convert("RGB")).astype(np.float32)

def glow_dots(img, pts, rad=5, col=WARM, gain=1.0):
    if not pts: return img
    H, W = img.shape[:2]; ov = np.zeros((H, W), np.float32)
    for x, y, a in pts:
        if -20 < x < W + 20 and -20 < y < H + 20: cv2.circle(ov, (int(x), int(y)), rad, float(a), -1, cv2.LINE_AA)
    core = ov; halo = cv2.GaussianBlur(ov, (0, 0), rad * 2.5)
    return img + (core * 0.9 + halo * 1.6)[..., None] * col * 0.9 * gain

def path_point(P, u):
    """u in [0,1] entlang der Polylinie, gleichmäßig nach Index (Punkte sind in 3D gleich weit verteilt); None hinter der Kamera"""
    n = len(P); x = (u % 1.0) * (n - 1); i = int(x); f = x - i; a, b = P[i], P[min(i + 1, n - 1)]
    if a[2] <= 0.05 or b[2] <= 0.05: return None
    return (a[0] * (1 - f) + b[0] * f, a[1] * (1 - f) + b[1] * f)

class Shot:
    def __init__(s, spec, rdir, W, H):
        s.sp = spec; b = os.path.join(rdir, spec["id"])
        s.A = load_rgb(b + "_A.png"); s.H, s.W = s.A.shape[:2]
        s.B = load_rgb(b + "_B.png") if os.path.exists(b + "_B.png") else None
        s.near = load_depth(b + "_Z.exr", s.W, s.H)
        s.anc = json.load(open(b + ".json"))["anchors"] if os.path.exists(b + ".json") else {}
        s.YY, s.XX = np.mgrid[:s.H, :s.W].astype(np.float32)
        if s.B is not None:
            diff = np.abs(s.A - s.B).mean(axis=2)
            s.dm = cv2.GaussianBlur((diff > 6).astype(np.float32), (0, 0), 1.5)
            rng = np.random.default_rng(abs(hash(spec["id"])) % 2**32)
            blocks = cv2.resize(rng.random((9, 16)).astype(np.float32), (s.W, s.H), interpolation=cv2.INTER_NEAREST)
            tr = spec.get("trans", "diff")
            if tr == "wipe_down": s.order = s.YY / s.H
            elif tr == "wipe_lr": s.order = s.XX / s.W
            elif tr == "rows": s.order = 0.7 * (1 - s.YY / s.H) + 0.3 * blocks
            elif tr == "fade": s.order = np.zeros_like(s.YY) + 0.5
            else: s.order = 0.5 * (s.XX / s.W) + 0.2 * (1 - s.YY / s.H) + 0.3 * blocks
        h = abs(hash(spec["id"])) % 1000 / 1000.0
        s.dir = (1 if h > 0.5 else -1)
        s.TS = np.clip((np.abs(s.YY - s.H * 0.5) - s.H * 0.2) / (s.H * 0.25), 0, 1) if spec.get("tilt", True) else None

    def warp(s, img, u):
        mv = s.sp.get("move", "push"); d = s.dir
        if mv == "flight": z0, z1, px, py = 1.0, 1.28, 160 * d, -40
        elif mv == "pan": z0, z1, px, py = 1.08, 1.1, 180 * d, 0
        elif mv == "pull": z0, z1, px, py = 1.2, 1.02, -60 * d, 20
        elif mv == "still": z0, z1, px, py = 1.04, 1.06, 10 * d, 0
        else: z0, z1, px, py = 1.03, 1.13, 50 * d, -15
        e = ease(u); z = z0 + (z1 - z0) * e; dx = -px / 2 + px * e; dy = -py / 2 + py * e
        k = 0.3 + 0.7 * s.near; cx, cy = s.W / 2, s.H / 2
        mx = cx + (s.XX - cx) / (1 + (z - 1) * k) - dx * k; my = cy + (s.YY - cy) / (1 + (z - 1) * k) - dy * k
        return cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def frame(s, t):
        sp = s.sp; dur = sp["dur"]; u = t / dur
        img = s.A.copy()
        if s.B is not None:
            a0, a1 = sp.get("t_trans", [0.2, 0.8]); g = (u - a0) / max(a1 - a0, 1e-3)
            if sp.get("trans") == "fade":
                m = np.full(s.order.shape, ease(g), np.float32)
            else:
                m = np.clip((g * 1.25 - s.order) * 7, 0, 1)
                if sp.get("trans") in ("lights",): m = m * s.dm
            img = img * (1 - m[..., None]) + s.B * m[..., None]
        for fx in sp.get("fx", []):
            img = s.effect(img, fx, t, u)
        fr = s.warp(img.astype(np.float32), u)
        if s.TS is not None:
            bl = cv2.GaussianBlur(fr, (0, 0), 6); fr = fr * (1 - s.TS[..., None]) + bl * s.TS[..., None]
        return fr

    def effect(s, img, fx, t, u):
        ty = fx["type"]; A = s.anc
        if ty == "dots" and fx["path"] in A:
            P = A[fx["path"]]; n = fx.get("n", 30); sp = fx.get("speed", 0.05); pts = []
            stop = fx.get("stop"); fade = 1.0
            if stop is not None:
                tt = min(u, stop); fade = 1 - ease((u - stop) / 0.25) if u > stop else 1.0
            else: tt = u
            for k in range(n):
                q = path_point(P, k / n + tt * sp * s.sp["dur"])
                if q is not None: pts.append((q[0], q[1], fade))
            return glow_dots(img, pts, fx.get("r", 4))
        if ty == "lines":
            fa = fx.get("fade"); al = 1.0
            if fa: al = 1 - ease((u - fa[0]) / (fa[1] - fa[0]))
            if fx.get("grow"): al = ease(u / fx["grow"])
            ov = np.zeros(img.shape[:2], np.float32)
            for k in fx["pairs"]:
                if k in A:
                    (x1, y1, _), (x2, y2, _) = A[k]
                    cv2.line(ov, (int(x1), int(y1)), (int(x2), int(y2)), 1.0, 3, cv2.LINE_AA)
            if "cities" in fx and fx["cities"] in A:
                for x, y, _ in A[fx["cities"]]: cv2.circle(ov, (int(x), int(y)), 6, 1.0, -1, cv2.LINE_AA)
            g = ov + cv2.GaussianBlur(ov, (0, 0), 8) * 2
            return img + (g * al)[..., None] * ORANGE * 0.6
        if ty == "clock" and fx["anchor"] in A:
            mins = fx["from"] + (fx["to"] - fx["from"]) * eo((u - fx.get("t0", 0.1)) / fx.get("tl", 0.6))
            return quad_overlay(img, A[fx["anchor"]], tex_clock(mins))
        if ty == "tafel" and fx["anchor"] in A:
            texts = fx["texts"]; k = min(len(texts) - 1, int(u * len(texts) * fx.get("rate", 1.0)))
            tx = tex_text(texts[k], fg=tuple(fx.get("fg", (245, 225, 190))))
            # Fallblatt-Klappen: kurz nach jedem Wechsel die obere Hälfte zusammenstauchen
            ph = (u * len(texts) * fx.get("rate", 1.0)) % 1
            if ph < 0.08 and k > 0:
                sq = int(tx.shape[0] / 2 * (ph / 0.08)); tx = tx.copy(); tx[:tx.shape[0] // 2 - sq] = (8, 10, 14, 255)
            return quad_overlay(img, A[fx["anchor"]], tx)
        if ty == "label":
            al = min(1, (u - fx.get("t0", 0.15)) / 0.1, (fx.get("t1", 0.95) - u) / 0.1)
            if al <= 0: return img
            if "anchor" in fx and fx["anchor"] in A:
                x, y, _ = A[fx["anchor"]][0]; y = y - 150
            else:
                x, y = fx.get("pos", (s.W * 0.5, s.H * 0.12))
            return label(img, fx["text"], x, y, al, fx.get("size", 44), fx.get("sub"))
        if ty == "frame" and fx["anchor"] in A:
            q = np.array([p[:2] for p in A[fx["anchor"]]], np.int32); al = ease((u - fx.get("t0", 0.2)) / 0.2)
            ov = np.zeros(img.shape[:2], np.float32); cv2.polylines(ov, [q], True, 1.0, 4, cv2.LINE_AA)
            return img + (ov + cv2.GaussianBlur(ov, (0, 0), 5) * 1.5)[..., None] * ORANGE * al * 0.8
        if ty == "grey":
            g = img.mean(axis=2, keepdims=True); a = fx.get("amount", 0.6) * ease((u - fx.get("t0", 0.3)) / 0.4)
            return img * (1 - a) + g * a * np.array([0.9, 0.95, 1.05])
        if ty == "flicker":
            return img * (0.9 + 0.1 * math.sin(t * 31) * math.sin(t * 7.3))
        return img

def grade(fr, grain_rng):
    H, W = fr.shape[:2]
    fr = cv2.resize(fr, (OW, OH), interpolation=cv2.INTER_CUBIC) if (W, H) != (OW, OH) else fr
    bl = cv2.GaussianBlur(fr, (0, 0), 1.2); fr = fr * 1.35 - bl * 0.35            # leicht schärfen nach Hochskalieren
    YY, XX = np.ogrid[:OH, :OW]
    vig = 1 - 0.32 * (((XX - OW / 2) / (OW / 2)) ** 2 + ((YY - OH / 2) / (OH / 2)) ** 2)
    fr = fr * vig[..., None]
    fr = fr + grain_rng.normal(0, 3.2, (OH // 2, OW // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.float32)
    return np.clip(fr, 0, 255).astype(np.uint8)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("rdir"); ap.add_argument("out")
    ap.add_argument("--from", dest="i0", type=int, default=0); ap.add_argument("--to", dest="i1", type=int, default=10**6)
    a = ap.parse_args()
    plan = json.load(open(a.plan))[a.i0:a.i1]
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    rng = np.random.default_rng(1); n = 0; tacc = 0.0
    for spec in plan:
        sh = Shot(spec, a.rdir, OW, OH)
        tacc += spec["dur"]; frames = int(round(tacc * FPS)) - n
        for k in range(frames):
            p.stdin.write(grade(sh.frame(k / FPS), rng).tobytes())
        n += frames; print("comp", spec["id"], flush=True)
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    main()
