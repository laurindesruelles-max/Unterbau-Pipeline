"""Unterbau-Compositor: Tonspur + Wortzeiten + Bilder -> fertiges Video (kostenlos, CPU).

Bewegung ohne Kling (Laurin 17.11.2026: Kling-Clips zu teuer):
  - jede Einstellung = KI-Standbild mit 2.5D-Tiefenfahrt (engine/depth25d.py, Depth Anything V2)
  - Leben im Bild: Licht atmet, Wasser schimmert, Nebel/Schwebeteilchen (engine/cinemagraph.py, Atmo)
  - Querschnitt-Moment (Markenzeichen): Oberfläche wird durchsichtig -> Innenbild (xsection)
  - Overlays im Unterbau-Look: Bauchbinde, Zahl, Text, Titelkarte, Kapitelkarte, Hinweis „Szene nachgestellt“

python3 engine/unterbau.py <videoordner> [still <sek> ...] [--from S --to S] [--out datei.mp4]
Videoordner enthält spec.json, audio/, img/, words/ (aus wordtimes.py), music/.
Mindestdauern (Projektregeln): Bild >= 2 s, Einblendung >= 2,5 s, Kapitelkarte = eigene Pause 4,5 s (>= 4 s sichtbar), Titelkarte >= 4 s.
"""
import sys, os, json, math, re, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import depth25d as D
import cinemagraph as CG
import motion as M

W, H, FPS, SR = 1920, 1080, 25, 48000
ORANGE = (255, 122, 26); WHITE = (245, 245, 242); PANEL = (5, 14, 30)
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
_F = {}
def font(p, s):
    k = (p, int(s))
    if k not in _F: _F[k] = ImageFont.truetype(p, int(s))
    return _F[k]
def ease(x): x = min(max(x, 0), 1); return x*x*(3-2*x)
def eout(x): x = min(max(x, 0), 1); return 1-(1-x)**3
norm = lambda w: re.sub(r"[^\wäöüß]", "", w.lower())

# ------------------------------------------------------------------ Zeitachse
class Timeline:
    def __init__(self, vid, spec):
        self.vid, self.spec = vid, spec; t = spec.get("lead", 0.4)
        self.parts, self.chapters = {}, []
        for p in spec["parts"]:
            if "chapter" in p:
                c = dict(p["chapter"]); c["t0"] = t; c["t1"] = t+c.get("pause", 4.5); self.chapters.append(c); t = c["t1"]; continue
            w = json.load(open(f"{vid}/{p['words']}"))
            self.parts[p["id"]] = dict(p, t0=t, words=w["words"], dur=w["dur"]); t += w["dur"]+p.get("gap_after", 0.5)
        self.total = t+spec.get("tail", 1.5)
    def at(self, a):
        """[teil, "wort(e)", versatz] -> Sekunde. Mehrere Wörter = Folge; "#2" am Ende = zweites Vorkommen."""
        if isinstance(a, (int, float)): return float(a)
        part, txt = a[0], a[1]; off = a[2] if len(a) > 2 else 0.0
        P = self.parts[part]
        if txt == "END": return P["t0"]+P["dur"]+off
        occ = 1
        m = re.match(r"(.*)#(\d+)$", txt)
        if m: txt, occ = m.group(1), int(m.group(2))
        q = [norm(x) for x in txt.split()]; ws = [norm(w["w"]) for w in P["words"]]; n = 0
        for i in range(len(ws)-len(q)+1):
            if ws[i:i+len(q)] == q:
                n += 1
                if n == occ: return P["t0"]+P["words"][i]["s"]+off
        raise ValueError(f"Anker nicht gefunden: {a}")
    def word_end(self, a):
        part, txt = a[0], a[1]; P = self.parts[part]; t0 = self.at(a)-P["t0"]-(a[2] if len(a) > 2 else 0)
        i = next(k for k, w in enumerate(P["words"]) if abs(w["s"]-t0) < 1e-6)
        return P["t0"]+P["words"][i+len(txt.split())-1]["e"]

# ------------------------------------------------------------------ Bilder
_IMG = {}
def image(vid, key):
    if key not in _IMG:
        if len(_IMG) > 6: _IMG.clear()
        im = cv2.imread(f"{vid}/img/{key}.png")[..., ::-1]
        im = cv2.resize(im, (2112, 1188), interpolation=cv2.INTER_AREA).astype(np.float32)
        d = D.load_depth(f"{vid}/img/{key}_depth.png", im.astype(np.uint8))
        _IMG[key] = (im, d)
    return _IMG[key]

