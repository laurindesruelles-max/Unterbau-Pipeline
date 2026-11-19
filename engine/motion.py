"""Unterbau-Motion (Laurin 19.11.2026: „Das Video ist so langweilig“ → Ziel ≥ 60 % Wiedergabe).
Kostenlos, CPU, wird von engine/unterbau.py benutzt.

1) split_shots: lange Einstellungen werden alle ~`cut` Sekunden an Wortgrenzen geschnitten; jeder Teil zeigt
   einen neuen Ausschnitt desselben Bildes (Totale → Nah auf das Motiv → Detail → Gegenschwenk). Das Motiv
   findet die Tiefenkarte (nächste Bildpartie). So entsteht Schnitt-Tempo ohne neue Bilder.
2) Animierte Grafiken als Overlays (spec.json → overlays):
   - karte:   Europa-/Deutschlandkarte (Natural Earth, gemeinfrei), Länder hervorheben, Routen wachsen,
              Lkw-Punkte fahren, Pins mit Beschriftung. {"type":"karte","view":[lon0,lat0,lon1,lat1],
              "hl":["DE"],"routes":[[[lon,lat],…],…],"pins":[[lon,lat,"Text"],…],"title":"…"}
   - ablauf:  Kette als Band unten, Stationen leuchten nacheinander auf (eigene Wortanker), optional Bruch.
              {"type":"ablauf","steps":[["Molkerei",[3,"Molkerei"]],…],"break":[index, anker]}
   - balken:  Balken wachsen. {"type":"balken","title":"…","bars":[["Lkw",79,"%"],["alle anderen",21,"%"]]}
   - zaehler: große Zahl zählt hoch. {"type":"zaehler","to":9100000,"unit":"t","sub":"…"}
   - tage:    Zeitstrahl Tag 1–3, Fortschritt bis Tag n, Stichpunkte erscheinen gestaffelt.
              {"type":"tage","n":2,"items":["Tankstellen leer","Müll bleibt liegen"]}
Motion-Regeln: Einblenden 200–400 ms ease-out, Ausblenden 150–250 ms ease-in, Gruppen 40–80 ms gestaffelt.
"""
import os, json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
ORANGE = (255, 122, 26); WHITE = (245, 245, 242); PANEL = (5, 14, 30); GREY = (120, 132, 150); RED = (226, 60, 50)
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
_F = {}
def font(p, s):
    k = (p, int(s))
    if k not in _F: _F[k] = ImageFont.truetype(p, int(s))
    return _F[k]
def eout(x): x = min(max(x, 0), 1); return 1-(1-x)**3
def ein(x): x = min(max(x, 0), 1); return x**3
def fade(lt, du, a=0.3, b=0.2): return eout(lt/a)*(1-ein(1-(du-lt)/b) if du-lt < b else 1)
FULL = ("karte", "balken", "zaehler")          # Vollbild-Grafiken: Hintergrund wird abgedunkelt
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ------------------------------------------------------------------ 1) Schnitt-Tempo
VARIANTS = [  # (Zoom-Start, Zoom-Ende, Richtung) – Ausschnitt um das Motiv
    ("nah", 1.42, 1.52), ("detail", 1.75, 1.85), ("total", 1.16, 1.06), ("gegen", 1.30, 1.36)]

def subject(depth):
    """Schwerpunkt der nächsten 12 % des Bildes (Tiefe 1 = nah) → (ox, oy) in Bildanteilen von der Mitte."""
    d = depth; thr = np.quantile(d, 0.88); ys, xs = np.nonzero(d >= thr)
    if len(xs) == 0: return 0.0, 0.0
    h, w = d.shape
    return float(xs.mean()/w-0.5), float(ys.mean()/h-0.5)

