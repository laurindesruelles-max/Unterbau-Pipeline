"""Unterbau-Shorts aus dem fertigen Video (kostenlos bis auf die neuen Ein-/Ausstiegssätze, ~0,25–0,5 Credits je Satz).

python3 engine/shorts.py <work> <shorts.json> <final.mp4> <outdir>

shorts.json: [{"name": "01_notreserve",
               "intro": "shorts/s1.mp3", "intro_text": "…",   # neuer Satz von Julian (exakt eingesprochen)
               "img": "46",                                   # stärkstes Bild für den Einstieg (img/NN.png)
               "from": [6, "Und tatsächlich"], "to": [6, "fehlt."],   # Ausschnitt aus dem Video (Wortanker, "to" = letztes Wort)
               "outro": "shorts/s2.mp3", "outro_text": "…",
               "top": ["Notreserve", "über 150 geheime Lager"],      # Aufhänger oben (weiß / orange)
               "tag": "Gedankenexperiment"}]                         # optional: Kennzeichnung oben
Aufbau nach KANAL.md: Querformat mittig, oben/unten dasselbe Bild unscharf + abgedunkelt, oben Aufhänger, unten Untertitel
mit Wortzeiten (Parakeet), Schlusskarte mit Profilbild und Verweis aufs ganze Video. 1080x1920, 25 fps, −14 LUFS.
"""
import sys, os, json, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unterbau as U
import wordtimes as WT
from PIL import Image, ImageDraw, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FB, FM = U.FB, U.FM

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def run(cmd): subprocess.run(cmd, check=True)