def shot_frame(vid, s, u, lt):
    im, d = image(vid, s["img"])
    src = CG.src(im, s["img"], lt, tuple(s.get("fx", []))) if s.get("fx") is not None else im
    return D.frame(src, d, u, s.get("move", "push"))

def xsection(vid, s, u, lt, prog):
    """Querschnitt-Moment: Wasseroberfläche wird von oben nach unten durchsichtig, Innenbild erscheint."""
    a = shot_frame(vid, dict(s, img=s["xsection"][0]), u, lt)
    if prog <= 0: return a
    b = shot_frame(vid, dict(s, img=s["xsection"][1], fx=s.get("fx_in", ["fog"])), u, lt)
    if prog >= 1: return b
    y0 = s.get("waterline", 0.42)*H; front = y0+(H*1.15-y0)*eout(prog)
    yy = np.arange(H, dtype=np.float32)[:, None]; xx = np.arange(W, dtype=np.float32)[None, :]
    wav = 18*np.sin(xx/70+lt*5)+10*np.sin(xx/23-lt*7)
    m = np.clip((front+wav-yy)/40, 0, 1)*(yy > y0-60)
    m = np.clip(m, 0, 1)[..., None]
    edge = np.exp(-((yy-(front+wav))/6)**2)[..., None]*(yy > y0-60)[..., None]
    # Wasser kräuselt sich vor der Front
    out = a*(1-m)+b*m
    return np.clip(out+edge*np.array([210, 235, 245], np.float32)*0.55*math.sin(prog*math.pi), 0, 255)

_CLIP = {}
def clip_frame(vid, s, lt, u):
    """echter Videoclip (Pixabay/Archiv) als Einstellung, mit leichtem Zoom und Unterbau-Grade"""
    p = f"{vid}/{s['clip']}"
    if p not in _CLIP:
        if len(_CLIP) > 3: [c.release() for c in _CLIP.values()]; _CLIP.clear()
        _CLIP[p] = cv2.VideoCapture(p)
    cap = _CLIP[p]; fps = cap.get(cv2.CAP_PROP_FPS) or 24; n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    idx = int((s.get("ss", 0)+lt*s.get("speed", 1.0))*fps) % n
    if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) != idx: cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ok, fr = cap.read()
    if not ok: return np.zeros((H, W, 3), np.float32)
    fr = cv2.resize(fr, (W, H))[..., ::-1].astype(np.float32)
    z = 1.04+0.06*u; M2 = cv2.getRotationMatrix2D((W/2, H/2), 0, z); fr = cv2.warpAffine(fr, M2, (W, H), borderMode=cv2.BORDER_REFLECT)
    g = fr.mean(axis=2, keepdims=True)   # Unterbau-Grade: entsättigt, kühl, Orange bleibt
    fr = g+(fr-g)*0.72; fr = fr*np.array([0.92, 0.98, 1.06], np.float32)
    return np.clip(fr*0.92, 0, 255)

# ------------------------------------------------------------------ Overlays (Unterbau-Look)
def panel(layer, box, a, radius=20):
    x0, y0, x1, y1 = box; p = Image.new("RGBA", layer.size, (0, 0, 0, 0)); d = ImageDraw.Draw(p)
    d.rounded_rectangle(box, radius, fill=PANEL+(int(205*a),)); d.rounded_rectangle([x0, y0, x0+10, y1], 4, fill=ORANGE+(int(255*a),))
    layer.alpha_composite(p)

def bauchbinde(layer, lt, dur, lines):
    a = ease(lt/0.3)*ease((dur-lt)/0.3); d = ImageDraw.Draw(layer)
    f1 = font(FB, 56); f2 = font(FB, 40)
    w = max(d.textlength(lines[0], font=f1), *(d.textlength(l, font=f2) for l in lines[1:])) if len(lines) > 1 else d.textlength(lines[0], font=f1)
    h = 56+20+len(lines[1:])*52+24; x0 = 90-40*(1-eout(lt/0.4)); y0 = H-150-h
    panel(layer, [x0, y0, x0+w+70, y0+h], a)
    d.text((x0+40, y0+18), lines[0], font=f1, fill=WHITE+(int(255*a),))
    for i, l in enumerate(lines[1:]): d.text((x0+40, y0+18+70+i*52), l, font=f2, fill=ORANGE+(int(255*a),))

