"""Ton für 005 (Pfand) nach Sound-Plan: Stimme (6 Teile), Musik je Kapitel atmet (Ducking, Pausen vor großen Sätzen, Swells, 2 s Überblendung,
Musik ≥ 16 dB unter der Stimme), Effekte nur auf echten Bild-Ereignissen. Casting Gemini 26.11.2026: Piep retail_scanner_1 PREMIUM, Text-Einblendung
whoosh_slow_soft PREMIUM (digital_denied CHEAP), Flaschen zerdrücken crushing_plastic_bottles PREMIUM, Geldzähler banknote_counter PREMIUM,
Fabrik-Atmo amb_factory PREMIUM; Münze, Glasklirren, Zug nur OK → nicht verwendet. Kapitel-Sound ub_hit. Master −14 LUFS / TP −2 dB.
python3 ton_005.py VIDEO_IN VIDEO_OUT WORK"""
import sys, json, wave, os, subprocess, numpy as np
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine/stilproben"); sys.path.insert(0, "/home/claude/unterbau-pipeline/engine")
from mixer import load, clip, place, SR, lufs
import motion_ub as MO
vin, vout, W = sys.argv[1], sys.argv[2], sys.argv[3]
U = "/home/claude/unterbau-pipeline/assets/"; X = W + "/sfx/"; V = W + "/v5/"
plan = json.load(open(V + "plan.json")); S = json.load(open(V + "saetze.json"))
# Satzzeiten immer aus dem Original-Plan (Ton bleibt, wo er war); Bild-Ereignisse aus dem ruhigen Schnitt, falls vorhanden
BP = os.environ.get("BILDPLAN", V + "plan_grafik_x.json")   # Bild-Ereignisse aus dem tatsächlich verwendeten Schnitt (23.11.: plan_grafik.json)
bild = json.load(open(BP)) if os.path.exists(BP) else None
jobs = {j["key"]: j for j in json.load(open(V + "motion_jobs.json"))}
for k, j in jobs.items(): MO._JOBS[k] = {"comp": j["comp"], "props": j["props"], "len": j["len"]}
T, tt = {}, 0.0
for p in plan:
    p["t"] = tt
    for k in p.get("keys", []): T.setdefault(k, tt)
    tt += p["dur"]
dur = tt; N = int(dur * SR); t = np.arange(N) / SR
if bild:
    tb = 0.0
    for p in bild: p["t"] = tb; tb += p["dur"]
    plan = bild

def wav(path, a):
    a = np.clip(a, -1, 1); st = np.stack([a, a], 1) if a.ndim == 1 else a
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())

# Stimme: Teil k beginnt dort, wo sein erster Satz im Plan beginnt
voice = np.zeros((N, 2), np.float32); kap = {}
for k in range(1, 7):
    i0 = min(i for i, s in enumerate(S) if s[0] == k); t0 = T[i0] - S[i0][1]; kap[k] = t0
    a = load(W + f"/audio/{k}.mp3"); j = int(t0 * SR); a = a[:N - j]; voice[j:j + len(a)] += a
