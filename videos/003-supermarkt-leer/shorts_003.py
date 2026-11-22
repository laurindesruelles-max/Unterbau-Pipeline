"""Shorts aus dem fertigen 003-Video (kostenlos): Ausschnitt nach Satz-Index, Hochformat mit unscharfem Hintergrund,
Aufhänger oben, Wort-Untertitel (Parakeet-Zeiten), Schlusskarte. python3 shorts_003.py FINAL.mp4 plan.json OUTDIR"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine")
from shorts import endcard, ass_time
V = "/home/claude/unterbau-work/v2/"
final, plan, out = sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3]; os.makedirs(out, exist_ok=True)
S = json.load(open(V + "saetze.json"))
T, t = {}, 0.0
for p in plan: T.setdefault(p["i"], t); t += p["dur"]
words = []   # globale Wortzeiten im fertigen Video
for k in range(1, 8):
    i0 = min(i for i, s in enumerate(S) if s[0] == k); off = T[i0] - S[i0][1]
    for w in json.load(open(V + f"words/w{k}.json"))["words"]: words.append((w["s"] + off, w["e"] + off, w["w"]))
SH = [("01_kein_lager", 26, 36, ["Dein Supermarkt", "hat fast kein Lager"]),
      ("02_eine_woche", 53, 66, ["7 Tage", "und Großbritannien stand still"]),
      ("03_sprit_ist_da", 86, 92, ["90 Tage Sprit", "aber er kommt nicht an"]),
      ("04_graefenhausen", 104, 112, ["Gräfenhausen 2023", "Fahrer streiken für ihren Lohn"]),
      ("05_notreserve", 133, 153, ["Die geheime Notreserve", "und ihr großes Problem"])]
tmp = tempfile.mkdtemp()
for name, a, b, top in SH:
    t0 = T[a] - 0.1; t1 = T[b + 1] if (b + 1) in T else T[b] + 4; de = t1 - t0; tot = de + 2.5
    endcard(f"{tmp}/{name}_end.png", "Das ganze Video auf dem Kanal")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.3f}", "-i", final, "-t", f"{de:.3f}", "-vf", "fps=25,format=yuv420p", "-af", "afade=t=in:d=0.2,afade=t=out:st=%.3f:d=0.4" % (de - 0.4),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-ar", "48000", "-ac", "2", f"{tmp}/{name}_b.mp4"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{tmp}/{name}_end.png", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "2.5",
                    "-vf", "scale=1920:1080,fps=25,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-shortest", f"{tmp}/{name}_c.mp4"], check=True)
    open(f"{tmp}/{name}_l.txt", "w").write(f"file '{tmp}/{name}_b.mp4'\nfile '{tmp}/{name}_c.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/{name}_l.txt", "-c", "copy", f"{tmp}/{name}_land.mp4"], check=True)
    ass = ["[Script Info]", "PlayResX: 1080", "PlayResY: 1920", "", "[V4+ Styles]",
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
           "Style: Sub,Inter Display Black,74,&H00F2F5F5,&H00F2F5F5,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,60,60,330,1",
           "Style: Top1,Inter Display Black,86,&H00F2F5F5,&H00F2F5F5,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,60,60,250,1",
           "Style: Top2,Inter Display Black,66,&H001A7AFF,&H001A7AFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,60,60,370,1",
           "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
           f"Dialogue: 0,{ass_time(0)},{ass_time(de)},Top1,,0,0,0,,{{\\fad(250,200)}}{top[0]}",
           f"Dialogue: 0,{ass_time(0.15)},{ass_time(de)},Top2,,0,0,0,,{{\\fad(300,200)}}{top[1]}"]
    ws = [(s - t0, e - t0, w) for s, e, w in words if t0 <= s < t1]
    i = 0
    while i < len(ws):
        g = ws[i:i + 3]; s = g[0][0]; e = min(ws[i + 3][0] if i + 3 < len(ws) else g[-1][1] + 0.3, g[-1][1] + 0.6)
        ass.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Sub,,0,0,0,,{' '.join(w for _, _, w in g)}"); i += 3
    open(f"{tmp}/{name}.ass", "w").write("\n".join(ass) + "\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", f"{tmp}/{name}_land.mp4", "-filter_complex",
                    "[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.18[bg];[b]scale=1080:-2[fg];"
                    f"[bg][fg]overlay=0:(H-h)/2,ass={tmp}/{name}.ass[v]", "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-af", "loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "192k", f"{out}/{name}.mp4"], check=True)
    print(name, f"{tot:.1f} s")