def zahl(layer, lt, dur, big, sub):
    a = ease(lt/0.3)*ease((dur-lt)/0.3); d = ImageDraw.Draw(layer); s = 1+0.12*(1-eout(lt/0.35))
    fb = font(FB, 150*s); fs = font(FB, 44)
    wb = d.textlength(big, font=fb); ws = d.textlength(sub, font=fs); w = max(wb, ws)+90
    x0 = W-140-w; y0 = 170
    panel(layer, [x0, y0, x0+w, y0+300], a, 24)
    d.text((x0+50, y0+30), big, font=fb, fill=ORANGE+(int(255*a),))
    d.text((x0+52, y0+215), sub, font=fs, fill=WHITE+(int(255*a),))

def hinweis(layer, lt, dur, text):
    a = ease(lt/0.3)*ease((dur-lt)/0.3); d = ImageDraw.Draw(layer); f = font(FM, 30)
    w = d.textlength(text, font=f); p = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(p).rounded_rectangle([W-90-w-36, 70, W-90, 122], 12, fill=PANEL+(int(170*a),)); layer.alpha_composite(p)
    d.text((W-90-w-18, 79), text, font=f, fill=WHITE+(int(230*a),))

def titelkarte(layer, lt, dur, claim):
    a = ease(lt/0.4)*ease((dur-lt)/0.5); d = ImageDraw.Draw(layer)
    s = 1.04-0.04*eout(lt/1.5); f = font(FB, 170*s)
    d.text((W/2, H/2-40), "UNTERBAU", font=f, fill=WHITE+(int(255*a),), anchor="mm")
    w = 520*eout((lt-0.3)/0.6); d.rectangle([W/2-w, H/2+70, W/2+w, H/2+78], fill=ORANGE+(int(255*a),))
    if lt > 0.6: d.text((W/2, H/2+135), claim, font=font(FM, 44), fill=WHITE+(int(230*ease((lt-0.6)/0.5)*a),), anchor="mm")

def kapitelkarte(layer, lt, dur, n, title):
    a = ease(lt/0.4)*ease((dur-lt)/0.4); d = ImageDraw.Draw(layer)
    d.text((W/2, H/2-95), f"KAPITEL {n}", font=font(FB, 44), fill=ORANGE+(int(255*a),), anchor="mm")
    s = 1.05-0.05*eout(lt/1.2)
    d.text((W/2, H/2+15), title, font=font(FB, 110*s), fill=WHITE+(int(255*ease((lt-0.25)/0.4)*a),), anchor="mm")

def videotitel(layer, lt, dur, lines):
    a = ease(lt/0.4)*ease((dur-lt)/0.4); d = ImageDraw.Draw(layer)
    for i, l in enumerate(lines):
        d.text((W/2, H/2-50+i*95), l, font=font(FB, 78), fill=(ORANGE if i == len(lines)-1 else WHITE)+(int(255*ease((lt-0.2*i)/0.4)*a),), anchor="mm")

