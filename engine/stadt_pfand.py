"""Zusatz-Welt „Pfand“ für die Unterbau-Modellstadt (Video 005). Laden mit stadt.py --extra pfand.
Alle Orte im Menschen-Maßstab (Meter), nachts, orange = echtes Licht:
  x=2000 Bahnsteig mit Bank, Flasche darunter, Mülleimer, Bahnhofsuhr, Laterne, Regionalzug
  x=2100 Leergut-Raum mit Pfandautomat (Öffnung, Display, Kamera-Ring innen, Presse, Behälter) – Querschnitt über Zustand cut
  x=2200 Kasse mit Laufband, Sechserpack, Kundendisplay
  x=2300 Abfüllerei (Band mit Flaschen, Füllkarussell, Paletten)
  x=2400 Zählzentrum (Sortiermaschine, Säcke, gepresste PET-Ballen)
  x=2500 Mehrweg (Kästen mit Glasflaschen, Waschtunnel)
  x=2600 Grenzladen (Halle, Parkplatz, Auto mit Dosen-Trays, Fahnen)
  x=2700 Gericht (Säulenbau)
  x=2800 Schreibtisch mit Dokument (Bundestags-Antwort, Gesetz)
Zustände: b_flasche, neben, sammler, zug, a_flasche (0 weg, 1 in der Hand, 2 halb drin), scan, cut, crushed, manip, adisp,
k_pack, ballen (0..14), f_band, kasten, dosen, flagge, g_licht, doc_licht. Figuren ohne Gesicht (Modellbau)."""
import math, random
from mathutils import Vector

S = None


def B(name, items, m, bevel=0.0): return S.boxes(name, items, m, bevel)


def cyl(name, items, m, seg=20):
    """items: (center, r, length, axis 'x'|'y'|'z')"""
    import bmesh
    bm = bmesh.new()
    for c, r, L, ax in items:
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=L)
        q = None if isinstance(ax, str) else Vector((0, 0, 1)).rotation_difference(Vector(ax))
        for v in res["verts"]:
            x, y, z = v.co
            if q is not None: x, y, z = q @ Vector((x, y, z))
            elif ax == "x": x, y, z = z, y, x
            elif ax == "y": x, y, z = x, z, y
            v.co = Vector((c[0] + x, c[1] + y, c[2] + z))
    o = S.mesh_obj(name, bm, m)
    for p in o.data.polygons: p.use_smooth = True
    return o


def bottle_parts(c, ax="z", k=1.0, lab=True):
    """0,5-l-PET-Flasche: Liste (center, r, L, ax, teil) – teil: body|label|neck|cap. c = Mitte des Körpers, Hals Richtung +ax."""
    d = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}[ax] if isinstance(ax, str) else ax
    C = Vector(c); out = []
    def at(off): p = C + d * off * k; return (p.x, p.y, p.z)
    out.append((at(0.0), 0.033 * k, 0.16 * k, ax, "body"))
    out.append((at(0.1), 0.025 * k, 0.04 * k, ax, "body"))
    out.append((at(0.13), 0.014 * k, 0.03 * k, ax, "body"))
    out.append((at(0.152), 0.016 * k, 0.016 * k, ax, "cap"))
    if lab: out.append((at(-0.005), 0.0336 * k, 0.07 * k, ax, "label"))
    return out


def bottles(name, lst, seg=18):
    g = {"body": [], "label": [], "cap": []}
    for p in lst: g[p[4]].append(p[:4])
    obs = []
    for t, m in (("body", "pet"), ("label", "etikett"), ("cap", "deckel")):
        if g[t]: obs.append(cyl(f"{name}_{t}", g[t], S.M[m], seg))
    return obs


def pet_mat():
    m = S.mat("pet", (0.62, 0.78, 0.86, 1), rough=0.08)
    b = m.node_tree.nodes["Principled BSDF"]
    for key in ("Transmission Weight", "Transmission"):
        if key in b.inputs: b.inputs[key].default_value = 0.85; break
    b.inputs["IOR"].default_value = 1.4
    return m


