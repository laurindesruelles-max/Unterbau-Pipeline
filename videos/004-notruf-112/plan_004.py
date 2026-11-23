"""Video 004 „Was wirklich passiert, wenn du 112 wählst“: Bild-Drehbuch → bilddrehbuch.json, shots.json (engine/stadt.py --extra notruf),
plan.json (engine/stadtcomp.py), motion-Jobs (engine/motion_ub.py). Satzzeiten aus saetze.json (Parakeet-Wortzeiten).
python3 plan_004.py WORK OUTDIR"""
import json, sys, os, hashlib
sys.path.insert(0, "/home/claude/unterbau-pipeline/engine")
WORK, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
S = json.load(open(os.path.join(WORK, "v4/saetze.json")))
V = WORK + "/vid/"; SC = WORK + "/scr/"

# ------------------------------------------------------------------ Kameras (loc, tgt, lens, Grundzustand, Anker)
TOWN = ["route_rtw", "haus", "leitstelle", "mast_top", "uhr", "tafel", "wache", "rtw_strasse", "rtw_haus", "funk_weg"]
PINS = ["pin_" + p for p in "kassel berlin winnenden koblenz essen muenchen paris london lissabon warschau duesseldorf stuttgart wiesbaden".split()]
SETS = {
 "k_handy":   ((300.62, 0.33, 0.72), (300.42, 0.62, 0.0), 34, {"phone": 1}, ["k_phone"]),
 "k_total":   ((302.2, -1.5, 2.3), (300.0, 0.9, 0.25), 24, {"phone": 1}, ["k_mann"]),
 "k_seite":   ((301.9, 0.7, 0.9), (300.0, 0.85, 0.3), 26, {"phone": 1}, ["k_mann"]),
 "k_uhr":     ((300.9, 0.55, 1.05), (301.3, 1.9, 0.73), 40, {"phone": 1}, ["k_uhr"]),
 "k_tuer":    ((299.0, 1.9, 1.7), (301.6, -0.6, 0.9), 26, {"phone": 1, "press": 1}, []),
 "haus_aussen": ((-15.0, -13.5, 2.4), (-12.0, -8.2, 0.6), 38, {"mine": 1, "lights": 0.6}, TOWN),
 "haus_nacht":  ((-13.6, -11.2, 1.3), (-12.0, -8.6, 0.8), 40, {"mine": 1, "lights": 0.6}, TOWN),
 "stadt_total": ((-4, -30, 16), (0, -1, 0), 40, {"lights": 0.8}, TOWN),
 "mast":        ((-13.5, -9, 1.6), (-10, -2, 3.0), 30, {}, ["mast_top", "funk_weg"]),
 "mast_haus":   ((-17.5, -15.5, 4.5), (-10, -4, 1.4), 30, {"mine": 1}, ["mast_top", "funk_weg", "haus", "leitstelle"]),
 "leitstelle_aussen": ((-3.9, -0.1, 1.1), (-6.0, 1.0, 0.55), 28, {}, ["leitstelle"]),
 "ls_innen":    ((1200, -2.8, 1.8), (1200, 2.5, 1.0), 24, {}, ["screen_l", "screen_c", "screen_r", "ls_mon"]),
 "ls_schulter": ((1199.9, -2.2, 1.75), (1199.15, -0.72, 0.62), 45, {}, ["ls_mon"]),
 "ls_wand":     ((1200, -0.4, 1.6), (1200, 2.5, 1.7), 30, {}, ["screen_l", "screen_c", "screen_r"]),
 "ls_mon_nah":  ((1199.15, -1.45, 0.78), (1199.15, -0.7, 0.62), 40, {}, ["ls_mon"]),
 "wache":       ((7.8, -8.0, 1.6), (6, -3.0, 0.3), 38, {"wache_licht": 1}, ["wache", "wache_tor"]),
 "wache_nah":   ((6.6, -5.2, 0.7), (5.4, -2.8, 0.3), 32, {}, ["wache_tor"]),
 "strasse_rtw": ((-0.6, -6.6, 1.2), (-3.5, -4.1, 0.25), 32, {"rtw_strasse": 1, "blaulicht": 1, "rtw_weg": 1}, ["rtw_strasse", "route_rtw"]),
 "route_total": ((1, -17, 9), (-3, -3, 0), 38, {"lights": 0.7, "rtw_weg": 1}, TOWN),
 "rathaus_uhr": ((0.6, 4.0, 1.4), (0, 7.5, 2.0), 50, {}, ["uhr"]),
 "bahnhof_tafel": ((-7.4, 4.4, 1.25), (-8, 7.1, 1.25), 42, {}, ["tafel"]),
 "karte_de":    ((0, 178, 18), (0, 200, 0), 45, {}, PINS),
 "karte_eu":    ((-3, 168, 38), (-3, 197, 0), 35, {}, PINS),
 "karte_kassel": ((-1.0, 192.5, 7), (-0.92, 200.2, 0), 38, {}, PINS),
 "karte_koblenz": ((-2.8, 191, 7), (-2.82, 198.7, 0), 38, {}, PINS),
 "karte_winnenden": ((-1.0, 189, 7), (-1.0, 196.3, 0), 38, {}, PINS),
 "s69":         ((1601, -6, 2.2), (1599.5, 1.5, 1.4), 30, {}, ["uhr69", "zelle"]),
 "s69_zelle":   ((1602.2, -2.6, 0.9), (1601, 0.2, 0.6), 32, {}, ["zelle"]),
 "s69_turm":    ((1598.2, -3.5, 1.6), (1597, 2.69, 3.6), 40, {}, ["uhr69"]),
 "uhren16":     ((1400, 12, 7), (1400, 22, 0.6), 35, {}, [f"uhr16_{k}" for k in range(16)]),
 "querschnitt_stadt": ((397, -8, 0.8), (400, 0, -0.4), 40, {"cut": 0}, ["cut"]),
}
DH, CD, LA, QS, TF, MK, ZW, LW, BW = "Dein Haus", "Countdown in der Welt", "Lichter gehen aus", "Querschnitt", "Tilt-Shift-Flug", "Modell-Karte", "Zahl in der Welt", "Leben in der Welt", "Bildschirm in der Welt"
FZ, AK2, LR, HB, WK, AD = "Fallblatt-Zahl (`motion` counter)", "Ablauf-Kette 2D (`motion` flow)", "Lichter-aus-Raster (`motion` grid)", "Häuserzeilen-Balken (`motion` bars)", "Warenstrom-Karte (`motion` map)", "Anzeigetafel dreht sich (`motion` flip)"
NP, MR, NK, TN, SZ, RF = "Netz-Puls", "Menschen reagieren", "Netzwerk-Karte", "Tag-Nacht-Zeitraffer", "Steuerzentrale", "Rückflug zum Anfang"

