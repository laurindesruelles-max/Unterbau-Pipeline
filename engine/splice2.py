"""Neues Bild-Video aus einem alten bauen, wenn sich Einstellungs-LÄNGEN geändert haben (z. B. nach grafik_zeit.py):
Einstellungen mit "grafik_neu" werden neu gerendert, alle anderen übernehmen ihre alten Bilder – gekürzt um "cut_head" (vorne)
bzw. "cut_tail" (hinten). Gleiche Zahl und Reihenfolge der Einstellungen in beiden Plänen.
python3 engine/splice2.py plan_alt.json plan_neu.json RENDERDIR bild_alt.mp4 bild_neu.mp4 "0,75,141"
("0,75,141" = Startindizes der Teile, mit denen bild_alt gerendert wurde, gleiche Rundung wie stadtcomp)"""
import sys, os, json, subprocess, numpy as np
po, pn, rdir, alt, neu, parts = sys.argv[1:7]; FPS = 25; W, H = 1920, 1080; SZ = W * H * 3
old = json.load(open(po)); new = json.load(open(pn)); assert len(old) == len(new)
def bounds(plan, parts):
    b = {}; base = 0; parts = parts + [len(plan)]
    for a, c in zip(parts, parts[1:]):
        n = 0; t = 0.0
        for k in range(a, c): t += plan[k]["dur"]; fr = int(round(t * FPS)) - n; b[k] = (base + n, base + n + fr); n += fr
        base += n
    return b
ob = bounds(old, [int(x) for x in parts.split(",")]); nb = bounds(new, [0])
redo = [k for k, p in enumerate(new) if p.get("grafik_neu") and abs(p["dur"] - old[k]["dur"]) > 1e-3]
segs = {}
for k in redo:
    out = f"/tmp/seg2_{k}.mp4"
    if not os.path.exists(out):
        subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "stadtcomp.py"), pn, rdir, out, "--from", str(k), "--to", str(k + 1)], check=True, stdout=subprocess.DEVNULL)
    segs[k] = out
def reader(p): return subprocess.Popen(["ffmpeg", "-v", "error", "-i", p, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
src = reader(alt); pos = 0; last = None
def read_until(i):          # liefert altes Bild Nr. i (nur vorwärts)
    global pos, last
    while pos <= i:
        fr = src.stdout.read(SZ)
        if len(fr) == SZ: last = fr
        pos += 1
    return last
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", neu], stdin=subprocess.PIPE)
for k in range(len(new)):
    n = nb[k][1] - nb[k][0]
    if k in segs:
        r = reader(segs[k]); lf = None
        for _ in range(n):
            fr = r.stdout.read(SZ); lf = fr if len(fr) == SZ else lf; enc.stdin.write(lf)
        r.stdout.close(); r.wait()
    else:
        o0, o1 = ob[k]; s0 = o0 + int(round(new[k].get("cut_head", 0) * FPS))
        s0 = min(s0, o1 - n) if new[k].get("cut_head") else s0       # Länge exakt treffen
        for f in range(s0, s0 + n): enc.stdin.write(read_until(min(f, o1 - 1)))
enc.stdin.close(); enc.wait(); print("fertig", len(redo), "neu gerendert:", ",".join(new[k]["id"] for k in redo))
