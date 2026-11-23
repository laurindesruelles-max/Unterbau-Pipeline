"""2D-Motion-Graphics fuer Unterbau (Remotion, engine/motion2d/) – Erweiterung aus der ANOM-Stilprobe (Laurin 23.11.2026:
"Genau so sollte ein Video aussehen" – vor allem die vielen 2D-Animationen). Ersetzt nichts: Miniaturwelt, Querschnitt,
Tilt-Shift-Flug und die bestehenden Overlays aus engine/motion.py (karte, ablauf, balken, zaehler, tage) bleiben.
Diese Vollbild-Grafiken kommen dazu, wo eine schnelle Grafik mehr erklärt als eine weitere Einstellung.

Look (engine/motion2d/src/theme.tsx): Modellstadt bei Nacht im Hintergrund (Fensterlichter gehen an/aus), Tilt-Shift oben/unten,
Nachtblau + orange Fensterlicht (kein Leuchteffekt), Inter sachlich. Eigene Formen: Zahl auf Bahnhofs-Fallblatt-Tafel,
Stationen als Modellhäuser (Ausfall: Licht aus + rote Lampe), Raster aus Modellhäusern (betroffene dunkel = „Lichter gehen aus“),
Balken als Häuserzeilen mit Fenstern, Routen als fahrende LKW-Lichter, Orte als Laternen. Infrastruktur-Symbole:
power water pipe train truck house tower store server ship clock person doc money factory.

Bausteine: map, flow (Ablauf-Kette „Wenn A ausfällt …“ mit Abzweig), counter (Fallblatt), grid, bars, flip, stack, phone.
Im Video-Skript:
    import motion_ub as MO
    K = MO.clip("flow", {...}, len=5.0); MO.build(WORK)
    frame = MO.frame(K, t - t0); events += MO.sounds(K, t0)
Einmalig: `cd engine/motion2d && npm install`. Tempo ~3,4 s bleibt. Fakten wie immer mit Quelle.
"""
import os, json, hashlib, subprocess
import numpy as np, cv2
from PIL import Image

W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
_JOBS = {}
_WK = {"dir": "."}


def clip(comp, props, len=5.0):
    j = json.dumps({"c": comp, "p": props, "l": float(len)}, sort_keys=True, ensure_ascii=False)
    k = hashlib.sha1(j.encode()).hexdigest()[:12]
    _JOBS[k] = {"comp": comp, "props": props, "len": float(len)}
    return k


def path(k): return os.path.join(_WK["dir"], "motion", f"{k}.mp4")


def build(wk="."):
    _WK["dir"] = wk; os.makedirs(os.path.join(wk, "motion"), exist_ok=True)
    todo = [dict(v, out=os.path.abspath(path(k)), scale=float(os.environ.get("MO_SCALE", "1"))) for k, v in _JOBS.items() if not os.path.exists(path(k))]
    if not todo: return
    jf = os.path.abspath(os.path.join(wk, "motion", "jobs.json")); json.dump(todo, open(jf, "w"), ensure_ascii=False, indent=1)
    print(f"motion: {len(todo)} Clips rendern ...")
    subprocess.run(["node", os.path.join(HERE, "motion2d", "render.mjs"), jf], check=True)


_CAP = {}
def frame(k, lt):
    p = path(k); c = _CAP.get(p)
    if c is None:
        cap = cv2.VideoCapture(p); c = _CAP[p] = [cap, -1, None, int(cap.get(cv2.CAP_PROP_FRAME_COUNT))]
    i = max(0, min(int(lt * FPS), c[3] - 1))
    if i != c[1]:
        if i != c[1] + 1: c[0].set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = c[0].read()
        if ok: c[1], c[2] = i, cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(c[2]).convert("RGBA")


WH = "whoosh_slow_soft"
def _ticks(t0, d, n=8, g=0.16): return [(t0 + d * (1 - (1 - i / (n - 1)) ** 2.2), "tick", g * (1 - 0.5 * i / (n - 1)), None) for i in range(n)]
def sounds(k, t0=0.0):
    """Ton-Ereignisse ab Clip-Start t0 (Unterbau-Sounds; ub_daten/ub_klick sind als billig durchgefallen und bleiben draußen)."""
    j = _JOBS[k]; c, q, L = j["comp"], j["props"], j["len"]
    ev = [(0.0, WH, 0.3, None)]
    if c == "map":
        if q.get("highlight"): ev += [(0.3, "diagram_whoosh", 0.25, None)]
        if q.get("counter"): ev += _ticks(0.4, 1.2)
    elif c == "flow":
        n = len(q.get("nodes", []))
        b = q.get("branch")
        if b: bt = 0.6 + 0.75 * (b["after"] + 0.5); ev += [(bt + 0.5, "ub_hit", 0.45, None), (bt + 0.7, "sub_drop", 0.4, None)]
    elif c == "flip":
        at = q.get("at", 2.4); ev += [(at - 0.05, "ub_whoosh", 0.4, None), (at + 0.12, "reveal_impact_01", 0.32, None)]
    elif c == "counter":
        ev += _ticks(0.1, 1.6, 7, 0.1) + [(1.7, "ub_hit", 0.2, None)]
    elif c == "grid":
        ev += [(0.9, "ub_drop", 0.35, None)] + _ticks(0.9, 1.0)
    elif c == "bars":
        ev += [(0.4 + i * 0.35, "diagram_whoosh", 0.2, None) for i in range(len(q.get("bars", [])))]
    elif c == "stack":
        ev += [(1.5, "sub_drop", 0.5, None)]
    return [(t0 + t, n, g, d) for t, n, g, d in ev if t < L and g > 0]
