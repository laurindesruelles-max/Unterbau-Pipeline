"""Video 005 „Wer an deiner Pfandflasche verdient“: Bild-Drehbuch → bilddrehbuch.json, shots.json (engine/stadt.py --extra pfand),
plan.json (engine/stadtcomp.py), motion-Jobs (engine/motion_ub.py). Satzzeiten aus saetze.json (Parakeet-Wortzeiten);
ohne saetze.json (vor dem Einsprechen) werden sie aus der Wortzahl geschätzt (2,5 Wörter/s) – nur für die Bild-Drehbuch-Prüfung.
python3 plan_005.py WORK OUTDIR [--build-motion]"""
import json, sys, os, hashlib
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine"); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sets_005 import SETS
WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
SP = os.path.join(WORK, "v5/saetze.json")
if os.path.exists(SP):
    S = json.load(open(SP))
else:
    T0 = json.load(open(os.path.join(WORK, "v5/saetze_text.json"))); S = []; acc = {}
    for k, s in T0:
        d = max(0.8, len(s.split()) / 2.5); t = acc.get(k, 0.0); S.append([k, t, t + d - 0.25, s]); acc[k] = t + d
V = WORK + "/vid/"; SC = WORK + "/scr/"

DH, CD, LA, QS, TF, MK, ZW, LW, BW = "Dein Haus", "Countdown in der Welt", "Lichter gehen aus", "Querschnitt", "Tilt-Shift-Flug", "Modell-Karte", "Zahl in der Welt", "Leben in der Welt", "Bildschirm in der Welt"
RL, WS = "Regale leeren sich", "Warenstrom"
FZ, AK2, LR, HB, WK, AD = "Fallblatt-Zahl (`motion` counter)", "Ablauf-Kette 2D (`motion` flow)", "Lichter-aus-Raster (`motion` grid)", "Häuserzeilen-Balken (`motion` bars)", "Warenstrom-Karte (`motion` map)", "Anzeigetafel dreht sich (`motion` flip)"
NP, MR, NK, TN, SZ, RF, LT, MW = "Netz-Puls", "Menschen reagieren", "Netzwerk-Karte", "Tag-Nacht-Zeitraffer", "Steuerzentrale", "Rückflug zum Anfang", "Lagerbestand-Turm", "Modellbahn-Warenstrom"

def b(st, zeigt, anim, gen="exakt", inh=("geschehen",), neu="", **kw): return dict(k="b", set=st, zeigt=zeigt, anim=anim, gen=gen, inh=list(inh), neu=neu, **kw)
def mo(comp, props, zeigt, anim, gen="exakt", inh=("zahl",), neu="", **kw): return dict(k="mo", comp=comp, props=props, zeigt=zeigt, anim=anim, gen=gen, inh=list(inh), neu=neu, **kw)
def cl(f, zeigt, ss=0.0, gen="exakt", inh=("geschehen",), neu="", **kw): return dict(k="cl", video=V + f, ss=ss, zeigt=zeigt, anim=BW, gen=gen, inh=list(inh), neu=neu, **kw)
def LB(text, anchor=None, sub=None, t0=0.15): d = {"type": "label", "text": text, "t0": t0}; d.update({"anchor": anchor} if anchor else {"pos": (800, 90)}); d.update({"sub": sub} if sub else {}); return d
def T(*texts, anchor="tafel", **kw): return {"type": "tafel", "anchor": anchor, "texts": list(texts), **kw}
def SCR(img=None, anchor="a_display", video=None, ss=0.0): return {"type": "screen", "anchor": anchor, **({"video": video, "ss": ss} if video else {"img": SC + img})}
def CLK(a, b_, anchor="b_uhr", t0=0.05, tl=0.8): return {"type": "clock", "anchor": anchor, "from": a, "to": b_, "t0": t0, "tl": tl}
GREY = {"type": "grey", "amount": 0.85, "t0": 0}
def DOTS(path, n=12, sp=0.05, r=5): return {"type": "dots", "path": path, "n": n, "speed": sp, "r": r}
Z = {}

