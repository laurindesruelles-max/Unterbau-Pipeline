"""Aus bilddrehbuch.json die Render-Liste (shots.json, engine/stadt.py) und den Compositing-Plan (plan.json, engine/stadtcomp.py).
python3 plan_003.py bilddrehbuch.json OUTDIR [--max-i N]
Kamera je Schauplatz (SETS) + kleine Variation je Einstellung, damit kein Bild zweimal vorkommt."""
import json, sys, os, hashlib, argparse

SETS = {   # loc, tgt, lens, A-Zustand, Anker
 "haus_kueche":      ((-12.9, -10.6, 0.8), (-12.1, -8.7, 0.6), 42, {"mine": 1}, ["haus"]),
 "haus_nacht":       ((-13.6, -11.2, 1.3), (-12.0, -8.6, 0.8), 40, {"mine": 1, "lights": 0.6}, ["haus"]),
 "haus_aussen":      ((-15.0, -13.5, 2.4), (-12.0, -8.2, 0.6), 38, {"mine": 1}, ["haus"]),
 "haus_vorrat":      ((299.3, -1.0, 1.4), (299.0, 2.2, 0.9), 26, {"vorrat": 0.15, "wasser": 0}, ["hv_regal"]),
 "haus_wasser":      ((301.3, -0.6, 1.0), (300.9, 1.4, 0.3), 30, {"vorrat": 1, "wasser": 4}, []),
 "kuehlschrank":     ((299.2, -1.4, 1.5), (300.0, 2.0, 0.95), 28, {"door": 0}, []),
 "markt_regal_voll": ((200.15, -5.8, 1.35), (201.0, 1.4, 0.7), 30, {"fill": 1, "gap": 0}, ["milchfach"]),
 "markt_regal_halb": ((199.8, -5.5, 1.3), (200.9, 1.0, 0.8), 30, {"fill": 0.55, "gap": 1}, ["milchfach"]),
 "markt_regal_leer": ((200.2, -5.6, 1.4), (199.0, 1.0, 0.8), 30, {"fill": 0.12, "gap": 1}, []),
 "markt_gang":       ((200.0, -6.2, 1.6), (200.0, 2.0, 1.0), 26, {"fill": 0.7, "gap": 1}, []),
 "markt_gang_leer":  ((200.0, -6.0, 1.2), (200.0, 3.0, 1.1), 24, {"fill": 0.03, "gap": 1}, []),
 "markt_kuehl_leer": ((200.5, -3.0, 1.0), (201.1, 0.5, 0.7), 32, {"fill": 0.0, "gap": 1}, []),
 "markt_brot":       ((199.6, -2.0, 1.25), (199.0, 1.5, 1.0), 34, {"fill": 0.7}, []),
 "markt_obst":       ((199.9, -1.5, 1.45), (201.0, 2.0, 0.6), 32, {"fill": 0.4}, []),
 "markt_milch":      ((200.3, -1.4, 1.05), (201.0, 1.6, 0.75), 35, {"fill": 0.8, "gap": 1}, ["milchfach"]),
 "markt_mehl":       ((199.7, 0.5, 1.0), (199.0, 3.5, 0.6), 34, {"fill": 0.15}, []),
 "es_regal":         ((200.4, 1.0, 1.1), (201.1, 4.0, 0.7), 34, {"fill": 0.9}, []),
 "markt_querschnitt":((1300, -7, 2.5), (1300, 0.4, 0.9), 35, {}, ["mc_lager"]),
 "markt_aussen":     ((3.2, -14.5, 2.6), (0, -9, 0.5), 38, {"people": 1}, ["markt"]),
 "markt_rampe":      ((3.6, -3.6, 1.3), (0.8, -6.6, 0.4), 38, {"door": 0}, ["rampe"]),
 "stadt_total":      ((-4, -30, 16), (0, -1, 0), 40, {"lights": 1, "lkw": 0}, ["route_autobahn", "haus", "tafel", "uhr", "markt"]),
 "stadt_morgen":     ((6, -30, 14), (0, 0, 0), 40, {"lights": 0.4, "day": 0.75, "lkw": 0}, ["route_autobahn"]),
 "autobahn_nacht":   ((-14, -24, 3.0), (-4, -16, 0), 35, {"lkw": 0}, ["route_autobahn"]),
 "autobahn_morgen":  ((10, -21, 2.5), (0, -16, 0), 35, {"day": 0.8, "lkw": 0}, ["route_autobahn"]),
 "autobahn_sonntag": ((-30, 4, 3), (-28, -6, 0), 35, {"day": 0.6, "lkw": 0}, ["route_autobahn"]),
 "uk_strasse":       ((24, -21, 2.0), (28, -12, 0.2), 35, {"lkw": 1}, ["route_autobahn"]),
 "molkerei":         ((-18.6, 4.2, 2.3), (-22.5, 9.5, 0.6), 38, {}, ["molkerei"]),
 "es_molkerei":      ((-26.5, 4.5, 1.6), (-22.5, 9.5, 0.8), 34, {"lights": 0.7}, ["molkerei"]),
 "route_lager":      ((-8, -8, 14), (2, 9, 0), 38, {"lkw": 0}, ["route_autobahn"]),
 "route_markt":      ((-7, -17, 5), (0, -7, 0), 38, {"lkw": 0}, ["route_autobahn", "markt"]),
 "zentrallager_innen":((698.5, -6.5, 2.0), (698.5, 4, 1.4), 28, {"rfill": 1}, ["zlager_zaehler"]),
 "zentrallager_kuehl":((758.5, -6.5, 1.8), (758.5, 4, 1.4), 28, {"rfill": 1}, ["kuehl_zaehler"]),
 "notreserve_innen": ((818.5, -6.5, 2.2), (818.5, 4, 1.2), 28, {"rfill": 1}, ["reserve_zaehler"]),
 "apotheke_innen":   ((878.5, -6.0, 1.6), (878.5, 2, 1.2), 30, {"rfill": 1}, ["apo_zaehler"]),
 "klinik":           ((14.5, 2.5, 2.4), (12, 6.8, 0.8), 38, {}, []),
 "klinik_regal":     ((938.5, -6.0, 1.6), (938.5, 2, 1.2), 30, {"rfill": 1}, ["klinik_zaehler"]),
 "rathaus_uhr":      ((0.6, 4.0, 1.4), (0, 7.5, 2.0), 50, {}, ["uhr"]),
 "bahnhof_tafel":    ((-7.4, 4.4, 1.25), (-8, 7.1, 1.25), 42, {}, ["tafel"]),
 "kalender":         ((-8.8, 4.2, 1.5), (-8, 7.1, 1.25), 40, {}, ["tafel"]),
 "notreserve_aussen":((-17.5, -19.5, 3.2), (-22, -11.5, 0.5), 40, {"lights": 0.3}, ["notreserve"]),
 "notreserve_strasse":((-24, -16.5, 3.5), (-14, -8, 0), 36, {"lights": 0.5, "lkw": 0}, ["route_autobahn", "haus"]),
 "querschnitt_stadt":((397, -8, 0.8), (400, 0, -0.4), 40, {"cut": 0}, ["cut"]),
 "wasserwerk":       ((-32.5, -13, 4), (-37, -5, 0), 38, {}, []),
 "wasserwerk_quer":  ((403, -7.5, 0.4), (400, 0, -0.6), 40, {"cut": 1}, ["cut"]),
 "apotheke_aussen":  ((10.5, -13.5, 1.9), (8, -8.8, 0.5), 38, {}, []),
 "apotheke_route":   ((4, -17, 7), (8, -8, 0), 38, {"lkw": 0}, ["route_autobahn"]),
 "tankstelle_nacht": ((15.5, -12.5, 1.9), (12, -8, 0.4), 38, {"tape": 0}, ["tankstelle"]),
 "tankstelle_tag":   ((9, -12.8, 1.6), (12, -8, 0.35), 38, {"tape": 1, "day": 0.7}, ["tankstelle"]),
 "tanklager":        ((18, -17.5, 4), (23.6, -11.2, 0.5), 38, {}, []),
 "tanklager_strasse":((10, -22, 8), (17, -10, 0), 38, {"lkw": 0}, ["route_autobahn"]),
 "strasse_muell":    ((-9.4, -11.2, 1.0), (-10.6, -9.1, 0.15), 38, {"muell": 1}, []),
 "geldautomat":      ((2.4, -11.6, 0.9), (1.3, -9.3, 0.35), 35, {}, ["atm"]),
 "fahrerkabine":     ((1100.15, -1.0, 1.4), (1099.7, 1.5, 0.95), 24, {}, ["cab_strasse"]),
 "uk_fahrer":        ((1101.0, -0.6, 1.5), (1099.8, 1.2, 0.9), 26, {"driver": 0}, []),
 "steuerzentrale":   ((1200, -2.5, 1.7), (1200, 2.5, 1.6), 24, {}, ["screen_l", "screen_c", "screen_r"]),
 "uk_raffinerie":    ((1199.2, -1.2, 1.7), (1200, 2.5, 1.7), 28, {}, ["screen_c"]),
 "uk_markt":         ((1199.0, -1.3, 1.6), (1200, 2.5, 1.7), 28, {}, ["screen_c"]),
 "uk_regal":         ((1201.0, -1.2, 1.7), (1200, 2.5, 1.7), 28, {}, ["screen_c"]),
 "uk_armee":         ((1200.6, -1.4, 1.8), (1200, 2.5, 1.7), 28, {}, ["screen_c"]),
 "es_streik":        ((1199.4, -1.5, 1.6), (1200, 2.5, 1.7), 28, {}, ["screen_c"]),
 "was_waere":        ((1400, -13, 6), (1400, 0, 1.5), 35, {"bars": [[9, True], [8, True], [6, True], [5, True]]}, []),
 "balken_tonnen":    ((1400, -14, 7), (1400, 0, 1.8), 35, {"bars": [[1, True], [1, False]]}, []),
 "balken_uk":        ((1401, -14, 7), (1400, 0, 1.8), 35, {"bars": [[4, False], [4, True]]}, []),
 "balken_mehl":      ((1399, -14, 7), (1400, 0, 1.8), 35, {"bars": [[3, False], [1, True]]}, []),
 "balken_handel":    ((1400, -16, 9), (1400, -10, 0), 35, {"pct": 0}, []),
 "balken_fahrer":    ((1400.5, -16, 9), (1400, -10, 0), 35, {"pct": 0}, []),
 "eiffel":           ((1392, 1, 6), (1401, 12, 1), 35, {"eiffel": 0}, []),
 "tage_skala":       ((1400, 1.5, 6), (1400, 8, 0), 38, {}, ["tag1", "tag2", "tag3", "tag4", "tag5"]),
 "karte_de":         ((0, 178, 18), (0, 200, 0), 45, {}, ["de_staedte", "de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"]),
 "karte_tankstellen":((2, 182, 14), (0, 200, 0), 45, {}, ["de_staedte", "de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"]),
 "karte_reserve":    ((-2, 183, 15), (0, 200, 0), 45, {}, ["de_staedte"]),
 "karte_hessen":     ((-2.5, 191, 6), (-1.7, 198.2, 0), 40, {}, ["de_staedte", "de_KF", "de_FN", "de_FS"]),
 "uk_karte":         ((-12, 192, 11), (-12.4, 203, 0), 40, {}, []),
 "uk_tankstellen":   ((-11, 195, 8), (-12.4, 203, 0), 40, {}, []),
 "es_karte":         ((-13, 172, 11), (-14.4, 182, 0), 40, {}, []),
 "rastplatz":        ((29, -7, 3.5), (34, 2, 0), 35, {"people": 0}, ["rastplatz"]),
 "rastplatz_sommer": ((38.5, -6.5, 3.0), (34, 2, 0), 35, {"people": 1, "day": 0.8}, ["rastplatz"]),
 "lkw_ladung":       ((1502.5, -2.5, 1.4), (1500, 0.3, 0.7), 30, {}, ["ld_milch"]),
}
IMG = "/home/claude/unterbau-work/img/"
# Welche Einstellung (Drehbuch-Index i, k-te Einstellung im Satz) bekommt was: set-Override, B-Zustand, Übergang, Bewegung, Effekte
SPEC = {
 (0, 0): dict(B={"mine": 1.8}, trans="fade", move="push", fx=[{"type": "label", "text": "Dein Haus", "anchor": "haus", "t0": 0.1}]),
 (1, 0): dict(B={"door": 1}, trans="wipe_lr", t_trans=[0.05, 0.6], move="push"),
 (2, 0): dict(B={"gap": 1}, trans="diff", t_trans=[0.3, 0.7], move="push", cam=((200.3, -1.4, 1.05), (201.0, 1.6, 0.75), 35), fx=[{"type": "frame", "anchor": "milchfach", "t0": 0.6}]),
 (3, 0): dict(move="flight"),
 (4, 0): dict(move="pan", A={"lkw": 0}, cam=((-2, -20.5, 1.6), (6, -16, 0.2), 40), fx=[{"type": "dots", "path": "route_autobahn", "n": 160, "speed": 0.012, "r": 6}]),
 (5, 0): dict(move="push", A={"lkw": 0}, fx=[{"type": "dots", "path": "route_autobahn", "n": 160, "speed": 0.01, "r": 5}]),
 (6, 0): dict(A={"lkw": 0}, move="still", cam=((-10, -27, 12), (-2, -6, 0), 40),
              fx=[{"type": "dots", "path": "route_autobahn", "n": 160, "speed": 0.01, "stop": 0.3, "r": 5}]),
 (7, 0): dict(A={"lights": 1, "trucks": 0}, B={"lights": 0.06, "mine": 0}, trans="lights", t_trans=[0.05, 0.9], move="push", cam=((-17, -23, 8), (-9, -7, 0), 40)),
 (8, 0): dict(move="pull", fx=[{"type": "lines", "pairs": ["de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"], "cities": "de_staedte", "fade": [0.1, 0.7]}]),
 (9, 0): dict(move="push", cam=((200.0, -5.6, 1.45), (200.5, 1.0, 0.9), 30), fx=[{"type": "label", "text": "Stunde 0", "pos": (800, 90), "t0": 0.3, "sub": "Kein Lkw fährt"}]),
 (10, 0): dict(B={"fill": 0.07}, trans="rows", t_trans=[0.05, 0.95], move="still", cam=((200.1, -4.5, 1.2), (201.1, -0.5, 0.8), 32)),
 (11, 0): dict(move="push", fx=[{"type": "clock", "anchor": "uhr", "from": 0, "to": 12 * 60, "t0": 0.1, "tl": 0.85}]),
 (12, 0): dict(set="bahnhof_tafel", move="still", fx=[{"type": "tafel", "anchor": "tafel", "texts": ["TAG 1", "TAG 2", "TAG 3"]}]),
 (13, 0): dict(move="push", fx=[{"type": "flicker"}]),
 (14, 0): dict(set="bahnhof_tafel", move="push", cam=((-9.2, 4.7, 1.0), (-8, 7.1, 1.25), 38), fx=[{"type": "tafel", "anchor": "tafel", "texts": ["GEDANKEN-", "GEDANKENEXPERIMENT"], "rate": 1.0}]),
 (15, 0): dict(B={"cut": 1}, trans="wipe_down", t_trans=[0.15, 0.7], move="push"),
}