def build(stadt):
    global S
    S = stadt; M, mat, ANCH, ST = S.M, S.mat, S.ANCH, S.STATE_OBJ
    import bpy
    from stadt_notruf import person
    pet_mat(); mat("etikett", (0.9, 0.9, 0.86, 1), rough=0.5); mat("deckel", (0.1, 0.3, 0.75, 1), rough=0.4)
    mat("beton", (0.2, 0.2, 0.21, 1), rough=0.9); mat("schotter", (0.07, 0.065, 0.06, 1), rough=1); mat("weiss_l", (0.85, 0.85, 0.8, 1), rough=0.6)
    mat("bank_h", (0.28, 0.16, 0.08, 1), rough=0.6); mat("eimer", (0.12, 0.14, 0.16, 1), rough=0.5, metal=0.5)
    mat("zug", (0.55, 0.57, 0.6, 1), rough=0.4); mat("zug_fen", (1.0, 0.85, 0.6, 1), 2.5); mat("zug_rot", (0.55, 0.06, 0.05, 1))
    mat("automat", (0.78, 0.8, 0.82, 1), rough=0.35); mat("a_ring", (1.0, 0.42, 0.08, 1), 0.0); mat("a_disp", (0.35, 0.55, 0.9, 1), 0.0)
    mat("scan_l", (0.7, 0.85, 1.0, 1), 0.0); mat("a_loch", (0.01, 0.01, 0.012, 1), rough=0.9); mat("gruen_l", (0.2, 0.9, 0.3, 1), 3.0)
    mat("rot_l", (1.0, 0.08, 0.04, 1), 0.0); mat("fliese", (0.55, 0.56, 0.58, 1), rough=0.3); mat("wandhell", (0.62, 0.62, 0.6, 1), rough=0.8)
    mat("rolle", (0.25, 0.27, 0.3, 1), rough=0.3, metal=0.8); mat("platt", (0.55, 0.7, 0.8, 1), rough=0.2)
    mat("gummi", (0.03, 0.03, 0.035, 1), rough=0.6); mat("kasse_k", (0.12, 0.13, 0.15, 1), rough=0.5); mat("deckenl", (1, 0.96, 0.9, 1), 6.0)
    mat("folie", (0.8, 0.85, 0.9, 1), rough=0.15); mat("palette", (0.42, 0.3, 0.18, 1), rough=0.8); mat("halle", (0.22, 0.23, 0.25, 1), rough=0.8)
    mat("sack", (0.85, 0.85, 0.82, 1), rough=0.9); mat("ballen", (0.45, 0.62, 0.72, 1), rough=0.6); mat("ballen2", (0.6, 0.7, 0.75, 1), rough=0.6)
    mat("kasten", (0.12, 0.3, 0.15, 1), rough=0.5); mat("glas_b", (0.25, 0.13, 0.04, 1), rough=0.1); mat("dampf_l", (1.0, 0.75, 0.45, 1), 3.0)
    mat("asphalt", (0.05, 0.05, 0.055, 1), rough=0.7); mat("laden_band", (1.0, 0.4, 0.08, 1), 5.0); mat("laden_glas", (1.0, 0.85, 0.65, 1), 3.0)
    mat("auto1", (0.3, 0.05, 0.05, 1), rough=0.3, metal=0.5); mat("auto2", (0.12, 0.14, 0.2, 1), rough=0.3, metal=0.5); mat("dose", (0.75, 0.76, 0.78, 1), rough=0.25, metal=0.9)
    mat("fl_rot", (0.75, 0.05, 0.08, 1)); mat("fl_weiss", (0.9, 0.9, 0.9, 1)); mat("fl_schw", (0.03, 0.03, 0.03, 1)); mat("fl_gold", (0.95, 0.7, 0.05, 1))
    mat("stein", (0.5, 0.48, 0.44, 1), rough=0.8); mat("tisch", (0.3, 0.2, 0.12, 1), rough=0.5); mat("papier", (0.92, 0.91, 0.87, 1), 0.0)
    mat("jacke2", (0.2, 0.25, 0.2, 1)); mat("hose2", (0.1, 0.1, 0.12, 1)); mat("haut2", (0.42, 0.31, 0.25, 1)); mat("jacke3", (0.45, 0.3, 0.15, 1))
    mat("tasche", (0.15, 0.25, 0.4, 1)); mat("kab", (0.9, 0.6, 0.1, 1))

    # ================= x=2000 Bahnsteig
    X = 2000
    B("b_steig", [((X, 0, -0.05), (34, 8, 0.1))], M["beton"])
    B("b_kante", [((X, 3.85, 0.005), (34, 0.25, 0.01))], M["weiss_l"])
    B("b_gleis", [((X, 6.5, -1.05), (34, 5, 0.1))], M["schotter"])
    B("b_schienen", [((X, 5.8, -0.93), (34, 0.07, 0.14)), ((X, 7.2, -0.93), (34, 0.07, 0.14))] + [((X - 16 + 0.65 * k, 6.5, -0.98), (0.25, 2.2, 0.06)) for k in range(50)], M["rolle"])
    B("b_steig_wand", [((X, 3.98, -0.55), (34, 0.05, 1.0))], M["beton"])
    # Bank
    B("b_bank", [((X, 0, 0.45), (1.8, 0.42, 0.05)), ((X, -0.22, 0.75), (1.8, 0.05, 0.36))], M["bank_h"], 0.01)
    B("b_bank_fuss", [((X + sx, 0, 0.22), (0.06, 0.42, 0.45)) for sx in (-0.75, 0.75)] + [((X + sx, -0.22, 0.6), (0.05, 0.05, 0.3)) for sx in (-0.75, 0.75)], M["eimer"])
    ST["b_flasche"] = bottles("b_fl", bottle_parts((X + 0.12, 0.06, 0.034), Vector((0.94, 0.34, 0)).normalized()))
    ANCH["b_flasche"] = [Vector((X + 0.12, 0.06, 0.04))]; ANCH["b_bank"] = [Vector((X, 0, 0.55))]
    # Mülleimer + Flasche daneben
    cyl("b_eimer", [((X + 1.45, -0.05, 0.38), 0.21, 0.76, "z")], M["eimer"], 28); cyl("b_eimer_in", [((X + 1.45, -0.05, 0.755), 0.185, 0.02, "z")], M["a_loch"], 28)
    ST["b_neben"] = bottles("b_nb", bottle_parts((X + 1.78, -0.12, 0.08), "z"))
    ANCH["b_eimer"] = [Vector((X + 1.45, -0.05, 0.85))]
    # Laterne + Bahnhofsuhr
    B("b_lat", [((X - 1.9, -0.7, 1.75), (0.08, 0.08, 3.5)), ((X - 1.9, -0.45, 3.45), (0.12, 0.6, 0.06))], M["eimer"])
    B("b_lat_k", [((X - 1.9, -0.25, 3.4), (0.2, 0.3, 0.04))], M["lamp"])
    bpy.ops.object.light_add(type="POINT", location=(X - 1.9, -0.25, 3.2)); L = bpy.context.object; L.data.energy = 260; L.data.color = (1.0, 0.7, 0.45); L.data.shadow_soft_size = 0.3
    bpy.ops.object.light_add(type="POINT", location=(X + 6, -0.5, 3.2)); L = bpy.context.object; L.data.energy = 180; L.data.color = (1.0, 0.7, 0.45)
    B("b_lat2", [((X + 6, -0.7, 1.75), (0.08, 0.08, 3.5))], M["eimer"]); B("b_lat2_k", [((X + 6, -0.45, 3.4), (0.2, 0.3, 0.04))], M["lamp"])
    B("b_uhrmast", [((X + 3.0, -0.3, 1.3), (0.07, 0.07, 2.6))], M["eimer"])
    cyl("b_uhr", [((X + 3.0, -0.36, 2.75), 0.3, 0.05, "y")], M["clock"], 40); cyl("b_uhr_r", [((X + 3.0, -0.34, 2.75), 0.33, 0.08, "y")], M["eimer"], 40)
    r = 0.29; ANCH["b_uhr"] = [Vector((X + 3 - r, -0.39, 2.75 + r)), Vector((X + 3 + r, -0.39, 2.75 + r)), Vector((X + 3 + r, -0.39, 2.75 - r)), Vector((X + 3 - r, -0.39, 2.75 - r))]
    # Bahnhofsgebäude hinten, Zug
    B("b_haus", [((X, -4.2, 2.0), (34, 0.6, 4.0))], M["bld"]); B("b_haus_fen", [((X - 15 + 2.5 * k, -3.88, 1.6), (1.4, 0.03, 1.4)) for k in range(13)], M["win"])
    ST["b_zug"] = [B("b_zug", [((X - 2, 6.5, 0.5), (26, 2.8, 2.9))], M["zug"], 0.1), B("b_zug_fen", [((X - 14 + 2.0 * k, 5.08, 0.9), (1.3, 0.03, 0.75)) for k in range(13)], M["zug_fen"]),
                   B("b_zug_band", [((X - 2, 5.08, 0.15), (26, 0.03, 0.18))], M["zug_rot"])]
    ppl = []; person(ppl, X - 6.5, 0.6, 0.0, "stand", 0.4); person(ppl, X - 7.3, 0.2, 0.0, "stand", -0.3, h=1.65); person(ppl, X + 9, 0.8, 0.0, "stand", 2.2)
    B("b_leute", ppl, [M["jacke2"], M["haut2"], M["hose2"]], 0.03)
    sm = []; person(sm, X + 2.35, -0.75, 0.0, "stand", 2.6, h=1.72)
    ST["b_sammler"] = [B("b_sammler", sm, [M["jacke3"], M["haut2"], M["hose2"]], 0.03), B("b_tasche", [((X + 2.0, -0.95, 0.55), (0.32, 0.18, 0.4))], M["tasche"], 0.03)]

    # ================= x=2100 Leergut-Raum mit Automat
    X = 2100
    B("a_boden", [((X, 0, -0.05), (12, 9, 0.1))], M["fliese"])
    B("a_wand", [((X - 3.3, 1.1, 1.5), (5.4, 0.2, 3.0)), ((X + 3.3, 1.1, 1.5), (5.4, 0.2, 3.0)), ((X, 1.1, 2.6), (1.2, 0.2, 0.8))], M["wandhell"])
    B("a_decke", [((X, -1, 3.05), (12, 9, 0.1))], M["halle"]); B("a_deckenl", [((X + dx, -1, 2.99), (1.2, 0.3, 0.02)) for dx in (-2.5, 0, 2.5)], M["deckenl"])
    ST["a_frontteile"] = [B("a_front", [((X, 0.93, 1.1), (1.2, 0.1, 2.2))], M["automat"], 0.02)]
    ST["a_seite"] = B("a_seite", [((X - 0.6, 1.75, 1.1), (0.04, 1.55, 2.2))], M["automat"])
    B("a_seite_r", [((X + 0.6, 1.75, 1.1), (0.04, 1.55, 2.2)), ((X, 2.52, 1.1), (1.2, 0.04, 2.2)), ((X, 1.75, 2.21), (1.24, 1.6, 0.04))], M["automat"])
    ST["a_frontteile"] += [cyl("a_loch", [((X, 0.86, 0.98), 0.13, 0.04, "y")], M["a_loch"], 40), cyl("a_ring", [((X, 0.875, 0.98), 0.155, 0.02, "y")], M["a_ring"], 40),
                           B("a_display", [((X, 0.875, 1.5), (0.4, 0.01, 0.26))], M["a_disp"])]
    ANCH["a_display"] = [Vector((X - 0.19, 0.868, 1.62)), Vector((X + 0.19, 0.868, 1.62)), Vector((X + 0.19, 0.868, 1.38)), Vector((X - 0.19, 0.868, 1.38))]
    ST["a_frontteile"] += [B("a_knopf", [((X + 0.33, 0.87, 1.2), (0.09, 0.02, 0.09))], M["gruen_l"]), B("a_bon", [((X - 0.3, 0.87, 1.2), (0.16, 0.02, 0.03))], M["a_loch"]),
                           B("a_rot", [((X, 0.87, 2.0), (0.12, 0.02, 0.06))], M["rot_l"])]
    ANCH["a_loch"] = [Vector((X, 0.85, 0.98))]
    # Innen: Röhre, Kamera-Ring, Band, Presse, Behälter
    cyl("a_roehre", [((X, 1.25, 0.98), 0.14, 0.6, "y")], M["platt"], 32)
    cams = [((X + 0.22 * math.cos(a), 1.25, 0.98 + 0.22 * math.sin(a)), (0.06, 0.08, 0.06)) for a in [k * math.pi / 3 for k in range(6)]]
    B("a_kameras", cams, M["eimer"]); B("a_kam_l", [((c[0][0] * 0.8 + X * 0.2, 1.25, c[0][2] * 0.8 + 0.98 * 0.2), (0.025, 0.09, 0.025)) for c in cams], M["scan_l"])
    B("a_band", [((X, 1.75, 0.82), (0.32, 0.5, 0.03))], M["gummi"])
    ST["a_rollen"] = cyl("a_rollen", [((X, 2.05, 0.66), 0.09, 0.5, "x"), ((X, 2.24, 0.66), 0.09, 0.5, "x")], M["rolle"], 24)
    B("a_behaelter", [((X, 2.12, 0.25), (0.6, 0.55, 0.45))], M["folie"], 0.02)
    B("a_platt", [((X + random.Random(k).uniform(-0.2, 0.2), 2.12 + random.Random(k + 9).uniform(-0.18, 0.18), 0.48 + 0.012 * k), (0.07, 0.17, 0.012)) for k in range(14)], M["platt"])
    ST["a_innen_fl"] = bottles("a_infl", bottle_parts((X, 1.22, 0.98), "y"))
    ST["a_hand_fl"] = bottles("a_hdfl", bottle_parts((X + 0.02, 0.58, 1.0), "y"))
    ST["a_halb_fl"] = bottles("a_hbfl", bottle_parts((X, 0.8, 0.98), "y"))
    ST["a_platt_neu"] = B("a_platt_neu", [((X, 2.14, 0.54), (0.075, 0.18, 0.014))], M["pet"])
    ST["a_manip"] = [B("a_kabel", [((X - 0.62, 1.4 + 0.08 * k, 1.3 - 0.1 * k), (0.02, 0.3, 0.015)) for k in range(5)], M["kab"]),
                     B("a_manip_l", [((X - 0.64, 1.2, 1.6), (0.03, 0.12, 0.08))], M["rot_l"])]
    ANCH["a_innen"] = [Vector((X, 1.25, 1.2))]; ANCH["a_presse"] = [Vector((X, 2.14, 0.8))]
    bpy.ops.object.light_add(type="POINT", location=(X - 0.2, 1.4, 1.6)); L = bpy.context.object; L.data.energy = 0; L.data.color = (0.75, 0.85, 1.0); ST["a_innenlicht"] = L
    ppl = []; person(ppl, X + 0.12, 0.25, 0.0, "stand", 0.0, h=1.8)
    ST["a_mann"] = B("a_mann", ppl, [M["jacke2"], M["haut2"], M["hose2"]], 0.03)
    ST["a_arm"] = S.curve("a_arm", [(X + 0.32, 0.25, 1.38), (X + 0.18, 0.45, 1.12), (X + 0.04, 0.6, 1.0)], 0.045, M["jacke2"])
    B("a_kaesten", [((X + 1.6 + 0.45 * k, 0.6, 0.15 + 0.3 * j), (0.4, 0.3, 0.28)) for k in range(3) for j in range(2)], M["kasten"], 0.01)
    B("a_automat2", [((X - 1.6, 0.93, 1.1), (1.2, 0.1, 2.2))], M["automat"], 0.02); cyl("a_ring2", [((X - 1.6, 0.875, 0.98), 0.155, 0.02, "y")], M["a_ring"], 40)
    cyl("a_loch2", [((X - 1.6, 0.86, 0.98), 0.13, 0.04, "y")], M["a_loch"], 40)

    # ================= x=2200 Kasse
    X = 2200
    B("k_boden", [((X, 0, -0.05), (12, 10, 0.1))], M["fliese"]); B("k_decke", [((X, 0, 3.05), (12, 10, 0.1))], M["halle"])
    B("k_dl", [((X + dx, dy, 2.99), (1.4, 0.3, 0.02)) for dx in (-2, 0, 2) for dy in (-2, 1.5)], M["deckenl"])
    B("k_tresen", [((X, 0, 0.45), (2.6, 0.7, 0.9))], M["kasse_k"], 0.02); B("k_band", [((X - 0.45, 0, 0.91), (1.6, 0.5, 0.02))], M["gummi"])
    B("k_scanner", [((X + 0.65, 0, 0.915), (0.3, 0.3, 0.01))], M["scan_l"])
    B("k_disp_mast", [((X + 0.95, -0.45, 1.05), (0.04, 0.04, 0.3))], M["eimer"]); B("k_disp", [((X + 0.95, -0.47, 1.3), (0.34, 0.03, 0.22))], M["a_disp"])
    ANCH["k_disp"] = [Vector((X + 0.79, -0.49, 1.4)), Vector((X + 1.11, -0.49, 1.4)), Vector((X + 1.11, -0.49, 1.2)), Vector((X + 0.79, -0.49, 1.2))]
    pk = []
    for i in range(3):
        for j in range(2): pk += bottle_parts((X - 0.7 + 0.07 * i, -0.04 + 0.07 * j, 1.0), "z")
    ST["k_pack"] = bottles("k_pk", pk)
    ppl = []; person(ppl, X + 0.6, 0.75, 0.0, "sit", math.pi); person(ppl, X - 1.45, -0.95, 0.0, "stand", 0.0)
    B("k_leute", ppl, [M["jacke2"], M["haut2"], M["hose2"]], 0.03)
    reg = []
    for side in (-1,):
        for z in (0.3, 0.8, 1.3, 1.8):
            for k in range(30): reg += bottle_parts((X - 3 + 0.2 * k, 2.6, z + 0.09), "z", 1.0, lab=True)
    bottles("k_regal_fl", reg, 10); B("k_regal", [((X, 2.6, z), (6.4, 0.5, 0.03)) for z in (0.3, 0.8, 1.3, 1.8)] + [((X, 2.88, 1.1), (6.4, 0.04, 2.2))], M["shelf"] if "shelf" in M else M["metal"])
    ANCH["k_band"] = [Vector((X - 0.7, 0, 1.0))]

    # ================= x=2300 Abfüllerei
    X = 2300
    B("f_boden", [((X, 0, -0.05), (24, 16, 0.1))], M["halle"]); B("f_wand", [((X, 7, 3), (24, 0.3, 6))], M["bld"])
    B("f_licht", [((X - 9 + 3 * k, dy, 5.6), (2.2, 0.25, 0.05)) for k in range(7) for dy in (-3, 0, 3)], M["deckenl"])
    B("f_band", [((X, 0, 0.88), (16, 0.35, 0.05)), ((X, 0, 0.45), (16, 0.2, 0.85))], M["metal"])
    fl = []
    for k in range(120): fl += bottle_parts((X - 8 + 0.12 * k, 0.0, 1.0), "z", 1.0, lab=(k % 3 != 0) or k > 40)
    ST["f_flaschen"] = bottles("f_fl", fl, 12)
    cyl("f_karussell", [((X - 5, 1.5, 1.4), 1.1, 1.0, "z")], M["metal"], 40); cyl("f_karussell_top", [((X - 5, 1.5, 2.2), 0.4, 0.6, "z")], M["white"], 30)
    B("f_duesen", [((X - 5 + 1.0 * math.cos(a), 1.5 + 1.0 * math.sin(a), 1.1), (0.04, 0.04, 0.3)) for a in [k * math.pi / 10 for k in range(20)]], M["rolle"])
    pal = []
    for i in range(4):
        for j in range(2): pal.append(((X + 2 + 1.3 * i, 3.2 + 1.3 * j, 0.07), (1.2, 1.0, 0.14)))
    B("f_paletten", pal, M["palette"]); B("f_packs", [((c[0], c[1], 0.75), (1.1, 0.9, 1.2)) for c, _ in pal], M["folie"], 0.03)
    B("f_packs_lab", [((c[0], c[1] - 0.46, 0.75), (0.9, 0.01, 0.25)) for c, _ in pal], M["laden_band"])
    ppl = []; person(ppl, X - 3.0, -2.6, 0, "stand", 0.5); person(ppl, X - 2.5, 1.0, 0, "stand", 2.0)
    B("f_leute", ppl, [M["jacke"] if "jacke" in M else M["jacke2"], M["haut2"], M["hose2"]], 0.03)
    ANCH["f_band"] = [Vector((X - 8 + 0.5 * k, 0, 1.15)) for k in range(32)]

    # ================= x=2400 Zählzentrum
    X = 2400
    B("z_boden", [((X, 0, -0.05), (24, 16, 0.1))], M["halle"]); B("z_wand", [((X, 7, 3), (24, 0.3, 6))], M["bld"])
    B("z_licht", [((X - 9 + 3 * k, dy, 5.6), (2.2, 0.25, 0.05)) for k in range(7) for dy in (-3, 0, 3)], M["deckenl"])
    B("z_maschine", [((X, 0.5, 1.3), (3.2, 1.8, 2.6)), ((X - 2.0, 0.5, 2.2), (0.9, 1.2, 0.8))], M["automat"], 0.03)
    B("z_masch_fen", [((X + 0.4, -0.41, 1.5), (1.6, 0.02, 0.7))], M["scan_l"]); B("z_masch_band", [((X, -0.42, 2.4), (3.0, 0.02, 0.08))], M["laden_band"])
    B("z_zulauf", [((X - 4.0, 0.5, 1.1), (3.0, 0.6, 0.06)), ((X - 4.0, 0.5, 0.55), (3.0, 0.3, 1.05))], M["metal"])
    zl = []
    for k in range(22): zl += bottle_parts((X - 5.4 + 0.13 * k, 0.5 + (0.12 if k % 2 else -0.12), 1.17), "x", 1.0)
    bottles("z_zulauf_fl", zl, 10)
    rnd = random.Random(5)
    B("z_saecke", [((X - 6.5 + 1.1 * (k % 4), -2.0 - 1.1 * (k // 4), 0.55), (0.95, 0.95, 1.1)) for k in range(8)], M["sack"], 0.15)
    bal = [((X + 3 + 1.15 * (k % 4), 2.4 + 1.15 * ((k // 4) % 2), 0.5 + 1.02 * (k // 8)), (1.1, 1.05, 1.0)) for k in range(16)]
    ST["z_ballen_items"] = bal
    B("z_presse", [((X + 3.2, -1.6, 1.1), (1.6, 1.4, 2.2))], M["rolle"], 0.03)
    ANCH["z_band"] = [Vector((X - 5.5 + 0.25 * k, 0.5, 1.3)) for k in range(26)]

    # ================= x=2500 Mehrweg
    X = 2500
    B("m_boden", [((X, 0, -0.05), (20, 14, 0.1))], M["halle"]); B("m_wand", [((X, 6, 3), (20, 0.3, 6))], M["bld"])
    B("m_licht", [((X - 6 + 3 * k, dy, 5.6), (2.2, 0.25, 0.05)) for k in range(5) for dy in (-2, 2)], M["deckenl"])
    ks, gb = [], []
    for i in range(4):
        for j in range(5):
            for st in range(2):
                cx, cy, cz = X - 2 + 0.45 * i, 1.2 + 0.36 * st, 0.15 + 0.3 * j
                ks.append(((cx, cy, cz), (0.42, 0.32, 0.28)))
                if j == 4: gb += [((cx - 0.15 + 0.1 * a, cy - 0.1 + 0.1 * b, cz + 0.22), 0.03, 0.24, "z") for a in range(4) for b in range(3)]
    B("m_kaesten", ks, M["kasten"], 0.01); cyl("m_glas", gb, M["glas_b"], 12)
    B("m_tunnel", [((X + 3, 1.0, 1.2), (4, 1.6, 2.4))], M["metal"], 0.03); B("m_tunnel_l", [((X + 1.0, 1.0, 1.1), (0.02, 1.2, 0.9))], M["dampf_l"])
    B("m_band", [((X + 0.5, 1.0, 0.85), (6, 0.5, 0.04))], M["gummi"])
    mb = [((X - 1.5 + 0.12 * k, 1.0 + 0.1 * (k % 2), 1.0), 0.03, 0.26, "z") for k in range(22)]
    cyl("m_band_fl", mb, M["glas_b"], 12)
    ANCH["m_band"] = [Vector((X - 1.5 + 0.25 * k, 1.0, 1.2)) for k in range(14)]

    # ================= x=2600 Grenzladen
    X = 2600
    B("g_boden", [((X, 0, -0.05), (60, 40, 0.1))], M["asphalt"])
    B("g_halle", [((X, 8, 2.6), (22, 9, 5.2))], M["bld"], 0.05); B("g_band", [((X, 3.48, 4.6), (18, 0.05, 0.7))], M["laden_band"])
    B("g_glas", [((X, 3.48, 1.3), (14, 0.04, 2.2))], M["laden_glas"])
    B("g_markierung", [((X - 12 + 2.6 * k, -3.0, 0.005), (0.08, 4.5, 0.01)) for k in range(10)], M["weiss_l"])
    cars = []
    for k in range(9):
        cx = X - 10.7 + 2.6 * k
        if k == 4: continue
        cars.append(((cx, -3.0, 0.45), (1.8, 4.2, 0.75))); cars.append(((cx, -2.8, 1.05), (1.6, 2.2, 0.55)))
    B("g_autos", cars, M["auto2"], 0.12)
    cx = X - 10.7 + 2.6 * 4
    B("g_auto", [((cx, -3.0, 0.45), (1.8, 4.2, 0.75)), ((cx, -2.6, 1.05), (1.6, 2.0, 0.55))], M["auto1"], 0.12)
    B("g_klappe", [((cx, -5.25, 1.5), (1.7, 0.6, 0.05))], M["auto1"], 0.02)
    trays = [((cx - 0.5 + 0.5 * (k % 3), -4.6 + 0.4 * ((k // 3) % 2), 0.95 + 0.14 * (k // 6)), (0.45, 0.35, 0.13)) for k in range(18)]
    ST["g_trays"] = B("g_trays", trays, M["folie"], 0.02)
    cyl("g_dosen", [((c[0] - 0.15 + 0.1 * a, c[1] - 0.1 + 0.1 * b, c[2]), 0.032, 0.12, "z") for c, _ in trays[-6:] for a in range(4) for b in range(3)], M["dose"], 12)
    pal = []
    for k in range(10): pal.append(((X - 6 + 1.3 * k, 2.4, 0.07), (1.2, 1.0, 0.14)))
    B("g_paletten", pal, M["palette"]); B("g_pal_dosen", [((c[0], c[1], 0.8), (1.1, 0.9, 1.3)) for c, _ in pal], M["dose"], 0.02)
    B("g_mast", [((X + 12, -6 + 1.6 * k, 3.0), (0.1, 0.1, 6.0)) for k in range(2)], M["metal"])
    # Fahnen: Dänemark (rot, weißes Kreuz), Deutschland (schwarz-rot-gold)
    fx, fz = X + 12.05, 5.2
    B("g_dk", [((fx, -6 - 0.75, fz), (0.02, 1.4, 1.0))], M["fl_rot"]); B("g_dk_x", [((fx - 0.015, -6 - 0.95, fz), (0.02, 0.16, 1.0)), ((fx - 0.015, -6 - 0.75, fz), (0.02, 1.4, 0.16))], M["fl_weiss"])
    B("g_de", [((fx, -4.4 - 0.75, fz + 0.33), (0.02, 1.4, 0.333)), ((fx, -4.4 - 0.75, fz), (0.02, 1.4, 0.333)), ((fx, -4.4 - 0.75, fz - 0.33), (0.02, 1.4, 0.333))], [M["fl_schw"]])
    B("g_de_r", [((fx - 0.012, -4.4 - 0.75, fz), (0.02, 1.4, 0.333))], M["fl_rot"]); B("g_de_g", [((fx - 0.012, -4.4 - 0.75, fz - 0.33), (0.02, 1.4, 0.333))], M["fl_gold"])
    for k, (lx, ly) in enumerate([(X - 8, -6), (X, -6), (X + 8, -6)]):
        B(f"g_lat{k}", [((lx, ly, 3), (0.12, 0.12, 6)), ((lx, ly + 0.4, 5.95), (0.4, 0.9, 0.08))], M["metal"])
        bpy.ops.object.light_add(type="POINT", location=(lx, ly + 0.6, 5.6)); L = bpy.context.object; L.data.energy = 900; L.data.color = (1.0, 0.72, 0.45)
    ppl = []; person(ppl, cx + 1.4, -5.4, 0, "stand", 1.2); person(ppl, X - 3, 1.5, 0, "stand", 0.2); person(ppl, X + 2, 1.2, 0, "stand", 2.8)
    B("g_leute", ppl, [M["jacke2"], M["haut2"], M["hose2"]], 0.03)
    ANCH["g_auto"] = [Vector((cx, -4.8, 1.4))]; ANCH["g_laden"] = [Vector((X, 3.4, 4.0))]

    # ================= x=2700 Gericht
    X = 2700
    B("r_boden", [((X, 0, -0.05), (40, 30, 0.1))], M["asphalt"])
    B("r_stufen", [((X, -0.6 + 0.3 * k, 0.1 + 0.2 * k), (14 - 0.4 * k, 1.2, 0.2)) for k in range(5)], M["stein"])
    B("r_bau", [((X, 4.5, 3.8), (14, 7, 6.8))], M["stein"], 0.03)
    cyl("r_saeulen", [((X - 6 + 1.33 * k, 0.9, 3.4), 0.32, 5.2, "z") for k in range(10)], M["stein"], 24)
    import bmesh
    bm = bmesh.new(); v = [bm.verts.new(p) for p in [(X - 7, 0.4, 6.1), (X + 7, 0.4, 6.1), (X, 0.4, 7.8), (X - 7, 1.4, 6.1), (X + 7, 1.4, 6.1), (X, 1.4, 7.8)]]
    for f in [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]: bm.faces.new([v[i] for i in f])
    S.mesh_obj("r_giebel", bm, M["stein"])
    B("r_gebaelk", [((X, 0.9, 6.0), (14.4, 1.2, 0.4))], M["stein"])
    B("r_tuer", [((X, 1.02, 1.9), (2.0, 0.05, 3.0))], M["laden_glas"]); B("r_fen", [((X + dx, 1.02, 3.5), (0.9, 0.05, 1.6)) for dx in (-4, -2.2, 2.2, 4)], M["win"])
    for k, lx in enumerate((X - 8, X + 8)):
        B(f"r_lat{k}", [((lx, -2.5, 2.0), (0.12, 0.12, 4.0))], M["metal"]); B(f"r_latk{k}", [((lx, -2.5, 4.05), (0.35, 0.35, 0.25))], M["lamp"])
        bpy.ops.object.light_add(type="POINT", location=(lx, -2.8, 3.7)); L = bpy.context.object; L.data.energy = 1500; L.data.color = (1.0, 0.72, 0.45)
    bpy.ops.object.light_add(type="AREA", location=(X, -6, 1.0), rotation=(math.radians(-70), 0, 0)); L = bpy.context.object; L.data.energy = 1800; L.data.size = 10; L.data.color = (1.0, 0.75, 0.5)

    # ================= x=2800 Schreibtisch mit Dokument
    X = 2800
    B("d_boden", [((X, 0, -0.05), (8, 8, 0.1))], M["kfloor"] if "kfloor" in M else M["halle"]); B("d_wand", [((X, 1.6, 1.5), (8, 0.2, 3))], M["kwand"] if "kwand" in M else M["bld"])
    B("d_tisch", [((X, 0.2, 0.74), (1.8, 0.9, 0.05))] + [((X + sx, 0.2 + sy, 0.36), (0.05, 0.05, 0.72)) for sx in (-0.85, 0.85) for sy in (-0.4, 0.4)], M["tisch"], 0.01)
    B("d_papier", [((X, 0.05, 0.768), (0.42, 0.594, 0.004))], M["papier"])
    ANCH["d_doc"] = [Vector((X - 0.21, 0.347, 0.771)), Vector((X + 0.21, 0.347, 0.771)), Vector((X + 0.21, -0.247, 0.771)), Vector((X - 0.21, -0.247, 0.771))]
    B("d_lampe", [((X + 0.65, 0.45, 0.95), (0.04, 0.04, 0.4)), ((X + 0.5, 0.3, 1.15), (0.3, 0.2, 0.08))], M["eimer"])
    bpy.ops.object.light_add(type="POINT", location=(X + 0.35, 0.2, 1.1)); L = bpy.context.object; L.data.energy = 40; L.data.color = (1.0, 0.75, 0.5); ST["d_licht"] = L
    B("d_stapel", [((X - 0.6, 0.35, 0.77 + 0.012 * k), (0.4, 0.55, 0.01)) for k in range(6)], M["papier"])

    # ================= Karten-Pins
    P = ANCH.get("karte_P")
    if P:
        for nm, ll in {"dortmund": (7.47, 51.51), "neuss": (6.69, 51.2), "berlin": (13.4, 52.5), "schleswig": (9.57, 54.52), "grenze": (9.28, 54.83),
                       "wien": (16.37, 48.21), "warschau": (21.0, 52.23), "oslo": (10.75, 59.91), "kopenhagen": (12.57, 55.68), "luxemburg": (6.13, 49.61),
                       "bruessel": (4.35, 50.85)}.items():
            ANCH[f"pin_{nm}"] = [Vector((*P(*ll), 0.32))]


def set_ballen(n):
    import bpy
    o = bpy.data.objects.get("z_ballen")
    if o: bpy.data.objects.remove(o)
    it = S.STATE_OBJ.get("z_ballen_items", [])[:int(n)]
    if it: S.boxes("z_ballen", [(c, s_, k % 2) for k, (c, s_) in enumerate(it)], [S.M["ballen"], S.M["ballen2"]], 0.04)


def state(stadt, st):
    S_ = stadt; ST, emit = S_.STATE_OBJ, S_.emit
    g = st.get
    if "b_flasche" not in ST: return
    def vis(key, on):
        v = ST[key]
        for o in (v if isinstance(v, list) else [v]): o.hide_render = not on
    vis("b_flasche", g("b_flasche", 1)); vis("b_neben", g("neben", 0)); vis("b_sammler", g("sammler", 0)); vis("b_zug", g("zug", 0))
    af = g("a_flasche", 1); vis("a_hand_fl", af == 1); vis("a_halb_fl", af == 2); vis("a_arm", af == 1)
    vis("a_innen_fl", g("innen", 0)); vis("a_seite", not g("cut", 0)); vis("a_frontteile", not g("cut", 0)); vis("a_mann", g("mann", 1) and not g("cut", 0)); vis("a_platt_neu", g("crushed", 0)); vis("a_manip", g("manip", 0))
    vis("a_rollen", not g("manip", 0))
    emit("a_ring", 3.5 * g("ring", 1)); emit("scan_l", 6.0 * g("scan", 0)); emit("a_disp", 1.2 * g("adisp", 1)); emit("rot_l", 6.0 * g("manip", 0))
    ST["a_innenlicht"].data.energy = 25 * g("cut", 0)
    vis("k_pack", g("k_pack", 1)); vis("f_flaschen", g("f_band", 1))
    set_ballen(g("ballen", 6))
    emit("papier", 0.12 * g("doc_licht", 1)); ST["d_licht"].data.energy = 40 * g("doc_licht", 1)