SH = {
 0: [b("flasche_makro", "Makro: die Pfandflasche liegt unter der Bank, Einblendung 25 Cent", LW, inh=("zahl",), fx=[LB("25 Cent", None, "Pfand")])],
 1: [b("bank_nah", "Die Flasche liegt allein unter der Bank, niemand kommt – Frage: Wer behält das Pfand?", LW, neu="frage:pfand", fx=[LB("Wer behält das Pfand?", None, None, 0.35)])],
 2: "merge",
 3: [b("bahnhof_uhr", "Bahnhofsuhr zeigt 18:40, Ortsmarke Dortmund, Samstag", CD, inh=("zeit", "ort"), fx=[CLK(1118, 1120), LB("Dortmund · Samstag, 18:40 Uhr", None, None, 0.1)])],
 4: [b("bahnhof_total", "Bahnsteig bei Nacht: Bank, Mülleimer, die Flasche liegt unter der Bank", LW, inh=("ort",))],
 5: [b("route_total", "Tilt-Shift-Flug vom Bahnhof zwei Straßen weiter zum Supermarkt", TF, inh=("ort",), fx=[LB("Supermarkt", "markt")]),
     b("automat_total", "Ein Mann steht am Pfandautomaten und schiebt die gleiche Flasche hinein", MR)],
 6: [b("automat_loch", "Die Flasche dreht sich in der Öffnung, das Scanlicht tastet sie ab – Piep", LW)],
 7: "merge",
 8: [b("automat_display", "Display des Automaten springt auf 0,25 €", BW, inh=("zahl",), fx=[SCR("display_025.png")])],
 9: [cl("px19543.mp4", "Echter Clip: weggeworfene Flasche am Ufer, Einblendung hunderte Millionen pro Jahr (Schätzung)", 1.0, inh=("zahl",), fx=[LB("Hunderte Millionen pro Jahr", None, "Schätzung", 0.1)])],
 10: [b("kasse_band", "An der Kasse liegt ein Sechserpack auf dem Band", MR)],
 11: [b("kasse_display", "Kundendisplay: 6 × Pfand 0,25 € = 1,50 €", BW, inh=("zahl",), fx=[SCR("kasse_pfand.png", "k_disp")])],
 12: [b("automat_front", "Querschnitt: die Front des Automaten wird durchsichtig – Röhre, Kamera-Ring, Presse; Einblendung 40.000 Automaten", QS, gen="schema", inh=("erklaerung", "zahl"),
        B={"cut": 1, "innen": 1, "scan": 1}, trans="wipe_down", t_trans=[0.1, 0.55], fx=[LB("über 40.000 Automaten", None, "7 Abrechnungsfirmen · 1 neues Gesetz", 0.2)])],
 13: [mo("flow", {"label": "AM ENDE WEISST DU", "nodes": [{"icon": "money", "label": "wer verdient"}, {"icon": "lock", "label": "wer betrügt"}, {"icon": "doc", "label": "was die EU verlangt"}], "packet": "bottle"},
        "Ablauf-Kette: wer verdient → wer betrügt → was die EU verlangt, eine Flasche wandert mit", AK2, gen="schema", inh=("erklaerung",), neu="teaser:versprechen")],
 14: [b("bahnhof_zug", "Regionalzug fährt ein, Bank mit Flasche, Einblendung Szene nachgestellt", LW, inh=("erklaerung",), fx=[LB("Szene nachgestellt", None, None, 0.05)])],
 15: "merge",
 "T": [b("stadt_total", "Titelkarte UNTERBAU über der Modellstadt", TF, inh=("erklaerung",), fx=[{"type": "card", "top": "WER AN DEINER PFANDFLASCHE VERDIENT", "title": "UNTERBAU", "sub": "Verstehen, wie die Welt funktioniert"}])],
 "K1": [b("automat_total", "Kapitelkarte 1 vor dem Automaten", TF, inh=("erklaerung",), fx=[{"type": "card", "top": "KAPITEL 1", "title": "Die Reise der Flasche"}])],
 16: [b("automat_loch", "Zurück am Automaten: die Flasche dreht sich noch, Scanlicht kreist", LW)],
 17: "merge", 18: "merge",
 19: [cl("px5351.mp4", "Strichcode-Linien laufen über den Bildschirm: Strichcode und Pfandzeichen werden gesucht", 0.5, inh=("erklaerung",), fx=[LB("Strichcode + Pfandzeichen", None, None, 0.1)])],
 20: [b("automat_total", "Der Mann wartet vor dem Automaten, ein paar Sekunden vergehen", MR, inh=("zeit",), fx=[LB("ältere Geräte: ein paar Sekunden", None, None, 0.1)])],
 21: [b("automat_innen", "Querschnitt innen: sechs Kameras im Ring blitzen gleichzeitig auf die Flasche", QS, gen="schema", inh=("erklaerung", "zahl"), fx=[LB("bis zu 6 Kameras", None, None, 0.15)])],
 22: [cl("px152728.mp4", "Echte Druckmaschine läuft – Einblendung Spezialfarbe, Eigenschaften geheim", 1.0, inh=("erklaerung",), fx=[LB("Spezialfarbe", None, "Eigenschaften geheim", 0.1)])],
 23: "merge",
 24: [mo("flip", {"front": {"icon": "doc", "title": "Pfandzeichen"}, "back": {"title": "= Geld", "sub": "nur zertifizierte Druckereien"}, "at": 2.2},
        "Tafel dreht sich: Pfandzeichen wird zu Geld – nur zertifizierte Druckereien", AD, inh=("erklaerung",))],
 25: "merge",
 26: [b("automat_display", "Automaten-Display zeigt eine Klopapierrolle mit gefälschtem Zeichen: angenommen – Fun-Fact", BW, inh=("geschehen",), fx=[SCR("display_klopapier.png"), LB("laut Medienberichten", None, None, 0.2)])],
 27: [b("automat_display", "Display: Pfandzeichen echt, Datensatz digital signiert", BW, gen="schema", inh=("erklaerung",), fx=[SCR("display_datensatz.png")])],
 28: "merge",
 29: [b("automat_presse", "Querschnitt: Walzen zerdrücken die Flasche, sie fällt platt in den Behälter", QS, gen="schema", A={"crushed": 0}, B={"crushed": 1}, trans="fade", t_trans=[0.25, 0.5])],
 30: "merge",
 31: [cl("px12564.mp4", "Echter Clip: eine Münze dreht sich – der Weg des Geldes beginnt", 0.5, inh=("erklaerung",), neu="frage:geldweg", fx=[LB("der Weg des Geldes", None, None, 0.2)])],
 32: "merge",
 33: [b("fabrik_band", "Abfüllerei: Flaschen laufen über das Band Richtung Supermarkt", MW, gen="schema", inh=("erklaerung",), fx=[DOTS("f_band", 10, 0.04), LB("Abfüller", None, None, 0.2)])],
 34: [b("fabrik_paletten", "Paletten mit Flaschen, Einblendung + 25 Cent Pfand an den Abfüller", WS, inh=("zahl",), fx=[LB("+ 25 Cent Pfand", None, "Supermarkt → Abfüller", 0.15)])],
 35: [b("kasse_total", "Kasse: Kundin zahlt, Display zeigt Pfand 0,25 €", MR, inh=("zahl",), fx=[SCR("kasse_pfand.png", "k_disp"), LB("25 Cent von dir", None, None, 0.3)])],
 36: [mo("flow", {"label": "DER WEG DER 25 CENT", "nodes": [{"icon": "factory", "label": "Abfüller"}, {"icon": "store", "label": "Supermarkt"}, {"icon": "person", "label": "du"}, {"icon": "store", "label": "Rücknahme"}], "packet": "money"},
        "Ablauf-Kette: Abfüller → Supermarkt → du → Rücknahme, eine Münze wandert, zurück zum Abfüller", AK2, gen="schema", inh=("erklaerung",), neu="antwort:geldweg"),
      b("fabrik_total", "Flug über die Abfüllerei: das Pfand geht zurück an den Abfüller", TF, gen="schema", inh=("erklaerung",), fx=[LB("zurück vom Abfüller", None, None, 0.2)])],
 37: "merge",
 38: [mo("counter", {"label": "CLEARING", "value": 7, "caption": "zugelassene Firmen verrechnen das Pfand"}, "Fallblatt-Zahl klappt auf 7: Clearing-Dienstleister", FZ)],
 39: "merge",
 40: [b("bahnhof_tafel", "Anzeigetafel klappt: D-P-G – KEIN GELD – NUR DATEN", ZW, gen="schema", inh=("erklaerung",), fx=[T("D-P-G", "KEIN GELD", "NUR DATEN")])],
 41: [b("doc_nah", "Auf dem Tisch eine Datenbank-Liste: Strichcodes aller Pfandverpackungen", BW, gen="schema", inh=("erklaerung",), fx=[SCR("datenbank.png", "d_doc")])],
 42: [mo("counter", {"label": "PFANDVERPACKUNGEN", "value": 18, "prefix": "≈ ", "suffix": " Mrd.", "caption": "pro Jahr · über 200 pro Kopf"}, "Fallblatt-Zahl klappt auf 18 Milliarden, Unterzeile über 200 pro Kopf", FZ),
      b("route_total", "Flug über die Stadt voller Lichter: über 200 Verpackungen pro Kopf", TF, inh=("zahl",), fx=[LB("über 200 pro Kopf", None, None, 0.2)])],
 43: "merge",
 44: [b("zaehl_total", "Zählzentrum: Säcke mit Leergut, große Sortiermaschine", WS, gen="schema", inh=("ort", "erklaerung"), fx=[LB("Zählzentrum", None, None, 0.2)])],
 45: [b("zaehl_band", "Flaschen laufen einzeln über das Band in die Sortiermaschine", MW, gen="schema", inh=("erklaerung",), fx=[DOTS("z_band", 10, 0.05)])],
 46: [b("zaehl_ballen", "Gepresste Plastikballen stapeln sich", LT, gen="schema", inh=("erklaerung",), A={"ballen": 4}, B={"ballen": 12}, trans="rows", t_trans=[0.1, 0.8]),
      cl("px202560.mp4", "Echter Clip: Recyclinghof, Material wird verladen", 1.0, inh=("erklaerung",))],
 47: [b("mehrweg_kaesten", "Mehrweg: Kästen mit Glasflaschen gestapelt", LW, gen="schema", inh=("erklaerung",))],
 48: [b("mehrweg_wasch", "Glasflaschen laufen in den Waschtunnel und werden neu befüllt", MW, gen="schema", inh=("erklaerung",), fx=[DOTS("m_band", 8, 0.05)])],
 49: [cl("px69.mp4", "Echter Clip: Förderband einer Abfüllanlage, Einblendung bis zu 50 Mal", 0.5, inh=("zahl",), fx=[LB("bis zu 50 Mal", None, "Glas-Mehrweg", 0.1)])],
 50: [b("stadt_total", "Die Stadt bei Nacht, alles läuft ruhig", TF, gen="stimmung", inh=("gefuehl",))],
 51: [b("regal_gang", "Der Supermarkt-Gang wird grau – Rückblende: vor gut 20 Jahren", LW, inh=("zeit",), neu="frage:chaos", fx=[GREY, LB("vor gut 20 Jahren", None, None, 0.2)])],
 "K2": [b("regal_voll", "Kapitelkarte 2 über dem grauen Regal", LW, inh=("erklaerung",), fx=[GREY, {"type": "card", "top": "KAPITEL 2", "title": "Das Chaos von 2003"}])],
 52: [b("bahnhof_tafel", "Tafel klappt auf 01.01.2003", CD, inh=("zeit",), fx=[GREY, T("01.01.2003")])],
 53: [b("regal_voll", "Graues Regal mit Dosen und Flaschen, Einblendung Pfand auf Bier, Wasser, Limo", LW, inh=("erklaerung",), fx=[GREY, LB("Pfand ab 2003", None, "Bier · Wasser · Limonade", 0.2)])],
 54: "merge",
 55: [b("doc_total", "Schreibtisch, Dokument Verpackungsverordnung 1991, Klaus Töpfer (CDU)", BW, inh=("zeit", "person"), fx=[GREY, SCR("doc_1991.png", "d_doc"), LB("1991 · Klaus Töpfer (CDU)", None, "Verpackungsverordnung", 0.2)])],
 56: [mo("grid", {"label": "DIE REGEL VON 1991", "n": 100, "icon": "bottle", "value": 72, "suffix": " %", "caption": "Mehrweg-Anteil – darunter wird Pfand fällig", "count": 72},
        "Raster aus 100 Flaschen, 72 leuchten: Mehrweg-Anteil, darunter wird Pfand fällig", LR)],
 57: [b("stadt_total", "Stadt: Lichter gehen Straße für Straße aus – Ende der 1990er unter 72 %", LA, inh=("zeit", "zahl"), A={"lights": 1}, B={"lights": 0.45}, trans="lights", t_trans=[0.2, 0.8], fx=[LB("Ende der 1990er: unter 72 %", None, None, 0.15)])],
 58: [b("doc_nah", "Dokument: Pfandpflicht ab 1. Januar 2003, umgesetzt 2002 von Rot-Grün (Jürgen Trittin)", BW, inh=("zeit", "person"), fx=[GREY, SCR("doc_2003.png", "d_doc"), LB("2002 · Jürgen Trittin (Grüne)", None, None, 0.2)])],
 59: [b("markt_aussen", "Der Supermarkt von außen, grau – kein gemeinsames System", LW, gen="schema", inh=("erklaerung",), fx=[GREY, LB("kein gemeinsames System", None, None, 0.2)])],
 60: [b("automat_total", "Grauer Automat, Einblendung: nur eigene Flaschen", LW, gen="schema", inh=("erklaerung",), fx=[GREY, LB("nur eigene Flaschen", None, None, 0.2)])],
 61: [mo("stack", {"label": "2003 BIS 2006", "cards": [["Pfandbon", "Laden A"], ["Pfandmarke", "Laden B"], ["eigenes Etikett", "Laden C"]], "symbol": "?", "question": "Wo gebe ich das zurück?"},
        "Drei Zettel stapeln sich: Pfandbon, Pfandmarke, eigenes Etikett – Fragezeichen", AD, gen="schema", inh=("erklaerung",))],
 62: [mo("flow", {"label": "INSELLÖSUNG", "nodes": [{"icon": "bottle", "label": "Flasche"}, {"icon": "store", "label": "Discounter A: ja"}], "packet": "bottle",
                  "branch": {"after": 0, "icon": "store", "label": "Discounter B", "text": "NEIN"}}, "Ablauf-Kette: Flasche geht bei Discounter A zurück, Abzweig zu Discounter B: NEIN", AK2, gen="schema", inh=("erklaerung",))],
 63: [mo("flip", {"front": {"icon": "can", "title": "Cola: Pfand"}, "back": {"title": "Cola + Rum", "sub": "kein Pfand"}, "at": 2.0}, "Tafel dreht sich: Cola-Dose mit Pfand, Cola mit Rum ohne – Fun-Fact", AD, inh=("erklaerung",))],
 64: "merge",
 65: [b("regal_voll", "Graues Regal: die Dosen verschwinden Reihe für Reihe", RL, A={"fill": 1}, B={"fill": 0.25}, trans="rows", t_trans=[0.15, 0.85], fx=[GREY])],
 66: [mo("bars", {"label": "DOSEN IN DEUTSCHLAND", "title": "Branchenangaben", "unit": " Mrd.", "bars": [["2002 verkauft", 7.5, False], ["2004 hergestellt", 0.3, True]]}, "Häuserzeilen-Balken: 2002 rund 7,5 Mrd., 2004 nur noch ein Bruchteil", HB, inh=("zahl", "vergleich"))],
 67: [b("regal_gang", "Leerer grauer Gang, Einblendung über 90 Prozent weniger", RL, inh=("zahl",), A={"fill": 0.06}, fx=[GREY, LB("− über 90 %", None, "laut Branchenangaben", 0.15)])],
 68: "merge",
 69: [mo("grid", {"label": "2003 BIS 2005", "n": 100, "icon": "bottle", "value": 25, "suffix": " %", "caption": "kamen nicht zurück (Schätzung Umweltbundesamt)", "count": 25},
        "Raster aus 100 Flaschen, jede vierte bleibt dunkel: kam nie zurück", LR, neu="frage:rest"),
      b("bahnhof_total", "Grauer Bahnsteig 2003: jede vierte Flasche bleibt liegen", LW, inh=("zahl",), fx=[GREY, LB("jede vierte", None, "kam nicht zurück", 0.15)])],
 70: "merge",
 71: [b("kasse_band", "Graue Kasse: Pfand bezahlt", LW, inh=("erklaerung",), fx=[GREY, LB("Pfand bezahlt", None, None, 0.15)])],
 72: [cl("px218339.mp4", "Echter Clip: Plastikflaschen am Flussufer – abgeholt hat es niemand", 2.0, inh=("geschehen",))],
 73: [b("bahnhof_tafel", "Tafel klappt auf 01.05.2006, die Farbe kehrt zurück", CD, inh=("zeit",), fx=[T("01.05.2006")])],
 74: [b("automat_total", "Automat in Farbe: nimmt alle Einweg-Pfandflaschen derselben Materialart an", LW, gen="schema", inh=("erklaerung",), fx=[LB("alle Einweg-Pfandverpackungen", None, "aus dem eigenen Material", 0.15)]),
      b("markt_aussen", "Kamera fliegt über die Märkte der Stadt – egal wo gekauft", TF, gen="schema", inh=("ort",))],
 75: [mo("flip", {"front": {"icon": "store", "title": "Insellösung"}, "back": {"title": "1 Zeichen", "sub": "seit Mai 2006"}, "at": 2.0}, "Tafel dreht sich: aus Insellösung wird ein Zeichen, seit Mai 2006", AD, inh=("erklaerung", "zeit"))],
 76: "merge",
 77: [mo("flow", {"label": "PFAND GILT FÜR", "nodes": [{"icon": "bottle", "label": "2003: Bier, Wasser, Limo"}, {"icon": "bottle", "label": "2022: Saft, Wein"}, {"icon": "bottle", "label": "2024: Milch"}], "packet": "can"},
        "Ablauf-Kette: 2003 Bier/Wasser/Limo → 2022 Saft/Wein → 2024 Milch", AK2, inh=("zeit",))],
 78: [b("regal_voll", "Regal füllt sich wieder mit Dosen, Einblendung rund 6 Mrd. pro Jahr", RL, inh=("zahl",), A={"fill": 0.3}, B={"fill": 1.0}, trans="rows", t_trans=[0.1, 0.7], fx=[LB("rund 6 Mrd. Dosen pro Jahr", None, "laut Bundestagsanfrage", 0.2)])],
 79: "merge",
 80: [b("zaehl_total", "Zählzentrum: fast alles kommt zurück", WS, gen="schema", inh=("erklaerung",))],
 81: "merge",
 82: [b("flasche_makro", "Zurück zur Flasche unter der Bank – im kleinen Rest steckt das Geld", RF, gen="schema", inh=("erklaerung",), neu="frage:rest2")],
 "K3": [b("bahnhof_total", "Kapitelkarte 3 am Bahnsteig", LW, inh=("erklaerung",), fx=[{"type": "card", "top": "KAPITEL 3", "title": "Der kleine Rest"}])],
 83: [b("bahnhof_uhr", "Bahnhofsuhr springt auf 18:50", CD, inh=("zeit",), fx=[CLK(1120, 1130)])],
 84: "merge",
 85: [b("bank_nah", "Die zweite Flasche liegt noch unter der Bank", LW)],
 86: [b("bahnhof_zug", "Ein Zug fährt ein, niemand bückt sich nach der Flasche", MR, neu="frage:selten")],
 87: [mo("counter", {"label": "RÜCKLAUF 2023", "value": 98.7, "dec": 1, "suffix": " %", "caption": "Pfand-Plastikflaschen · Studie für das UBA"}, "Fallblatt-Zahl klappt auf 98,7 Prozent", FZ, neu="antwort:selten"),
      b("zaehl_band", "Sortiermaschine: fast alle Flaschen laufen durch", MW, inh=("erklaerung",), fx=[DOTS("z_band", 14, 0.06)])],
 88: [mo("bars", {"label": "SAMMELQUOTE PLASTIKFLASCHEN", "unit": " %", "bars": [["DE 2023 (Pfand-PET)", 98.7, True], ["Europa 2022 (PET)", 60, False]]}, "Häuserzeilen-Balken: Deutschland 98,7 % gegen Europa 60 %", HB, inh=("zahl", "vergleich")),
      cl("px19543.mp4", "Echter Clip: weggeworfene Flasche am Strand – ohne Pfand oft Alltag", 10.0, inh=("vergleich",))],
 89: [mo("grid", {"label": "ALLE PFANDVERPACKUNGEN", "n": 100, "icon": "bottle", "value": 4, "prefix": "1–", "suffix": " von 100", "caption": "kommen nicht zurück", "count": 4},
        "Raster aus 100 Flaschen, 1 bis 4 bleiben dunkel", LR)],
 90: [b("bahnhof_zug", "Der Zug steht am Bahnsteig: das klingt nach wenig", LW, gen="schema", inh=("erklaerung",))],
 91: [cl("px36473.mp4", "Echter Clip: Deponie von oben, Einblendung geschätzt hunderte Millionen Stück", 1.0, inh=("zahl",), fx=[LB("geschätzt: hunderte Millionen Stück", None, "pro Jahr", 0.1)])],
 92: [b("muelleimer", "Am Mülleimer bückt sich eine Sammlerin nach einer Flasche", MR, A={"neben": 1, "sammler": 1})],
 93: [mo("counter", {"label": "PFANDSAMMLER", "value": 1, "prefix": "≈ ", "suffix": " Mio.", "caption": "Umfragen einer Initiative eines Getränkeherstellers"}, "Fallblatt-Zahl klappt auf rund 1 Million Pfandsammler", FZ),
      cl("px3178.mp4", "Echter Clip: Bahnsteig eines echten Bahnhofs, Menschen warten", 2.0, inh=("ort",))],
 94: "merge",
 95: [b("bahnhof_total", "Die Sammlerin geht mit ihrer Tasche über den Bahnsteig, Einblendung unter 200 € im Monat", MR, inh=("zahl",), A={"sammler": 1}, fx=[LB("meist unter 200 € im Monat", None, None, 0.15)])],
 96: [b("flasche_makro", "Die Flasche bleibt liegen, niemand findet sie", LW)],
 97: [b("bank_nah", "Unter der Bank: Wer behält ihre 25 Cent?", LW, inh=("zahl",), neu="frage:pfand_b", fx=[LB("Wer behält die 25 Cent?", None, None, 0.1)])],
 99: "merge",
 98: [b("doc_nah", "Gesetzestext auf dem Tisch: ohne Rücknahme kein Pfand", BW, inh=("erklaerung",), fx=[SCR("doc_gesetz.png", "d_doc")]), mo("flow", {"label": "WER ALS ERSTER KASSIERT", "nodes": [{"icon": "person", "label": "Kunde"}, {"icon": "store", "label": "Händler"}, {"icon": "factory", "label": "Abfüller"}], "packet": "money"},
        "Ablauf-Kette: das Geld wandert vom Kunden über den Händler zum Abfüller und bleibt dort", AK2, gen="schema", inh=("erklaerung",))],
 100: [b("fabrik_total", "Flug über die Abfüllerei: der Erstinverkehrbringer", TF, gen="schema", inh=("erklaerung",), fx=[LB("Abfüller = Erstinverkehrbringer", None, None, 0.2)])],
 101: [b("bahnhof_tafel", "Tafel klappt auf PFANDSCHLUPF", ZW, gen="schema", inh=("erklaerung",), fx=[T("PFAND", "PFANDSCHLUPF")])],
 102: [b("fabrik_paletten", "Paletten der Getränkeindustrie – kassiert sie?", LW, gen="schema", inh=("erklaerung",), fx=[LB("Getränkeindustrie?", None, None, 0.2)])],
 103: [b("markt_aussen", "Der Supermarkt im Dunkeln – ganz so einfach ist es nicht", LW, gen="schema", inh=("erklaerung",), neu="frage:wer2")],
 104: [b("automat_front", "Am Automaten blinkt eine rote Lampe: jemand hat ihn umgebaut", LW, gen="schema", A={"manip": 1, "mann": 0}, neu="frage:betrug")],
 "K4": [b("automat_total", "Kapitelkarte 4 vor dem Automaten im Dunkeln", LW, inh=("erklaerung",), A={"manip": 1}, fx=[{"type": "card", "top": "KAPITEL 4", "title": "Die Lücken im System"}])],
 105: [b("bahnhof_tafel", "Tafel klappt auf 2016", CD, inh=("zeit",), fx=[T("2016")])],
 106: [b("automat_loch", "Eine Flasche geht in den Automaten", LW, A={"manip": 1})],
 107: [b("automat_display", "Display zählt: 0,25 – 0,50 – 0,75 €, immer dieselbe Flasche", BW, inh=("zahl",), fx=[SCR(anchor="a_display", video=SC + "zaehler.mp4")])],
 108: "merge",
 109: [b("automat_presse", "Querschnitt: die Walzen fehlen, Kabel und rote Lampe – der Automat zerdrückt nichts", QS, gen="schema", A={"manip": 1})],
 110: "merge",
 111: [mo("counter", {"label": "DIESELBE FLASCHE", "value": 177000, "prefix": "> ", "caption": "Mal gezählt (laut Medienberichten)"}, "Fallblatt-Zahl klappt auf über 177.000", FZ, neu="antwort:betrug")],
 112: [cl("px59138.mp4", "Echter Clip: Geldzählmaschine, Einblendung über 44.000 €, Ausgang unbekannt", 0.5, inh=("zahl",), fx=[LB("über 44.000 €", None, "Ausgang des Verfahrens unbekannt", 0.1)])],
 113: "merge",
 115: "merge",
 114: [b("karte_de", "Modellkarte: Neuss leuchtet auf, rund 1,8 Mio. €", MK, inh=("ort", "zahl"), fx=[LB("Neuss · rund 1,8 Mio. €", "pin_neuss")]), b("automat_front", "Querschnitt des manipulierten Automaten: die Flasche bleibt ganz", QS, A={"manip": 1, "mann": 0, "cut": 1, "innen": 1})],
 116: [b("gericht_total", "Gerichtsgebäude bei Nacht, Einblendung rechtskräftig freigesprochen", LW, inh=("erklaerung",), fx=[LB("Angeklagter rechtskräftig freigesprochen", None, None, 0.15)])],
 117: [cl("px35574.mp4", "Echter Clip: Plastikflaschen, Einblendung Berlin – Verdacht auf falsche Pfandetiketten", 0.5, inh=("ort",), fx=[LB("Berlin: Verdacht", None, "Pfandetiketten auf pfandfreie Flaschen", 0.1)])],
 118: [b("bahnhof_tafel", "Tafel klappt auf JUNI 2024 – RAZZIA – KEIN URTEIL BEKANNT", CD, inh=("zeit",), fx=[T("JUNI 2024", "RAZZIA", "URTEIL?")])],
 119: "merge",
 121: "merge",
 120: [b("karte_nord", "Modellkarte zoomt nach Norden an die Grenze zu Dänemark", MK, inh=("ort",), neu="frage:grenze", fx=[LB("Grenze zu Dänemark", "pin_grenze")]),
       b("grenze_total", "Grenzladen bei Nacht, Parkplatz voller Autos, Paletten mit Dosen", WS, inh=("ort",))],
 122: [b("grenze_fahnen", "Dänische und deutsche Fahne an der Grenze – ohne Pfand", LW, inh=("erklaerung",), fx=[LB("ohne Pfand", None, None, 0.1)])],
 123: [b("grenze_auto", "Kofferraum voller Dosen-Trays, Einblendung Unterschrift: Ausfuhr", MR, gen="schema", inh=("erklaerung",), fx=[LB("eine Unterschrift: „Ausfuhr“", None, None, 0.15)])],
 124: [mo("map", {"label": "GRENZHANDEL", "view": [10.5, 55.6, 5200], "pins": [{"lonlat": [9.43, 54.79], "label": "Grenzläden"}, {"lonlat": [9.2, 55.35], "label": "Dänemark"}],
                 "highlight": ["208"], "counter": {"value": 650, "prefix": "> ", "suffix": " Mio.", "label": "Dosen pro Jahr (Schätzung DUH)"}},
         "Karte: Route von den Grenzläden nach Dänemark, Zähler über 650 Mio. Dosen pro Jahr", WK, inh=("zahl", "ort"))],
 125: [cl("px262213.mp4", "Echter Clip: dänischer Strand, Einblendung bis zu 9 von 10 Dosen aus Deutschland (2020)", 1.0, inh=("zahl", "ort"), fx=[LB("bis zu 9 von 10 gesammelten Dosen", None, "aus Deutschland · Dänemark, 2020", 0.1)])],
 126: [b("karte_eu", "Modellkarte Europa: Luxemburg – Europäischer Gerichtshof 2023", MK, inh=("ort", "zeit"), fx=[LB("EuGH, 2023", "pin_luxemburg")]),
       b("gericht_saeulen", "Säulen des Gerichts von unten: keine Pflicht zur Durchsetzung", LW, inh=("erklaerung",), fx=[LB("keine Pflicht zur Durchsetzung", None, None, 0.1)])],
 127: [b("karte_nord", "Modellkarte: Schleswig leuchtet auf – Verwaltungsgericht Mai 2026: Pfand gilt auch für Skandinavier", MK, inh=("ort", "zeit"), fx=[LB("VG Schleswig · Mai 2026", "pin_schleswig", "Pfand gilt auch für Skandinavier")])],
 128: [b("doc_nah", "Urteil auf dem Tisch, Stempel: nicht rechtskräftig", BW, inh=("erklaerung",), fx=[SCR("doc_urteil.png", "d_doc")])],
 129: "merge",
 130: [mo("counter", {"label": "VOR DEM PFAND", "value": 3, "prefix": "bis ", "suffix": " Mrd.", "caption": "Dosen und Flaschen pro Jahr an Straßen und in Parks (DUH)"}, "Fallblatt-Zahl klappt auf bis zu 3 Milliarden", FZ),
       cl("px218339.mp4", "Echter Clip: weggeworfene Plastikflasche im Gestrüpp", 11.0, inh=("geschehen",))],
 131: [b("bahnhof_uhr", "Bahnhofsuhr springt weiter auf 18:55", CD, inh=("zeit",), fx=[CLK(1130, 1135)])],
 132: [b("flasche_makro", "Die Flasche unter der Bank – wer bekommt ihr Pfand?", LW, neu="frage:final", fx=[LB("Wer bekommt das Pfand?", None, None, 0.2)])],
 "K5": [b("bahnhof_total", "Kapitelkarte 5 am Bahnsteig", LW, inh=("erklaerung",), fx=[{"type": "card", "top": "KAPITEL 5", "title": "Wer das Pfand behält"}])],
 133: [b("bank_nah", "Kamera kriecht unter die Bank zur Flasche", LW)],
 134: [b("flasche_makro", "Makro aufs Etikett: kein Brunnen, sondern Eigenmarke", LW, gen="exakt", inh=("erklaerung",), fx=[LB("Eigenmarke", None, "eines Supermarkts", 0.15)])],
 135: [b("fabrik_total", "Flug über die Abfüllerei: Wer ist eigentlich der Abfüller?", TF, gen="schema", inh=("erklaerung",), fx=[LB("Wer ist der Abfüller?", None, None, 0.2)])],
 136: "merge",
 137: [b("fabrik_band", "Band mit Eigenmarken-Flaschen, orange Etiketten", MW, gen="schema", inh=("erklaerung",), fx=[DOTS("f_band", 10, 0.04), LB("Eigenmarke, selbst abgefüllt", None, None, 0.2)])],
 138: [mo("flow", {"label": "EINE UNTERNEHMENSGRUPPE", "nodes": [{"icon": "store", "label": "Discounter"}, {"icon": "factory", "label": "eigene Getränkefirma"}, {"icon": "bottle", "label": "Eigenmarke"}], "packet": "money"},
         "Ablauf-Kette: Discounter → eigene Getränkefirma → Eigenmarke, alles in einer Unternehmensgruppe", AK2, gen="schema", inh=("erklaerung",), neu="antwort:final")],
 139: [b("kasse_total", "Kasse: das Pfand landet als Erstes beim Konzern", MR, gen="schema", inh=("erklaerung",), fx=[SCR("kasse_pfand.png", "k_disp"), LB("als Erster kassiert", None, None, 0.2)])],
 140: [b("bahnhof_total", "Rückflug zum Bahnsteig: das Pfand der Flasche wird nie zurückgegeben", RF, gen="schema", inh=("erklaerung",))],
 141: [b("doc_total", "Schreibtisch mit Bundestagsdrucksache, Ende 2025", BW, inh=("zeit",), fx=[SCR("doc_btdrs.png", "d_doc"), LB("Bundesregierung, Dezember 2025", None, None, 0.2)]),
       b("doc_nah", "Nah: Zitat weit überwiegend beim Einzelhandel wird orange markiert", BW, inh=("erklaerung",), fx=[SCR("doc_btdrs_hl.png", "d_doc")])],
 142: [b("markt_aussen", "Der Supermarkt leuchtet auf: beim Handel", LW, gen="schema", inh=("erklaerung",), fx=[LB("beim Handel", "markt")])],
 143: "merge",
 144: [b("bahnhof_tafel", "Tafel klappt: WIE VIEL? – KEINE AMTLICHE ZAHL", ZW, gen="schema", inh=("erklaerung",), fx=[T("WIE VIEL?", "KEINE AMTL. ZAHL")])],
 145: "merge",
 146: [mo("counter", {"label": "PFANDSCHLUPF", "value": 180, "prefix": "≈ ", "suffix": " Mio. €", "caption": "pro Jahr · Schätzung NABU für 2015"}, "Fallblatt-Zahl klappt auf rund 180 Mio. Euro pro Jahr", FZ)],
 147: [b("rathaus_uhr", "Rathausuhr dreht einen ganzen Tag, Einblendung fast eine halbe Million pro Tag", CD, inh=("zahl", "zeit"), fx=[CLK(0, 1440, "uhr"), LB("≈ 490.000 € pro Tag", None, "rechnerisch · Schätzung NABU 2015", 0.15)])],
 148: [b("zaehl_total", "Zählzentrum, Einblendung Annahme: 4 von 100 kommen nicht zurück", WS, inh=("zahl",), fx=[LB("Annahme: 4 von 100", None, "kommen nicht zurück", 0.15)])],
 149: [b("zaehl_ballen", "Die Ballen stapeln sich höher: das Material gehört meist dem Handel", LT, gen="schema", inh=("erklaerung",), A={"ballen": 5}, B={"ballen": 14}, trans="rows", t_trans=[0.1, 0.8], fx=[LB("gehört meist dem Handel", None, None, 0.2)])],
 150: "merge",
 151: [mo("counter", {"label": "MATERIAL", "value": 68, "prefix": "≈ ", "suffix": " Mio. €", "caption": "Erlös pro Jahr · ältere Schätzung (NABU)"}, "Fallblatt-Zahl klappt auf rund 68 Mio. Euro", FZ)],
 152: [b("stadt_total", "Flug über die Stadt, Einblendung Skandal?", TF, gen="schema", inh=("erklaerung",), fx=[LB("Skandal?", None, None, 0.1)])],
 153: "merge",
 154: [b("automat_total", "Der Automat im Supermarkt, gekauft vom Handel", LW, gen="schema", inh=("erklaerung",))],
 155: [mo("bars", {"label": "AUTOMATENPREISE · BRANCHENANGABEN", "unit": " Tsd. €", "bars": [["einfach (ab, AT)", 10, False], ["leistungsstark (AT)", 30, False], ["Großanlage (DE 2012)", 300, True]]},
         "Häuserzeilen-Balken: einfaches Gerät ab 10.000 €, Großanlage ein Vielfaches", HB, inh=("zahl", "vergleich"))],
 156: [b("karte_eu", "Modellkarte: Norwegen leuchtet auf, 1972 erster Pfandautomat", MK, inh=("ort", "zeit"), fx=[LB("Norwegen, 1972", "pin_oslo", "Automat der Brüder Planke")]),
       b("automat_loch", "Die Öffnung des Automaten, Fun-Fact zwei Brüder", LW, inh=("erklaerung",), fx=[LB("2 Brüder, 1 genervter Händler", None, None, 0.1)])],
 158: [b("automat_front", "Automat von außen: Platz, Strom, Personal", LW, gen="schema", inh=("erklaerung",), A={"mann": 0}, fx=[LB("Platz · Strom · Personal", None, None, 0.15)])],
 159: [b("doc_total", "Dokument der Bundesregierung: Handel trägt den Großteil der Kosten", BW, inh=("erklaerung",), fx=[SCR("doc_kosten.png", "d_doc")])],
 160: [b("kasse_total", "Kasse mit Display: Rücknahmegebühr – keine", BW, gen="schema", inh=("erklaerung",), fx=[SCR("kasse_gebuehr.png", "k_disp")])],
 157: "merge", 162: "merge",
 161: [mo("flow", {"label": "ÖSTERREICH", "nodes": [{"icon": "bottle", "label": "liegengebliebenes Pfand"}, {"icon": "gear", "label": "Pfandsystem"}, {"icon": "store", "label": "Rücknahme"}], "packet": "money"},
         "Ablauf-Kette: das liegengebliebene Pfand fließt ins System und finanziert die Rücknahme", AK2, gen="schema", inh=("erklaerung",))],
 163: [b("karte_eu", "Modellkarte Europa: Flug über den ganzen Kontinent", MK, gen="schema", inh=("ort",), fx=[LB("Europa", None, None, 0.2)])],
 164: [b("doc_nah", "Dokument: EU-Verpackungsverordnung, gilt seit 12.08.2026", BW, inh=("zeit",), fx=[SCR("doc_ppwr.png", "d_doc")])],
 165: [mo("map", {"label": "EU-VERPACKUNGSVERORDNUNG", "view": "europe", "highlight": ["040", "056", "100", "191", "196", "203", "208", "233", "246", "250", "276", "300", "348", "372", "380", "428", "440", "442", "470", "528", "616", "620", "642", "703", "705", "724", "752"],
                  "counter": {"value": 90, "suffix": " %", "label": "getrennt sammeln bis 2029"}}, "Europakarte: alle EU-Länder leuchten nacheinander, Zähler 90 % bis 2029", WK, inh=("zahl", "zeit")),
      b("automat_total", "Pfandautomat: Pfandsysteme werden in fast ganz Europa Pflicht, bis 2029", LW, inh=("erklaerung",), fx=[LB("Pfandsystem bis 2029", None, "in fast der ganzen EU", 0.15)])],
 166: "merge",
 167: [b("bahnhof_tafel", "Tafel klappt: 2026 80 % – AUSNAHME MÖGLICH", ZW, inh=("zahl", "zeit"), fx=[T("2026: 80 % + PLAN", "AUSNAHME")])],
 168: [mo("bars", {"label": "ÖSTERREICH, ERSTES PFANDJAHR", "unit": " %", "bars": [["Ziel", 80, False], ["2025 erreicht", 81.5, True]]}, "Häuserzeilen-Balken: Ziel 80 %, erreicht 81,5 %", HB, inh=("zahl", "vergleich"))],
 169: [b("doc_total", "Gesetz auf dem Tisch: § 46 VerpackDG, mindestens 25 Cent", BW, inh=("zahl",), fx=[SCR("doc_verpackdg.png", "d_doc"), LB("mindestens 25 Cent", None, "wie seit 2006", 0.3)])],
 170: "merge",
 171: [b("bahnhof_total", "Bahnsteig, Einblendung Szene nachgestellt", LW, inh=("erklaerung",), fx=[LB("Szene nachgestellt", None, None, 0.05)])],
 172: [b("route_total", "Flug über die nächtliche Stadt: überall solche Bänke", TF, gen="schema", inh=("ort",))],
 173: [b("bahnhof_uhr", "Bahnhofsuhr springt auf 19:00, Einblendung 3 Möglichkeiten", CD, inh=("zeit",), fx=[CLK(1135, 1140), LB("3 Möglichkeiten", None, None, 0.3)])],
 174: "merge",
 175: [b("automat_loch", "1 · Die Flasche geht in den Automaten", LW, fx=[LB("1 · zurückbringen", None, None, 0.1)])],
 176: [b("automat_display", "Display: 0,25 € ausgezahlt, aus dem Plastik wird neuer Kunststoff", BW, inh=("zahl",), fx=[SCR("display_025.png")])],
 177: [b("muelleimer", "2 · Die Flasche steht neben dem Mülleimer, eine Sammlerin nimmt sie mit", MR, A={"neben": 1, "sammler": 0}, B={"neben": 1, "sammler": 1}, trans="fade", t_trans=[0.45, 0.6],
         fx=[LB("2 · daneben stellen", None, None, 0.1)])],
 178: "merge",
 179: [cl("px35574.mp4", "3 · Echter Clip: Plastikflaschen fallen weg", 5.0, fx=[LB("3 · wegwerfen", None, None, 0.1)])],
 180: [b("fabrik_total", "Das Pfand bleibt beim Abfüller", TF, gen="schema", inh=("erklaerung",), fx=[LB("Pfand bleibt beim Abfüller", None, None, 0.15)])],
 181: [b("flasche_makro", "Rahmen: wieder die Flasche unter der Bank, 25 Cent", RF, inh=("zahl",), fx=[LB("25 Cent", None, None, 0.1)])],
 182: [b("automat_front", "Querschnitt am Schluss: der Automat wird durchsichtig – für wen?", QS, gen="schema", inh=("erklaerung",), A={"mann": 0}, B={"cut": 1, "innen": 1, "scan": 1}, trans="wipe_down", t_trans=[0.1, 0.6])],
 183: [b("bahnhof_zug", "Bahnsteig mit Zug, Einblendung: Bringst du jede Flasche zurück?", LW, inh=("erklaerung",), fx=[LB("Bringst du jede Flasche zurück?", None, None, 0.1)])],
 184: "merge", 185: "merge",
 186: [b("stadt_total", "Flug über die Stadt bei Nacht", TF, gen="stimmung", inh=("gefuehl",))],
 187: [b("stadt_total", "Schlusskarte: die Stadt bei Nacht dunkelt ab, Schriftzug UNTERBAU und Claim erscheinen", TF, inh=("erklaerung",), fx=[{"type": "card", "title": "UNTERBAU", "sub": "Verstehen, wie die Welt funktioniert", "fade": False}])],
}
Z.update({0: "25 Cent.", 3: "18:40 Uhr, Bahnhof Dortmund.", 8: "25 Cent.", 9: "Hunderte Millionen pro Jahr.", 11: "6 x 0,25 Euro.", 12: "Über 40.000 Automaten, 7 Firmen.",
          21: "Bis zu 6 Kameras.", 34: "25 Cent Pfand.", 35: "25 Cent von dir.", 38: "7 Firmen.", 42: "18 Milliarden, über 200 pro Kopf.", 49: "Bis zu 50 Mal.", 51: "Vor 20 Jahren.",
          52: "1. Januar 2003.", 55: "1991 Klaus Töpfer.", 56: "72 Prozent.", 57: "Ende der 1990er.", 58: "2002 Trittin.", 66: "2002 7,5 Milliarden Dosen.", 67: "Über 90 Prozent.",
          69: "Jeder vierte, 25 Prozent.", 73: "1. Mai 2006.", 77: "2024 Milch.", 78: "6 Milliarden im Jahr.", 83: "18:50 Uhr.", 87: "2023 98,7 Prozent.", 88: "2022 60 Prozent.",
          89: "1 bis 4 von 100.", 91: "18 Milliarden, hunderte Millionen.", 93: "1 Million Menschen.", 95: "200 Euro im Monat.", 97: "25 Cent.", 105: "2016.", 111: "177.000 Mal.",
          112: "44.000 Euro.", 114: "1,8 Millionen Euro.", 118: "Juni 2024.", 124: "650 Millionen Dosen im Jahr.", 125: "2020: 9 von 10.", 126: "2023.", 127: "Mai 2026.",
          130: "3 Milliarden im Jahr.", 141: "Ende 2025.", 146: "2015 180 Millionen Euro.", 147: "500.000 Euro am Tag.", 148: "4 von 100.", 151: "70 Millionen Euro im Jahr.",
          155: "10.000 Euro.", 157: "1972.", 164: "12. August 2026.", 165: "Bis 2029 90 Prozent.", 167: "2026 80 Prozent.", 168: "2025: 81,5 Prozent.", 169: "25 Cent seit 2006.",
          176: "25 Cent.", 181: "25 Cent."})

