"""Kameras der Pfand-Welt (engine/stadt_pfand.py) + Stadt. SETS[name] = (loc, tgt, lens, Grundzustand, Anker)."""
TOWN = ["uhr", "tafel", "markt", "haus"]
PINS = ["pin_" + p for p in "dortmund neuss berlin schleswig grenze wien warschau oslo kopenhagen luxemburg bruessel".split()]
SETS = {
 # Bahnsteig x=2000
 "bahnhof_total": ((2004.6, -3.4, 2.4), (2000.2, 0.6, 0.7), 28, {}, ["b_flasche", "b_uhr", "b_bank", "b_eimer"]),
 "bank_nah":      ((2000.95, -1.35, 0.38), (2000.1, 0.05, 0.1), 32, {}, ["b_flasche"]),
 "flasche_makro": ((2000.42, -0.4, 0.11), (2000.1, 0.07, 0.04), 45, {}, ["b_flasche"]),
 "bahnhof_uhr":   ((2002.3, -2.8, 2.25), (2003.0, -0.36, 2.72), 42, {}, ["b_uhr"]),
 "muelleimer":    ((2002.7, -2.2, 1.0), (2001.5, -0.1, 0.45), 32, {"neben": 1}, ["b_eimer"]),
 "bahnhof_zug":   ((1996.5, -2.8, 1.6), (2001.0, 3.5, 0.6), 26, {"zug": 1}, ["b_flasche", "b_bank"]),
 # Automat x=2100
 "automat_total":  ((2101.7, -2.3, 1.65), (2100.0, 0.8, 1.05), 26, {}, ["a_display", "a_loch"]),
 "automat_loch":   ((2099.58, 0.38, 1.1), (2100.0, 0.86, 0.97), 38, {"a_flasche": 2, "scan": 1}, ["a_loch"]),
 "automat_display": ((2099.72, 0.4, 1.56), (2100.0, 0.86, 1.48), 42, {"a_flasche": 0}, ["a_display"]),
 "automat_front":  ((2100.9, -1.7, 1.45), (2100.0, 1.4, 1.0), 30, {"a_flasche": 0, "mann": 0}, ["a_innen", "a_presse"]),
 "automat_innen":  ((2099.3, 0.15, 1.3), (2100.0, 1.25, 0.97), 36, {"a_flasche": 0, "cut": 1, "innen": 1, "scan": 1}, ["a_innen"]),
 "automat_presse": ((2099.05, 1.75, 1.15), (2100.0, 2.12, 0.55), 32, {"a_flasche": 0, "cut": 1}, ["a_presse"]),
 # Kasse x=2200
 "kasse_total":   ((2197.9, -2.7, 1.9), (2200.0, 0.0, 0.9), 28, {}, ["k_disp", "k_band"]),
 "kasse_band":    ((2199.3, -0.72, 1.25), (2199.75, 0.0, 0.98), 38, {}, ["k_band"]),
 "kasse_display": ((2200.55, -1.45, 1.38), (2200.95, -0.47, 1.3), 42, {}, ["k_disp"]),
 # Abfüllerei x=2300
 "fabrik_total":  ((2306.5, -6.5, 3.6), (2299.5, 0.6, 0.9), 26, {}, ["f_band"]),
 "fabrik_band":   ((2301.3, -1.25, 1.25), (2299.6, 0.0, 1.0), 34, {}, ["f_band"]),
 "fabrik_paletten": ((2302.5, -2.2, 1.7), (2304.0, 3.4, 0.8), 30, {}, []),
 # Zählzentrum x=2400
 "zaehl_total":   ((2406.5, -6.6, 3.8), (2400.0, 0.6, 1.1), 26, {}, ["z_band"]),
 "zaehl_band":    ((2397.0, -1.6, 1.7), (2395.5, 0.5, 1.1), 32, {}, ["z_band"]),
 "zaehl_ballen":  ((2406.4, -1.4, 1.8), (2404.5, 2.6, 0.9), 32, {"ballen": 6}, []),
 # Mehrweg x=2500
 "mehrweg_kaesten": ((2502.0, -2.3, 1.7), (2499.6, 1.3, 0.8), 30, {}, []),
 "mehrweg_wasch": ((2499.2, -1.9, 1.5), (2501.2, 1.0, 1.0), 32, {}, ["m_band"]),
 # Grenzladen x=2600
 "grenze_total":  ((2590.0, -16.0, 6.5), (2600.0, 1.0, 1.5), 30, {}, ["g_laden", "g_auto"]),
 "grenze_auto":   ((2601.7, -8.2, 1.7), (2600.0, -4.8, 0.95), 32, {}, ["g_auto"]),
 "grenze_fahnen": ((2609.0, -9.5, 3.4), (2612.0, -5.2, 5.0), 32, {}, []),
 # Gericht x=2700
 "gericht_total": ((2703.0, -15.5, 3.0), (2700.0, 0.8, 3.6), 30, {}, []),
 "gericht_saeulen": ((2703.4, -3.4, 0.9), (2700.6, 0.9, 4.2), 24, {}, []),
 # Dokument x=2800
 "doc_nah":       ((2800.0, -0.42, 1.32), (2800.0, 0.05, 0.77), 38, {}, ["d_doc"]),
 "doc_total":     ((2801.4, -1.6, 1.55), (2800.0, 0.15, 0.8), 30, {}, ["d_doc"]),
 # Stadt
 "stadt_total":   ((-4, -30, 16), (0, -1, 0), 40, {"lights": 0.8}, TOWN),
 "markt_aussen":  ((3.6, -14.5, 2.6), (0.0, -8.6, 0.5), 34, {}, ["markt"]),
 "bahnhof_aussen": ((-4.6, 1.6, 2.2), (-8.0, 7.4, 0.8), 32, {}, ["tafel"]),
 "bahnhof_tafel": ((-7.4, 4.4, 1.25), (-8, 7.1, 1.25), 42, {}, ["tafel"]),
 "rathaus_uhr":   ((0.6, 4.0, 1.4), (0, 7.5, 2.0), 50, {}, ["uhr"]),
 "route_total":   ((-14, -18, 11), (-3, 0, 0), 34, {"lights": 0.75}, TOWN),
 "regal_voll":    ((200.15, -5.8, 1.35), (201.0, 1.4, 0.7), 30, {"fill": 1, "gap": 0}, []),
 "regal_gang":    ((200.0, -6.2, 1.6), (200.0, 2.0, 1.0), 26, {"fill": 0.85, "gap": 0}, []),
 "karte_de":      ((0, 178, 18), (0, 200, 0), 45, {}, PINS),
 "karte_nord":    ((-0.5, 196, 9), (-0.5, 204.5, 0), 42, {}, PINS),
 "karte_eu":      ((-3, 168, 38), (-3, 197, 0), 35, {}, PINS),
}