def b(st, zeigt, anim, gen="exakt", inh=("geschehen",), neu="", **kw): return dict(k="b", set=st, zeigt=zeigt, anim=anim, gen=gen, inh=list(inh), neu=neu, **kw)
def mo(comp, props, zeigt, anim, gen="exakt", inh=("zahl",), neu="", **kw): return dict(k="mo", comp=comp, props=props, zeigt=zeigt, anim=anim, gen=gen, inh=list(inh), neu=neu, **kw)
def cl(f, zeigt, ss=0.0, gen="exakt", inh=("geschehen",), neu="", **kw): return dict(k="cl", video=V + f, ss=ss, zeigt=zeigt, anim=BW, gen=gen, inh=list(inh), neu=neu, **kw)
def LB(text, anchor=None, sub=None, t0=0.15): d = {"type": "label", "text": text, "t0": t0}; d.update({"anchor": anchor} if anchor else {"pos": (800, 90)}); d.update({"sub": sub} if sub else {}); return d
def T(*texts, anchor="tafel", **kw): return {"type": "tafel", "anchor": anchor, "texts": list(texts), **kw}
def SCR(img=None, anchor="screen_c", video=None, ss=0.0): return {"type": "screen", "anchor": anchor, **({"video": video, "ss": ss} if video else {"img": img})}
def CLK(a, b_, anchor="uhr", t0=0.05, tl=0.8): return {"type": "clock", "anchor": anchor, "from": a, "to": b_, "t0": t0, "tl": tl}
GREY = {"type": "grey", "amount": 0.85, "t0": 0}
RTWDOTS = {"type": "dots", "path": "route_rtw", "n": 3, "speed": 0.03, "r": 7, "col": "blue", "blink": True}
def U16(spread=True): return [CLK(60 * (k % 12) + k * 7, 60 * (k % 12) + k * 7 + 40 + k * 3, f"uhr16_{k}", 0.05, 0.9) for k in range(16)]
Z = {}   # Satz mit Ziffern für die Prüfung (Sprechtext schreibt Zahlen aus)