# ------------------------------------------------------------------ Zeiten
parts = {}
for i, (k, s, e, t) in enumerate(S): parts.setdefault(k, []).append(i)
dur = {}
for k, ids in parts.items():
    for j, i in enumerate(ids):
        dur[i] = (S[ids[j + 1]][1] - S[i][1]) if j + 1 < len(ids) else (S[i][2] - S[i][1] + 0.6)
order = []
CARDS = {3: ("K2", 4.5), 4: ("K3", 4.5), 5: ("K4", 4.5), 6: ("K5", 4.5)}
for k in sorted(parts):
    if k == 2: order.append(("T", 4.6, "Titelkarte")); order.append(("K1", 4.5, "Kapitel 1"))
    elif k in CARDS: order.append((CARDS[k][0], CARDS[k][1], f"Kapitel {k - 1}"))
    for i in parts[k]: order.append((i, dur[i], S[i][3]))
order[-1] = (order[-1][0], order[-1][1] + 2.0, order[-1][2])

rows = []
for key, sek, satz in order:
    if SH.get(key) == "merge":
        rows[-1][1] += sek; rows[-1][2] += " " + satz; rows[-1][3].append(key); continue
    rows.append([key, sek, satz, [key]])

# ------------------------------------------------------------------ Einstellungen erzeugen
import motion_ub as MO
MAXS = 4.4
plan, shots, dreh, t = [], [], [], 0.0
def jitter(sid, v, amt):
    h = int(hashlib.md5(sid.encode()).hexdigest()[:8], 16)
    return tuple(x + ((h >> (4 * i)) % 100 / 100 - 0.5) * amt for i, x in enumerate(v))
