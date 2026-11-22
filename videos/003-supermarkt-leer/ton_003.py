"""Ton für 003 (ganzes Video) nach Sound-Plan: Stimme (7 Kapitel), Musik je Kapitel atmet (Ducking −9 dB, Pausen vor großen Sätzen,
Swells vor Enthüllungen, 2 s Überblendung), Effekte nur auf echten Bild-Ereignissen. Master −14 LUFS / TP −2 dB (mixer.py).
python3 ton_003.py VIDEO_IN VIDEO_OUT plan.json"""
import sys, json, wave, numpy as np
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine/stilproben")
from mixer import load, mix, SR
U = "/home/claude/unterbau-pipeline/assets/"; X = "/home/claude/ub_sfx/"; V = "/home/claude/unterbau-work/v2/"; W2 = "/home/claude/unterbau-work/sfx/"
vin, vout, plan = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
S = json.load(open(V + "saetze.json"))
T, tt = {}, 0.0
for p in plan: T.setdefault(p["i"], tt); p["t"] = tt; tt += p["dur"]
dur = tt; N = int(dur * SR)

def wav(path, a):
    a = np.clip(a, -1, 1); st = np.stack([a, a], 1) if a.ndim == 1 else a
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())

# Stimme: Kapitel k beginnt dort, wo sein erster Satz im Plan beginnt (minus Startzeit des ersten Wortes)
voice = np.zeros((N, 2), np.float32); kap_start = {}
for k in range(1, 8):
    i0 = min(i for i, s in enumerate(S) if s[0] == k); t0 = T[i0] - S[i0][1]; kap_start[k] = t0
    a = load(V + f"audio/{k}.mp3"); j = int(t0 * SR); a = a[:N - j]; voice[j:j + len(a)] += a
wav(V + "voll_stimme.wav", voice)

# Musik je Kapitel
plan_m = {1: ("ub_kaltstart_meer", 0), 2: ("ub_system_puls", 0), 3: ("ub_spannung_aufbau", 0), 4: ("ub_ausfall_dunkel", 0),
          5: ("ub_spannung_aufbau", 40), 6: ("ub_system_puls", 70), 7: ("ub_aufloesung_weit", 0)}
music = np.zeros((N, 2), np.float32)
edges = [kap_start[k] for k in range(1, 8)] + [dur]
for k in range(1, 8):
    name, off = plan_m[k]; m = load(U + f"music/{name}.mp3")
    a, b = max(0, edges[k - 1] - 1.0), min(dur, edges[k] + 1.0); n = int((b - a) * SR)
    seg = np.concatenate([m[int(off * SR):], m, m])[:n]
    env = np.ones(len(seg), np.float32); f = int(2.0 * SR)
    env[:f] *= np.linspace(0, 1, min(f, len(env))); env[-f:] *= np.linspace(1, 0, min(f, len(env)))
    j = int(a * SR); music[j:j + len(seg)] += seg * env[:, None]
t = np.arange(N) / SR
ev = np.abs(voice[:, 0]); k = int(0.25 * SR); ev = np.convolve(ev, np.ones(k) / k, "same")
act = np.convolve(np.clip(ev / 0.02, 0, 1), np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
gain = 10 ** (-9 * act / 20) * 0.5
for i in (6, 37, 117, 121, 153):          # Musik weg vor großen Sätzen, mit dem Satz zurück
    ts = T[i]; gain *= np.clip(1 - np.clip((t - (ts - 0.9)) / 0.15, 0, 1) + np.clip((t - (ts + 0.1)) / 0.5, 0, 1), 0, 1)
for i in (9, 27, 89, 132, 152, 181):      # Swell vor Enthüllungen
    gain *= 10 ** (5 * np.clip(1 - np.abs(t - (T[i] - 0.5)) / 2.5, 0, 1) / 20)
music *= gain[:, None]; music[-int(2 * SR):] *= np.linspace(1, 0, int(2 * SR))[:, None]
wav(V + "voll_musik.wav", music)

# Stromausfall-Brummen (Tonhöhe fällt, erstirbt)
hum = load(X + "fire_electric_hum_39.wav")[:, 0]; n = int(3.2 * SR); pos = np.cumsum(np.linspace(1.0, 0.45, n)); pos = pos[pos < len(hum) - 1]
wav(V + "hum_fall.wav", np.interp(pos, np.arange(len(hum)), hum) * np.linspace(1, 0, len(pos)) ** 1.5)

E = []
def add(tt, f, g): E.append((tt, f, g))
for p in plan:
    a, t0 = p["anim"], p["t"]
    for fx in p["fx"]:
        if fx["type"] == "tafel":
            for j in range(len(fx["texts"])): add(t0 + j * p["dur"] / len(fx["texts"]) + 0.02, X + "paper_flip.wav", 0.42)
        if fx["type"] == "clock": add(t0 + 0.15, W2 + "tick.wav", 0.25)
    if a in ("Tilt-Shift-Flug", "Rückflug zum Anfang"): add(t0 + 0.05, U + "sfx/whoosh_slow_soft.wav", 0.18)
    if a == "Lichter gehen aus" and p.get("trans") == "lights": add(t0 + p["dur"] * p["t_trans"][0], V + "hum_fall.wav", 0.3)
    if a == "Bildschirm in der Welt": add(t0 + 0.05, U + "sfx/whoosh_slow_soft.wav", 0.1)
for i in (6, 24, 25, 33, 56, 59, 98, 102, 103, 108, 121, 132, 139, 153, 168, 181, 185):
    add(T[i] + 0.05, U + "sfx/sub_drop.wav", 0.55)
for i in (1, 192): add(T[i] + 0.15, X + "door_open.wav", 0.32)
add(T[39] + 0.1, X + "door_open.wav", 0.25)
ambs = [(W2 + "amb_night.wav", 0.05, 0.0, 2.0, 2.0)]
for i in (42, 45, 58, 60, 70):            # Markt-Atmo unter Menschen-Szenen
    p = [q for q in plan if q["i"] == i][0]; ambs.append((W2 + "amb_market.wav", 0.07, p["t"], 0.3, 0.4, [], 0, p["t"] + p["dur"]))
mus = [(V + "voll_stimme.wav", 1.0, 0.0, 0.0, 0.05), (V + "voll_musik.wav", 1.0, 0.0, 0.0, 0.05)] + ambs
print(mix(vin, vout, E, dur, mus))
