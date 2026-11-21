"""Ton für die Kapitel-1-Vorschau (Sound-Plan nach EFFEKTE.md/HANDWERK.md): Stimme, Musik atmet (Ducking -9 dB, Pause vor dem großen Satz,
Swell vor der Frage), Effekte nur auf echten Bild-Ereignissen."""
import sys, json, subprocess, numpy as np
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine/stilproben")
from mixer import load, mix, SR
U = "/home/claude/unterbau-pipeline/assets/"; X = "/home/claude/ub_sfx/"; V = "/home/claude/unterbau-work/v2/"
vin, vout = sys.argv[1], sys.argv[2]
plan = json.load(open(sys.argv[3]))
T = {}; t = 0
for p in plan:
    T.setdefault(p["i"], t); t += p["dur"]
dur = t
voice = load(V + "audio/1.mp3")[: int(dur * SR)]
# Stromausfall-Brummen: Tonhöhe gleitet ab und erstirbt (keine Klacks)
hum = load(X + "fire_electric_hum_39.wav")[:, 0]
n = int(3.2 * SR); rate = np.linspace(1.0, 0.45, n); pos = np.cumsum(rate); pos = pos[pos < len(hum) - 1]
fall = np.interp(pos, np.arange(len(hum)), hum) * np.linspace(1, 0, len(pos)) ** 1.5
import wave
def wav(p, a):
    a = np.clip(a, -1, 1); st = np.stack([a, a], 1) if a.ndim == 1 else a
    with wave.open(p, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype("<i2").tobytes())
wav(V + "hum_fall.wav", fall)
# Musik: Kaltstart-Track, Ducking unter der Stimme, Pause vor „Heute Nacht fährt kein einziger Lkw“, Swell vor der Frage
mus = load(U + "music/ub_kaltstart_meer.mp3")
m = np.zeros((int(dur * SR), 2), np.float32); L = min(len(mus), len(m)); m[:L] = mus[:L]
env_v = np.abs(np.pad(voice[:, 0], (0, max(0, len(m) - len(voice))))[:len(m)])
k = int(0.25 * SR); env_v = np.convolve(env_v, np.ones(k) / k, "same"); act = np.clip(env_v / 0.02, 0, 1)
act = np.convolve(act, np.ones(int(0.3 * SR)) / int(0.3 * SR), "same")
gain = 10 ** (-9 * act / 20) * 0.55
tt = np.arange(len(m)) / SR
t6 = T[6]; rest = np.clip(1 - np.clip((tt - (t6 - 0.9)) / 0.15, 0, 1) + np.clip((tt - (t6 + 0.15)) / 0.4, 0, 1), 0, 1)   # 0.9 s Stille vor dem Satz
t9 = T[9]; swell = 10 ** (5 * np.clip(1 - np.abs(tt - (t9 - 0.4)) / 2.5, 0, 1) / 20)
m = m * (gain * rest * swell)[:, None]
m[-int(1.5 * SR):] *= np.linspace(1, 0, int(1.5 * SR))[:, None]
wav(V + "k1_musik.wav", m * 1.0)
wav(V + "k1_stimme.wav", np.pad(voice, ((0, len(m) - len(voice)), (0, 0))) if len(voice) < len(m) else voice[:len(m)])
ev = [(T[0] + 0.2, U + "sfx/whoosh_slow_soft.wav", 0.18),
      (T[1] + 0.15, X + "door_open.wav", 0.35),
      (T[3] + 0.0, U + "sfx/whoosh_slow_soft.wav", 0.22),
      (t6 + 0.05, U + "sfx/sub_drop.wav", 0.8),
      (T[7] + 0.1, V + "hum_fall.wav", 0.35),
      (T[11] + 0.2, X + "paper_flip.wav", 0.4)]
for j in range(3): ev.append((T[12] + j * plan[[p["i"] for p in plan].index(12)]["dur"] / 3 + 0.02, X + "paper_flip.wav", 0.45))
ev += [(T[14] + 0.05, X + "paper_flip.wav", 0.45), (T[14] + plan[[p["i"] for p in plan].index(14)]["dur"] / 2, X + "paper_flip.wav", 0.45),
       (T[15] + 0.3, U + "sfx/whoosh_slow_soft.wav", 0.2)]
music = [(V + "k1_stimme.wav", 1.0, 0.0, 0.0, 0.05), (V + "k1_musik.wav", 1.0, 0.0, 0.0, 0.05),
         (U + "sfx/amb_night.wav" if False else "/home/claude/unterbau-work/sfx/amb_night.wav", 0.06, 0.0, 1.0, 1.0)]
print(mix(vin, vout, ev, dur, music))