n = 0
for key, sek, satz, keys in rows:
    lst = SH[key]
    isg = lambda e: e["k"] == "mo" or e["anim"] == MK
    if len(lst) == 1 and sek > MAXS and isinstance(key, int) and not isg(lst[0]):
        k2 = max(2, int(sek / MAXS + 0.999)); lst = [dict(lst[0], cont=c) for c in range(k2)]
    # 2D-Grafiken bekommen mindestens 4,3 s (Zeit von der Einstellung daneben), Blender-Einstellungen teilen sich den Rest
    nmo = sum(1 for e in lst if isg(e))
    if nmo and len(lst) > nmo:
        tmo = max(4.3, sek / len(lst)); rest = max(1.0, (sek - tmo * nmo) / (len(lst) - nmo)); shares = [tmo if isg(e) else rest for e in lst]
    else:
        shares = [sek / len(lst)] * len(lst)
    for e, share in zip(lst, shares):
        sid = f"s{n:03d}"; n += 1
        zsatz = " ".join(Z.get(k, "") for k in keys if isinstance(k, int)).strip() or satz
        dreh.append({"satz": zsatz if e.get("cont", 0) == 0 else "(Fortsetzung) " + satz[:40], "sek": round(share, 2), "zeigt": e["zeigt"], "animation": e["anim"],
                     "inhalt": e["inh"], "genauigkeit": e["gen"], "neugier": e["neu"] if e.get("cont", 0) == 0 else "", "i": key if isinstance(key, int) else -1, "t0": round(t, 2)})
        c = e.get("cont", 0)
        if e["k"] == "b":
            loc, tgt, lens, A0, anc = SETS[e["set"]]
            A = {**A0, **e.get("A", {})}; B = e.get("B")
            if c > 0 and B: A = {**A, **B}; B = None
            shots.append({"id": sid, "set": e["set"], "cam": {"loc": list(loc), "tgt": list(tgt), "lens": lens}, "A": A, "B": B, "anchors": anc})
            fx = [f for f in e.get("fx", []) if not (c > 0 and f.get("type") in ("label",))]
            tilt = abs(loc[0]) < 150 and abs(loc[1]) < 150 and loc[2] > 2.5
            plan.append({"id": sid, "tilt": tilt, "dur": round(share, 3), "move": e.get("move", "push"), "trans": e.get("trans", "diff"), "t_trans": e.get("t_trans", [0.2, 0.8]),
                         "fx": fx, "anim": e["anim"], "i": key if isinstance(key, int) else -1, "keys": [k for k in keys], "set": e["set"]})
        else:
            if e["k"] == "mo":
                mk = MO.clip(e["comp"], e["props"], len=round(max(share, 2.0) + 0.3, 2)); video = os.path.join(WORK, "motion", mk + ".mp4"); ss = 0.0
            else:
                video = e["video"]; ss = e["ss"] + c * share
            plan.append({"id": sid, "video": video, "ss": round(ss, 3), "kind": "clip" if e["k"] == "cl" else "mo", "dur": round(share, 3), "fx": e.get("fx", []) if c == 0 else [],
                         "anim": e["anim"], "i": key if isinstance(key, int) else -1, "keys": keys, "set": e["k"] + ":" + os.path.basename(video)})
        t += share