def split_shots(T, shots, cut, depth_of):
    out = []
    words = sorted([(p["t0"]+w["s"]) for p in T.parts.values() for w in p["words"]])
    for s in shots:
        dur = s["t1"]-s["t0"]
        if s.get("black") or s.get("xsection") or s.get("clip") or s.get("nosplit") or dur < 1.7*cut:
            out.append(s); continue
        n = max(2, int(round(dur/cut))); cuts = [s["t0"]]
        for k in range(1, n):
            target = s["t0"]+dur*k/n
            c = min((w for w in words if s["t0"]+1.8 < w < s["t1"]-1.8), key=lambda w: abs(w-target), default=None)
            if c and c-cuts[-1] >= 2.0: cuts.append(c)
        cuts.append(s["t1"])
        ox, oy = subject(depth_of(s["img"]))
        for i in range(len(cuts)-1):
            p = dict(s); p["t0"], p["t1"] = cuts[i], cuts[i+1]; p["sub"] = i
            if i > 0:
                name, z0, z1 = VARIANTS[(i-1+hash(s["img"]) % 2) % len(VARIANTS)]
                mx = 0.5*(1-1/z1)*0.9                     # größter erlaubter Versatz
                fx = ox if name != "gegen" else -ox*0.6; fy = oy if name != "gegen" else -oy*0.6
                p["move"] = {"dx": 0.012*(1 if i % 2 else -1), "dy": 0.0, "z0": z0, "z1": z1, "par": 0.05,
                             "ox": float(np.clip(fx, -mx, mx)), "oy": float(np.clip(fy, -mx*0.6, mx*0.6))}
                p["cutfx"] = True
            out.append(p)
    return out

# ------------------------------------------------------------------ 2) Grafiken
_GEO = {}
def geo():
    if "e" not in _GEO: _GEO["e"] = json.load(open(f"{REPO}/assets/geo/europa.json"))
    return _GEO["e"]

class Proj:
    def __init__(self, view, box):
        self.l0, self.b0, self.l1, self.b1 = view; x0, y0, x1, y1 = box
        k = math.cos(math.radians((self.b0+self.b1)/2))
        sx = (x1-x0)/((self.l1-self.l0)*k); sy = (y1-y0)/(self.b1-self.b0); self.s = min(sx, sy); self.k = k
        cx = (x0+x1)/2; cy = (y0+y1)/2; self.cx, self.cy = cx, cy; self.ml = (self.l0+self.l1)/2; self.mb = (self.b0+self.b1)/2
    def __call__(self, lon, lat): return (self.cx+(lon-self.ml)*self.k*self.s, self.cy-(lat-self.mb)*self.s)

_MAP = {}
def basemap(view, hl):
    key = (tuple(view), tuple(hl))
    if key not in _MAP:
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); P = Proj(view, (120, 150, W-120, H-90))
        for iso, polys in geo().items():
            for ring in polys:
                pts = [P(x, y) for x, y in ring]
                if len(pts) > 2: d.polygon(pts, fill=(40, 52, 70, 255) if iso in hl else (22, 31, 46, 255), outline=(70, 84, 104, 255))
        for iso in hl:
            for ring in geo().get(iso, []):
                d.line([P(x, y) for x, y in ring]+[P(*ring[0])], fill=ORANGE+(255,), width=4, joint="curve")
        _MAP[key] = (im, P)
    return _MAP[key]

def _poly_point(pts, f):
    """Punkt bei Anteil f entlang einer Linie"""
    L = [math.dist(pts[i], pts[i+1]) for i in range(len(pts)-1)]; tot = sum(L) or 1; t = f*tot
    for i, l in enumerate(L):
        if t <= l: a = t/(l or 1); return (pts[i][0]+(pts[i+1][0]-pts[i][0])*a, pts[i][1]+(pts[i+1][1]-pts[i][1])*a), i
        t -= l
    return pts[-1], len(pts)-2