L = ["de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"]
def T(*texts, **kw): return {"type": "tafel", "anchor": kw.get("anchor", "tafel"), "texts": list(texts), **{k: v for k, v in kw.items() if k != "anchor"}}
def LB(text, anchor=None, sub=None, t0=0.15): d = {"type": "label", "text": text, "t0": t0}; d.update({"anchor": anchor} if anchor else {"pos": (800, 90)}); d.update({"sub": sub} if sub else {}); return d
def SCR(n, anchor="screen_c"): return {"type": "screen", "anchor": anchor, "img": IMG + f"{n}.png"}
DOTS = lambda **kw: {"type": "dots", "path": "route_autobahn", "n": 160, "speed": 0.01, "r": 5, **kw}
SPEC.update({
 (16, 0): dict(move="flight"), (17, 0): dict(fx=[LB("Deine Palette", "molkerei")]),
 (18, 0): dict(fx=[LB("22:00 Uhr", "molkerei", "Molkerei")]),
 (19, 0): dict(fx=[{"type": "lines", "pairs": [], "grow": 0.9}, DOTS(n=60)]),
 (20, 0): dict(B={"rfill": 1}, A={"rfill": 0.5}, trans="rows"), (20, 1): dict(fx=[T("FILIALE 0417", anchor="zlager_zaehler")]),
 (21, 0): dict(fx=[DOTS(n=80), LB("04:30 Uhr", None, "vor Sonnenaufgang")]), (21, 1): dict(B={"door": 1}, trans="wipe_down"),
 (22, 0): dict(move="pull", fx=[{"type": "lines", "pairs": L, "cities": "de_staedte", "grow": 0.6}]),
 (23, 0): dict(fx=[{"type": "lines", "pairs": L, "cities": "de_staedte"}]),
 (24, 0): dict(B={"bars": [[8, True], [2, False]]}, trans="rows", fx=[LB("4 von 5 Tonnen", None, "fahren auf dem Lkw", 0.5)]),
 (25, 0): dict(B={"eiffel": 36}, trans="rows", fx=[LB("900 Eiffeltürme", None, "an Ware – jeden Tag", 0.45)]),
 (27, 0): dict(fx=[{"type": "frame", "anchor": "mc_lager", "t0": 0.35}, LB("Lager", "mc_lager", None, 0.4)]),
 (28, 0): dict(fx=[SCR("05")]), (29, 0): dict(move="pan"),
 (30, 0): dict(fx=[{"type": "frame", "anchor": "milchfach", "t0": 0.3}]),
 (31, 0): dict(fx=[DOTS(n=200, speed=0.012)]), (32, 0): dict(B={"rfill": 0.55}, trans="rows"),
 (33, 0): dict(fx=[T("4 TAGE", anchor="zlager_zaehler")]), (34, 0): dict(fx=[T("5 TAGE", anchor="kuehl_zaehler")]),
 (35, 0): dict(fx=[DOTS()]), (36, 0): dict(fx=[DOTS(n=120)]),
 (37, 0): dict(fx=[DOTS(n=120, stop=0.15)]),
 (38, 0): dict(fx=[{"type": "clock", "anchor": "uhr", "from": 270, "to": 300, "t0": 0.05, "tl": 0.5}]),
 (39, 0): dict(B={"door": 1}, trans="wipe_down", t_trans=[0.05, 0.6]), (40, 0): dict(move="still", A={"door": 1}),
 (41, 0): dict(A={"day": 0.3}, fx=[{"type": "clock", "anchor": "uhr", "from": 300, "to": 420, "t0": 0.05, "tl": 0.6}]),
 (42, 0): dict(A={"day": 0.3, "people": 0}, B={"people": 1}, trans="diff"), (43, 0): dict(),
 (44, 0): dict(set="bahnhof_tafel", A={"day": 0.15}, fx=[T("TAG 1", "TAG 1 · 18:00")]),
 (45, 0): dict(A={"day": 0.15}, fx=[LB("Du", "markt")]),
 (46, 0): dict(move="pan"), (47, 0): dict(B={"fill": 0.35}, trans="rows"), (48, 0): dict(B={"fill": 0.15}, trans="rows"),
 (49, 0): dict(fx=[{"type": "frame", "anchor": "milchfach", "t0": 0.2}]),
 (51, 0): dict(move="pull", fx=[{"type": "grey", "amount": 0.7, "t0": 0.2}]),
 (52, 0): dict(move="flight", fx=[{"type": "grey", "amount": 0.5, "t0": 0}]), (53, 0): dict(set="kalender", fx=[T("GB", "SEPT. 2000")]),
 (54, 0): dict(fx=[SCR(20)]), (54, 1): dict(set="uk_strasse", B={"trucks": 0}, trans="diff"),
 (55, 0): dict(B={"trucks": 0}, trans="lights"),
 (56, 0): dict(B={"lights": 0.2}, trans="lights", fx=[LB("3 von 4 Tankstellen", None, "ohne Sprit", 0.4)]),
 (57, 0): dict(fx=[SCR(22)]), (58, 0): dict(set="markt_aussen", A={"people": 1}),
 (59, 0): dict(B={"bars": [[4, False], [6, True]]}, trans="rows", fx=[LB("+50 %", None, "in 2 Tagen", 0.5)]),
 (60, 0): dict(set="markt_aussen", A={"people": 1}, fx=[{"type": "flicker"}]),
 (61, 0): dict(fx=[SCR(23)]), (62, 0): dict(set="markt_regal_halb", fx=[LB("Max. 1 pro Kunde", "milchfach", None, 0.2)]),
 (63, 0): dict(fx=[T("07.09.", "08.09.", "10.09.", "12.09.", "14.09.")]), (64, 0): dict(fx=[T("07.09.–14.09.2000")]),
 (65, 0): dict(set="bahnhof_tafel", fx=[T("7 TAGE")]), (66, 0): dict(fx=[{"type": "grey", "amount": 0.5, "t0": 0}]),
 (67, 0): dict(move="flight"), (70, 0): dict(set="markt_aussen", A={"people": 1}),
 (71, 0): dict(B={"fill": 0.1}, trans="rows", t_trans=[0.0, 0.7]),
 (72, 0): dict(move="flight"), (73, 0): dict(), (74, 0): dict(fx=[DOTS(n=60), LB("08:00 · 12:00 · 16:00", None, "Lieferungen am Tag")]),
 (75, 0): dict(fx=[DOTS(n=60, stop=0.2)]), (76, 0): dict(fx=[{"type": "flicker"}]), (77, 0): dict(fx=[SCR(14)]),
 (78, 0): dict(set="klinik_regal", fx=[T("STUNDE 1", "STUNDE 4", "STUNDE 8", anchor="klinik_zaehler")]),
 (79, 0): dict(set="klinik_regal", B={"rfill": 0.15}, trans="rows"),
 (80, 0): dict(B={"mine": 0}, trans="fade", t_trans=[0.5, 0.8]), (81, 0): dict(move="flight"),
 (82, 0): dict(set="bahnhof_tafel", A={"day": 0.4}, fx=[T("TAG 2", "TAG 2 · 07:00")]),
 (83, 0): dict(A={"tape": 0, "day": 0.7}, B={"tape": 1}, trans="wipe_lr"),
 (84, 0): dict(fx=[{"type": "lines", "pairs": L, "cities": "de_staedte", "grow": 0.8}, LB("14.000 Tankstellen", None, None, 0.3)]),
 (85, 0): dict(fx=[{"type": "lines", "pairs": L, "cities": "de_staedte"}]),
 (86, 0): dict(move="flight"), (87, 0): dict(fx=[LB("90 Tage", None, "Erdöl und Kraftstoffe", 0.4)]),
 (89, 0): dict(set="wasserwerk_quer", fx=[{"type": "dots", "path": "cut", "n": 20, "speed": 0.04, "r": 6}]),
 (90, 0): dict(move="pull"), (91, 0): dict(fx=[DOTS(n=8, speed=0.02, r=7)]),
 (92, 0): dict(fx=[DOTS(n=8, speed=0.02, r=7, stop=0.25)]),
 (93, 0): dict(fx=[SCR(14)]), (94, 0): dict(A={"muell": 0}, B={"muell": 1}, trans="diff"),
 (95, 0): dict(B={"atm_off": 1}, trans="fade", t_trans=[0.3, 0.5]),
 (96, 0): dict(A={"driver": 0}, move="push"), (97, 0): dict(),
 (98, 0): dict(A={"pct": 0}, B={"pct": 85}, trans="rows"), (98, 1): dict(set="balken_handel", A={"pct": 85}, fx=[LB("85 %", None, "der Ware kaufen 4 Gruppen ein", 0.1)]),
 (99, 0): dict(set="was_waere", fx=[LB("Edeka · Rewe · Schwarz-Gruppe · Aldi", None, None, 0.1)]),
 (100, 0): dict(set="fahrerkabine", A={"driver": 1}), (101, 0): dict(),
 (102, 0): dict(A={"pct": 0}, B={"pct": 40}, trans="rows", fx=[LB("2 von 5 Fahrern", None, "55 Jahre oder älter", 0.4)]),
 (103, 0): dict(set="uk_fahrer", fx=[LB("70.000", None, "Fahrer fehlen (Schätzung)", 0.3)]),
 (104, 0): dict(fx=[{"type": "lines", "pairs": ["de_KF", "de_FN", "de_FS"], "cities": "de_staedte"}, LB("Gräfenhausen", None, "Südhessen")]),
 (105, 0): dict(fx=[LB("Gräfenhausen · 2023", "rastplatz")]),
 (106, 0): dict(fx=[LB("über 60 Fahrer", "rastplatz", None, 0.3)]), (106, 1): dict(B={"people": 1}, trans="diff"),
 (107, 0): dict(A={"people": 1}), (108, 0): dict(A={"people": 1}, fx=[LB("fast 100.000 €", "rastplatz", "Forderung der Fahrer", 0.2)]),
 (109, 0): dict(A={"people": 1}, B={"people": 0, "day": 0.5}, trans="fade", fx=[LB("5 Wochen", None, None, 0.1)]),
 (110, 0): dict(A={"people": 0}), (110, 1): dict(),
 (111, 0): dict(fx=[LB("rund 80", "rastplatz", None, 0.2)]), (112, 0): dict(fx=[LB("etwa 30", "rastplatz", "im Hungerstreik", 0.2)]),
 (113, 0): dict(move="pull"), (114, 0): dict(move="flight"), (116, 0): dict(fx=[LB("Deine Palette", "molkerei")]),
 (117, 0): dict(B={"lights": 0.1}, trans="lights", fx=[LB("abgelaufen", "molkerei", None, 0.5)]),
 (118, 0): dict(set="bahnhof_tafel", A={"day": 0.6}, fx=[T("TAG 3", "TAG 3 · 10:00")]),
 (119, 0): dict(A={"day": 0.6, "people": 0}), (120, 0): dict(move="pan"), (121, 0): dict(B={"fill": 0.0}, trans="rows"),
 (122, 0): dict(move="push"), (123, 0): dict(fx=[{"type": "flicker"}]),
 (124, 0): dict(A={"day": 0.6}, fx=[{"type": "grey", "amount": 0.6}]), (125, 0): dict(fx=[{"type": "grey", "amount": 0.7}]),
 (126, 0): dict(fx=[{"type": "flicker"}]), (127, 0): dict(fx=[SCR("01")]), (127, 1): dict(fx=[LB("andere Ursache: Stromausfall", None, None, 0.1)]),
 (128, 0): dict(fx=[{"type": "flicker"}]),
 (129, 0): dict(fx=[{"type": "hl", "anchors": ["tag2", "tag3", "tag4", "tag5"], "t0": 0.2}, LB("2 bis 5 Tage", None, "Studie für den Bundestag", 0.3)]),
 (130, 0): dict(fx=[{"type": "hl", "anchors": ["tag1"], "t0": 0.1}, LB("Tag 1: knapp", None, "US-Szenario", 0.2)]),
 (130, 1): dict(fx=[{"type": "hl", "anchors": ["tag2", "tag3"], "t0": 0.1}, LB("Tag 2–3: Hamsterkäufe", None, None, 0.2)]),
 (131, 0): dict(fx=[{"type": "hl", "anchors": ["tag2", "tag3"], "t0": 0}]),
 (132, 0): dict(fx=[{"type": "hl", "anchors": ["tag3"], "t0": 0.05}, LB("rund 3 Tage", None, None, 0.3)]),
 (133, 0): dict(move="flight", fx=[{"type": "grey", "amount": 0.6, "t0": 0}]),
 (135, 0): dict(set="notreserve_innen", A={"rfill": 1}, fx=[{"type": "fadein"}]),
 (137, 0): dict(fx=[LB("Reis · Erbsen · Linsen · Kondensmilch", None, None, 0.1)]), (138, 0): dict(fx=[LB("+ Getreide", None, None, 0.1)]),
 (139, 0): dict(fx=[{"type": "scatter", "n": 150, "t0": 0.1}, LB("über 150 Lager", None, "Standorte geheim", 0.4)]),
 (140, 0): dict(fx=[{"type": "scatter", "n": 150, "fade": 0.3}]),
 (141, 0): dict(fx=[LB("1 Mahlzeit am Tag", None, None, 0.2)]),
 (142, 0): dict(set="karte_de", fx=[{"type": "lines", "pairs": [], "cities": "de_staedte"}]),
 (143, 0): dict(B={"mine": 2.2}, trans="fade", fx=[LB("Du?", "haus")]),
 (144, 0): dict(B={"rfill": 0.2}, trans="rows", t_trans=[0.0, 0.9]), (145, 0): dict(),
 (146, 0): dict(fx=[{"type": "lines", "pairs": [], "grow": 0.5}, LB("Lager → du", None, None, 0.3)]),
 (147, 0): dict(fx=[SCR(46)]), (148, 0): dict(fx=[LB("kein Gleisanschluss", "notreserve", None, 0.2)]),
 (149, 0): dict(fx=[DOTS(n=30)]), (150, 0): dict(fx=[DOTS(n=40)]), (150, 1): dict(fx=[DOTS(n=40, stop=0.6)]),
 (151, 0): dict(set="uk_fahrer"), (152, 0): dict(set="notreserve_innen", move="pull"),
 (153, 0): dict(B={"lights": 0.15}, trans="lights", fx=[LB("Nur der Weg fehlt", None, None, 0.4)]),
 (154, 0): dict(move="flight"), (155, 0): dict(fx=[{"type": "dots", "path": "cut", "n": 20, "speed": 0.04, "r": 6, "stop": 0.5}, LB("Woche 2", None, None, 0.2)]),
 (156, 0): dict(fx=[LB("Chemikalien fehlen", None, "Wasseraufbereitung", 0.3)]),
 (157, 0): dict(A={"day": 0.0, "lights": 0.4}, B={"day": 0.75, "lights": 0.4}, trans="fade", fx=[DOTS(n=160)]),
 (158, 0): dict(fx=[DOTS(n=160)]), (159, 0): dict(set="bahnhof_tafel", A={"day": 0.7}, fx=[T("GEDANKENEXPERIMENT")]),
 (160, 0): dict(fx=[DOTS(n=160)]), (160, 1): dict(fx=[{"type": "lines", "pairs": L, "cities": "de_staedte"}]),
 (161, 0): dict(fx=[{"type": "flicker"}]), (162, 0): dict(fx=[LB("seit 2017", None, "Gesetz für Versorgungskrisen", 0.1)]),
 (162, 1): dict(fx=[DOTS(n=40)]), (163, 0): dict(fx=[LB("Höchstmenge je Kunde", "milchfach", None, 0.2)]),
 (164, 0): dict(A={"lights": 1}, B={"lights": 0.15}, trans="wipe_lr", t_trans=[0.3, 0.55]),
 (165, 0): dict(A={"lights": 0.5}),
 (166, 0): dict(set="kalender", fx=[T("MÄRZ 2020")]), (167, 0): dict(),
 (168, 0): dict(B={"bars": [[3, False], [8, True]]}, trans="rows", fx=[LB("fast 3 × so viel Mehl", None, None, 0.5)]),
 (169, 0): dict(fx=[DOTS(n=160)]), (170, 0): dict(fx=[LB("Sonntagsfahrverbot ausgesetzt", None, "2020", 0.2)]), (170, 1): dict(fx=[DOTS(n=200)]),
 (171, 0): dict(fx=[LB("Großbritannien · Herbst 2021", None, None, 0.1)]), (171, 1): dict(fx=[LB("Zehntausende Fahrer fehlen", None, None, 0.2)]),
 (172, 0): dict(fx=[{"type": "scatter", "n": 60, "t0": 0}]), (172, 1): dict(fx=[{"type": "scatter", "n": 60, "fade": 0.2}]),
 (173, 0): dict(fx=[SCR(24)]), (174, 0): dict(set="uk_strasse", fx=[DOTS(n=30), LB("rund 100 Soldaten", None, "fahren Tanklaster", 0.2)]),
 (175, 0): dict(fx=[LB("Spanien · 2022", None, None, 0.1)]), (175, 1): dict(fx=[SCR(27), LB("rund 3 Wochen Streik", None, None, 0.4)]),
 (176, 0): dict(B={"lights": 0.15}, trans="lights"), (177, 0): dict(B={"fill": 0.1}, trans="rows"),
 (178, 0): dict(move="pull"), (179, 0): dict(A={"day": 0.7}),
 (180, 0): dict(A={"vorrat": 0.1}, B={"vorrat": 1}, trans="rows"),
 (181, 0): dict(A={"vorrat": 1}, fx=[T("10 TAGE", anchor="hv_regal")]), (182, 0): dict(A={"vorrat": 0.35}, fx=[T("3 TAGE", anchor="hv_regal")]),
 (183, 0): dict(fx=[{"type": "hl", "anchors": ["tag3"], "t0": 0}, LB("dein Markt: 3 Tage · dein Vorrat: 3 Tage", None, None, 0.2)]),
 (184, 0): dict(A={"wasser": 2}, fx=[LB("2 Liter", None, "pro Person und Tag", 0.2)]),
 (185, 0): dict(A={"wasser": 2}, B={"wasser": 20}, trans="rows", fx=[LB("20 Liter", None, "für 10 Tage", 0.5)]),
 (186, 0): dict(A={"wasser": 20}, fx=[LB("= 2 Putzeimer", None, None, 0.2)]),
 (187, 0): dict(A={"lights": 1}, fx=[DOTS(n=6, speed=0.02, r=7)]),
 (188, 0): dict(), (189, 0): dict(fx=[{"type": "frame", "anchor": "ld_milch", "t0": 0.1}, LB("Deine Milch", "ld_milch")]),
 (190, 0): dict(A={"driver": 1}), (191, 0): dict(A={"driver": 1}, move="pull"),
 (192, 0): dict(B={"door": 1}, trans="wipe_lr", t_trans=[0.1, 0.6]),
 (193, 0): dict(A={"vorrat": 0.5}, fx=[T("? TAGE", anchor="hv_regal")]),
 (194, 0): dict(fx=[LB("Schreib's in die Kommentare", "haus")]),
 (195, 0): dict(B={"cut": 1}, trans="wipe_down"), (196, 0): dict(fx=[{"type": "clock", "anchor": "uhr", "from": 1380, "to": 1440, "t0": 0, "tl": 0.8}]),
 (197, 0): dict(fx=[T("UNTERBAU")]),
})
SET_OVERRIDE = {"stadt_total": None}

