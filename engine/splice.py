"""Einzelne Einstellungen in einem fertig gerenderten Bild-Video ersetzen, ohne alles neu zu rendern (Ton bleibt synchron).
python3 engine/splice.py plan.json RENDERDIR bild_alt.mp4 bild_neu.mp4 "0,75,141" "7,8,43" [--fps 25]
Teile = Startindizes der Abschnitte, mit denen bild_alt gerendert wurde (gleiche Rundung wie stadtcomp)."""
import sys, os, json, subprocess, numpy as np
plan_p, rdir, alt, neu, parts, ch = sys.argv[1:7]; FPS = 25; W, H = 1920, 1080
plan = json.load(open(plan_p)); parts = [int(x) for x in parts.split(",")] + [len(plan)]; ch = [int(x) for x in ch.split(",")]
bounds = {}; base = 0
for a, b in zip(parts, parts[1:]):
    n = 0; tacc = 0.0
    for k in range(a, b):
        tacc += plan[k]["dur"]; fr = int(round(tacc * FPS)) - n; bounds[k] = (base + n, base + n + fr); n += fr
    base += n
segs = {}
for k in ch:
    out = f"/tmp/seg_{k}.mp4"
    subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "stadtcomp.py"), plan_p, rdir, out, "--from", str(k), "--to", str(k + 1)], check=True)
    segs[k] = out
def reader(p): return subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
src = reader(alt)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", neu], stdin=subprocess.PIPE)
total = base; cur = None; curk = None; last = None; sz = W * H * 3
for i in range(total):
    fr = src.stdout.read(sz)
    if len(fr) < sz: fr = last
    k = next((k for k in ch if bounds[k][0] <= i < bounds[k][1]), None)
    if k is not None:
        if curk != k: cur = reader(segs[k]); curk = k; lastseg = None
        f2 = cur.stdout.read(sz)
        if len(f2) == sz: lastseg = f2
        fr = lastseg if lastseg is not None else fr
    last = fr; enc.stdin.write(fr)
enc.stdin.close(); enc.wait(); print("fertig", total, "Bilder,", len(ch), "Einstellungen ersetzt")