def karte(layer, o, lt, du):
    a = fade(lt, du); im, P = basemap(o.get("view", [5.5, 47.0, 15.5, 55.2]), o.get("hl", ["DE"]))
    base = im.copy(); base.putalpha(Image.eval(im.getchannel("A"), lambda v: int(v*a))); layer.alpha_composite(base)
    d = ImageDraw.Draw(layer)
    for r, route in enumerate(o.get("routes", [])):
        pts = [P(x, y) for x, y in route]; g = eout((lt-0.35-0.08*r)/1.4)
        if g <= 0: continue
        end, i = _poly_point(pts, g); line = pts[:i+1]+[end]
        d.line(line, fill=ORANGE+(int(230*a),), width=6, joint="curve")
        for k in range(3):   # fahrende Lkw-Punkte
            f = ((lt*0.18+k/3+r*0.13) % 1.0)*g; (px, py), _ = _poly_point(pts, f)
            d.ellipse([px-7, py-7, px+7, py+7], fill=WHITE+(int(255*a),))
    for k, (lon, lat, txt) in enumerate(o.get("pins", [])):
        g = eout((lt-0.4-0.07*k)/0.35)
        if g <= 0: continue
        x, y = P(lon, lat); r = 14*g
        d.ellipse([x-r-6, y-r-6, x+r+6, y+r+6], outline=ORANGE+(int(255*a*g),), width=4)
        d.ellipse([x-r*0.55, y-r*0.55, x+r*0.55, y+r*0.55], fill=ORANGE+(int(255*a*g),))
        if txt:
            f = font(FB, 46); tw = d.textlength(txt, font=f)
            bx = x+34 if x+34+tw+40 < W else x-34-tw-40
            d.rounded_rectangle([bx, y-34, bx+tw+40, y+34], 12, fill=PANEL+(int(215*a*g),))
            d.text((bx+20, y), txt, font=f, fill=WHITE+(int(255*a*g),), anchor="lm")
    if o.get("title"):
        d.text((120, 92), o["title"], font=font(FB, 64), fill=WHITE+(int(255*eout((lt-0.1)/0.35)*a),), anchor="lm")

def balken(layer, o, lt, du):
    a = fade(lt, du); d = ImageDraw.Draw(layer)
    d.text((W/2, 230), o.get("title", ""), font=font(FB, 72), fill=WHITE+(int(255*a),), anchor="mm")
    bars = o["bars"]; mx = max(b[1] for b in bars); y0 = 380; bh = 120; gap = 70; x0 = 360; maxw = W-x0-360
    for i, b in enumerate(bars):
        g = eout((lt-0.3-0.07*i)/0.9); y = y0+i*(bh+gap)
        d.text((x0-30, y+bh/2), b[0], font=font(FB, 52), fill=WHITE+(int(255*a),), anchor="rm")
        d.rounded_rectangle([x0, y, x0+maxw, y+bh], 14, fill=(30, 40, 58, int(220*a)))
        w = maxw*b[1]/mx*g
        if w > 4: d.rounded_rectangle([x0, y, x0+w, y+bh], 14, fill=(ORANGE if i == 0 else GREY)+(int(255*a),))
        val = f"{b[1]*min(1, g/0.999):.0f} {b[2] if len(b) > 2 else ''}".strip()
        d.text((x0+max(w, 0)+24, y+bh/2), val, font=font(FB, 60), fill=WHITE+(int(255*a*min(1, g*2)),), anchor="lm")
    if o.get("quelle"): d.text((W/2, H-110), o["quelle"], font=font(FM, 30), fill=GREY+(int(230*a),), anchor="mm")

def zaehler(layer, o, lt, du):
    a = fade(lt, du); d = ImageDraw.Draw(layer); g = eout((lt-0.15)/1.4)
    v = o["to"]*g; txt = f"{v:,.0f}".replace(",", ".")+(" "+o["unit"] if o.get("unit") else "")
    d.text((W/2, H/2-40), txt, font=font(FB, 190), fill=ORANGE+(int(255*a),), anchor="mm")
    if o.get("sub"): d.text((W/2, H/2+110), o["sub"], font=font(FB, 58), fill=WHITE+(int(255*eout((lt-0.4)/0.35)*a),), anchor="mm")
    if o.get("quelle"): d.text((W/2, H-110), o["quelle"], font=font(FM, 30), fill=GREY+(int(230*a),), anchor="mm")