def ass_time(t):
    t = max(0, t); h = int(t//3600); m = int(t % 3600//60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def endcard(path, text):
    W, H = 1920, 1080; im = Image.new("RGB", (W, H), (5, 14, 30)); d = ImageDraw.Draw(im)
    pb = Image.open(f"{REPO}/assets/brand/profilbild.png").convert("RGBA").resize((360, 360))
    im.paste(pb, (W//2-180, 200), pb)
    d.text((W//2, 650), "UNTERBAU", font=ImageFont.truetype(FB, 110), fill=(245, 245, 242), anchor="mm")
    d.text((W//2, 770), text, font=ImageFont.truetype(FM, 50), fill=(255, 122, 26), anchor="mm")
    im.save(path)

def build(work, cfg, final, outdir):
    spec, T, shots, ovs = U.build(work); os.makedirs(outdir, exist_ok=True)
    tmp = tempfile.mkdtemp()
    for c in cfg:
        n = c["name"]
        # Wortzeiten der neuen Sätze
        wi = f"{tmp}/{n}_i.txt"; open(wi, "w").write(c["intro_text"]); wo = f"{tmp}/{n}_o.txt"; open(wo, "w").write(c["outro_text"])
        iw = WT.align(c["intro_text"].split(), WT.recognize(WT.load(f"{work}/{c['intro']}")))
        ow = WT.align(c["outro_text"].split(), WT.recognize(WT.load(f"{work}/{c['outro']}")))
        di, do = dur(f"{work}/{c['intro']}")+0.35, dur(f"{work}/{c['outro']}")+1.0
        t0 = T.at(list(c["from"])+[-0.15]); t1 = T.word_end(c["to"])+0.45; de = t1-t0
        # Ausschnitt-Wörter
        ew = [(T.parts[pid]["t0"]+w["s"]-t0, T.parts[pid]["t0"]+w["e"]-t0, w["w"]) for pid, p in T.parts.items() for w in p["words"]
              if t0 <= T.parts[pid]["t0"]+w["s"] < t1]
        words = [(w["s"], w["e"], w["w"]) for w in iw] + [(s+di, e+di, w) for s, e, w in ew] + [(w["s"]+di+de, w["e"]+di+de, w["w"]) for w in ow]
        total = di+de+do
        # 1) Querformat-Zeitleiste: Einstieg (Bild mit Fahrt) + Ausschnitt + Schlusskarte
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{work}/img/{c['img']}.png", "-t", f"{di:.3f}",
             "-vf", f"scale=2112:1188,zoompan=z='1.0+0.0009*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(di*25)+1}:s=1920x1080:fps=25,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", f"{tmp}/{n}_a.mp4"])
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t0:.3f}", "-i", final, "-t", f"{de:.3f}", "-an", "-vf", "fps=25,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", f"{tmp}/{n}_b.mp4"])
        endcard(f"{tmp}/{n}_end.png", "Das ganze Video auf dem Kanal")
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", f"{tmp}/{n}_end.png", "-t", f"{do:.3f}", "-vf", "fps=25,format=yuv420p",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", f"{tmp}/{n}_c.mp4"])
        open(f"{tmp}/{n}_l.txt", "w").write("".join(f"file '{tmp}/{n}_{k}.mp4'\n" for k in "abc"))
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/{n}_l.txt", "-c", "copy", f"{tmp}/{n}_land.mp4"])
        # 2) Ton: neuer Satz + Ausschnitt aus dem Mix + Schlusssatz, Musikbett unter Ein-/Ausstieg
        mus = f"{REPO}/assets/music/ub_system_puls.mp3"
        run(["ffmpeg", "-y", "-v", "error", "-i", f"{work}/{c['intro']}", "-ss", f"{t0:.3f}", "-t", f"{de:.3f}", "-i", final, "-i", f"{work}/{c['outro']}", "-i", mus,
             "-filter_complex",
             f"[0]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={di:.3f}[i];[1:a]aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.25[e];"
             f"[2]aresample=48000,aformat=channel_layouts=stereo,adelay=300|300,apad=whole_dur={do:.3f}[o];[i][e][o]concat=n=3:v=0:a=1[v];"
             f"[3]aresample=48000,atrim=0:{total:.3f},volume='if(lt(t,{di:.3f})+gt(t,{di+de:.3f}),0.16,0)':eval=frame,afade=t=out:st={total-1.2:.3f}:d=1.2[m];"
             f"[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[out]",
             "-map", "[out]", f"{tmp}/{n}.wav"])
        # 3) Untertitel + Aufhänger (ASS)
        ass = ["[Script Info]", "PlayResX: 1080", "PlayResY: 1920", "", "[V4+ Styles]",
               "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
               "Style: Sub,Inter Display Black,74,&H00F2F5F5,&H00F2F5F5,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,2,60,60,330,1",
               "Style: Top1,Inter Display Black,86,&H00F2F5F5,&H00F2F5F5,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,60,60,250,1",
               "Style: Top2,Inter Display Black,74,&H001A7AFF,&H001A7AFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,5,2,8,60,60,360,1",
               "Style: Tag,Inter Display Medium,40,&H00F2F5F5,&H00F2F5F5,&H00000000,&H96000000,0,0,0,0,100,100,0,0,3,10,0,8,60,60,150,1",
               "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
        end_top = di+de
        ass.append(f"Dialogue: 0,{ass_time(0)},{ass_time(end_top)},Top1,,0,0,0,,{{\\fad(250,200)}}{c['top'][0]}")
        if len(c["top"]) > 1: ass.append(f"Dialogue: 0,{ass_time(0.15)},{ass_time(end_top)},Top2,,0,0,0,,{{\\fad(300,200)}}{c['top'][1]}")
        if c.get("tag"): ass.append(f"Dialogue: 0,{ass_time(di)},{ass_time(end_top)},Tag,,0,0,0,,{c['tag']}")
        i = 0
        while i < len(words):
            g = words[i:i+3]; s = g[0][0]; e = (words[i+3][0] if i+3 < len(words) else g[-1][1]+0.3)
            e = min(e, g[-1][1]+0.6)
            ass.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},Sub,,0,0,0,,{' '.join(w for _, _, w in g)}"); i += 3
        open(f"{tmp}/{n}.ass", "w").write("\n".join(ass)+"\n")
        # 4) Hochformat: Hintergrund = dasselbe Bild unscharf/dunkel, Mitte = Querformat
        run(["ffmpeg", "-y", "-v", "error", "-i", f"{tmp}/{n}_land.mp4", "-i", f"{tmp}/{n}.wav", "-filter_complex",
             "[0]split[a][b];[a]scale=-2:1920,crop=1080:1920,gblur=sigma=28,eq=brightness=-0.18[bg];[b]scale=1080:-2[fg];"
             f"[bg][fg]overlay=0:(H-h)/2,ass={tmp}/{n}.ass[v]", "-map", "[v]", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-c:a", "aac", "-b:a", "192k", "-shortest", f"{outdir}/{n}.mp4"])
        print(n, f"{total:.1f} s")

if __name__ == "__main__":
    build(sys.argv[1], json.load(open(sys.argv[2])), sys.argv[3], sys.argv[4])