DEFAULT = {   # Animation -> Standard-Spezifikation, wenn SPEC nichts sagt
 "Tilt-Shift-Flug": dict(move="flight"), "Rückflug zum Anfang": dict(move="pull"), "Leben in der Welt": dict(move="push"),
 "Menschen reagieren": dict(move="push", A={"people": 1}), "Warenstrom": dict(fx=[DOTS()]),
 "Lichter gehen aus": dict(B={"lights": 0.1}, trans="lights"), "Regale leeren sich": dict(B={"fill": 0.1}, trans="rows"),
 "Lagerbestand-Turm": dict(B={"rfill": 0.35}, trans="rows"), "Tag-Nacht-Zeitraffer": dict(B={"day": 0.8}, trans="fade"),
 "Querschnitt": dict(B={"cut": 1}, trans="wipe_down"), "Steuerzentrale": dict(fx=[{"type": "flicker"}]),
}

def jitter(sid, v, amt):
    h = int(hashlib.md5(sid.encode()).hexdigest()[:8], 16)
    return tuple(x + ((h >> (4 * i)) % 100 / 100 - 0.5) * amt for i, x in enumerate(v))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("drehbuch"); ap.add_argument("out"); ap.add_argument("--max-i", type=int, default=10**6)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    D = json.load(open(a.drehbuch)); shots, plan = [], []; seen = {}
    for n, e in enumerate(D):
        if e["i"] > a.max_i: break
        k = seen.get(e["i"], 0); seen[e["i"]] = k + 1
        sp = dict(DEFAULT.get(e["animation"], {})); sp.update(SPEC.get((e["i"], k), {})); st = sp.get("set", e["set"])
        if st in ("bahnhof_tafel", "kalender") and not any(f.get("type") == "tafel" for f in sp.get("fx", [])): pass
        if st not in SETS: print("FEHLT Set", st, "für", e["i"]); continue
        loc, tgt, lens, A, anc = SETS[st]
        if "cam" in sp: loc, tgt, lens = sp["cam"]
        sid = f"s{n:03d}"
        if "cam" not in sp: loc = jitter(sid, loc, 0.6)
        shots.append({"id": sid, "set": st, "cam": {"loc": list(loc), "tgt": list(tgt), "lens": lens}, "A": {**A, **sp.get("A", {})},
                      "B": sp.get("B"), "anchors": anc})
        if st == "steuerzentrale" and not any(f.get("type") == "screen" for f in sp.get("fx", [])):
            sp["fx"] = list(sp.get("fx", [])) + [dict(SCR("02"), anchor="screen_l"), dict(SCR(14), anchor="screen_c"), dict(SCR(26), anchor="screen_r")]
        tilt = abs(loc[0]) < 150 and abs(loc[1]) < 150 and loc[2] > 2.5     # Miniatur-Unschärfe nur bei Blicken von oben auf die Stadt
        plan.append({"id": sid, "tilt": tilt, "dur": e["sek"], "move": sp.get("move", "push"), "trans": sp.get("trans", "diff"),
                     "t_trans": sp.get("t_trans", [0.2, 0.8]), "fx": sp.get("fx", []), "anim": e["animation"], "i": e["i"]})
    # Folgen am selben Schauplatz = eine Kamera, eine durchgehende Fahrt (Laurin 22.11.2026: keine Sprung-Schnitte)
    i = 0
    while i < len(shots):
        j = i
        while j + 1 < len(shots) and shots[j + 1]["set"] == shots[i]["set"]: j += 1
        tot = sum(plan[k]["dur"] for k in range(i, j + 1)); acc = 0.0
        mv = plan[i]["move"] if plan[i]["move"] != "still" else "push"
        for k in range(i, j + 1):
            shots[k]["cam"] = shots[i]["cam"]
            plan[k].update(run_k=k - i, run_len=j - i + 1, run_move=mv, run_dir=1 if (i % 2) else -1,
                           run_u=[acc / tot, (acc + plan[k]["dur"]) / tot]); acc += plan[k]["dur"]
        i = j + 1
    # Gleicher Ort, aber anderer Schauplatz-Name (z. B. zwei Regal-Ansichten) oder Flug zwischen Stadtansichten: weich überblenden
    def ort(sh):
        x, y, z = sh["cam"]["loc"]
        if 150 < x < 260: return "gang"
        if 1380 < x < 1420: return "modellgelaende"
        if y > 150: return "karte"
        if 1190 < x < 1210: return "leitstand"
        if 1090 < x < 1110: return "kabine"
        if sh["set"] in ("bahnhof_tafel", "kalender"): return "tafel"
        if abs(x) < 50 and abs(y) < 40: return "stadt"
        return sh["set"]
    for k in range(1, len(shots)):
        if plan[k]["run_k"] == 0 and ort(shots[k]) == ort(shots[k - 1]): plan[k]["xfade"] = True
    json.dump(shots, open(os.path.join(a.out, "shots.json"), "w"), indent=0)
    json.dump(plan, open(os.path.join(a.out, "plan.json"), "w"), indent=0, ensure_ascii=False)
    print(len(shots), "Einstellungen,", round(sum(p["dur"] for p in plan), 1), "s")

if __name__ == "__main__":
    main()