sh_by = {s["id"]: s for s in shots}
k = 0
while k < len(plan):
    if "video" in plan[k]: k += 1; continue
    j = k
    while j + 1 < len(plan) and "video" not in plan[j + 1] and plan[j + 1]["set"] == plan[k]["set"]: j += 1
    s0 = sh_by[plan[k]["id"]]
    if s0["set"] not in ("flasche_makro", "automat_loch", "automat_display", "kasse_display", "doc_nah", "bahnhof_uhr", "bahnhof_tafel", "rathaus_uhr", "automat_innen", "automat_presse"):
        s0["cam"]["loc"] = list(jitter(s0["id"], s0["cam"]["loc"], 0.25 if s0["cam"]["loc"][0] > 250 else 0.6))
    tot = sum(plan[q]["dur"] for q in range(k, j + 1)); acc = 0.0
    mv = plan[k]["move"]
    for q in range(k, j + 1):
        sh_by[plan[q]["id"]]["cam"] = s0["cam"]
        plan[q].update(run_k=q - k, run_len=j - k + 1, run_move=mv, run_dir=1 if (k % 2) else -1, run_u=[acc / tot, (acc + plan[q]["dur"]) / tot]); acc += plan[q]["dur"]
    k = j + 1
json.dump(shots, open(os.path.join(OUT, "shots.json"), "w"), indent=0)
json.dump(plan, open(os.path.join(OUT, "plan.json"), "w"), indent=0, ensure_ascii=False)
json.dump(dreh, open(os.path.join(OUT, "bilddrehbuch.json"), "w"), indent=1, ensure_ascii=False)
json.dump([dict(v, key=k) for k, v in MO._JOBS.items()], open(os.path.join(OUT, "motion_jobs.json"), "w"), ensure_ascii=False)
print(len(plan), "Einstellungen,", len(shots), "Blender,", len(MO._JOBS), "Motion,", round(t, 1), "s")
if "--build-motion" in sys.argv: MO.build(WORK)