SH = {
 0: [b("k_handy", "Handy-Bildschirm am Küchenboden: Anruf an 112 läuft, Zeit tickt", BW, fx=[SCR(SC + "call.png", "k_phone")])],
 1: [b("haus_aussen", "Dein Haus in der Modellstadt bei Nacht, Ortsmarke Kassel · 04:12", DH, inh=("zeit", "ort"), fx=[LB("Kassel · 04:12 Uhr", "haus", "eine Novembernacht")]),
     b("k_uhr", "Ofenuhr in der Küche klappt auf 04:12", CD, inh=("zeit",), fx=[T("04:12", anchor="k_uhr")])],
 2: [b("k_total", "Küche von oben: Mann liegt vor dem Kühlschrank, Frau kniet daneben, Handy leuchtet am Boden", MR)],
 3: [b("k_seite", "Nah am liegenden Mann, Licht flackert leicht", LW, fx=[{"type": "flicker"}])],
 4: [b("rathaus_uhr", "Rathausuhr der Modellstadt springt von 04:12 weiter", CD, inh=("zeit",), fx=[CLK(252, 254)])],
 5: [b("bahnhof_tafel", "Fallblatt-Tafel am Bahnhof klappt auf MINUTE 0", CD, inh=("zeit",), neu="frage:rechtzeitig", fx=[T("MINUTE 0")])],
 6: [mo("grid", {"label": "OHNE WIEDERBELEBUNG", "n": 100, "icon": "heart", "value": 10, "suffix": " %", "caption": "weniger Chance – pro Minute", "hot": 10},
       "Raster aus 100 Herzen, pro Minute werden 10 dunkel, Zahl 10 % klappt hoch", LR)],
 7: [b("ls_innen", "Leitstelle bei Nacht: an einem Platz blinkt das orange Telefonlicht – einmal, zweimal", SZ, fx=[{"type": "flicker"}])],
 8: "merge", 9: "merge",
 10: [b("stadt_total", "Tilt-Shift-Flug über die Stadt zur Leitstelle, Ortsmarke erscheint", TF, inh=("ort",), fx=[LB("Leitstelle", "leitstelle")])],
 11: [b("ls_schulter", "Über die Schulter des Disponenten: Einsatzmonitor füllt sich – Ort, Meldebild, Fahrzeug", BW, fx=[SCR(SC + "einsatz.png", "ls_mon")])],
 12: [mo("map", {"label": "LEITSTELLEN", "view": [10.4, 51.2, 2600], "highlight": ["276"], "swarm": 240}, "Deutschlandkarte, 240 Lichtpunkte für die Leitstellen schwärmen aus", WK),
      b("stadt_total", "Die Stadt bei Nacht: ganze Straßenzüge werden dunkel – Hinweis auf den Ausfall", LA, neu="frage:ausfall", A={"lights": 1}, B={"lights": 0.12}, trans="lights", t_trans=[0.25, 0.85])],
 13: [b("querschnitt_stadt", "Querschnitt: die Straße reißt auf, darunter laufen orange Impulse durch die Leitungen", QS, gen="schema", inh=("erklaerung",), neu="frage:dreidinge",
        B={"cut": 1}, trans="wipe_down", t_trans=[0.1, 0.6], fx=[{"type": "dots", "path": "cut", "n": 14, "speed": 0.05, "r": 6}])],
 14: [b("k_total", "Küche, Einblendung Szene nachgestellt", LW, inh=("erklaerung",), fx=[LB("Szene nachgestellt", None, None, 0.05)])],
 15: [b("haus_nacht", "Kamera fährt vom Haus zurück in die nächtliche Stadt", RF, gen="schema", inh=("ort",))],
 "T": [b("stadt_total", "Titelkarte UNTERBAU über der Modellstadt", TF, inh=("erklaerung",), fx=[{"type": "card", "top": "WAS WIRKLICH PASSIERT, WENN DU 112 WÄHLST", "title": "UNTERBAU", "sub": "Verstehen, wie die Welt funktioniert"}])],
 "K1": [b("leitstelle_aussen", "Kapitelkarte 1 vor der Leitstelle", TF, inh=("erklaerung",), fx=[{"type": "card", "top": "KAPITEL 1", "title": "Die erste Minute"}])],
 16: [b("bahnhof_tafel", "Tafel klappt auf MINUTE 0 · 04:12", CD, inh=("zeit",), fx=[T("MINUTE 0", "04:12")])],
 17: [b("mast_haus", "Vom Haus springt ein oranger Impuls zum Funkmast, die Mastlampe blinkt", NP, gen="schema", inh=("erklaerung",), fx=[{"type": "dots", "path": "funk_weg", "n": 6, "speed": 0.06, "r": 6}, LB("Funkmast", "mast_top")])],
 18: [b("karte_de", "Modellkarte Deutschland: keine einzelne Zentrale, viele Lichter", MK, gen="schema", inh=("erklaerung",), fx=[LB("keine Zentrale für ganz Deutschland", None, None, 0.2)])],
 19: [cl("px129409.mp4", "Echter Funkmast vor Wolkenhimmel (Match-Cut zum Modellmast)", 2.0, inh=("ort",))],
 20: [mo("flow", {"label": "WOHIN DER NOTRUF GEHT", "nodes": [{"icon": "phone", "label": "Handy"}, {"icon": "tower", "label": "Funkmast"}, {"icon": "house", "label": "zuständige Leitstelle"}], "packet": "phone"},
        "Ablauf-Kette: Handy → Funkmast → zuständige Leitstelle, ein Paket wandert mit", AK2, gen="schema", inh=("erklaerung",))],
 21: [mo("counter", {"label": "LEITSTELLEN", "value": 240, "prefix": "≈ ", "caption": "in Deutschland"}, "Fallblatt-Zahl klappt auf 240", FZ)],
 22: [b("leitstelle_aussen", "Die Leitstelle der Modellstadt, Schild: Träger Kreis oder Stadt", LW, inh=("erklaerung",), gen="schema", fx=[LB("betrieben von Kreis oder Stadt", "leitstelle")])],
 23: [b("stadt_total", "Über der Stadt leuchten hunderte orange Punkte auf – Notrufe", NK, A={"lights": 0.7}, fx=[{"type": "scatter", "n": 220, "t0": 0.0}])],
 24: [mo("counter", {"label": "NOTRUFE PRO JAHR", "value": 30000000, "prefix": "> ", "caption": "110 + 112 · ≈ 1 pro Sekunde"}, "Fallblatt-Zahl über 30.000.000, Unterzeile 1 pro Sekunde", FZ)],
 25: [b("karte_de", "Modellkarte: Berlin markiert, alle 28 Sekunden ein Notruf", MK, fx=[LB("Berlin: alle 28 s ein Notruf", "pin_berlin", "2024")])],
 26: [cl("px1110.mp4", "Echte Hände tippen auf einem Smartphone, Einblendung: ohne SIM kein Notruf seit 2009", 0.5, inh=("zahl",), fx=[LB("ohne SIM-Karte: kein Notruf", None, "seit 2009", 0.1)])],
 27: [cl("px204018.mp4", "Funknetz-Waben leuchten auf: fremdes Netz trägt den Notruf", 3.0, inh=("erklaerung",), fx=[LB("fremdes Netz: geht", None, "auch ohne Guthaben", 0.1)])],
 28: [b("ls_schulter", "Disponent nimmt ab, auf dem Monitor das Anrufbild", SZ, fx=[SCR(SC + "call.png", "ls_mon")])],
 29: [mo("flip", {"front": {"icon": "doc", "title": "Was?"}, "back": {"title": "Wo?", "sub": "Wo ist der Notfallort?"}, "at": 2.6}, "Tafel dreht sich: aus WAS? wird WO?", AD, inh=("erklaerung",))],
 30: "merge",
 31: [b("wache", "Rettungswache im Dunkeln, die Wagen stehen – niemand weiß wohin", LW, gen="schema", inh=("erklaerung",), A={"wache_licht": 0.15})],
 32: [b("k_seite", "Die Frau kniet am Boden, das Handy leuchtet, Licht zittert", MR, fx=[{"type": "flicker"}])],
 33: [b("haus_aussen", "Dein Haus von außen, Fragezeichen an der Hausnummer", DH, fx=[LB("Hausnummer?", "haus")])],
 34: [b("k_handy", "Das Handy am Boden leuchtet stärker auf", LW, fx=[SCR(SC + "call.png", "k_phone")])],
 35: [b("mast_haus", "Ein oranger Punkt springt vom Haus über den Funkmast zur Leitstelle", NP, gen="schema", inh=("erklaerung",), fx=[{"type": "dots", "path": "funk_weg", "n": 3, "speed": 0.08, "r": 8}])],
 36: [b("ls_wand", "Großbildschirm der Leitstelle: Karte mit pulsierendem Standortpunkt", BW, fx=[SCR(anchor="screen_c", video=SC + "aml.mp4")])],
 37: [mo("flip", {"front": {"icon": "phone", "title": "AML"}, "back": {"title": "Standort", "sub": "automatisch vom Handy"}, "at": 1.2}, "Tafel dreht sich: AML wird zu Standort", AD, inh=("erklaerung",))],
 38: [mo("bars", {"label": "LEITSTELLEN MIT AML", "title": "2022", "bars": [["nutzen AML", 223, True], ["alle Leitstellen", 234, False]]}, "Häuserzeilen-Balken: 223 von 234 Leitstellen", HB)],
 39: [b("ls_schulter", "Monitor zeigt den Punkt mit 30-Meter-Kreis", BW, fx=[SCR(anchor="ls_mon", video=SC + "aml.mp4"), LB("8 von 10 Fällen: ± 30 m", None, None, 0.2)])],
 40: [b("bahnhof_tafel", "Tafel klappt auf MINUTE 1", CD, inh=("zeit",), fx=[T("MINUTE 1")])],
 41: [b("ls_mon_nah", "Nah am Monitor: der orange Punkt blinkt mitten in ihrer Straße", BW, fx=[SCR(anchor="ls_mon", video=SC + "aml.mp4", ss=1.0)])],
 42: [b("ls_innen", "Alarmlampen in der Leitstelle gehen an, Einsatz auf dem Großbildschirm", SZ, fx=[SCR(SC + "einsatz.png", "screen_c"), {"type": "flicker"}])],
 43: [b("wache", "In der Rettungswache springt das Licht an", LW, A={"wache_licht": 0.1}, B={"wache_licht": 1}, trans="lights", t_trans=[0.2, 0.5])],
 44: [b("wache_nah", "Das Rolltor fährt hoch, der Rettungswagen steht im Licht", LW, A={"wache_licht": 1}, B={"wache_licht": 1, "wache_tor": 1}, trans="wipe_down", t_trans=[0.1, 0.8])],
 45: [mo("phone", {"label": "DER DISPONENT SAGT", "app": "NOTRUF 112", "messages": [["Legen Sie das Handy neben ihn.", False], ["Ich bleibe dran.", False], ["Wir drücken jetzt zusammen.", False]]},
        "Handy-Bildschirm: die Sätze des Disponenten erscheinen nacheinander", BW, inh=("geschehen",))],
 46: "merge", 47: "merge",
 48: [b("k_total", "Die Frau legt die Hände auf die Brust des Mannes und drückt", MR, A={"press": 0}, B={"press": 1}, trans="fade", t_trans=[0.2, 0.5])],
 49: [cl("px86507.mp4", "Echter Clip: Hände drücken im Takt auf eine Übungspuppe", 3.0)],
 50: [b("k_seite", "Die Frau drückt, Einblendung Telefonreanimation", MR, inh=("erklaerung",), A={"press": 1}, fx=[LB("Telefonreanimation", None, None, 0.1)])],
 51: [mo("bars", {"label": "TELEFONREANIMATION", "unit": " %", "bars": [["Ziel der Fachleute", 100, False], ["tatsächlich (2025)", 37, True]]}, "Häuserzeilen-Balken: Ziel 100 %, tatsächlich 37 %", HB)],
 52: "merge",
 53: [b("strasse_rtw", "Der Rettungswagen fährt mit Blaulicht durch die Straße", LW, fx=[{"type": "blink", "anchors": ["rtw_strasse"]}, RTWDOTS])],
 54: [b("s69", "Rückblende: eine graue Straße von früher mit Telefonzelle", TN, gen="schema", inh=("zeit",), neu="frage:junge", fx=[GREY])],
 "K2": [b("s69", "Kapitelkarte 2 über der grauen Straße", LW, inh=("erklaerung",), fx=[GREY, {"type": "card", "top": "KAPITEL 2", "title": "Winnenden, 1969"}])],
 55: [b("s69", "Graue Straße, Datum 3. Mai 1969 erscheint", CD, inh=("zeit",), fx=[GREY, LB("3. Mai 1969", None, None, 0.05)])],
 56: [b("karte_winnenden", "Modellkarte: Winnenden bei Stuttgart markiert", MK, inh=("ort",), fx=[GREY, LB("Winnenden", "pin_winnenden", "bei Stuttgart")])],
 57: [b("s69", "Die Straße am Nachmittag, leer, grau – der Heimweg", LW, gen="schema", fx=[GREY])],
 58: [b("s69_zelle", "Das Bild zuckt, die Lichter der Straße flackern – der Unfall wird nicht gezeigt", LA, A={"lights": 1}, B={"lights": 0.3}, trans="lights", t_trans=[0.1, 0.4], fx=[GREY, {"type": "flicker"}])],
 59: [b("s69_zelle", "Die gelbe Telefonzelle leuchtet: Welche Nummer?", LW, fx=[GREY, LB("Welche Nummer?", "zelle")])],
 60: [mo("flip", {"front": {"icon": "phone", "title": "Notruf?"}, "back": {"title": "keine Nummer", "sub": "die überall gilt"}, "at": 1.6}, "Tafel dreht sich: Notruf? – keine Nummer", AD, inh=("erklaerung",))],
 61: [b("s69_turm", "Die Kirchturmuhr dreht fast eine ganze Stunde weiter", CD, inh=("zeit",), fx=[GREY, CLK(720, 775, "uhr69", 0.0, 0.95)])],
 62: [b("s69", "Graue Straße, Einblendung Björn Steiger, 8 Jahre", LW, inh=("person",), neu="antwort:junge", fx=[GREY, LB("Björn Steiger", None, "8 Jahre", 0.05)])],
 63: [b("s69", "Die Lichter der Straße erlöschen", LA, A={"lights": 1}, B={"lights": 0.05}, trans="lights", t_trans=[0.1, 0.8], fx=[GREY])],
 64: [mo("flip", {"front": {"icon": "heart", "title": "Verletzungen?"}, "back": {"title": "Schock", "sub": "laut Björn Steiger Stiftung"}, "at": 2.2}, "Tafel dreht sich: Verletzungen? – Schock", AD, inh=("erklaerung",))],
 65: [b("s69_zelle", "Telefonzelle, Datum 7. Juli 1969 – Gründung der Stiftung", CD, inh=("zeit",), fx=[GREY, LB("7. Juli 1969", "zelle", "Björn Steiger Stiftung")])],
 66: [mo("flow", {"label": "DAS ZIEL", "nodes": [{"icon": "car", "label": "Unfall"}, {"icon": "phone", "label": "Notruf"}, {"icon": "truck", "label": "Hilfe kommt"}], "packet": "phone"}, "Ablauf-Kette: Unfall → Notruf → Hilfe", AK2, gen="schema", inh=("erklaerung",))],
 67: [mo("flip", {"front": {"icon": "gavel", "title": "Klage"}, "back": {"title": "1973", "sub": "gegen Land und Bund"}, "at": 2.0}, "Tafel dreht sich: Klage 1973 gegen Land und Bund", AD, inh=("zeit",))],
 68: [b("bahnhof_tafel", "Fallblatt-Tafel am Bahnhof klappt: KLAGE – ABGEWIESEN", ZW, fx=[GREY, T("KLAGE", "ABGEWIESEN")])],
 69: [b("s69", "Zeitraffer: Tag bricht an, die Straße wird hell – Druck wächst", TN, gen="schema", A={"day": 0.0}, B={"day": 0.7}, trans="fade", fx=[GREY])],
 70: [b("bahnhof_tafel", "Tafel klappt auf 20.09.1973", CD, inh=("zeit",), fx=[{"type": "grey", "amount": 0.5, "t0": 0}, T("20.09.1973")]),
      b("rathaus_uhr", "Rathaus mit Uhr: Ministerpräsidenten treffen den Kanzler, Datum 1973", LW, fx=[{"type": "grey", "amount": 0.5, "t0": 0}, LB("Ministerpräsidenten + Bundeskanzler", None, "Bonn, 1973", 0.1)])],
 71: [mo("flip", {"front": {"icon": "doc", "title": "Beschluss"}, "back": {"title": "110 · 112", "sub": "Westdeutschland, 1973"}, "at": 1.8}, "Tafel dreht sich: Beschluss – 110 · 112", AD, inh=("zahl",))],
 72: [b("bahnhof_tafel", "Fallblatt-Tafel klappt 110 und 112", ZW, inh=("zahl",), fx=[T("110", "112")])],
 73: [b("karte_de", "Modellkarte: Leitungen wachsen von Stadt zu Stadt, Ende 1979", NK, inh=("zeit",), fx=[{"type": "lines", "pairs": ["de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"], "cities": "de_staedte", "grow": 0.8}, LB("Ende 1979", None, "letztes Ortsnetz angeschlossen", 0.3)])],
 74: [b("karte_eu", "Modellkarte Europa, Jahreszahl 1991", MK, inh=("zeit",), fx=[LB("1991", None, "Europa zieht nach", 0.1)])],
 75: [mo("map", {"label": "EG 1991", "view": "europe", "highlight": ["056", "208", "276", "300", "724", "250", "372", "380", "442", "528", "620", "826"], "title": "112 in allen 12 Mitgliedsländern"},
        "Europakarte: die 12 EG-Länder von 1991 leuchten nacheinander auf", WK, inh=("zeit",))],
 76: [b("karte_eu", "Modellkarte: 112 in Lissabon und Warschau markiert", MK, inh=("ort",), fx=[LB("112", "pin_lissabon", "Lissabon", 0.1), LB("112", "pin_warschau", "Warschau", 0.45)])],
 77: [b("bahnhof_tafel", "Fallblatt-Tafel zeigt groß 112", ZW, inh=("zahl",), fx=[T("112")])],
 78: [b("uhren16", "Sechzehn Uhren auf dem Modellgelände laufen unterschiedlich", CD, inh=("zeit",), neu="frage:frist", fx=U16())],
 "K3": [b("uhren16", "Kapitelkarte 3 vor den sechzehn Uhren", LW, inh=("erklaerung",), fx=U16() + [{"type": "card", "top": "KAPITEL 3", "title": "Sechzehn Uhren"}])],
 79: [b("haus_aussen", "Rückflug zum Haus in Kassel", RF, inh=("ort",))],
 80: [b("bahnhof_tafel", "Tafel klappt auf MINUTE 4", CD, inh=("zeit",), fx=[T("MINUTE 4")])],
 81: [b("k_total", "Die Frau drückt im Takt, das Handy leuchtet neben dem Mann", MR, A={"press": 1})],
 82: [b("route_total", "Blaues Licht zieht auf der Route von der Wache zum Haus durch die dunkle Stadt", TF, inh=("ort", "geschehen"), fx=[RTWDOTS, {"type": "blink", "anchors": ["haus"], "gain": 0.6}])],
 83: [cl("px7315.mp4", "Echter Clip: Blaulicht in der Nacht", 0.5)],
 84: [b("karte_de", "Modellkarte Deutschland, Ländergrenzen treten hervor", MK, gen="schema", inh=("erklaerung",))],
 85: [mo("map", {"label": "RETTUNGSDIENST", "view": [10.4, 51.2, 2600], "highlight": ["276"], "title": "Sache der 16 Länder"}, "Deutschlandkarte, Titel Sache der 16 Länder", WK, gen="schema", inh=("erklaerung",))],
 86: [b("uhren16", "Sechzehn Uhren, jede zeigt eine andere Zeit", ZW, inh=("zahl",), fx=U16() + [LB("16 Rettungsdienstgesetze", None, None, 0.1)])],
 87: [b("karte_kassel", "Modellkarte: Kassel in Hessen markiert", MK, inh=("ort",), fx=[LB("Kassel", "pin_kassel", "Hessen")])],
 88: [mo("counter", {"label": "HESSEN", "value": 10, "suffix": " MIN", "caption": "in 9 von 10 Fällen"}, "Fallblatt-Zahl 10 MIN, darunter in 9 von 10 Fällen", FZ, neu="antwort:frist")],
 89: [b("rathaus_uhr", "Uhr startet in dem Moment, in dem der Notruf eingeht", CD, inh=("zeit",), fx=[CLK(252, 262)])],
 90: [mo("bars", {"label": "NORDRHEIN-WESTFALEN", "unit": " min", "bars": [["Stadt", 8, True], ["Land", 12, False]]}, "Häuserzeilen-Balken: NRW Stadt 8 min, Land 12 min", HB)],
 91: [b("uhren16", "Eine der sechzehn Uhren leuchtet: Bayern 12 Minuten", CD, inh=("zeit",), fx=U16() + [LB("Bayern: 12 Minuten", None, None, 0.1)])],
 92: [b("wache_nah", "Das Tor fährt hoch – erst hier startet in Bayern die Uhr", LW, inh=("erklaerung",), A={"wache_licht": 1}, B={"wache_tor": 1}, trans="wipe_down", t_trans=[0.1, 0.7], fx=[LB("Uhr startet beim Ausrücken", None, "Bayern", 0.3)])],
 93: [mo("flip", {"front": {"icon": "gavel", "title": "Gericht 2023"}, "back": {"title": "Frist gekippt", "sub": "der Landtag hatte nicht entschieden"}, "at": 2.4}, "Tafel dreht sich: Gericht 2023 – Frist gekippt", AD, inh=("zeit",))],
 94: [mo("counter", {"label": "BADEN-WÜRTTEMBERG", "value": 12, "suffix": " MIN", "caption": "in 95 von 100 Fällen · neues Gesetz"}, "Fallblatt-Zahl 12 MIN, in 95 von 100 Fällen", FZ)],
 95: [b("uhren16", "Alle sechzehn Uhren ticken gegeneinander", CD, inh=("zeit",), fx=U16() + [LB("dieselbe Not · 16 Uhren", None, None, 0.1)])],
 96: "merge",
 97: [b("wache", "Die Rettungswache von außen, Rettungswagen im Hof", LW, neu="frage:wer")],
 98: [mo("flow", {"label": "WER BESTELLT?", "nodes": [{"icon": "bank", "label": "Kreis / Stadt"}, {"icon": "doc", "label": "Auftrag"}, {"icon": "truck", "label": "Rettungsdienst"}], "packet": "doc"}, "Ablauf-Kette: Kreis oder Stadt vergibt den Auftrag an den Rettungsdienst", AK2, gen="schema", inh=("erklaerung",))],
 99: [b("wache_nah", "Rettungswagen vor dem offenen Tor", MR, A={"wache_licht": 1, "wache_tor": 1})],
 100: [mo("bars", {"label": "WER DEN RETTUNGSDIENST FÄHRT", "unit": " %", "bars": [["Hilfsorganisationen", 80, True], ["Kommunen / Feuerwehr", 15, False], ["Private", 5, False]]}, "Häuserzeilen-Balken: 80 % Hilfsorganisationen", HB, neu="antwort:wer")],
 101: "merge",
 102: [mo("flow", {"label": "WER ZAHLT?", "nodes": [{"icon": "person", "label": "dein Beitrag"}, {"icon": "bank", "label": "Krankenkasse"}, {"icon": "truck", "label": "Rettungsdienst"}], "packet": "money"}, "Ablauf-Kette: dein Beitrag → Krankenkasse → Rettungsdienst", AK2, gen="schema", inh=("erklaerung",))],
 103: [b("bahnhof_tafel", "Fallblatt-Tafel: MEHRERE 100 €", ZW, fx=[T("EINSATZ", "MEHRERE 100 €")])],
 104: [mo("counter", {"label": "ESSEN · GEBÜHRENSATZUNG", "value": 1020, "suffix": " €", "caption": "pro Einsatz mit dem Rettungswagen"}, "Fallblatt-Tafel klappt auf 1.020 € pro Einsatz", FZ)],
 105: [b("ls_innen", "Leitstelle: alle Telefonlichter blinken gleichzeitig", SZ, fx=[{"type": "flicker"}, SCR(SC + "einsatz.png", "screen_l")])],
 106: [b("stadt_total", "Über der Stadt blinken viele orange Anrufpunkte", NK, A={"lights": 0.7}, fx=[{"type": "scatter", "n": 160, "t0": 0.0}])],
 107: [mo("flip", {"front": {"icon": "phone", "title": "112"}, "back": {"title": "116 117", "sub": "ärztlicher Bereitschaftsdienst"}, "at": 2.5}, "Tafel dreht sich: 112 – 116 117", AD, inh=("zahl",))],
 108: [cl("px87884.mp4", "Echter Clip: nächtliche Autobahn mit Lichtern", 1.0)],
 109: [mo("flow", {"label": "eCALL", "nodes": [{"icon": "car", "label": "Unfall"}, {"icon": "tower", "label": "automatisch"}, {"icon": "phone", "label": "112"}], "packet": "phone"}, "Ablauf-Kette: Unfall → automatisch → 112, seit 2018", AK2, inh=("zeit",), fx=[])],
 110: [mo("grid", {"label": "eCALL IN BAYERN", "n": 10, "icon": "car", "value": 90, "prefix": "> ", "suffix": " %", "caption": "Fehlalarme", "hot": 9}, "Raster aus 10 Autos, 9 werden markiert: über 90 % Fehlalarme", LR)],
 111: [b("bahnhof_tafel", "Tafel klappt: OKT. 2026 – NOTFALLREFORM", CD, inh=("zeit",), fx=[T("OKT. 2026", "NOTFALLREFORM")])],
 112: [mo("flip", {"front": {"icon": "doc", "title": "Bundesrat"}, "back": {"title": "gebilligt", "sub": "November 2026"}, "at": 1.4}, "Tafel dreht sich: Bundesrat – gebilligt", AD, inh=("zeit",))],
 113: [mo("flow", {"label": "NEU VERNETZT", "nodes": [{"icon": "phone", "label": "112"}, {"icon": "server", "label": "vernetzt"}, {"icon": "phone", "label": "116 117"}], "packet": "doc"}, "Ablauf-Kette: 112 und 116 117 werden digital verbunden", AK2, gen="schema", inh=("erklaerung",))],
 114: [b("haus_nacht", "Zurück zum Haus, Licht im Fenster", DH, inh=("ort",))],
 115: [b("bahnhof_tafel", "Tafel klappt auf MINUTE 5", CD, inh=("zeit",), fx=[T("MINUTE 5")])],
 116: [b("k_seite", "Die Frau drückt weiter, das Bild zittert vor Anstrengung", MR, A={"press": 1}, fx=[{"type": "flicker"}])],
 117: [b("ls_schulter", "Disponent spricht weiter, Monitor mit laufendem Anruf", SZ, fx=[SCR(SC + "call.png", "ls_mon")])],
 118: [mo("bars", {"label": "LAIEN BEGINNEN MIT WIEDERBELEBUNG", "unit": " %", "bars": [["2010", 14, False], ["2024", 55, True]]}, "Häuserzeilen-Balken: 14 % 2010, 55 % 2024", HB, inh=("zahl", "zeit"))],
 119: "merge",
 120: [mo("map", {"label": "LAIENHILFE", "view": [12, 58, 1500], "highlight": ["578", "752", "528"], "title": "7 bis 8 von 10"}, "Karte: Norwegen, Schweden, Niederlande leuchten, 7 bis 8 von 10", WK)],
 121: [cl("px4360.mp4", "Echter Clip: EKG-Linie schlägt auf dem Monitor", 2.0, inh=("erklaerung",))],
 122: [b("ls_innen", "Leitstelle, der Anruf steht, die Lampe am Platz leuchtet ruhig", SZ)],
 123: [b("stadt_total", "Die Stadt: einzelne Viertel werden dunkel – Vorbote", LA, A={"lights": 1}, B={"lights": 0.3}, trans="lights", t_trans=[0.3, 0.9])],
 "K4": [b("stadt_total", "Kapitelkarte 4 über der dunklen Stadt", LW, inh=("erklaerung",), A={"lights": 0.2}, fx=[{"type": "card", "top": "KAPITEL 4", "title": "Wenn niemand durchkommt"}])],
 124: [b("mast", "Die Lampe am Funkmast erlischt", LA, A={"mast_on": 1}, B={"mast_on": 0}, trans="fade", t_trans=[0.3, 0.6])],
 125: [b("bahnhof_tafel", "Tafel klappt auf 11.11.2021", CD, inh=("zeit",), fx=[T("11.11.2021")])],
 126: [b("rathaus_uhr", "Die Rathausuhr der Modellstadt springt auf 04:30", CD, inh=("zeit",), fx=[CLK(268, 270)])],
 127: [b("k_uhr", "Küchenuhr der Szene: 04:12 – fast dieselbe Stunde", RF, inh=("zeit",), fx=[T("04:12", "04:30", anchor="k_uhr")])],
 128: [b("stadt_total", "Überall in der Stadt blinken Anrufe auf – und werden rot", NK, neu="antwort:ausfall", A={"lights": 0.6}, fx=[{"type": "scatter", "n": 180, "t0": 0.0, "col": "red"}])],
 129: [b("ls_innen", "Leitstelle: Bildschirme schwarz, KEINE VERBINDUNG", SZ, A={"ls_dark": 1, "phones": 0}, fx=[SCR(SC + "ausfall.png", "screen_c")])],
 130: [cl("px14900.mp4", "Echter Clip: Netzwerk-Technik mit Lichtern, Einblendung Wartung", 2.0, inh=("erklaerung",), fx=[LB("Wartung · neue Software", None, None, 0.1)])],
 131: [mo("flip", {"front": {"icon": "gear", "title": "getestet"}, "back": {"title": "Fehler", "sub": "trotzdem"}, "at": 1.4}, "Tafel dreht sich: getestet – Fehler", AD, inh=("erklaerung",))],
 132: "merge",
 133: [mo("grid", {"label": "11.11.2021", "n": 60, "icon": "phone", "value": 70, "suffix": " min", "caption": "110 und 112 gestört", "hot": 60}, "Raster aus Telefonen, alle werden dunkel: 70 Minuten gestört", LR, inh=("zahl", "zeit"))],
 134: [b("rathaus_uhr", "Rathausuhr springt auf 05:40", CD, inh=("zeit",), fx=[CLK(270, 340)])],
 135: [mo("flip", {"front": {"icon": "lock", "title": "Hacker?"}, "back": {"title": "Nein", "sub": "ein Fehler bei einem Update"}, "at": 1.6}, "Tafel dreht sich: Hacker? – Nein", AD, inh=("erklaerung",))],
 136: "merge",
 137: [b("karte_eu", "Modellkarte Europa, Blick nach Westen", MK, inh=("ort",), neu="frage:haerter")],
 138: [mo("map", {"label": "FRANKREICH", "view": [2.5, 46.5, 2600], "highlight": ["250"], "pins": [{"lonlat": [2.35, 48.86], "label": "2. Juni 2021"}], "title": "Notruf-Ausfall"}, "Karte Frankreich, Pin 2. Juni 2021", WK, inh=("zeit", "ort"))],
 139: [b("rathaus_uhr", "Uhr dreht vom Nachmittag bis Mitternacht", CD, inh=("zeit",), fx=[CLK(990, 1440, t0=0.0, tl=0.95)])],
 140: [mo("counter", {"label": "FRANKREICH", "value": 11800, "prefix": "≈ ", "caption": "Anrufe kamen nicht durch"}, "Fallblatt-Tafel klappt auf 11.800 nicht durchgekommene Anrufe", FZ, neu="antwort:haerter")],
 141: [b("stadt_total", "Die Stadt wird grau und still, Einblendung 3 Todesfälle", LA, A={"lights": 0.6}, B={"lights": 0.15}, trans="lights", fx=[{"type": "grey", "amount": 0.5, "t0": 0.2}, LB("3 Todesfälle", None, "mit dem Ausfall in Verbindung gebracht", 0.2)])],
 142: [mo("map", {"label": "GROSSBRITANNIEN", "view": [-2.5, 54.5, 2400], "highlight": ["826"], "pins": [{"lonlat": [-0.13, 51.5], "label": "25. Juni 2023"}], "title": "Notruf gestört"}, "Karte Großbritannien, Pin 25. Juni 2023", WK, inh=("zeit", "ort")),
       mo("counter", {"label": "GROSSBRITANNIEN", "value": 14000, "prefix": "≈ ", "caption": "Anrufversuche gescheitert"}, "Fallblatt-Tafel klappt auf 14.000 gescheiterte Anrufversuche", FZ)],
 143: [mo("counter", {"label": "STRAFE DER AUFSICHT", "value": 17.5, "dec": 1, "prefix": "£ ", "suffix": " MIO.", "caption": "Ofcom"}, "Fallblatt-Zahl 17,5 Mio. Pfund", FZ)],
 144: [b("stadt_total", "Hunderte Anrufpunkte über der Stadt, sie stapeln sich", NK, A={"lights": 0.6}, fx=[{"type": "scatter", "n": 320, "t0": 0.0}])],
 145: [cl("px14324.mp4", "Echter Clip: Hochwasser reißt an Brückenpfeilern, Einblendung 14. Juli 2021 · Ahrtal", 0.0, inh=("zeit", "ort"), fx=[LB("14. Juli 2021", None, "Flutnacht im Ahrtal", 0.05)])],
 146: [b("karte_koblenz", "Modellkarte: Koblenz markiert, Leitstelle", MK, inh=("ort",), fx=[LB("Leitstelle Koblenz", "pin_koblenz")])],
 147: [b("mast", "Funkmast, Impulse stauen sich und bleiben stehen", NP, gen="schema", inh=("geschehen",), fx=[{"type": "dots", "path": "funk_weg", "n": 40, "speed": 0.02, "r": 5, "stop": 0.4}])],
 148: [mo("counter", {"label": "AHRTAL", "value": 11000, "prefix": "≈ ", "caption": "Notrufe – vom LKA ausgewertet"}, "Fallblatt-Tafel klappt auf 11.000 ausgewertete Notrufe", FZ)],
 149: [b("ls_innen", "Leitstelle voll besetzt, alle Telefone blinken, Warteschlange auf dem Bildschirm", SZ, fx=[{"type": "flicker"}, SCR(SC + "schlange.png", "screen_c")])],
 150: "merge",
 151: [b("ls_wand", "Großbildschirm zeigt die Flut", BW, fx=[SCR(anchor="screen_c", video=V + "px14324.mp4", ss=7.0), SCR(SC + "schlange.png", "screen_l")])],
 152: [b("stadt_total", "Stromausfall: die ganze Stadt wird dunkel", LA, neu="frage:analog", A={"lights": 1}, B={"lights": 0.04}, trans="lights", t_trans=[0.2, 0.9])],
 153: [cl("px4101.mp4", "Echter Clip: eine Kerze brennt im Dunkeln", 1.0)],
 154: [b("karte_de", "Modellkarte: Berlin markiert, Leuchttürme", MK, inh=("ort",), neu="antwort:analog", fx=[LB("Leuchttürme", "pin_berlin", "Berlin")])],
 155: [b("wache", "Die Stadt ist dunkel, nur die Wache leuchtet als Anlaufstelle", LA, A={"lights": 0.04, "wache_licht": 0.2}, B={"wache_licht": 1}, trans="lights")],
 156: [b("wache", "Menschen kommen zur hellen Wache, von dort geht der Notruf weiter", MR, A={"lights": 0.04, "wache_licht": 1, "people_w": 1}, fx=[{"type": "blink", "anchors": ["wache"], "gain": 0.5}])],
 157: [b("route_total", "Von oben: Lichter bewegen sich durch die dunkle Stadt zur Wache", TF, inh=("ort", "geschehen"), A={"lights": 0.04, "people_w": 1, "wache_licht": 1}, fx=[{"type": "dots", "path": "route_rtw", "n": 8, "speed": -0.01, "r": 4}])],
 158: [cl("px63970.mp4", "Echter Clip: leere Straße bei Nacht", 2.0)],
 "K5": [b("haus_nacht", "Kapitelkarte 5 vor dem Haus", LW, inh=("erklaerung",), fx=[{"type": "card", "top": "KAPITEL 5", "title": "Minute neun"}])],
 159: [b("haus_aussen", "Rückflug zum Haus: der Rettungswagen steht davor, Blaulicht", RF, inh=("ort",), A={"rtw_haus": 1, "blaulicht": 1}, fx=[{"type": "blink", "anchors": ["rtw_haus"]}])],
 160: [b("k_uhr", "Küchenuhr klappt auf 04:21", CD, inh=("zeit",), fx=[T("04:21", anchor="k_uhr")])],
 161: [b("k_total", "Blaues Licht wandert über die Küchenwand", LW, A={"press": 1, "blau": 1}, fx=[{"type": "wash"}])],
 162: [b("k_tuer", "Zwei Retter treten in die Tür", MR, A={"blau": 1}, B={"retter": 1}, trans="fade", t_trans=[0.2, 0.6], fx=[{"type": "wash", "gain": 0.5}, LB("Minute 9", None, None, 0.4)])],
 163: [b("k_seite", "Die Retter übernehmen, der Defibrillator steht bereit", LW, A={"retter": 1, "press": 0, "blau": 1}, fx=[{"type": "wash", "gain": 0.4}])],
 164: "merge",
 165: [b("querschnitt_stadt", "Querschnitt: die Straße reißt auf, Impulse laufen durch das System", QS, gen="schema", inh=("erklaerung",), B={"cut": 1}, trans="wipe_down", t_trans=[0.1, 0.6], fx=[{"type": "dots", "path": "cut", "n": 14, "speed": 0.05, "r": 6}])],
 166: [b("route_total", "Blaulicht auf der Straße von oben", TF, inh=("ort",), fx=[RTWDOTS])],
 167: [b("k_total", "Die Küche: die ersten Minuten", DH, neu="antwort:rechtzeitig", A={"press": 1})],
 168: [b("ls_schulter", "Der Disponent am Telefon", SZ, fx=[SCR(SC + "call.png", "ls_mon")])],
 169: [mo("counter", {"label": "HERZSTILLSTAND PRO JAHR", "value": 136000, "prefix": "≈ ", "caption": "außerhalb einer Klinik in Deutschland"}, "Fallblatt-Tafel klappt auf 136.000 Herzstillstände pro Jahr", FZ)],
 170: [b("bahnhof_tafel", "Fallblatt-Tafel: 370 PRO TAG", ZW, fx=[T("370 PRO TAG")])],
 171: [mo("grid", {"label": "NACH WIEDERBELEBUNG", "n": 50, "icon": "person", "value": 10, "prefix": "≈ ", "suffix": " %", "caption": "überleben", "hot": 5}, "Raster aus 50 Figuren, 5 leuchten: jeder Zehnte überlebt", LR)],
 172: [b("k_total", "Die Küche mit den Rettern, Einblendung Szene nachgestellt", LW, inh=("erklaerung",), A={"retter": 1, "blau": 1}, fx=[LB("Szene nachgestellt", None, None, 0.05)])],
 173: [b("stadt_total", "Über ganz Deutschland verteilt: hunderte Punkte am Tag", NK, A={"lights": 0.7}, fx=[{"type": "scatter", "n": 370, "t0": 0.0}])],
 174: [b("bahnhof_tafel", "Tafel klappt 1 – 2 – 3", ZW, inh=("zahl",), neu="antwort:dreidinge", fx=[T("1", "2", "3")])],
 175: [mo("phone", {"label": "ERSTENS", "app": "NOTRUF 112", "messages": [["Wo ist der Notfallort?", False], ["Straße, Hausnummer, Ort", True]]}, "Handy-Bildschirm: Wo ist der Notfallort? – Antwort mit Adresse", BW, inh=("erklaerung",))],
 176: [b("k_handy", "Handy am Boden: der Anruf läuft weiter, Einblendung nicht auflegen", LW, inh=("erklaerung",), fx=[SCR(SC + "call.png", "k_phone"), LB("nicht auflegen", None, None, 0.1)])],
 177: [mo("flow", {"label": "ZWEITENS", "nodes": [{"icon": "phone", "label": "112"}, {"icon": "phone", "label": "noch einmal"}, {"icon": "phone", "label": "anderes Telefon"}], "packet": "phone"}, "Ablauf-Kette: 112 → noch einmal → anderes Telefon", AK2, gen="schema", inh=("erklaerung",))],
 178: [b("wache", "Die helle Wache als Anlaufstelle, Menschen davor", MR, A={"wache_licht": 1, "people_w": 1})],
 179: [cl("px86507.mp4", "Echter Clip: Hände drücken fest auf die Brustmitte einer Übungspuppe", 8.0, inh=("erklaerung",), fx=[LB("Drittens: drücken", None, None, 0.1)])],
 180: [b("k_total", "Die Frau drückt in der Mitte der Brust, Einblendung fest und schnell", MR, inh=("erklaerung",), A={"press": 1}, fx=[LB("fest und schnell · Mitte der Brust", None, None, 0.1)])],
 181: [b("ls_innen", "Leitstelle, der Disponent zählt mit", SZ)],
 182: [b("k_handy", "Das Handy vom Anfang, 112 auf dem Bildschirm", BW, fx=[SCR(SC + "call.png", "k_phone")])],
 183: [b("stadt_total", "Kamera steigt auf: Wache, Leitstelle, Funkmast – das ganze System", TF, gen="schema", inh=("erklaerung",), fx=[RTWDOTS, {"type": "dots", "path": "funk_weg", "n": 4, "speed": 0.05, "r": 6}])],
 184: [b("haus_aussen", "Dein Haus leuchtet auf: das erste Glied bist du", DH, B={"mine": 2.2}, trans="fade", fx=[LB("du", "haus", None, 0.3)])],
 185: [b("bahnhof_tafel", "Die Fallblatt-Tafel am Bahnhof klappt auf 112?", ZW, inh=("zahl",), fx=[T("112?")])],
 186: [b("rathaus_uhr", "Uhr dreht sich: wie lange?", CD, inh=("zeit",), fx=[CLK(0, 30)])],
 187: [b("leitstelle_aussen", "Leitstelle bei Nacht, Einblendung Schreib's in die Kommentare", LW, inh=("erklaerung",), fx=[LB("Schreib's in die Kommentare", "leitstelle")])],
 188: [b("stadt_total", "Kamera zieht weit zurück über die nächtliche Modellstadt", TF, gen="schema", inh=("ort",), fx=[RTWDOTS])],
 189: [b("k_handy", "Das Handy vom Anfang liegt dunkel am Boden – Abspann UNTERBAU", RF, gen="schema", inh=("erklaerung",), A={"phone": 0}, fx=[{"type": "card", "title": "UNTERBAU", "sub": "Verstehen, wie die Welt funktioniert", "fade": True}])],
}
Z.update({0: "Eine Frau wählt 112.", 1: "04:12 Uhr, eine Novembernacht in Kassel.", 6: "Ohne Wiederbelebung sinkt seine Chance mit jeder Minute um etwa 10 Prozent.",
          12: "Dahinter stehen 240 Leitstellen, 16 Gesetze und ein Netz.", 21: "Davon gibt es in Deutschland rund 240.", 23: "Über 30 Millionen Notrufe pro Jahr.",
          25: "In Berlin alle 28 Sekunden.", 26: "Ohne SIM-Karte seit 2009 nicht mehr.", 39: "In 8 von 10 Fällen auf 30 Meter genau.", 55: "3. Mai 1969.",
          61: "Fast eine Stunde vergeht.", 67: "1973 vor Gericht.", 70: "Am 20. September 1973.", 73: "Ende 1979.", 74: "1991 zieht Europa nach.", 75: "1991: 112 in jedem Mitgliedsland.",
          88: "In 9 von 10 Fällen nach 10 Minuten.", 90: "8 Minuten in der Stadt und 12 auf dem Land.", 91: "In Bayern 12 Minuten.", 93: "2023 kippte ein Gericht eine Frist.",
          94: "12 Minuten, in 95 von 100 Fällen.", 103: "mehrere 100 Euro.", 104: "1020 Euro.", 109: "Seit 2018 automatisch.", 111: "Im Oktober 2026 Notfallreform.",
          112: "Im November 2026.", 115: "Seit 5 Minuten.", 118: "2010: 14 Prozent, heute gut die Hälfte.", 125: "11. November 2021.", 126: "4:30 Uhr.", 127: "04:12 Uhr – fast dieselbe Stunde.",
          133: "Mehr als 1 Stunde gestört.", 134: "5:40 Uhr.", 138: "Am 2. Juni 2021.", 142: "Am 25. Juni 2023 rund 14.000 Anrufversuche.", 143: "17,5 Millionen Pfund.",
          145: "14. Juli 2021.", 160: "4:21 Uhr.", 162: "9 Minuten nach dem Anruf.", 169: "136.000 Mal im Jahr.", 170: "370 Menschen am Tag.", 171: "jeder Zehnte, 10 Prozent."})