# ------------------------------------------------------------------ Look
_GR = {}
def finish(fr, t):
    if "v" not in _GR:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _GR["v"] = (1-0.32*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)**1.3)[..., None].clip(0.55, 1)
        _GR["g"] = [np.random.default_rng(i).normal(0, 7, (H//2, W//2)).astype(np.float32) for i in range(6)]
    g = cv2.resize(_GR["g"][int(t*FPS) % 6], (W, H))[..., None]
    return np.clip(fr*_GR["v"]+g, 0, 255)

# ------------------------------------------------------------------ Render
def build(vid):
    spec = json.load(open(f"{vid}/spec.json")); T = Timeline(vid, spec)
    shots = []
    for s in spec["shots"]:
        s = dict(s); s["t0"] = T.at(s["at"]); shots.append(s)
    shots.sort(key=lambda s: s["t0"])
    for i, s in enumerate(shots): s["t1"] = shots[i+1]["t0"] if i+1 < len(shots) else T.total
    if spec.get("cut"):   # Schnitt-Tempo (Laurin 19.11.2026): lange Einstellungen in Ausschnitte teilen
        shots = M.split_shots(T, shots, spec["cut"], lambda k: image(vid, k)[1])
    ovs = []
    for o in spec.get("overlays", []):
        o = dict(o); o["t0"] = T.at(o["at"]); o["t1"] = o["t0"]+max(2.5, o.get("dur", 3.0)); ovs.append(M.prepare(o, T))
    for c in T.chapters: ovs.append(dict(type="kapitel", t0=c["t0"], t1=c["t1"], n=c["n"], title=c["title"]))
    if spec.get("title"):
        ti = spec["title"]; t0 = T.at(ti["at"]); ovs.append(dict(type="titel", t0=t0, t1=t0+max(4.0, ti.get("dur", 4.2)), claim=ti.get("claim", "Verstehen, wie die Welt funktioniert")))
    return spec, T, shots, ovs

def check(T, shots, ovs):
    bad = [f"Bild {s.get('img', s.get('xsection'))} nur {s['t1']-s['t0']:.2f} s" for s in shots if s["t1"]-s["t0"] < 2.0 and not s.get("black")]
    bad += [f"Kapitelkarte nur {c['t1']-c['t0']:.2f} s" for c in T.chapters if c["t1"]-c["t0"] < 4.0]
    return bad

def render_frame(vid, T, shots, ovs, t, atmo):
    s = next((x for x in shots if x["t0"] <= t < x["t1"]), shots[-1]); lt = t-s["t0"]; u = lt/max(0.1, s["t1"]-s["t0"])
    if s.get("black"): fr = np.zeros((H, W, 3), np.float32)
    elif s.get("clip"): fr = clip_frame(vid, s, lt, u)
    elif s.get("xsection"):
        r0 = T.at(s["reveal"]) - s["t0"] if s.get("reveal") else 0.6
        fr = xsection(vid, s, u, lt, (lt-r0)/s.get("reveal_dur", 1.3))
    else: fr = shot_frame(vid, s, u, lt)
    if s.get("atmo"): fr = atmo[s["atmo"]].apply(fr, t)
    if not s.get("black"): fr = CG.screen(fr, s.get("img", "x"), lt, tuple(s.get("fx", [])))
    dim = s.get("dim", 0.0)
    for o in ovs:
        if o["t0"] <= t < o["t1"] and o["type"] in ("kapitel", "titel", "videotitel")+M.FULL:
            lo = t-o["t0"]; dim = max(dim, (0.72 if o["type"] == "kapitel" else 0.84 if o["type"] in M.FULL else 0.55)*M.eout(lo/0.3)*ease((o["t1"]-t)/0.25))
    fr = fr*(1-dim)
    fr = finish(fr, t)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for o in ovs:
        if not (o["t0"] <= t < o["t1"]): continue
        lt, du = t-o["t0"], o["t1"]-o["t0"]; k = o["type"]
        if k == "bauchbinde": bauchbinde(layer, lt, du, o["lines"])
        elif k == "zahl": zahl(layer, lt, du, o["big"], o["sub"])
        elif k == "hinweis": hinweis(layer, lt, du, o["text"])
        elif k == "kapitel": kapitelkarte(layer, lt, du, o["n"], o["title"])
        elif k == "titel": titelkarte(layer, lt, du, o["claim"])
        elif k == "videotitel": videotitel(layer, lt, du, o["lines"])
        else: M.draw(layer, o, lt, du)
    im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).convert("RGBA"); im.alpha_composite(layer)
    return np.asarray(im.convert("RGB"))

def video(vid, out, a=0.0, b=None):
    spec, T, shots, ovs = build(vid); b = b or T.total
    atmo = {k: D.Atmo(k, seed=7) for k in ("dust", "snow", "rain")}
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(a*FPS), int(b*FPS)):
        p.stdin.write(render_frame(vid, T, shots, ovs, i/FPS, atmo).tobytes())
    p.stdin.close(); p.wait()

# ------------------------------------------------------------------ Ton
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _audiokit():
    """Gemeinsames Ton-Werkzeug (Repo sound-mediathek/audiokit, setup.sh lädt es). Fehlt es, läuft der alte Weg weiter."""
    d = os.environ.get("AUDIOKIT", "/home/claude/audiokit")
    if not os.path.exists(f"{d}/adapter.py"): print("WARNUNG: audiokit fehlt – sh setup.sh ausführen"); return None
    sys.path.insert(0, d); import adapter; return adapter
def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

def sfx_path(vid, name):
    for d in (f"{vid}/sfx", os.environ.get("SFX", "/home/claude/unterbau-work/sfx")):
        for ext in ("wav", "mp3"):
            if os.path.exists(f"{d}/{name}.{ext}"): return f"{d}/{name}.{ext}"
    raise FileNotFoundError(name)

def audio(vid, out):
    spec, T, shots, ovs = build(vid); N = int(T.total*SR)+SR
    voice = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32)
    def put(buf, x, t, g):
        i = int(t*SR); x = x[:max(0, N-i)]; buf[i:i+len(x)] += x*g
    for p in T.parts.values(): put(voice, load(f"{vid}/{p['audio']}"), p["t0"], 1.0)
    ev = []   # (t, name, gain) – erst sammeln, dann von audiokit aufräumen lassen, dann mischen
    for o in ovs:   # Einblendungen bekommen den Unterbau-eigenen Klick (assets/sfx/ub_klick)
        if o["type"] in ("bauchbinde", "zahl"): ev.append((o["t0"], "ub_klick", 0.42))
    for c in T.chapters: ev.append((c["t0"]+0.15, spec.get("chapter_hit", "ub_hit"), 0.55))
    for e in spec.get("sfx", []): ev.append((T.at(e[0]), e[1], e[2] if len(e) > 2 else 0.6))
    if spec.get("cut"):   # Schnitt-Sounds: Szenenwechsel leiser Whoosh, Grafiken Daten-Sound
        for s in shots[1:]:
            if not s.get("sub") and not s.get("black"): ev.append((s["t0"]-0.05, spec.get("cut_sound", "ub_whoosh"), 0.2))
        for o in ovs:
            if o["type"] in M.FULL+("tage", "ablauf"): ev.append((o["t0"], "ub_daten", 0.32))
    AK0 = _audiokit()
    if AK0: ev = AK0.clean_events(ev, "unterbau", os.path.join(REPO, "assets", "sfx"), extra_dirs=(f"{vid}/sfx", os.environ.get("SFX", "/home/claude/unterbau-work/sfx")))
    for t, name, g in ev: put(fx, load(sfx_path(vid, name)), t, g)
    for e in spec.get("amb", []):   # Raumklang: [von, bis, name, gain]
        t0, t1 = T.at(e[0]), T.at(e[1]); x = load(sfx_path(vid, e[2])); n = int((t1-t0)*SR)
        x = np.concatenate([x]*(1+n//len(x)))[:n]; f = min(int(0.8*SR), n//3)
        x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]; put(fx, x, t0, e[3])
    # Musik: läuft durch, taucht unter Julian ab (sidechain-ähnlich), Pausen laut spec "music_rests"
    mus = np.zeros((N, 2), np.float32); m = spec.get("music", {})
    AK = _audiokit()
    if AK and m.get("mode", "dramaturgie") == "dramaturgie":
        # Spannungskurve (audiokit, 18.11.2026): Track je Kapitel aus assets/music, Wechsel spätestens alle ~70 s,
        # Anschwellen vor Enthüllungen/Zahlen, kurze Stille bei großen Enthüllungen, Bogen pro Kapitel.
        lib = os.path.join(REPO, "assets", "music")
        plan = m.get("chapters") or []   # optional: ["ub_kaltstart_meer", "ub_system_puls", ...] – je Abschnitt (Einstieg + Kapitel)
        rot = ["ub_system_puls", "ub_ausfall_dunkel", "ub_spannung_aufbau", "ub_system_puls", "ub_ausfall_dunkel"]
        first = os.path.splitext(os.path.basename(m["file"]))[0] if m.get("file") else "ub_kaltstart_meer"
        names = [first] + [plan[i + 1] if i + 1 < len(plan) else rot[i % len(rot)] for i in range(len(T.chapters))]
        if len(T.chapters) >= 2 and not plan: names[-1] = "ub_aufloesung_weit"
        alt = {"ub_system_puls": "ub_ausfall_dunkel", "ub_ausfall_dunkel": "ub_system_puls", "ub_spannung_aufbau": "ub_ausfall_dunkel",
               "ub_kaltstart_meer": "ub_spannung_aufbau", "ub_aufloesung_weit": "ub_system_puls"}
        def mp(n):
            for d in (lib, f"{vid}/music"):
                if os.path.exists(f"{d}/{n}.mp3"): return f"{d}/{n}.mp3"
            return f"{lib}/{n}.mp3"
        pools = [[mp(n), mp(alt.get(n, "ub_system_puls"))] for n in names]
        chapters = [(0.0, None)] + [(c["t0"], c["title"], c["t1"] - 0.3) for c in T.chapters]
        words = [(p["t0"] + w["s"], w["w"]) for p in T.parts.values() for w in p["words"]]
        beats = [(o["t0"], "zahl", 3 if any(ch.isdigit() for ch in str(o.get("big", ""))) else 2) for o in ovs if o["type"] == "zahl"]
        stim = [o["t0"] for o in ovs] + [s["t0"] for s in shots]
        mus = AK.music_bed("unterbau", N, SR, voice.mean(1), T.total, chapters, words, pools, beats, stimuli=stim)
        m = {}   # alter Ein-Track-Weg wird übersprungen
    if m:
        x = load(f"{vid}/{m['file']}"); x = np.concatenate([x]*(1+N//len(x)))[:N]; mus = x*m.get("gain", 0.5)
        env = np.abs(voice).mean(1); k = int(0.3*SR); env = np.convolve(env, np.ones(k)/k, "same")
        duck = 1-0.62*np.clip(env/0.02, 0, 1); duck = np.convolve(duck, np.ones(k)/k, "same")
        rest = np.ones(N, np.float32)
        for r in m.get("rests", []):
            a, b = int(T.at(r[0])*SR), int(T.at(r[1])*SR); f = int(0.5*SR)
            rest[a:b] = 0; rest[max(0, a-f):a] = np.minimum(rest[max(0, a-f):a], np.linspace(1, 0, a-max(0, a-f)))
            rest[b:b+int(1.5*SR)] = np.minimum(rest[b:b+int(1.5*SR)], np.linspace(0, 1, len(rest[b:b+int(1.5*SR)])))
        mus *= (duck*rest)[:, None]; fo = int(2*SR); mus[int(T.total*SR)-fo:int(T.total*SR)] *= np.linspace(1, 0, fo)[:, None]
    mix = (voice+fx*0.9+mus)[:int(T.total*SR)]
    tmp = out+".raw.wav"
    import scipy.io.wavfile as wf
    wf.write(tmp, SR, (np.clip(mix/max(1, np.abs(mix).max()/0.97), -1, 1)*32767).astype(np.int16))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), out], check=True); os.remove(tmp)
    if AK0:
        wf.write(out + ".voice.wav", SR, voice[:int(T.total*SR)].astype(np.float32)); wf.write(out + ".music.wav", SR, mus[:int(T.total*SR)].astype(np.float32))
        AK0.final_check(out, out + ".voice.wav", out + ".music.wav"); AK0.write_report(f"{vid}/ton_bericht.txt")
        os.remove(out + ".voice.wav"); os.remove(out + ".music.wav")

if __name__ == "__main__":
    vid = sys.argv[1]; args = sys.argv[2:]
    if args and args[0] == "still":
        spec, T, shots, ovs = build(vid); atmo = {k: D.Atmo(k, seed=7) for k in ("dust", "snow", "rain")}
        for t in map(float, args[1:]): Image.fromarray(render_frame(vid, T, shots, ovs, t, atmo)).save(f"{vid}/still_{t:06.2f}.jpg", quality=88)
    elif args and args[0] == "check":
        spec, T, shots, ovs = build(vid); print(f"Länge {T.total:.1f} s"); print("\n".join(check(T, shots, ovs)) or "Mindestdauern ok")
        for s in shots: print(f"{s['t0']:6.2f}-{s['t1']:6.2f}  {s.get('img', s.get('xsection', 'schwarz'))}")
    elif args and args[0] == "audio":
        audio(vid, args[1])
    else:
        a = float(args[args.index("--from")+1]) if "--from" in args else 0.0
        b = float(args[args.index("--to")+1]) if "--to" in args else None
        out = args[args.index("--out")+1] if "--out" in args else f"{vid}/video.mp4"
        video(vid, out, a, b)
