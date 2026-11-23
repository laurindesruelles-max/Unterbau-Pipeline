"""Zusatz-Welt „Notruf 112“ für die Unterbau-Modellstadt (Video 004). Wird von stadt.py mit --extra notruf geladen.
Neue Orte: Leitstelle (Stadt -6,2 + Innenraum bei x=1200), Rettungswache mit Rettungswagen (6,-2), Funkmast (-10,-2),
Küche mit Figuren (x=300, Szene „Frau wählt 112“), Straße 1969 mit Telefonzelle und Kirchturmuhr (x=1600),
16 Uhren der Länder (x=1400, y=+20), Karten-Pins für Städte in Europa.
Zustände (state): phone, press, retter, blau (Blaulicht in der Küche), k_licht, wache_tor, wache_licht, blaulicht, rtw_haus,
rtw_strasse, ls_dark, phones, people_w, alt (1969 grau), mast_on.
Figuren sind Modellbau-Figuren ohne Gesicht."""
import math, random
from mathutils import Vector

S = None   # stadt-Modul


def B(name, items, m, bevel=0.0): return S.boxes(name, items, m, bevel)


def rtw_items(x, y, ang=0.0, s=1.0):
    """Rettungswagen im Stadt-Maßstab (Länge 0.55). ang=0: fährt Richtung -y. Gibt (body, stripe, blue, head) zurück."""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(dx, dy, z, lx, ly, lz):
        X = x + (dx * ca - dy * sa) * s; Y = y + (dx * sa + dy * ca) * s
        ex = abs(lx * ca) + abs(ly * sa); ey = abs(lx * sa) + abs(ly * ca)
        return ((X, Y, z * s), (ex * s, ey * s, lz * s))
    body = [P(0, 0.06, 0.17, 0.26, 0.42, 0.26), P(0, -0.2, 0.12, 0.25, 0.16, 0.17)]
    stripe = [P(0, 0.02, 0.15, 0.265, 0.5, 0.035)]
    blue = [P(-0.07, -0.13, 0.31, 0.07, 0.04, 0.03), P(0.07, -0.13, 0.31, 0.07, 0.04, 0.03), P(0, 0.26, 0.31, 0.16, 0.03, 0.025)]
    head = [P(-0.08, -0.285, 0.1, 0.05, 0.01, 0.03), P(0.08, -0.285, 0.1, 0.05, 0.01, 0.03)]
    return body, stripe, blue, head


def person(items, x, y, z, pose="stand", ang=0.0, h=1.75, mi=(0, 1, 2)):
    """Blockfigur (Modellbau): Körper, Kopf, Beine. mi = Materialindex (Jacke, Kopf, Hose)."""
    k = h / 1.75; ca, sa = math.cos(ang), math.sin(ang)
    def R(dx, dy): return x + dx * ca - dy * sa, y + dx * sa + dy * ca
    def box(dx, dy, dz, lx, ly, lz, m):
        X, Y = R(dx * k, dy * k); ex = abs(lx * ca) + abs(ly * sa); ey = abs(lx * sa) + abs(ly * ca)
        items.append(((X, Y, z + dz * k), (ex * k, ey * k, lz * k), m))
    if pose == "stand":
        for sx in (-0.09, 0.09): box(sx, 0, 0.43, 0.13, 0.15, 0.86, mi[2])
        box(0, 0, 1.15, 0.4, 0.22, 0.6, mi[0]); box(0, 0, 1.58, 0.19, 0.21, 0.23, mi[1])
        for sx in (-0.25, 0.25): box(sx, 0, 1.12, 0.09, 0.1, 0.58, mi[0])
    elif pose == "sit":
        box(0, 0.05, 0.5, 0.36, 0.42, 0.14, mi[2]); box(0, -0.12, 0.88, 0.4, 0.22, 0.6, mi[0]); box(0, -0.12, 1.32, 0.19, 0.21, 0.23, mi[1])
    elif pose == "lie":   # liegt entlang +x, Kopf bei -x
        box(0.0, 0, 0.11, 0.58, 0.38, 0.2, mi[0]); box(-0.42, 0, 0.1, 0.22, 0.2, 0.19, mi[1])
        for sy in (-0.09, 0.09): box(0.74, sy, 0.07, 0.88, 0.14, 0.13, mi[2])
        for sy in (-0.25, 0.25): box(0.12, sy, 0.06, 0.55, 0.09, 0.09, mi[0])
    elif pose == "kneel":  # kniet, Blick +y
        for sx in (-0.09, 0.09): box(sx, -0.22, 0.06, 0.13, 0.48, 0.12, mi[2])
        box(0, 0.02, 0.32, 0.32, 0.18, 0.38, mi[2]); box(0, 0.1, 0.78, 0.38, 0.22, 0.56, mi[0]); box(0, 0.18, 1.2, 0.19, 0.21, 0.23, mi[1])


