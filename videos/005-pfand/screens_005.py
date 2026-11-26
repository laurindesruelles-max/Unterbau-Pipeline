"""Bildschirm- und Dokument-Texturen für 005 (eigene Gestaltung, keine Logos). python3 screens_005.py OUTDIR"""
import sys, os, subprocess
from PIL import Image, ImageDraw, ImageFont
O = sys.argv[1]; os.makedirs(O, exist_ok=True)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
def f(s, b=True): return ImageFont.truetype(FB if b else FM, s)
OR = (255, 130, 40); BL = (225, 235, 250)

def display(name, lines, bg=(14, 28, 52)):
    im = Image.new("RGB", (960, 540), bg); d = ImageDraw.Draw(im)
    y = 270 - sum(l[1] for l in lines) * 0.6
    for txt, sz, col in lines:
        w = d.textlength(txt, font=f(sz)); d.text(((960 - w) / 2, y), txt, font=f(sz), fill=col); y += sz * 1.25
    im.save(os.path.join(O, name))

def doc(name, title, lines, hl=None, stamp=None):
    im = Image.new("RGB", (600, 850), (236, 234, 226)); d = ImageDraw.Draw(im)
    d.text((48, 50), title, font=f(30), fill=(25, 25, 30)); d.line([(48, 98), (552, 98)], fill=(60, 60, 70), width=3)
    y = 130
    for i, l in enumerate(lines):
        if hl is not None and i in hl:
            d.rectangle([40, y - 6, 560, y + 40], fill=(255, 175, 90))
        d.text((48, y), l, font=f(25, False), fill=(30, 30, 35)); y += 48
    for k in range(6):
        d.rectangle([48, y + 20 + k * 30, 48 + (460 if k % 3 else 380), y + 34 + k * 30], fill=(200, 198, 190))
    if stamp:
        s = Image.new("RGBA", (440, 120), (0, 0, 0, 0)); sd = ImageDraw.Draw(s)
        sd.rectangle([4, 4, 436, 116], outline=(190, 40, 30, 255), width=7); sd.text((26, 30), stamp, font=f(44), fill=(190, 40, 30, 255))
        s = s.rotate(8, expand=True); im.paste(s, (80, 600), s)
    im.resize((960, 540)).save(os.path.join(O, name))

display("display_025.png", [("PFAND", 48, (150, 180, 220)), ("0,25 €", 170, BL), ("Bon drücken", 40, OR)])
display("display_klopapier.png", [("Klopapierrolle + Pfandzeichen?", 46, (150, 180, 220)), ("0,25 €", 150, BL), ("früher: angenommen", 44, OR)])
display("display_datensatz.png", [("Pfandzeichen  ✓   Strichcode  ✓", 46, BL), ("Datensatz angelegt", 64, BL), ("digital signiert", 48, OR)])
display("kasse_pfand.png", [("6 × Wasser 0,5 l", 52, BL), ("6 × Pfand  0,25 €", 64, OR), ("= 1,50 € Pfand", 56, BL)], bg=(10, 18, 30))
display("kasse_gebuehr.png", [("Rücknahme-Gebühr", 60, (150, 180, 220)), ("gesetzlich: keine", 80, OR)], bg=(10, 18, 30))
doc("datenbank.png", "Pfandverpackungen – Datenbank", ["Strichcode         Material   Pfand", "40xxxxx00012  PET        0,25 €", "40xxxxx00029  Dose       0,25 €", "40xxxxx00036  PET        0,25 €", "40xxxxx00043  PET        0,25 €", "40xxxxx00050  Dose       0,25 €", "…"])
doc("doc_1991.png", "Verpackungsverordnung 1991", ["Mehrweganteil unter 72 %?", "→ Pflichtpfand auf", "   Einweg-Getränkeverpackungen", "", "(Kern der Regel, verkürzt)"], hl=[0])
doc("doc_2003.png", "Pfandpflicht ab 1. Januar 2003", ["Bier, Wasser, Erfrischungsgetränke", "mit Kohlensäure in Einweg:", "25 Cent (bis 1,5 l)", "50 Cent (über 1,5 l)", "", "Umsetzung 2002"], hl=[0])
doc("doc_gesetz.png", "§ 46 VerpackDG (verkürzt)", ["Pfand auf Einweg-Getränke-", "verpackungen: mindestens 0,25 €.", "", "„Ohne eine Rücknahme der", "Verpackung darf das Pfand", "nicht erstattet werden.“"], hl=[3, 4, 5])
doc("doc_urteil.png", "VG Schleswig, 20.05.2026", ["Az. 6 A 74/21", "Pfand gilt auch beim", "Verkauf an Skandinavier.", "", "Stand Mai 2026:"], stamp="NICHT RECHTSKRÄFTIG")
doc("doc_btdrs.png", "Antwort der Bundesregierung", ["Drucksache 21/3361, 18.12.2025", "", "„… fällt der Pfandschlupf", "weit überwiegend beim", "Einzelhandel an …“"])
doc("doc_btdrs_hl.png", "Antwort der Bundesregierung", ["Drucksache 21/3361, 18.12.2025", "", "„… fällt der Pfandschlupf", "weit überwiegend beim", "Einzelhandel an …“"], hl=[3, 4])
doc("doc_kosten.png", "Antwort der Bundesregierung", ["Drucksache 21/3361, 18.12.2025", "(sinngemäß)", "Der Handel trägt einen", "Großteil der Rücknahmekosten:", "Automaten, Fläche, Personal"], hl=[2, 3])
doc("doc_ppwr.png", "EU-Verpackungsverordnung", ["gilt seit 12.08.2026", "", "Art. 50: bis 2029 mindestens", "90 % getrennt sammeln –", "mit Pfandsystem"], hl=[0])
doc("doc_verpackdg.png", "§ 46 VerpackDG", ["seit August 2026", "", "Einwegpfand:", "mindestens 0,25 €", "(wie seit 2006)"], hl=[3])
# Zähler-Video für den manipulierten Automaten: 0,25 → … schnell hochzählen
tmp = os.path.join(O, "_z"); os.makedirs(tmp, exist_ok=True)
for i in range(150):
    v = 0.25 * (1 + int((i / 150) ** 1.6 * 60))
    im = Image.new("RGB", (960, 540), (40, 10, 10)); d = ImageDraw.Draw(im)
    t1 = "DIESELBE FLASCHE"; t2 = f"{v:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    d.text(((960 - d.textlength(t1, font=f(48))) / 2, 120), t1, font=f(48), fill=(240, 150, 120))
    d.text(((960 - d.textlength(t2, font=f(150))) / 2, 220), t2, font=f(150), fill=(255, 220, 200))
    im.save(os.path.join(tmp, f"{i:04d}.png"))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "25", "-i", os.path.join(tmp, "%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", os.path.join(O, "zaehler.mp4")], check=True)
print("ok")