# ------------------------------------------------------------------ Zeiten
parts = {}
for i, (k, s, e, t) in enumerate(S): parts.setdefault(k, []).append(i)
dur = {}
for k, ids in parts.items():
    for j, i in enumerate(ids):
        dur[i] = (S[ids[j + 1]][1] - S[i][1]) if j + 1 < len(ids) else (S[i][2] - S[i][1] + 0.6)
order = []   # (key, sek, satz)
CARDS = {2: ("T", 4.6), 3: ("K2", 4.5), 4: ("K3", 4.5), 5: ("K4", 4.5), 6: ("K5", 4.5)}
for k in sorted(parts):
    if k == 2: order.append(("T", 4.6, "Titelkarte")); order.append(("K1", 4.5, "Kapitel 1"))
    elif k in CARDS: order.append((CARDS[k][0], CARDS[k][1], f"Kapitel {k - 1}"))
    for i in parts[k]: order.append((i, dur[i], S[i][3]))
order[-1] = (order[-1][0], order[-1][1] + 1.6, order[-1][2])   # Schlussbild steht nach

# merge: Satz ohne eigene Einstellung verlängert den vorigen
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
    if len(lst) == 1 and sek > MAXS and isinstance(key, int):     # lange Sätze: gleiche Einstellung als zweites Bild-Ereignis fortsetzen
        k2 = max(2, int(sek / MAXS + 0.999)); lst = [dict(lst[0], cont=c) for c in range(k2)]
    share = sek / len(lst)
    for e in lst:
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
                L = sek if c == 0 else sek
                mk = MO.clip(e["comp"], e["props"], len=round(max(L, 2.0) + 0.3, 2)); video = os.path.join(WORK, "motion", mk + ".mp4"); ss = c * share
            else:
                video = e["video"]; ss = e["ss"] + c * share
            plan.append({"id": sid, "video": video, "ss": round(ss, 3), "kind": "clip" if e["k"] == "cl" else "mo", "dur": round(share, 3), "fx": e.get("fx", []) if c == 0 else [],
                         "anim": e["anim"], "i": key if isinstance(key, int) else -1, "keys": keys, "set": e["k"] + ":" + os.path.basename(video)})
        t += share

# gleiche Szene hintereinander = eine durchgehende Fahrt (keine Sprung-Schnitte); sonst leichte Variation, damit kein Bild doppelt ist
bi = [k for k, p in enumerate(plan) if "video" not in p]
sh_by = {s["id"]: s for s in shots}
k = 0
while k < len(plan):
    if "video" in plan[k]: k += 1; continue
    j = k
    while j + 1 < len(plan) and "video" not in plan[j + 1] and plan[j + 1]["set"] == plan[k]["set"]: j += 1
    s0 = sh_by[plan[k]["id"]]
    if s0["set"] not in ("k_handy", "k_uhr", "ls_mon_nah", "querschnitt_stadt"):
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