def tage(layer, o, lt, du):
    a = fade(lt, du); d = ImageDraw.Draw(layer); n = o.get("n", 1)
    x0, x1, y = 260, W-260, 150
    p = Image.new("RGBA", layer.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(p)
    pd.rounded_rectangle([x0-90, y-70, x1+90, y+70+70*len(o.get("items", []))+30], 24, fill=PANEL+(int(200*a),)); layer.alpha_composite(p)
    d.line([x0, y, x1, y], fill=(60, 72, 92, int(255*a)), width=10)
    prog = (n-1)/2*eout((lt-0.2)/0.8) + ((n-2)/2 if n > 1 else 0)*(1-eout((lt-0.2)/0.8))
    d.line([x0, y, x0+(x1-x0)*max(0, prog), y], fill=ORANGE+(int(255*a),), width=10)
    for k in range(3):
        x = x0+(x1-x0)*k/2; on = k < n-1 or (k == n-1 and lt > 0.6)
        r = 26 if k == n-1 else 20
        d.ellipse([x-r, y-r, x+r, y+r], fill=(ORANGE if on else (60, 72, 92))+(int(255*a),))
        d.text((x, y+56), f"Tag {k+1}", font=font(FB, 40 if k == n-1 else 34), fill=(WHITE if on else GREY)+(int(255*a),), anchor="mm")
    for i, it in enumerate(o.get("items", [])):
        g = eout((lt-0.7-0.06*i)/0.3)
        d.rounded_rectangle([x0, y+122+i*70, x0+16, y+138+i*70], 4, fill=ORANGE+(int(255*a*g),))
        d.text((x0+40, y+130+i*70), it, font=font(FB, 46), fill=WHITE+(int(255*a*g),), anchor="lm")

def ablauf(layer, o, lt, du, T=None):
    a = fade(lt, du); d = ImageDraw.Draw(layer); steps = o["steps"]; n = len(steps)
    y = H-150; x0, x1 = 170, W-170; pos = [x0+(x1-x0)*i/(n-1) for i in range(n)]
    p = Image.new("RGBA", layer.size, (0, 0, 0, 0)); pd = ImageDraw.Draw(p)
    pd.rounded_rectangle([x0-120, y-70, x1+120, y+70], 26, fill=PANEL+(int(205*a),)); layer.alpha_composite(p)
    on = [lt >= st.get("lt", 0.25*i) for i, st in enumerate(o["_st"])]
    brk = o.get("_break")
    for i in range(n-1):
        g = eout((lt-o["_st"][i+1].get("lt", 0)+0.35)/0.35) if on[i] else 0
        col = RED if (brk is not None and i == brk[0]-1 and lt >= brk[1]) else ORANGE
        d.line([pos[i]+20, y, pos[i]+20+(pos[i+1]-pos[i]-40)*g, y], fill=col+(int(255*a),), width=8)
    for i, st in enumerate(steps):
        lit = on[i]; f = font(FB, 40); txt = st[0] if isinstance(st, list) else st
        broken = brk is not None and i >= brk[0] and lt >= brk[1]
        c = (RED if broken else (ORANGE if lit else (60, 72, 92)))
        r = 18 if lit else 13
        d.ellipse([pos[i]-r, y-r-18, pos[i]+r, y+r-18], fill=c+(int(255*a),))
        d.text((pos[i], y+30), txt, font=f, fill=(WHITE if lit and not broken else GREY)+(int(255*a),), anchor="mm")
    if brk is not None and lt >= brk[1]:
        g = eout((lt-brk[1])/0.3); xm = (pos[brk[0]-1]+pos[brk[0]])/2; s = 26*g
        d.line([xm-s, y-18-s, xm+s, y-18+s], fill=RED+(int(255*a),), width=9); d.line([xm-s, y-18+s, xm+s, y-18-s], fill=RED+(int(255*a),), width=9)

def prepare(o, T):
    """Wortanker der Grafik in Zeiten relativ zum Overlay-Start umrechnen"""
    if o["type"] == "ablauf":
        st = []
        for i, s in enumerate(o["steps"]):
            st.append({"lt": (T.at(s[1])-o["t0"]) if isinstance(s, list) and len(s) > 1 else 0.25+0.35*i})
        o["_st"] = st
        if o.get("break"): o["_break"] = (o["break"][0], T.at(o["break"][1])-o["t0"])
    return o

def draw(layer, o, lt, du):
    k = o["type"]
    if k == "karte": karte(layer, o, lt, du)
    elif k == "balken": balken(layer, o, lt, du)
    elif k == "zaehler": zaehler(layer, o, lt, du)
    elif k == "tage": tage(layer, o, lt, du)
    elif k == "ablauf": ablauf(layer, o, lt, du)
    else: return False
    return True