def build(stadt):
    global S
    S = stadt; M, mat, ANCH, ST = S.M, S.mat, S.ANCH, S.STATE_OBJ
    mat("rtw_w", (0.82, 0.83, 0.85, 1), rough=0.35); mat("rtw_s", (0.95, 0.3, 0.05, 1), rough=0.4)
    mat("blau_l", (0.15, 0.35, 1.0, 1), 0.0); mat("ls_glas", (0.55, 0.7, 1.0, 1), 2.5); mat("mon", (0.25, 0.38, 0.62, 1), 0.35)
    mat("wache_in", (1.0, 0.92, 0.8, 1), 0.0); mat("mast_rot", (1.0, 0.1, 0.05, 1), 6.0); mat("ls_tel", (1.0, 0.45, 0.1, 1), 3.0)
    mat("jacke", (0.75, 0.18, 0.06, 1), rough=0.6); mat("hose", (0.08, 0.1, 0.14, 1)); mat("refl", (0.9, 0.9, 0.85, 1), 0.4)
    mat("hemd", (0.18, 0.26, 0.42, 1)); mat("strick", (0.45, 0.35, 0.3, 1)); mat("haut", (0.42, 0.31, 0.25, 1))
    mat("handy", (0.02, 0.02, 0.025, 1), rough=0.2); mat("handy_l", (0.7, 0.85, 1.0, 1), 0.0); mat("defi", (0.95, 0.4, 0.05, 1))
    mat("gelb", (0.95, 0.72, 0.1, 1), rough=0.4); mat("zelle_l", (1.0, 0.9, 0.7, 1), 4.0); mat("altbau", (0.32, 0.29, 0.26, 1))
    mat("altdach", (0.35, 0.18, 0.12, 1)); mat("strasse69", (0.12, 0.12, 0.13, 1), rough=0.6)
    # ---------------- Leitstelle in der Stadt (-6, 2), Front Richtung y=0
    lx, ly = -6.0, 2.2
    B("leitstelle", [((lx, ly, 0.5), (3.0, 2.4, 1.0)), ((lx, ly, 1.04), (3.1, 2.5, 0.08))], M["bld"], 0.03)
    B("ls_band", [((lx, ly - 1.21, 0.62), (2.7, 0.02, 0.22)), ((lx, ly - 1.21, 0.32), (2.7, 0.02, 0.14))], M["ls_glas"])
    B("ls_schild", [((lx, ly - 1.22, 0.9), (1.2, 0.03, 0.08))], M["sign"])
    B("ls_antennen", [((lx + 1.1, ly + 0.5, 1.4), (0.04, 0.04, 0.8)), ((lx + 0.8, ly + 0.5, 1.25), (0.03, 0.03, 0.5)), ((lx - 0.9, ly, 1.16), (0.4, 0.3, 0.16))], M["metal"])
    ANCH["leitstelle"] = [Vector((lx, ly - 1.25, 0.6))]
    # ---------------- Rettungswache (6, -2): Halle mit zwei Toren nach y=-4
    wx, wy = 6.0, -1.9
    B("wache", [((wx, wy, 0.42), (2.9, 2.0, 0.84)), ((wx, wy, 0.87), (3.0, 2.1, 0.06))], M["white"], 0.03)
    B("wache_innen", [((wx + dx, wy - 1.006, 0.3), (0.8, 0.01, 0.52)) for dx in (-0.7, 0.7)], M["wache_in"])
    tore = B("wache_tore", [((wx + dx, wy - 1.04, 0.3), (0.84, 0.03, 0.56)) for dx in (-0.7, 0.7)], M["metal"]); ST["wache_tore"] = (tore, 0.0)
    B("wache_band", [((wx, wy - 1.03, 0.72), (2.6, 0.02, 0.07))], M["rtw_s"])
    B("wache_hof", [((wx, wy - 1.55, 0.008), (2.8, 1.0, 0.01))], M["road"])
    for i, dx in enumerate((-0.7, 0.7)):
        b, st, bl, hd = rtw_items(wx + dx, wy - 1.42, 0.0)
        ST[f"w_rtw{i}"] = [B(f"w_rtw{i}", b, M["rtw_w"], 0.015), B(f"w_rtw{i}_s", st, M["rtw_s"]), B(f"w_rtw{i}_b", bl, M["blau_l"]), B(f"w_rtw{i}_h", hd, M["hl"])]
    ANCH["wache"] = [Vector((wx, wy - 1.1, 0.4))]; ANCH["wache_tor"] = [Vector((wx - 0.7, wy - 1.05, 0.3))]
    # Rettungswagen auf der Straße (y=-4, fährt Richtung -x) und vor deinem Haus
    b, st, bl, hd = rtw_items(-3.0, -4.18, -math.pi / 2)
    ST["rtw_strasse"] = [B("s_rtw", b, M["rtw_w"], 0.015), B("s_rtw_s", st, M["rtw_s"]), B("s_rtw_b", bl, M["blau_l"]), B("s_rtw_h", hd, M["hl"])]
    ANCH["rtw_strasse"] = [Vector((-3.0, -4.18, 0.33))]
    b, st, bl, hd = rtw_items(-12.0, -6.75, math.pi)
    ST["rtw_haus"] = [B("h_rtw", b, M["rtw_w"], 0.015), B("h_rtw_s", st, M["rtw_s"]), B("h_rtw_b", bl, M["blau_l"]), B("h_rtw_h", hd, M["hl"])]
    ANCH["rtw_haus"] = [Vector((-12.0, -6.75, 0.33))]
    pts = [(wx - 0.7, wy - 0.9), (wx - 0.7, -4.0), (-12.0, -4.0), (-12.0, -6.6)]
    dense = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.2))
        dense += [Vector((x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n, 0.3)) for k in range(n)]
    ANCH["route_rtw"] = dense
    # ---------------- Funkmast (-10, -2)
    mx, my, H = -10.0, -2.0, 4.6
    legs = [((mx + sx * 0.22, my + sy * 0.22, H / 2), (0.035, 0.035, H)) for sx in (-1, 1) for sy in (-1, 1)]
    rings = [((mx, my + sy * 0.22, z), (0.47, 0.02, 0.02)) for z in [0.4 + 0.45 * k for k in range(10)] for sy in (-1, 1)]
    rings += [((mx + sx * 0.22, my, z), (0.02, 0.47, 0.02)) for z in [0.4 + 0.45 * k for k in range(10)] for sx in (-1, 1)]
    B("mast", legs + rings, M["metal"])
    B("mast_ant", [((mx + 0.3 * math.cos(a), my + 0.3 * math.sin(a), H - 0.35), (0.08 + 0.05 * abs(math.sin(a)), 0.08 + 0.05 * abs(math.cos(a)), 0.5)) for a in (0, 2.1, 4.2)], M["white"])
    B("mast_lampe", [((mx, my, H + 0.06), (0.08, 0.08, 0.08))], M["mast_rot"])
    B("mast_huette", [((mx + 0.9, my - 0.6, 0.2), (0.7, 0.5, 0.4))], M["grey"], 0.02)
    ANCH["mast_top"] = [Vector((mx, my, H - 0.2))]
    fw = [(-12.0, -8.0, 1.2), (mx, my, H - 0.3), (-6.0, 1.0, 1.0)]; dense = []
    for a, b in zip(fw, fw[1:]):
        n = max(2, int((Vector(b) - Vector(a)).length / 0.15)); dense += [Vector(a).lerp(Vector(b), k / n) for k in range(n)]
    ANCH["funk_weg"] = dense
    # ---------------- Küche (x=300): Mann, Frau, Handy, Fenster, Blaulicht, Retter
    X = 300
    ppl = []
    person(ppl, X - 0.05, 1.05, 0.0, "lie", 0.0, mi=(0, 1, 2))
    ST["k_mann"] = B("k_mann", ppl, [M["hemd"], M["haut"], M["hose"]], 0.03)
    fr = []; person(fr, X - 0.1, 0.38, 0.0, "kneel", 0.0, mi=(0, 1, 2))
    ST["k_frau"] = B("k_frau", fr, [M["strick"], M["haut"], M["hose"]], 0.03)
    ST["k_arme_auf"] = S.curve("k_arme_auf", [(X - 0.28, 0.48, 0.98), (X - 0.3, 0.55, 0.72), (X - 0.22, 0.62, 0.58)], 0.04, M["strick"])
    ST["k_arme_druck"] = S.curve("k_arme_druck", [(X - 0.27, 0.48, 0.98), (X - 0.15, 0.78, 0.55), (X - 0.08, 0.98, 0.25), (X + 0.08, 0.78, 0.55), (X + 0.07, 0.48, 0.98)], 0.04, M["strick"])
    B("k_handy", [((X + 0.42, 0.62, 0.008), (0.08, 0.16, 0.012))], M["handy"])
    ST["k_handy_l"] = B("k_handy_l", [((X + 0.42, 0.62, 0.016), (0.07, 0.145, 0.002))], M["handy_l"])
    ANCH["k_phone"] = [Vector((X + 0.385, 0.692, 0.018)), Vector((X + 0.455, 0.692, 0.018)), Vector((X + 0.455, 0.548, 0.018)), Vector((X + 0.385, 0.548, 0.018))]
    B("k_fenster", [((X - 2.47, 0.2, 1.4), (0.02, 1.2, 0.9))], M["ls_glas"])
    B("k_ofen", [((X + 1.3, 2.2, 0.45), (0.6, 0.55, 0.9)), ((X + 1.3, 2.2, 0.93), (1.6, 0.6, 0.04))], [M["grey"]])
    ANCH["k_uhr"] = [Vector((X + 1.1, 1.89, 0.8)), Vector((X + 1.5, 1.89, 0.8)), Vector((X + 1.5, 1.89, 0.66)), Vector((X + 1.1, 1.89, 0.66))]
    ANCH["k_mann"] = [Vector((X - 0.05, 1.05, 0.3))]
    import bpy
    bpy.ops.object.light_add(type="POINT", location=(X - 1.8, 0.2, 1.6)); L = bpy.context.object; L.data.energy = 0; L.data.color = (0.2, 0.4, 1.0); ST["k_blau"] = L
    bpy.ops.object.light_add(type="POINT", location=(X + 0.3, 0.6, 2.3)); L = bpy.context.object; L.data.energy = 60; L.data.color = (1.0, 0.75, 0.5); ST["k_licht"] = L
    bpy.ops.object.light_add(type="POINT", location=(X + 0.42, 0.62, 0.12)); L = bpy.context.object; L.data.energy = 0; L.data.color = (0.7, 0.85, 1.0); ST["k_handylicht"] = L
    rt = []
    person(rt, X + 1.5, -0.9, 0.0, "stand", math.pi * 0.85, mi=(0, 1, 2)); person(rt, X + 2.0, -0.2, 0.0, "stand", math.pi * 0.7, mi=(0, 1, 2))
    ST["k_retter"] = [B("k_retter", rt, [M["jacke"], M["haut"], M["hose"]], 0.03), B("k_defi", [((X + 0.55, 0.75, 0.15), (0.3, 0.2, 0.3))], M["defi"], 0.02)]
    # ---------------- Leitstelle innen (x=1200): Arbeitsplätze mit Monitoren, Figuren von hinten
    o = bpy.data.objects.get("ls_tisch")
    if o: bpy.data.objects.remove(o)
    desks, mons, chairs, tel = [], [], [], []
    disp = []
    for row, (yy, n) in enumerate(((0.6, 4), (-0.9, 4))):
        for k in range(n):
            x = 1200 - 2.55 + k * 1.7
            desks.append(((x, yy, 0.37), (1.4, 0.7, 0.05))); desks.append(((x, yy + 0.3, 0.18), (1.4, 0.06, 0.36)))
            for j, dx in enumerate((-0.42, 0, 0.42)):
                mons.append(((x + dx, yy + 0.18, 0.62), (0.4, 0.03, 0.26)))
                if row == 1 and k == 1 and j == 1:
                    ANCH["ls_mon"] = [Vector((x + dx - 0.19, yy + 0.16, 0.74)), Vector((x + dx + 0.19, yy + 0.16, 0.74)), Vector((x + dx + 0.19, yy + 0.16, 0.5)), Vector((x + dx - 0.19, yy + 0.16, 0.5))]
            tel.append(((x + 0.55, yy - 0.1, 0.41), (0.12, 0.08, 0.03)))
            person(disp, x, yy - 0.62, 0.0, "sit", 0.0, h=1.7, mi=(0, 1, 2))
            chairs.append(((x, yy - 0.68, 0.22), (0.4, 0.4, 0.44)))
    B("ls_desks", desks, M["desk"]); ST["ls_mons"] = B("ls_mons", mons, M["mon"]); B("ls_chairs", chairs, M["dark"], 0.03)
    ST["ls_tel"] = B("ls_tel", tel, M["ls_tel"])
    B("ls_disp", disp, [M["hemd"], M["haut"], M["hose"]], 0.03)
    hs = [((1200 - 2.55 + k * 1.7, yy - 0.74, 1.38), (0.26, 0.04, 0.04)) for yy in (0.6, -0.9) for k in range(4)]
    B("ls_headsets", hs, M["dark"])
    # ---------------- Straße 1969 (x=1600): Altbauten, Telefonzelle, Kirchturm mit Uhr
    X6 = 1600
    B("s69_boden", [((X6, 0, -0.01), (24, 16, 0.02))], M["ground"]); B("s69_strasse", [((X6, -1.2, 0.0), (24, 1.6, 0.02))], M["strasse69"])
    B("s69_gehweg", [((X6, 0.15, 0.03), (24, 1.1, 0.06))], M["grey"])
    rnd = random.Random(69); hh = []
    for i in range(8):
        x = X6 - 8 + i * 2.1; h = rnd.uniform(1.1, 1.7); hh.append(((x, 1.8, h / 2), (1.9, 2.2, h)))
    B("s69_haeuser", hh, M["altbau"], 0.02)
    B("s69_daecher", [((c[0], c[1], s_[2] + 0.12), (s_[0] + 0.1, s_[1] + 0.1, 0.24)) for c, s_ in hh], M["altdach"], 0.02)
    B("s69_fenster", [((X6 - 8 + i * 2.1 + dx, 0.69, z), (0.22, 0.02, 0.28)) for i in range(8) for dx in (-0.5, 0.5) for z in (0.4,)], M["win"])
    B("s69_zelle", [((X6 + 1.0, 0.25, 0.42), (0.5, 0.5, 0.84))], M["gelb"], 0.02)
    B("s69_zelle_l", [((X6 + 1.0, -0.005, 0.5), (0.4, 0.02, 0.55))], M["zelle_l"])
    B("s69_turm", [((X6 - 3.0, 3.2, 2.2), (1.0, 1.0, 4.4)), ((X6 - 3.0, 3.2, 4.7), (0.6, 0.6, 0.6))], M["altbau"], 0.02)
    r = 0.32; cy = 2.69; cz = 3.6
    ANCH["uhr69"] = [Vector((X6 - 3 - r, cy, cz + r)), Vector((X6 - 3 + r, cy, cz + r)), Vector((X6 - 3 + r, cy, cz - r)), Vector((X6 - 3 - r, cy, cz - r))]
    B("s69_lampe", [((X6 + 2.5, -0.3, 0.6), (0.05, 0.05, 1.2)), ((X6 + 2.5, -0.45, 1.2), (0.16, 0.3, 0.05))], M["metal"])
    ANCH["zelle"] = [Vector((X6 + 1.0, -0.02, 0.6))]
    # ---------------- 16 Uhren der Länder (x=1400, y=20..26)
    pf = []
    for k in range(16):
        cx, cy2 = 1400 - 4.5 + (k % 4) * 3.0, 20 + (k // 4) * 2.2
        pf.append(((cx, cy2 + 0.1, 0.55), (0.9, 0.12, 1.1)))
        rr = 0.36; ANCH[f"uhr16_{k}"] = [Vector((cx - rr, cy2 + 0.03, 0.75 + rr)), Vector((cx + rr, cy2 + 0.03, 0.75 + rr)), Vector((cx + rr, cy2 + 0.03, 0.75 - rr)), Vector((cx - rr, cy2 + 0.03, 0.75 - rr))]
    B("uhren16", pf, M["bar_g"], 0.03)
    # ---------------- Karten-Pins (Europa-Modellkarte bei y=+200)
    P = ANCH.get("karte_P")
    if P:
        for nm, ll in {"kassel": (9.48, 51.31), "berlin": (13.4, 52.5), "winnenden": (9.4, 48.88), "koblenz": (7.59, 50.36), "essen": (7.01, 51.46),
                       "muenchen": (11.58, 48.14), "paris": (2.35, 48.86), "london": (-0.13, 51.5), "lissabon": (-9.14, 38.72), "warschau": (21.0, 52.23),
                       "duesseldorf": (6.78, 51.23), "stuttgart": (9.18, 48.78), "wiesbaden": (8.24, 50.08)}.items():
            ANCH[f"pin_{nm}"] = [Vector((*P(*ll), 0.32))]
    # ---------------- Menschen auf dem Weg zur Wache (Leuchtturm)
    pp = []; rnd = random.Random(12)
    for _ in range(18):
        x, y = rnd.uniform(3.5, 8.5), rnd.uniform(-5.6, -4.4)
        pp.append(((x, y, 0.09), (0.06, 0.06, 0.16), 0)); pp.append(((x, y, 0.2), (0.05, 0.05, 0.05), 1))
    if "person" not in M: mat("person", (0.2, 0.22, 0.28, 1)); mat("kopf", (0.4, 0.3, 0.25, 1))
    ST["wache_leute"] = B("wache_leute", pp, [M["person"], M["kopf"]])


def state(stadt, st):
    S_ = stadt; ST, emit = S_.STATE_OBJ, S_.emit
    g = st.get
    if "k_handy_l" in ST:
        emit("handy_l", 3.0 * g("phone", 1)); ST["k_handylicht"].data.energy = 2.0 * g("phone", 1)
        pr = g("press", 0); ST["k_arme_auf"].hide_render = pr > 0.5; ST["k_arme_druck"].hide_render = pr <= 0.5
        ST["k_blau"].data.energy = 300 * g("blau", 0); ST["k_licht"].data.energy = 60 * g("k_licht", 1)
        for o in ST["k_retter"]: o.hide_render = not g("retter", 0)
    if "wache_tore" in ST:
        o, _ = ST["wache_tore"]; o.location.z = 0.5 * g("wache_tor", 0)
        emit("wache_in", 5.0 * g("wache_licht", 0)); emit("blau_l", 9.0 * g("blaulicht", 0))
        for o in ST["w_rtw0"]: o.hide_render = bool(g("rtw_weg", 0))
        for k in ("rtw_haus", "rtw_strasse"):
            for o in ST[k]: o.hide_render = not g(k, 0)
        emit("mon", 0.35 * (1 - g("ls_dark", 0))); emit("ls_tel", 3.0 * g("phones", 1)); emit("ls_glas", 2.5 * g("lights", 1.0) ** 0.5 if not g("ls_dark", 0) else 0.3)
        emit("mast_rot", 6.0 * g("mast_on", 1)); ST["wache_leute"].hide_render = not g("people_w", 0)