# Musik je Kapitel (Teil), Titel-/Kapitelkarte gehört zum folgenden Teil
pm = {1: ("ub_kaltstart_meer", 0), 2: ("ub_system_puls", 0), 3: ("ub_ausfall_dunkel", 0), 4: ("ub_system_puls", 60), 5: ("ub_spannung_aufbau", 0), 6: ("ub_aufloesung_weit", 0)}
starts = {1: 0.0, 2: T["T"] - 0.3, 3: T["K2"], 4: T["K3"], 5: T["K4"], 6: T["K5"]}
music = np.zeros((N, 2), np.float32)
for k in range(1, 7):
    name, off = pm[k]; m = load(U + f"music/{name}.mp3")
    a = max(0, starts[k] - 1.0); b = min(dur, (starts[k + 1] if k < 6 else dur) + 1.0); n = int((b - a) * SR)
    seg = np.concatenate([m[int(off * SR):], m, m])[:n]; env = np.ones(len(seg), np.float32); f = int(2.0 * SR)
    seg = seg * (10 ** (-20 / 20) / (np.sqrt(np.mean(seg ** 2)) + 1e-9))   # jedes Kapitel gleich laut (Laurin 24.11.: Musik stellenweise viel zu laut, z. B. 2:20)
    # Pegel-Glätter (Laurin 27.11.2026: Musik am Anfang „laut leise laut leise“): Wellen und Anstiege im Stück selbst ausgleichen,
    # ±10 dB, 2-s-Fenster, Regelung 2,5 s – Spannung kommt weiter aus Swells/Pausen, nicht aus Zufallswellen im Track
    _k = int(2.0 * SR); _c = np.cumsum(np.concatenate([np.zeros(1), seg[:, 0].astype(np.float64) ** 2]))
    _r = np.sqrt(np.maximum((_c[_k:] - _c[:-_k]) / _k, 1e-10)); _r = np.concatenate([np.full(_k // 2, _r[0]), _r, np.full(len(seg) - len(_r) - _k // 2, _r[-1])])
    _g = np.clip(10 ** (-20 / 20) / _r, 10 ** (-10 / 20), 10 ** (10 / 20)); _k2 = int(2.5 * SR); _c2 = np.cumsum(np.concatenate([np.zeros(1), _g]))
    _g = np.concatenate([np.full(_k2 // 2, _g[0]), (_c2[_k2:] - _c2[:-_k2]) / _k2, np.full(len(seg) - (len(_c2) - _k2) - _k2 // 2, _g[-1])])[:len(seg)]
    seg = seg * _g[:, None].astype(np.float32)
    env[:f] *= np.linspace(0, 1, min(f, len(env))); env[-f:] *= np.linspace(1, 0, min(f, len(env)))
    j = int(a * SR); music[j:j + len(seg)] += seg * env[:, None]
def _ma(x, k):                      # schneller gleitender Mittelwert (cumsum), gleiche Länge
    c = np.cumsum(np.concatenate([np.zeros(k // 2 + 1), x, np.zeros(k - k // 2)])); return ((c[k:] - c[:-k]) / k)[:len(x)]
def _env(x, sek): return np.sqrt(_ma(x.astype(np.float64) ** 2, int(sek * SR)) + 1e-12)
# Ducking ohne Pumpen (Laurin 27.11.2026: „am Anfang so komisch laut leise laut leise“): Pausen unter 2,5 s zählen als Sprache,
# die Musik bleibt dort auf EINEM Pegel; Bezug ist der mittlere Stimmpegel (nicht die Hüllkurve jedes Wortes), Rampen 1,5 s.
_va = (_env(voice[:, 0], 0.05) > 0.008).astype(np.float64)
_d = (_ma(_va, int(2.5 * SR)) > 0).astype(np.float64)
sp = (_ma(_d, int(2.5 * SR)) > 0.999).astype(np.float64)
sp = _ma(sp, int(1.5 * SR)); sp[:int(2.5 * SR)] = sp[int(2.5 * SR)]; act = sp
gain = np.full(N, 0.5)
for i in (69, 141, 181):            # Musik weg vor großen Sätzen, mit dem Satz zurück (nicht mehr im Kaltstart)
    ts = T[i]; gain *= np.clip(1 - np.clip((t - (ts - 0.9)) / 0.3, 0, 1) + np.clip((t - (ts + 0.1)) / 1.0, 0, 1), 0, 1)
for key in ("T", "K1", "K2", "K3", "K4", "K5"):   # Musik trägt unter Kapitelkarten
    ts = T[key]; gain *= 10 ** ((12 if key == "T" else 7) * np.clip(1 - np.abs(t - (ts + 2.2)) / 2.6, 0, 1) / 20)
for i in (97, 132, 165):            # Swell vor Enthüllungen (nur in Sprechpausen hörbar, unter Sprache greift die Decke)
    gain *= 10 ** (5 * np.clip(1 - np.abs(t - (T[i] - 0.5)) / 2.5, 0, 1) / 20)
gain *= 10 ** (16 * np.clip(1.6 - np.abs(t - (T["K5"] + 2.0)) / 1.8, 0, 1) / 20)   # Höhepunkt: Kapitelkarte vor der Auflösung
music *= gain[:, None]; music[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))[:, None]
vref = np.median(_env(voice[:, 0], 0.4)[_va > 0.5])            # mittlerer Stimmpegel
me = _env(music[:, 0], 4.0)                                     # Musikpegel, 4 s geglättet (kein Wort-für-Wort-Folgen)
decke = np.minimum(1.0, vref * 10 ** (-18 / 20) / me)
g2 = 1 - sp * (1 - decke); g2 = _ma(g2, int(1.5 * SR)); music *= np.clip(g2, 0, 1)[:, None]
if os.environ.get("DUMP"): wav(V + "music_stem.wav", music); wav(V + "voice_stem.wav", voice)
# Brummen, das tiefer wird und erstirbt (Lichter gehen aus)
hum = load(X + "fire_electric_hum_39.wav")[:, 0]; n = int(3.2 * SR); pos = np.cumsum(np.linspace(1.0, 0.45, n)); pos = pos[pos < len(hum) - 1]
hum_fall = np.interp(pos, np.arange(len(hum)), hum) * np.linspace(1, 0, len(pos)) ** 1.5; hum_fall = np.stack([hum_fall, hum_fall], 1).astype(np.float32)

E = []
def add(tt_, f, g): E.append((tt_, f, g))
F = {"whoosh_slow_soft": X + "whoosh_slow_soft.wav", "diagram_whoosh": X + "diagram_whoosh.wav", "ub_hit": X + "ub_hit.wav", "sub_drop": X + "sub_drop.wav",
     "tick": X + "tick.wav", "reveal_impact_01": X + "reveal_impact_01.wav", "ub_whoosh": X + "ub_whoosh.wav", "ub_drop": X + "ub_drop.wav"}
last_label = -9
for q, p in enumerate(plan):
    t0, d = p["t"], p["dur"]
    if "video" in p and p.get("kind") == "mo" and p.get("ss", 0) == 0:
        key = os.path.basename(p["video"])[:-4]
        if key in MO._JOBS:
            for (te, nm, g, _) in MO.sounds(key, t0):
                if te < t0 + d and nm in F: add(te, F[nm], g * (0.45 if nm == "tick" else 0.8))
    for fx in p.get("fx", []):
        ty = fx["type"]
        if ty == "tafel":
            for j in range(len(fx["texts"])): add(t0 + j * d / len(fx["texts"]) + 0.02, X + "paper_flip.wav", 0.4)
        elif ty == "clock":
            if not p.get("_tick"):
                p["_tick"] = 1
                for j in range(5): add(t0 + 0.15 + j * 0.32, X + "tick.wav", 0.16 * (1 - j * 0.15))
        elif ty == "label" and p.get("run_k", 0) == 0 or (ty == "label" and "video" in p):
            tl = t0 + fx.get("t0", 0.15) * d
            if tl - last_label > 2.0: add(tl - 0.05, X + "whoosh_slow_soft.wav", 0.18); last_label = tl
        elif ty == "card":
            add(t0 + 0.05, X + "ub_hit.wav", 0.38)
    if p.get("trans") == "lights" and p.get("anim") == "Lichter gehen aus": add(t0 + d * p["t_trans"][0], "HUM", 0.3)
    if p.get("anim") == "Tilt-Shift-Flug" and p.get("run_k", 0) == 0: add(t0 + 0.05, X + "whoosh_slow_soft.wav", 0.14)
# Weniger Whooshes (Laurin 24.11.2026: „kommt zu oft“): je Grafik höchstens einer, Kamerafahrt ohne, zwischen zwei Whooshes ≥ 6 s;
# Vorrang: Grafik-Start > Einblendung
WH = ("whoosh",); _isw = lambda f: any(w in os.path.basename(f) for w in WH)
_rest = [e for e in E if not _isw(e[1])]; _w = sorted([e for e in E if _isw(e[1])], key=lambda e: e[0])
_prio = {}; _seen = set()
for e in _w:
    q = next((p for p in plan if p["t"] <= e[0] + 0.3 < p["t"] + p["dur"]), None)
    mo = q is not None and q.get("kind") == "mo"; key = q.get("video") if mo else None
    if mo and key in _seen: continue                     # nur der erste Whoosh einer Grafik
    if mo: _seen.add(key)
    if e[2] <= 0.14: continue                            # leiser Kamerafahrt-Whoosh fällt weg
    _prio[e] = 0 if mo else 1
_keep = []
for e in sorted(_prio, key=lambda e: (_prio[e], e[0])):
    if all(abs(e[0] - k[0]) >= 6.0 for k in _keep): _keep.append(e)
E = _rest + sorted(_keep); print(len(_keep), "Whooshes (vorher", len(_w), ")")
# Einzelne Geräusche zu Bild-Ereignissen (nur PREMIUM aus dem Casting)
wp = json.load(open(W + "/words/w1.json"))["words"]; tpiep = next(x["s"] for x in wp if x["w"].startswith("Piep")) + kap[1]
add(tpiep - 0.02, X + "retail_scanner_1.wav#1.0", 0.32)
for i in (16, 106, 175):
    if i in T: add(T[i] + 1.2, X + "retail_scanner_1.wav#1.0", 0.22)
_cr = clip(X + "crushing_plastic_bottles_wav.wav")
for i in (29,):
    add(T[i] + 0.8, "CRUSH", 0.42); add(T[i] + 0.9, X + "sub_drop.wav", 0.3)   # Gemini 26.11.: Presse klang dünn → Bass darunter
add(T[112] + 0.1, X + "banknote_counter.wav", 0.3)
for i in (9, 69, 101, 111, 124, 141):
    add(T[i] + 0.05, X + "sub_drop.wav", 0.45)
add(T[141] - 2.2, X + "ub_riser.wav", 0.4)
add(dur - 2.4, X + "ub_hit.wav", 0.5)
# Atmos: Bahnhof bei Nacht (amb_night), Fabrik/Zählzentrum (amb_factory) – leise, nur wo das Bild es zeigt
ambs = [(T[0], T["T"], "amb_night.wav", 0.06), (T[83], T[87], "amb_night.wav", 0.06), (T[131], T[135], "amb_night.wav", 0.06), (T[171], T[175], "amb_night.wav", 0.05)]
for qi, p in enumerate(plan):
    if p.get("set", "").startswith(("fabrik", "zaehl", "automat_loch", "automat_innen", "automat_presse")) and p.get("run_k", 0) == 0:
        L = sum(plan[q]["dur"] for q in range(qi, min(len(plan), qi + p.get("run_len", 1))))
        ambs.append((p["t"], p["t"] + min(L, 12), "amb_factory.wav", 0.14 if p["set"].startswith(("fabrik", "zaehl")) else 0.1))   # Gemini 26.11.: Band/Automat zu leer
buf = voice + music
for a0, a1, af, ag in ambs:
    am = clip(X + af); n = int((a1 - a0) * SR)
    if n <= 0: continue
    m = np.concatenate([am] * (n // len(am) + 1))[:n].copy(); k2 = min(n, int(0.8 * SR))
    m[:k2] *= np.linspace(0, 1, k2)[:, None]; m[-k2:] *= np.linspace(1, 0, k2)[:, None]; place(buf, m, a0, ag)
for tt_, f, g in E:
    if f == "HUM": place(buf, hum_fall, tt_, g); continue
    if f == "CRUSH":
        e_ = np.convolve(np.abs(_cr[:, 0]), np.ones(SR // 2) / (SR // 2), "same"); pk = int(np.argmax(e_[:len(e_) - 2 * SR]))
        a = _cr[max(0, pk - int(0.6 * SR)): pk + int(1.4 * SR)].copy(); fo = int(0.3 * SR); a[-fo:] *= np.linspace(1, 0, fo)[:, None]; place(buf, a, tt_, g); continue
    cut = None
    if "#" in f: f, cut = f.split("#"); cut = float(cut)
    a = clip(f)
    if cut: a = a[:int(cut * SR)].copy(); fo = int(0.3 * SR); a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    place(buf, a, tt_, g)
buf = buf / (np.abs(buf).max() + 1e-9) * 0.9
wav(V + "voll_roh.wav", buf)
import unterbau as UB
UB.master(V + "voll_roh.wav", V + "voll_master.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vin, "-i", V + "voll_master.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", f"{dur:.3f}", vout], check=True)
print(len(E), "Effekte", lufs(vout))
