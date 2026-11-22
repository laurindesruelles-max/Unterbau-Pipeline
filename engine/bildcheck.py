"""Bild-Prüfung vor jeder Abgabe (Laurin 22.11.2026: „Sowas sollte dir bei der Prüfung auffallen!“).
Findet automatisch, was ein Zuschauer als Fehler sieht:
  1. Sprung-Schnitte: harter Schnitt zwischen zwei Bildern, die sich stark ähneln (gleicher Ort, anderer Winkel/Ausschnitt)
     -> statt Schnitt durchgehende Kamerafahrt oder Überblendung.
  2. Unschärfe: Einstellungen, die deutlich weicher sind als der Rest des Videos (z. B. 2,5D-Verzerrung, zu starkes Hochskalieren).
  3. Zu dunkle / zu leere Einstellungen (mittlere Helligkeit, Anteil fast schwarzer Pixel).
  4. Standbild: Einstellung ohne Eigenbewegung über > 5 s.
python3 engine/bildcheck.py VIDEO.mp4 [--out qa_bild.md]   -> Exit 1 bei Fehlern
"""
import sys, subprocess, argparse, numpy as np, cv2

def frames(path, fps=5, w=320):
    h = int(w * 9 / 16)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(w * h)
        if len(b) < w * h: break
        yield np.frombuffer(b, np.uint8).reshape(h, w).astype(np.float32)

def sharp_frames(path, fps=1):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale=1920:1080", "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    n = 1920 * 1080
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        g = np.frombuffer(b, np.uint8).reshape(1080, 1920).astype(np.float32)
        yield cv2.Laplacian(g[200:880, 300:1620], cv2.CV_32F).var(), g.mean(), (g < 12).mean()

def ncc(a, b):
    a = a - a.mean(); b = b - b.mean(); return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-6))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("--out", default=None); ap.add_argument("--fps", type=int, default=5)
    ap.add_argument("--plan", help="Render-Plan (shots.json + plan.json im selben Ordner): gleicher Schauplatz nacheinander mit anderer Kamera = Sprung-Schnitt")
    a = ap.parse_args(); F = a.fps
    fr = list(frames(a.video, F)); fehler, warn = [], []
    if a.plan:
        import json, os
        sh = json.load(open(os.path.join(a.plan, "shots.json"))); pl = json.load(open(os.path.join(a.plan, "plan.json"))); t = 0.0
        for k in range(1, len(sh)):
            t += pl[k - 1]["dur"]
            if sh[k]["set"] == sh[k - 1]["set"] and sh[k]["cam"] != sh[k - 1]["cam"]:
                fehler.append(f"{t:6.1f}s Sprung-Schnitt laut Plan: {sh[k]['set']} zweimal hintereinander mit anderer Kamera")
    # Schnitte finden: großer Sprung zwischen Nachbarbildern
    d = [np.abs(fr[i] - fr[i - 1]).mean() for i in range(1, len(fr))]
    med = np.median(d) + 1e-6; cuts = [i for i in range(1, len(fr)) if d[i - 1] > max(18, 6 * med)]
    for i in cuts:
        if i < 2 or i + 1 >= len(fr): continue
        before, after = fr[i - 1], fr[i]
        # Ähnlichkeit nach Ausrichtung: Histogramm + grobe Struktur (verkleinert, weichgezeichnet)
        sb = cv2.GaussianBlur(cv2.resize(before, (64, 36)), (0, 0), 1.5); sa = cv2.GaussianBlur(cv2.resize(after, (64, 36)), (0, 0), 1.5)
        hb = cv2.calcHist([before.astype(np.uint8)], [0], None, [32], [0, 256]); ha = cv2.calcHist([after.astype(np.uint8)], [0], None, [32], [0, 256])
        hs = cv2.compareHist(hb, ha, cv2.HISTCMP_CORREL); st = ncc(sb, sa)
        if hs > 0.9 and st > 0.35:
            fehler.append(f"{i / F:6.1f}s Sprung-Schnitt: Bild davor und danach sehr ähnlich (Histogramm {hs:.2f}, Struktur {st:.2f}) – gleiche Szene? Durchgehende Fahrt oder Überblendung statt Schnitt")
    # Standbild: Abschnitte ohne Bewegung
    still = 0
    for i, x in enumerate(d):
        still = still + 1 if x < 0.4 else 0
        if still == int(5 * F): warn.append(f"{(i - still + 1) / F:6.1f}s über 5 s kaum Bewegung im Bild")
    # Schärfe, Helligkeit
    S = list(sharp_frames(a.video)); lap = np.array([s[0] for s in S]); ref = np.median(lap)
    for t, (l, m, black) in enumerate(S):
        if l < 0.25 * ref and m > 30: fehler.append(f"{t:6d}s unscharf (Schärfe {l:.0f} vs. Median {ref:.0f})")
        if m < 18: warn.append(f"{t:6d}s sehr dunkel (Helligkeit {m:.0f})")
        if black > 0.55: warn.append(f"{t:6d}s über die Hälfte des Bildes fast schwarz/leer")
    rep = [f"# Bild-Prüfung {a.video}", f"{len(cuts)} Schnitte erkannt, Schärfe-Median {ref:.0f}", ""] + [f"- FEHLER {x}" for x in fehler] + [f"- Warnung {x}" for x in warn]
    rep.append("OK ✅" if not fehler else f"{len(fehler)} Fehler ❌")
    print("\n".join(rep))
    if a.out: open(a.out, "w").write("\n".join(rep) + "\n")
    sys.exit(1 if fehler else 0)

if __name__ == "__main__":
    main()
