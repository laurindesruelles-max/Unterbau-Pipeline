"""Unterbau-Modellstadt bei Nacht (Blender/bpy, keine Credits) – Renderer für das Bild-Drehbuch.

python3 engine/stadt.py shots.json OUTDIR [--w 1600 --h 900 --samples 10] [--only ID,ID]
shots.json: [{"id": "s012", "set": "stadt_total", "cam": {"loc": [x,y,z], "tgt": [x,y,z], "lens": 50},
              "A": {state…}, "B": {state…} | null, "anchors": ["uhr", "tafel", "screen", "route_autobahn"]}]
Pro Einstellung: OUTDIR/<id>_A.png, <id>_B.png (falls B), <id>_Z.exr (Tiefe), <id>.json (Projektion der Anker in Pixeln).
Zustände (state): lights 0..1 (Stadtfenster), mine 0/1 (dein Haus), trucks 0/1 (Lkw-Lichter), fill 0..1 (Regale/Lager),
gap 0/1 (Lücke im Milchfach), door 0..1 (Tor/Kühlschrank offen), tape 0/1 (Absperrband), day 0..1 (Tageslicht), grey 0/1 (Märkte grau).
Welt: Nachtblau, orange Lichter = echtes Licht (Emission an Fenstern/Lampen), kein Leuchteffekt. Tilt-Shift kommt im Compositing dazu.
Immer mit setsid nohup starten; nie zwei Blender-Prozesse parallel.
"""
import sys, os, math, json, random, argparse
import bpy, bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

C = dict(night=(0.010, 0.022, 0.055, 1), ground=(0.035, 0.05, 0.085, 1), road=(0.018, 0.022, 0.032, 1), bld=(0.13, 0.16, 0.22, 1),
         roof=(0.22, 0.25, 0.31, 1), white=(0.62, 0.64, 0.68, 1), orange=(1.0, 0.36, 0.06, 1), warm=(1.0, 0.58, 0.26, 1),
         cold=(0.55, 0.7, 1.0, 1), dark=(0.012, 0.012, 0.016, 1), wood=(0.33, 0.21, 0.12, 1), green=(0.25, 0.6, 0.35, 1),
         red=(0.8, 0.1, 0.06, 1), grass=(0.03, 0.06, 0.05, 1), earth=(0.2, 0.13, 0.08, 1))
M = {}

def mat(name, col, emit=0.0, rough=0.7, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col; b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Emission Color"].default_value = col; b.inputs["Emission Strength"].default_value = emit
    M[name] = m; return m

def emit(name, v):
    M[name].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = v

def mesh_obj(name, bm, m, bevel=0.0):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if isinstance(m, list):
        for mm in m: me.materials.append(mm)
    else:
        me.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2; md.limit_method = "ANGLE"
    return o

def boxes(name, items, m, bevel=0.0):
    """viele Quader in EINEM Objekt (schnell). items: (center, size[, matindex])"""
    bm = bmesh.new()
    for it in items:
        c, s = it[0], it[1]; mi = it[2] if len(it) > 2 else 0
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
        for f in {f for v in r["verts"] for f in v.link_faces}: f.material_index = mi
    return mesh_obj(name, bm, m, bevel)

def cyls(name, items, m, seg=24):
    bm = bmesh.new()
    for c, r, h in items:
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=h)
        for v in res["verts"]: v.co += Vector(c)
    o = mesh_obj(name, bm, m)
    for p in o.data.polygons: p.use_smooth = True
    return o

def curve(name, pts, depth, m, extrude=0.0):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"; sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (c[0], c[1], c[2], 1)
    cu.bevel_depth = depth; cu.extrude = extrude; cu.bevel_resolution = 2
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o)
    if m: cu.materials.append(m)
    return o

def text(name, s, loc, size, m, rot=(math.pi / 2, 0, 0)):
    cu = bpy.data.curves.new(name, "FONT"); cu.body = s; cu.size = size; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    try: cu.font = bpy.data.fonts.load("/usr/share/fonts/opentype/inter/Inter-Bold.otf", check_existing=True)
    except Exception: pass
    o = bpy.data.objects.new(name, cu); bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_euler = rot
    cu.materials.append(m); return o

ANCH = {}    # Name -> Liste 3D-Punkte (Ecken oder Pfad)
STATE_OBJ = {}

# ------------------------------------------------------------------ Stadt
def house_items(x, y, w, d, h, rnd, win_items, mine=False):
    items = [((x, y, h / 2), (w, d, h))]
    floors = max(1, int(h / 0.32)); cols = max(1, int(w / 0.22))
    for f in range(floors):
        z = 0.2 + f * 0.3
        if z > h - 0.1: break
        for c in range(cols):
            if rnd.random() < 0.45: continue
            xx = x - w / 2 + (c + 0.5) * w / cols
            win_items.append(((xx, y - d / 2 - 0.006, z), (w / cols * 0.45, 0.012, 0.13)))
            if rnd.random() < 0.5: win_items.append(((xx, y + d / 2 + 0.006, z), (w / cols * 0.45, 0.012, 0.13)))
    return items

def build_town():
    rnd = random.Random(7)
    mat("ground", C["ground"], rough=0.95); mat("road", C["road"], rough=0.45); mat("bld", C["bld"]); mat("roof", C["roof"])
    mat("white", C["white"]); mat("win", C["warm"], 7.0); mat("win_mine", C["warm"], 3.0); mat("orange", C["orange"], 0, 0.4)
    mat("sign", C["orange"], 6.0); mat("dark", C["dark"], rough=0.3); mat("lane", (0.5, 0.5, 0.45, 1), 0.3)
    mat("hl", C["warm"], 30.0); mat("tail", C["red"], 8.0); mat("grass", C["grass"], rough=1); mat("lamp", C["warm"], 12.0)
    mat("shop", (0.9, 0.95, 1.0, 1), 4.0); mat("clock", (0.95, 0.93, 0.85, 1), 1.2); mat("tafel", (0.02, 0.025, 0.035, 1), 0, 0.2)
    mat("tape", (0.9, 0.9, 0.9, 1), 0.0); mat("tape_r", C["red"]); mat("cross", C["green"], 5.0); mat("metal", (0.5, 0.52, 0.55, 1), 0, 0.35, 0.8)
    mat("grey", (0.06, 0.065, 0.075, 1))
    boxes("base", [((0, 0, -0.2), (96, 64, 0.4))], M["ground"], 0.1)
    # Straßenraster (Stadt in der Mitte, -16..16 x -12..12)
    roads = []
    for x in range(-16, 17, 4): roads.append(((x, 0, 0.005), (0.7, 24.7, 0.01)))
    for y in range(-12, 13, 4): roads.append(((0, y, 0.006), (32.7, 0.7, 0.01)))
    boxes("roads", roads, M["road"])
    lanes = [((x, y + 0.5, 0.012), (0.03, 0.5, 0.004)) for x in range(-16, 17, 4) for y in range(-12, 12, 2)]
    boxes("lanes", lanes, M["lane"])
    # Autobahn: Ring um die Stadt
    ring = [(-22, -16), (22, -16), (28, -10), (28, 12), (22, 18), (-22, 18), (-28, 12), (-28, -10), (-22, -16)]
    ring3 = [(x, y, 0.01) for x, y in ring]
    bm = bmesh.new(); seg_marks = []
    for (x1, y1, _), (x2, y2, _) in zip(ring3, ring3[1:]):
        d = Vector((x2 - x1, y2 - y1, 0)); L = d.length; d.normalize(); nrm = Vector((-d.y, d.x, 0)) * 0.9
        a0, b0 = Vector((x1, y1, 0.012)), Vector((x2, y2, 0.012)); ext = d * 0.9
        vs = [bm.verts.new(v) for v in (a0 - ext - nrm, b0 + ext - nrm, b0 + ext + nrm, a0 - ext + nrm)]; bm.faces.new(vs)
        for k in range(int(L / 1.0)):
            c = a0 + d * (k + 0.5); seg_marks.append(((c.x, c.y, 0.018), (abs(d.x) * 0.5 + 0.03, abs(d.y) * 0.5 + 0.03, 0.004)))
    mesh_obj("autobahn", bm, M["road"]); boxes("ab_marks", seg_marks, M["lane"])
    dense = []
    for (x1, y1, _), (x2, y2, _) in zip(ring3, ring3[1:]):
        L = math.hypot(x2 - x1, y2 - y1); n = max(2, int(L / 0.25))
        dense += [Vector((x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n, 0.15)) for k in range(n)]
    ANCH["route_autobahn"] = dense
    # Häuser in den Blöcken (nicht auf Sonderflächen)
    special = {(0, -8): "markt", (-12, -8): "haus", (0, 8): "rathaus", (-8, 8): "bahnhof", (8, -8): "apotheke",
               (12, 8): "klinik", (12, -8): "tankstelle"}
    items, win = [], []
    for bx in range(-14, 15, 4):
        for by in range(-10, 11, 4):
            key = (bx - 2 if bx > 0 else bx + 2, by)
            if any(abs(bx - sx) < 2.1 and abs(by - sy) < 2.1 for sx, sy in special): continue
            for i in range(2):
                for j in range(2):
                    x = bx - 0.8 + 1.6 * i + rnd.uniform(-0.1, 0.1); y = by - 0.8 + 1.6 * j + rnd.uniform(-0.1, 0.1)
                    h = rnd.choice([0.6, 0.9, 1.2, 1.5, 2.2]) * rnd.uniform(0.85, 1.15)
                    items += house_items(x, y, 1.25, 1.2, h, rnd, win)
    boxes("houses", items, M["bld"], 0.02); boxes("windows", win, M["win"])
    # Straßenlaternen
    lamps = [((x + 0.45, y + 0.45, 0.35), (0.04, 0.04, 0.7)) for x in range(-16, 17, 4) for y in range(-12, 13, 4)]
    boxes("lampposts", lamps, M["metal"]); boxes("lampheads", [((p[0][0], p[0][1], 0.72), (0.1, 0.1, 0.04)) for p in lamps], M["lamp"])
    # --- Dein Haus (-12,-8): Satteldach, eigene Fenster
    hx, hy = -12, -8
    boxes("haus_body", [((hx, hy, 0.45), (1.6, 1.3, 0.9))], M["bld"], 0.02)
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(hx - 0.85, hy - 0.72, 0.9), (hx + 0.85, hy - 0.72, 0.9), (hx + 0.85, hy + 0.72, 0.9), (hx - 0.85, hy + 0.72, 0.9),
                                     (hx - 0.85, hy, 1.45), (hx + 0.85, hy, 1.45)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]: bm.faces.new([v[i] for i in f])
    mesh_obj("haus_dach", bm, M["roof"])
    boxes("haus_win", [((hx - 0.4, hy - 0.66, 0.5), (0.42, 0.02, 0.32)), ((hx + 0.4, hy - 0.66, 0.5), (0.42, 0.02, 0.32)),
                       ((hx + 0.4, hy - 0.66, 1.0), (0.3, 0.02, 0.2))], M["win_mine"])
    ANCH["haus"] = [Vector((hx, hy - 0.7, 0.5))]; ANCH["haus_top"] = [Vector((hx, hy, 1.6))]
    # --- Markt (0,-8): Halle, oranges Band, Glasfront, Rampe hinten
    boxes("markt", [((0, -8, 0.55), (3.4, 2.6, 1.1))], M["bld"], 0.03)
    boxes("markt_band", [((0, -9.32, 0.95), (3.4, 0.04, 0.18))], M["sign"])
    boxes("markt_glas", [((0, -9.32, 0.4), (2.4, 0.03, 0.55))], M["shop"])
    boxes("markt_rampe", [((0.8, -6.55, 0.12), (1.4, 0.4, 0.24))], M["grey"])
    door = boxes("markt_tor", [((0.8, -6.68, 0.55), (0.9, 0.04, 0.6))], M["metal"]); STATE_OBJ["tor"] = (door, 0.55)
    boxes("markt_tor_licht", [((0.8, -6.66, 0.55), (0.86, 0.02, 0.56))], M["win"])
    ANCH["markt"] = [Vector((0, -9.4, 0.6))]; ANCH["rampe"] = [Vector((0.8, -6.3, 0.4))]
    # --- Rathaus (0,8) mit Uhrturm
    boxes("rathaus", [((0, 8, 0.6), (3.2, 2.0, 1.2)), ((0, 8, 1.9), (0.9, 0.9, 1.4))], M["bld"], 0.03)
    boxes("rathaus_dach", [((0, 8, 2.65), (1.0, 1.0, 0.1))], M["roof"])
    bm = bmesh.new(); res = bmesh.ops.create_circle(bm, cap_ends=True, segments=48, radius=0.34)
    for vv in res["verts"]: vv.co = Vector((vv.co.x, 7.535, 2.1 + vv.co.y))
    mesh_obj("uhr", bm, M["clock"])
    r = 0.34; ANCH["uhr"] = [Vector((-r, 7.52, 2.1 + r)), Vector((r, 7.52, 2.1 + r)), Vector((r, 7.52, 2.1 - r)), Vector((-r, 7.52, 2.1 - r))]
    boxes("rathaus_win", [((x, 6.99, z), (0.22, 0.02, 0.18)) for x in (-1.2, -0.7, 0.7, 1.2) for z in (0.35, 0.8)], M["win"])
    # --- Bahnhof (-8,8) mit Fallblatt-Anzeigetafel
    boxes("bahnhof", [((-8, 8, 0.5), (3.4, 1.6, 1.0))], M["bld"], 0.03)
    boxes("tafel_rahmen", [((-8, 7.15, 1.25), (2.2, 0.08, 0.7)), ((-8.9, 7.15, 0.95), (0.06, 0.06, 1.0)), ((-7.1, 7.15, 0.95), (0.06, 0.06, 1.0))], M["metal"])
    boxes("tafel", [((-8, 7.1, 1.25), (2.05, 0.02, 0.58))], M["tafel"])
    ANCH["tafel"] = [Vector((-9.02, 7.08, 1.54)), Vector((-6.98, 7.08, 1.54)), Vector((-6.98, 7.08, 0.96)), Vector((-9.02, 7.08, 0.96))]
    # --- Apotheke, Klinik, Tankstelle
    boxes("apotheke", [((8, -8, 0.45), (2.0, 1.6, 0.9))], M["bld"], 0.02)
    boxes("apo_kreuz", [((8, -8.82, 0.75), (0.08, 0.02, 0.24)), ((8, -8.82, 0.75), (0.24, 0.02, 0.08))], M["cross"])
    boxes("apo_glas", [((8, -8.82, 0.32), (1.2, 0.02, 0.4))], M["shop"])
    boxes("klinik", [((12, 8, 0.8), (3.2, 2.4, 1.6))], M["white"], 0.03)
    boxes("klinik_win", [((12 + dx, 6.79, z), (0.3, 0.02, 0.16)) for dx in (-1.1, -0.55, 0, 0.55, 1.1) for z in (0.4, 0.8, 1.2)], M["win"])
    boxes("tank_dach", [((12, -8, 0.75), (2.6, 1.6, 0.08))], M["white"], 0.01)
    boxes("tank_dachlicht", [((12, -8, 0.705), (2.4, 1.4, 0.01))], M["shop"])
    boxes("tank_stuetzen", [((12 + dx, -8 + dy, 0.37), (0.08, 0.08, 0.74)) for dx in (-1.1, 1.1) for dy in (-0.6, 0.6)], M["metal"])
    pumps = [((12 + dx, -8, 0.22), (0.22, 0.32, 0.44)) for dx in (-0.6, 0, 0.6)]
    boxes("tank_saeulen", pumps, M["grey"], 0.01)
    tape = []
    for dx in (-0.6, 0, 0.6):
        x = 12 + dx
        tape += [((x, -8.28, 0.3), (0.5, 0.01, 0.03)), ((x, -7.72, 0.3), (0.5, 0.01, 0.03)), ((x - 0.25, -8, 0.3), (0.01, 0.56, 0.03)), ((x + 0.25, -8, 0.3), (0.01, 0.56, 0.03))]
    STATE_OBJ["tape"] = boxes("tank_band", tape, M["tape_r"])
    ANCH["tankstelle"] = [Vector((12, -8.9, 0.4))]
    # --- Lkw auf Autobahn und Straßen (Lichter = Zustand trucks)
    tr_body, tr_hl = [], []
    pts = ANCH["route_autobahn"]
    for k in range(26):
        u = k / 26; seg = u * (len(pts) - 1); i = int(seg); f = seg - i
        p = pts[i].lerp(pts[i + 1], f); d = (pts[i + 1] - pts[i]).normalized()
        ang = math.atan2(d.y, d.x); off = Vector((-d.y, d.x, 0)) * 0.18
        c = p + off
        for dd, s in ((0.0, (0.9, 0.28, 0.32)),):
            tr_body.append(((c.x, c.y, 0.2), (0.9 * abs(math.cos(ang)) + 0.28 * abs(math.sin(ang)), 0.9 * abs(math.sin(ang)) + 0.28 * abs(math.cos(ang)), 0.32)))
        hp = c + d * 0.47
        tr_hl.append(((hp.x, hp.y, 0.12), (0.12 + 0.05 * abs(math.sin(ang)), 0.12 + 0.05 * abs(math.cos(ang)), 0.05)))
    STATE_OBJ["lkw_body"] = boxes("lkw_body", tr_body, M["white"], 0.02); STATE_OBJ["lkw_hl"] = boxes("lkw_hl", tr_hl, M["hl"])
    # --- Molkerei, Zentrallager, Notreserve, Tanklager (Stadtrand)
    boxes("molkerei", [((-22, 10, 0.6), (3.0, 2.0, 1.2))], M["bld"], 0.03)
    cyls("silos", [((-24.2, 9.2 + 0.8 * i, 1.2), 0.36, 2.4) for i in range(3)], M["white"])
    boxes("molk_rampe", [((-22, 8.95, 0.5), (1.6, 0.04, 0.5))], M["win"])
    ANCH["molkerei"] = [Vector((-22, 8.7, 0.3))]
    boxes("zlager", [((20, 10, 0.7), (6.0, 3.4, 1.4))], M["bld"], 0.03)
    boxes("zlager_docks", [((17.6 + 0.6 * i, 8.28, 0.4), (0.38, 0.03, 0.5)) for i in range(9)], M["win"])
    boxes("notreserve", [((-22, -11, 0.75), (5.0, 3.0, 1.5)), ((-22, -11, 1.55), (5.2, 3.2, 0.1))], M["grey"], 0.03)
    boxes("nr_zaun", [((-25.2 + 0.5 * k, -13.6, 0.25), (0.03, 0.03, 0.5)) for k in range(14)] + [((-22, -13.6, 0.45), (6.6, 0.02, 0.03)), ((-22, -13.6, 0.15), (6.6, 0.02, 0.03))], M["metal"])
    boxes("nr_rampen", [((-23.8 + 1.2 * k, -12.52, 0.35), (0.7, 0.04, 0.55)) for k in (0, 3)], M["metal"])
    boxes("nr_lampen", [((-24.5 + 1.6 * k, -12.56, 1.25), (0.12, 0.04, 0.04)) for k in range(4)], M["lamp"])
    boxes("notreserve_tor", [((-22, -12.52, 0.5), (1.4, 0.04, 0.9))], M["metal"])
    STATE_OBJ["nr_licht"] = boxes("notreserve_licht", [((-22, -12.55, 1.05), (0.25, 0.04, 0.06))], M["lamp"])
    ANCH["notreserve"] = [Vector((-22, -12.6, 0.5))]
    cyls("tanklager", [((22 + 1.6 * i, -12 + 1.6 * j, 0.5), 0.65, 1.0) for i in range(3) for j in range(2)], M["white"])

def build_karte():
    """Modell-Karte: Länder als extrudierte Platten (Natural Earth, public domain) – bei y=+200."""
    geo = json.load(open(os.path.join(os.path.dirname(__file__), "..", "assets", "geo", "europa.json")))
    mat("land", (0.10, 0.13, 0.19, 1), rough=0.9); mat("land_de", (0.2, 0.25, 0.36, 1), rough=0.9); mat("sea", (0.008, 0.016, 0.04, 1), rough=0.3)
    boxes("meer", [((0, 200, -0.3), (80, 60, 0.4))], M["sea"])
    bpy.ops.object.light_add(type="AREA", location=(0, 196, 28)); L = bpy.context.object; L.data.energy = 9000; L.data.size = 40; L.data.color = (0.6, 0.7, 1.0)
    lon0, lat0, k = 10.4, 51.2, 1.6
    def P(lon, lat): return ((lon - lon0) * k * math.cos(math.radians(lat0)), 200 + (lat - lat0) * k)
    for iso, polys in geo.items():
        if not isinstance(polys, list): continue
        for pi, poly in enumerate(polys):
            ring = poly[0] if poly and isinstance(poly[0][0], (list, tuple)) else poly
            if len(ring) < 4: continue
            bm = bmesh.new()
            vs = [bm.verts.new((*P(x, y), 0)) for x, y in ring[:-1]]
            try:
                f = bm.faces.new(vs)
            except ValueError:
                bm.free(); continue
            h = 0.28 if iso == "DE" else 0.12
            ex = bmesh.ops.extrude_face_region(bm, geom=[f]); [setattr(v, "co", v.co + Vector((0, 0, h))) for v in ex["geom"] if isinstance(v, bmesh.types.BMVert)]
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            mesh_obj(f"land_{iso}_{pi}", bm, M["land_de"] if iso == "DE" else M["land"])
    ANCH["karte_P"] = P
    # Autobahn-Hauptachsen DE (grob, als Lichtpfade)
    staedte = {"HH": (10.0, 53.55), "B": (13.4, 52.5), "K": (6.96, 50.94), "F": (8.68, 50.11), "M": (11.58, 48.14), "S": (9.18, 48.78),
               "H": (9.73, 52.37), "L": (12.37, 51.34), "N": (11.08, 49.45), "DO": (7.47, 51.51)}
    for a, b in [("HH", "H"), ("H", "DO"), ("DO", "K"), ("K", "F"), ("F", "N"), ("N", "M"), ("F", "S"), ("S", "M"), ("H", "L"), ("L", "B"), ("HH", "B"), ("L", "N")]:
        A, B = P(*staedte[a]), P(*staedte[b]); ANCH[f"de_{a}{b}"] = [Vector((A[0], A[1], 0.32)), Vector((B[0], B[1], 0.32))]
    ANCH["de_staedte"] = [Vector((*P(*v), 0.32)) for v in staedte.values()]

def build_aisle():
    """Supermarkt-Gang innen bei x=+200: zwei Regalreihen, Produkte als kleine Quader; Zustand fill/gap."""
    mat("floor", (0.18, 0.19, 0.21, 1), rough=0.25); mat("shelf", (0.55, 0.57, 0.6, 1), rough=0.4, metal=0.5)
    mat("ceil_l", (1, 0.97, 0.92, 1), 8.0); mat("pricetag", C["orange"], 2.0)
    pal = [(0.75, 0.72, 0.62, 1), (0.6, 0.15, 0.1, 1), (0.85, 0.7, 0.2, 1), (0.2, 0.35, 0.6, 1), (0.9, 0.9, 0.88, 1), (0.3, 0.5, 0.3, 1), (0.55, 0.3, 0.15, 1)]
    for i, c in enumerate(pal): mat(f"prod{i}", c, rough=0.5)
    X = 200
    boxes("a_floor", [((X, 0, -0.01), (6, 14, 0.02))], M["floor"]); boxes("a_ceil", [((X, 0, 2.6), (6, 14, 0.05))], M["bld"])
    boxes("a_lights", [((X, y, 2.55), (0.15, 1.6, 0.03)) for y in range(-6, 7, 2)], M["ceil_l"])
    sh = []
    for side in (-1, 1):
        x = X + side * 1.1
        sh.append(((x + side * 0.25, 0, 0.9), (0.05, 12, 1.8)))
        for z in (0.1, 0.5, 0.9, 1.3, 1.7): sh.append(((x, 0, z), (0.55, 12, 0.03)))
    boxes("a_shelves", sh, M["shelf"])
    boxes("a_tags", [((X + s * 0.82, y, z - 0.03), (0.01, 0.12, 0.05)) for s in (-1, 1) for y in range(-5, 6) for z in (0.5, 0.9, 1.3)], M["pricetag"])
    rnd = random.Random(3); prods = []
    for side in (-1, 1):
        x = X + side * 1.1
        for z in (0.12, 0.52, 0.92, 1.32):
            y = -5.9
            while y < 5.9:
                w = rnd.choice([0.12, 0.16, 0.2]); h = rnd.choice([0.16, 0.22, 0.28]); col = int((y + 6) * 0.7 + z * 3) % len(pal)
                for dx in (-0.12, 0.08):
                    prods.append(dict(c=(x + dx * side, y + w / 2, z + 0.015 + h / 2), s=(0.18, w * 0.92, h), m=col, y=y, z=z, side=side, r=rnd.random()))
                y += w
    STATE_OBJ["prods"] = prods
    ANCH["gang"] = [Vector((X, -6, 1.2)), Vector((X, 6, 1.2))]
    ANCH["milchfach"] = [Vector((X + 1.0, 1.2, 0.95)), Vector((X + 1.0, 2.0, 0.95)), Vector((X + 1.0, 2.0, 0.55)), Vector((X + 1.0, 1.2, 0.55))]

def set_products(fill=1.0, gap=0, empty_order="bottom"):
    o = bpy.data.objects.get("a_prods")
    if o: bpy.data.objects.remove(o)
    items = []
    for p in STATE_OBJ.get("prods", []):
        keep = p["r"] < fill
        if gap and p["side"] == 1 and 1.2 < p["y"] < 2.0 and 0.5 < p["z"] < 0.6: keep = False
        if keep: items.append((p["c"], p["s"], p["m"]))
    if items:
        boxes("a_prods", items, [M[f"prod{i}"] for i in range(7)], 0.01)

def build_fridge():
    """Küche mit Kühlschrank bei x=+300 (Tür = Zustand door)."""
    mat("kwand", (0.16, 0.17, 0.2, 1)); mat("kfloor", (0.2, 0.16, 0.12, 1), rough=0.6); mat("fridge", (0.8, 0.82, 0.84, 1), rough=0.3)
    mat("flicht", (0.85, 0.92, 1.0, 1), 6.0); mat("milch", (0.95, 0.95, 0.93, 1)); mat("milch_o", C["orange"])
    X = 300
    boxes("k_raum", [((X, 0, -0.01), (5, 5, 0.02)), ((X, 2.5, 1.3), (5, 0.05, 2.6)), ((X - 2.5, 0, 1.3), (0.05, 5, 2.6))], M["kwand"])
    boxes("k_boden", [((X, 0, 0.0), (4.9, 4.9, 0.01))], M["kfloor"])
    boxes("k_fridge", [((X, 2.43, 0.9), (0.8, 0.04, 1.8)), ((X - 0.38, 2.1, 0.9), (0.04, 0.7, 1.8)), ((X + 0.38, 2.1, 0.9), (0.04, 0.7, 1.8)), ((X, 2.1, 1.79), (0.8, 0.7, 0.04)), ((X, 2.1, 0.02), (0.8, 0.7, 0.04))], M["fridge"], 0.01)
    boxes("k_innen", [((X, 2.40, 0.95), (0.68, 0.02, 1.5))], M["flicht"])
    boxes("k_faecher", [((X, 2.0, z), (0.66, 0.5, 0.02)) for z in (0.5, 0.9, 1.3)], M["white"])
    boxes("k_milch", [((X - 0.15, 1.95, 1.03), (0.12, 0.12, 0.24)), ((X - 0.15, 1.888, 1.06), (0.12, 0.005, 0.04))], [M["milch"], M["milch_o"]])
    door = boxes("k_tuer", [((X, 1.73, 0.9), (0.8, 0.05, 1.78))], M["fridge"], 0.01)
    STATE_OBJ["k_tuer"] = door
    bpy.ops.object.light_add(type="POINT", location=(X, 1.5, 1.0)); L = bpy.context.object; L.data.energy = 0; L.data.color = (0.85, 0.92, 1.0); STATE_OBJ["k_lamp"] = L

def build_cut():
    """Querschnitt-Diorama bei x=+400: Straße mit Häusern oben, darunter Erdschichten mit Leitungen und Lieferwegen.
    Zustand door: 0 = Erde geschlossen (Deckel vorne), 1 = aufgeschnitten."""
    mat("erde", C["earth"], rough=1); mat("erde2", (0.14, 0.095, 0.06, 1), rough=1); mat("pipe_w", (0.15, 0.35, 0.7, 1), 0.4, 0.3)
    mat("pipe_g", (0.35, 0.36, 0.38, 1), 0, 0.4, 0.6); mat("route", C["orange"], 5.0)
    X = 400
    boxes("c_erde", [((X, 1.0, -0.6), (8, 1.0, 1.2)), ((X, 0, -1.6), (8, 3, 0.8)), ((X, 0, -1.19), (8, 3, 0.02))], [M["erde"], M["erde2"]])
    boxes("c_deckschicht", [((X, -0.5, -0.06), (8, 2.0, 0.08))], M["erde"])
    boxes("c_strasse", [((X, 0, 0.02), (8, 3, 0.04))], M["road"])
    rnd = random.Random(4); it, win = [], []
    for i in range(6):
        x = X - 3.3 + i * 1.3; h = rnd.uniform(0.6, 1.6); it += house_items(x, 0.9, 1.0, 1.0, h, rnd, win)
    boxes("c_haeuser", it, M["bld"], 0.02); boxes("c_win", win, M["win"])
    for name, y, z, r, m in (("c_rohr_w", -0.6, -0.5, 0.12, "pipe_w"), ("c_rohr_g", 0.3, -0.9, 0.18, "pipe_g"), ("c_route", 0.0, -0.25, 0.05, "route"), ("c_route2", -1.0, -1.4, 0.05, "route")):
        curve(name, [(X - 4, y, z), (X + 4, y, z)], r, M[m])
    STATE_OBJ["c_deckel"] = boxes("c_deckel", [((X, -0.5, -0.6), (8.0, 2.0, 1.1))], M["erde"])
    ANCH["cut"] = [Vector((X - 4, -1.5, -0.25)), Vector((X + 4, -1.5, -0.25))]

# ------------------------------------------------------------------ Details + weitere Schauplätze (22.11.2026)
def build_detail():
    rnd = random.Random(11)
    mat("tree", (0.025, 0.07, 0.045, 1), rough=0.9); mat("trunk", (0.08, 0.05, 0.03, 1)); mat("pool", (0.16, 0.09, 0.04, 1), 0.35)
    for i, c in enumerate([(0.5, 0.06, 0.05, 1), (0.08, 0.15, 0.35, 1), (0.6, 0.6, 0.62, 1), (0.05, 0.05, 0.06, 1), (0.25, 0.3, 0.33, 1)]):
        mat(f"car{i}", c, rough=0.35, metal=0.4)
    # Dachkanten + Dachaufbauten auf allen Häusern
    hs = bpy.data.objects["houses"]; caps, ac = [], []
    me = hs.data; import collections
    # Häuser aus Bounding-Boxen der Mesh-Inseln (je 8 Vertices = 1 Quader)
    vs = [hs.matrix_world @ v.co for v in me.vertices]
    for k in range(0, len(vs), 8):
        q = vs[k:k + 8]; xs = [v.x for v in q]; ys = [v.y for v in q]; zs = [v.z for v in q]
        cx, cy, top = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(zs); w, d = max(xs) - min(xs), max(ys) - min(ys)
        caps.append(((cx, cy, top + 0.02), (w + 0.05, d + 0.05, 0.04)))
        if rnd.random() < 0.5: ac.append(((cx + rnd.uniform(-w / 4, w / 4), cy + rnd.uniform(-d / 4, d / 4), top + 0.08), (0.18, 0.14, 0.1)))
    boxes("dachkanten", caps, M["roof"]); boxes("dachaufbauten", ac, M["grey"], 0.01)
    # Lichtkegel unter den Laternen (Fake-Licht auf dem Boden)
    bm = bmesh.new()
    for x in range(-16, 17, 4):
        for y in range(-12, 13, 4):
            r = bmesh.ops.create_circle(bm, cap_ends=True, segments=24, radius=0.32)
            for v in r["verts"]: v.co += Vector((x + 0.45, y + 0.45, 0.014))
    o = mesh_obj("lichtkegel", bm, M["pool"]); STATE_OBJ["pools"] = o
    # Bäume außerhalb der Stadt und in Lücken
    tr, tk = [], []
    for _ in range(420):
        x, y = rnd.uniform(-46, 46), rnd.uniform(-31, 31)
        if abs(x) < 17 and abs(y) < 13: continue
        if (abs(x) > 21 and abs(x) < 29 and -17 < y < 19) or (abs(y + 16) < 1.6 or abs(y - 18) < 1.6) and abs(x) < 29: continue
        if (-26 < x < -16 and -15 < y < -8) or (15 < x < 25 and 7 < y < 13) or (-26 < x < -19 and 7 < y < 13) or (20 < x < 27 and -15 < y < -9) or (29 < x < 38 and -6 < y < 10): continue
        h = rnd.uniform(0.5, 1.1); tr.append(((x, y, 0.15 + h / 2), h * 0.38, h)); tk.append(((x, y, 0.08), (0.06, 0.06, 0.16)))
    bm = bmesh.new()
    for c, r, h in tr:
        res = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=0.02, depth=h)
        for v in res["verts"]: v.co += Vector(c)
    mesh_obj("baeume", bm, M["tree"]); boxes("staemme", tk, M["trunk"])
    # Parkende Autos an den Straßenrändern
    cars = []
    for _ in range(160):
        if rnd.random() < 0.5:
            x = rnd.choice(range(-16, 17, 4)) + rnd.choice([-0.42, 0.42]); y = rnd.uniform(-11.5, 11.5); s = (0.16, 0.34, 0.12)
        else:
            y = rnd.choice(range(-12, 13, 4)) + rnd.choice([-0.42, 0.42]); x = rnd.uniform(-15.5, 15.5); s = (0.34, 0.16, 0.12)
        if abs(x + 12) < 1.5 and abs(y + 8) < 1.5: continue
        cars.append(((x, y, 0.07), s, rnd.randrange(5)))
    boxes("autos", cars, [M[f"car{i}"] for i in range(5)], 0.02)
    # Lkw: Fahrerhaus + Auflieger statt Kiste
    bpy.data.objects.remove(STATE_OBJ["lkw_body"]); bpy.data.objects.remove(STATE_OBJ["lkw_hl"])
    body, hl, tail = [], [], []
    pts = ANCH["route_autobahn"]; n = len(pts)
    for k in range(0, n, max(1, n // 34)):
        p = pts[k]; q = pts[min(k + 1, n - 1)]; d = (q - p); d.z = 0
        if d.length < 1e-4: continue
        d.normalize(); side = Vector((-d.y, d.x, 0)) * (0.35 if (k // (n // 34)) % 2 else -0.35)
        c = p + side; c.z = 0
        def ob(center, lx, ly, h):
            return ((center.x, center.y, h / 2 + 0.03), (abs(d.x) * lx + abs(d.y) * ly, abs(d.y) * lx + abs(d.x) * ly, h))
        body.append(ob(c - d * 0.12, 0.7, 0.24, 0.3) + (0,)); body.append(ob(c + d * 0.35, 0.2, 0.24, 0.26) + (1,))
        f = c + d * 0.46; hl.append(((f.x, f.y, 0.08), (0.05 + abs(d.y) * 0.16, 0.05 + abs(d.x) * 0.16, 0.04)))
        b = c - d * 0.48; tail.append(((b.x, b.y, 0.1), (0.04 + abs(d.y) * 0.18, 0.04 + abs(d.x) * 0.18, 0.03)))
    STATE_OBJ["lkw_body"] = boxes("lkw_body", body, [M["white"], M["orange"]], 0.015)
    STATE_OBJ["lkw_hl"] = boxes("lkw_hl", hl + tail, M["hl"])
    # Wiesen/Felder am Stadtrand
    boxes("felder", [((x, y, 0.004), (7.5, 5.5, 0.006)) for x, y in ((-38, 22), (-38, -22), (38, 22), (38, -22), (0, 26), (0, -27))], M["grass"])

def build_racks(name, X, kind="kisten", rows=3, levels=4, light=(1, 0.95, 0.85)):
    """Hochregal-Halle bei x=X: kind kisten|saecke|weiss|klein. Zustand rfill."""
    rnd = random.Random(len(name))
    mat(f"{name}_l", (*light, 1), 7.0)
    boxes(f"{name}_boden", [((X, 0, -0.01), (10, 14, 0.02))], M["floor"]); boxes(f"{name}_decke", [((X, 0, 4.2), (10, 14, 0.05))], M["bld"])
    boxes(f"{name}_lampen", [((X + dx, y, 4.1), (0.12, 1.8, 0.04)) for dx in (-2, 0, 2) for y in range(-6, 7, 3)], M[f"{name}_l"])
    rk, items = [], []
    pal = {"kisten": [(0.7, 0.55, 0.35, 1), (0.6, 0.15, 0.1, 1), (0.85, 0.75, 0.3, 1), (0.25, 0.4, 0.65, 1)], "saecke": [(0.72, 0.66, 0.5, 1), (0.6, 0.55, 0.42, 1), (0.8, 0.8, 0.78, 1)],
           "weiss": [(0.85, 0.88, 0.9, 1), (0.75, 0.8, 0.85, 1)], "klein": [(0.9, 0.9, 0.88, 1), (0.3, 0.5, 0.75, 1), (0.85, 0.3, 0.2, 1)]}[kind]
    for i, c in enumerate(pal): mat(f"{name}_p{i}", c, rough=0.8)
    for r in range(rows):
        x = X - 3 + r * 3
        for lv in range(levels):
            z = 0.05 + lv * 0.95; rk.append(((x, 0, z), (1.1, 12, 0.05)))
            for y in [k * 1.2 - 5.4 for k in range(10)]:
                for side in (-0.28, 0.28):
                    if kind == "saecke":
                        for st in range(3): items.append(dict(c=(x + side, y, z + 0.12 + st * 0.2), s=(0.5, 1.0, 0.18), m=rnd.randrange(len(pal)), r=rnd.random()))
                    else:
                        hh = rnd.uniform(0.4, 0.75); items.append(dict(c=(x + side, y, z + 0.03 + hh / 2), s=(0.5, 1.05, hh), m=rnd.randrange(len(pal)), r=rnd.random()))
        rk += [((x + sx, y, levels * 0.95 / 2), (0.06, 0.06, levels * 0.95)) for sx in (-0.55, 0.55) for y in (-6, -2, 2, 6)]
    boxes(f"{name}_regal", rk, M["orange"] if kind in ("kisten", "saecke") else M["shelf"])
    STATE_OBJ.setdefault("racks", {})[name] = (items, len(pal))
    ANCH[f"{name}_zaehler"] = [Vector((X - 4.5, -6.9, 3.3)), Vector((X - 2.5, -6.9, 3.3)), Vector((X - 2.5, -6.9, 2.5)), Vector((X - 4.5, -6.9, 2.5))]
    boxes(f"{name}_tafel", [((X - 3.5, -6.95, 2.9), (2.1, 0.04, 0.9))], M["tafel"])
    set_rack(name, 1.0)

def set_rack(name, fill):
    o = bpy.data.objects.get(f"{name}_ware")
    if o: bpy.data.objects.remove(o)
    items, npal = STATE_OBJ["racks"][name]
    keep = [(it["c"], it["s"], it["m"]) for it in items if it["r"] < fill]
    if keep: boxes(f"{name}_ware", keep, [M[f"{name}_p{i}"] for i in range(npal)], 0.01)

def build_cab(X=1100):
    mat("cab_in", (0.05, 0.055, 0.065, 1), rough=0.6); mat("dash_l", (1.0, 0.55, 0.2, 1), 3.0); mat("skin", (0.35, 0.25, 0.2, 1)); mat("shirt", (0.12, 0.16, 0.22, 1))
    boxes("cab_raum", [((X, 0, 0), (3, 3, 0.05)), ((X, 0.9, 0.6), (2.4, 0.6, 0.25)), ((X - 1.3, 0, 1.0), (0.05, 3, 2.0)), ((X, -1.0, 1.9), (3, 1.2, 0.05))], M["cab_in"])
    boxes("cab_dash_l", [((X + dx, 0.62, 0.74), (0.12, 0.01, 0.05)) for dx in (-0.6, -0.4, 0.3)], M["dash_l"])
    whl = cyls("cab_lenkrad", [((X - 0.5, 0.55, 0.95), 0.22, 0.04)], M["dark"], 32)
    bpy.ops.object.light_add(type="POINT", location=(X - 0.2, 0.3, 1.2)); Lc = bpy.context.object; Lc.data.energy = 90; Lc.data.color = (1.0, 0.7, 0.4)
    bpy.ops.object.light_add(type="AREA", location=(X, -1.2, 1.8)); La = bpy.context.object; La.data.energy = 60; La.data.size = 1.5; La.data.color = (0.6, 0.7, 1.0)
    boxes("cab_sitz", [((X - 0.5, -0.2, 0.45), (0.5, 0.5, 0.12)), ((X - 0.5, -0.45, 0.85), (0.5, 0.1, 0.8))], M["dark"])
    STATE_OBJ["fahrer"] = [boxes("fahrer_k", [((X - 0.5, -0.25, 0.9), (0.42, 0.26, 0.55))], M["shirt"], 0.08), cyls("fahrer_kopf", [((X - 0.5, -0.25, 1.32), 0.12, 0.22)], M["skin"])]
    # Blick durch die Frontscheibe: Straße bei Nacht
    boxes("cab_strasse", [((X, 12, -0.6), (6, 22, 0.05))], M["road"]); boxes("cab_marks", [((X, y, -0.57), (0.06, 0.6, 0.01)) for y in range(2, 24, 2)], M["lane"])
    ANCH["cab_strasse"] = [Vector((X + 0.3 + 0.05 * k, 3 + k * 0.5, -0.5)) for k in range(40)]

def build_leitstand(X=1200):
    mat("screen", (0.01, 0.012, 0.02, 1), 0, 0.1); mat("desk", (0.12, 0.13, 0.16, 1), rough=0.4)
    boxes("ls_raum", [((X, 0, 0), (8, 6, 0.05)), ((X, 2.6, 1.5), (8, 0.05, 3)), ((X, 0, 3), (8, 6, 0.05))], M["bld"])
    bpy.ops.object.light_add(type="AREA", location=(X, -1, 2.8)); Ll = bpy.context.object; Ll.data.energy = 250; Ll.data.size = 4; Ll.data.color = (0.6, 0.7, 1.0)
    boxes("ls_tisch", [((X, 0.6, 0.45), (5, 0.9, 0.9))], M["desk"])
    boxes("ls_lampen", [((X + dx, 0, 2.95), (1.2, 0.1, 0.03)) for dx in (-2.5, 0, 2.5)], M["ceil_l"])
    scr = []
    for name, cx in (("screen_l", -2.1), ("screen_c", 0), ("screen_r", 2.1)):
        scr.append(((X + cx, 2.5, 1.7), (1.9, 0.06, 1.1)))
        ANCH[name] = [Vector((X + cx - 0.9, 2.46, 2.22)), Vector((X + cx + 0.9, 2.46, 2.22)), Vector((X + cx + 0.9, 2.46, 1.18)), Vector((X + cx - 0.9, 2.46, 1.18))]
    boxes("ls_screens", scr, M["screen"])
    STATE_OBJ["alarm"] = boxes("ls_alarm", [((X + dx, 1.0, 0.92), (0.1, 0.1, 0.04)) for dx in (-1.5, 0, 1.5)], M["sign"])

def build_markt_cut(X=1300):
    """Supermarkt im Querschnitt: großer Verkaufsraum, dahinter winziger Lagerraum."""
    boxes("mc_boden", [((X, 0, -0.01), (8, 4, 0.02)), ((X, 0, -0.3), (8.4, 4.4, 0.6))], [M["floor"], M["ground"]])
    boxes("mc_waende", [((X, 2.0, 1.2), (8, 0.06, 2.4)), ((X + 4, 0, 1.2), (0.06, 4, 2.4)), ((X - 4, 0, 1.2), (0.06, 4, 2.4)), ((X + 2.6, 0.6, 1.2), (0.06, 2.8, 2.4))], M["bld"])
    boxes("mc_dach", [((X, 0.4, 2.42), (8, 3.2, 0.05))], M["roof"])
    sh, pr = [], []; rnd = random.Random(9)
    for r in range(4):
        x = X - 3.2 + r * 1.4
        sh.append(((x, 0.4, 0.9), (0.45, 2.6, 0.04)))
        for z in (0.1, 0.5, 0.9, 1.3): sh.append(((x, 0.4, z), (0.5, 2.6, 0.03)))
        for z in (0.12, 0.52, 0.92, 1.32):
            for y in [k * 0.2 - 0.85 for k in range(13)]: pr.append(((x + rnd.choice([-0.12, 0.12]), y, z + 0.11), (0.18, 0.17, 0.2), rnd.randrange(7)))
    boxes("mc_regale", sh, M["shelf"]); boxes("mc_ware", pr, [M[f"prod{i}"] for i in range(7)], 0.01)
    boxes("mc_lager", [((X + 3.3, 1.0, 0.15), (0.5, 0.5, 0.3)), ((X + 3.3, 1.0, 0.45), (0.4, 0.4, 0.3))], M["prod0"], 0.01)
    boxes("mc_lager_l", [((X + 3.3, 0.6, 2.35), (0.4, 0.3, 0.03))], M["lamp"]); boxes("mc_licht", [((X - 0.7, 0.4, 2.36), (4.5, 0.3, 0.03))], M["ceil_l"])
    ANCH["mc_lager"] = [Vector((X + 2.65, -1.1, 2.3)), Vector((X + 3.95, -1.1, 2.3)), Vector((X + 3.95, -1.1, 0.02)), Vector((X + 2.65, -1.1, 0.02))]

def build_bars(X=1400):
    """Modellgelände für Zahlen: Häuserzeilen (Balken), 100-Häuser-Raster (Prozent), Eiffeltürme, Tage-Skala."""
    mat("bar_o", C["orange"], 1.5, 0.5); mat("bar_g", (0.3, 0.34, 0.42, 1)); mat("pct_on", C["orange"], 3.0)
    boxes("bars_boden", [((X, 0, -0.01), (30, 30, 0.02))], M["ground"])
    ANCH["bars_base"] = [Vector((X - 6, -3, 0)), Vector((X + 6, -3, 0))]
    # Tage-Skala 1..5 (Platten mit Ziffern)
    for k in range(5):
        boxes(f"tag{k}", [((X - 4 + 2 * k, 8, 0.05), (1.7, 1.7, 0.1))], M["bar_g"], 0.02)
        text(f"tagz{k}", str(k + 1), (X - 4 + 2 * k, 8, 0.11), 1.0, M["clock"], rot=(0, 0, 0))
        ANCH[f"tag{k + 1}"] = [Vector((X - 4.85 + 2 * k, 8.85, 0.12)), Vector((X - 3.15 + 2 * k, 8.85, 0.12)), Vector((X - 3.15 + 2 * k, 7.15, 0.12)), Vector((X - 4.85 + 2 * k, 7.15, 0.12))]

def set_bars(vals, X=1400):
    """vals: Liste (höhe, orange?) -> Häuserzeilen nebeneinander; Höhe in Häusern."""
    for n in ("bars_haeuser", "bars_haeuser_o"):
        o = bpy.data.objects.get(n)
        if o: bpy.data.objects.remove(o)
    g, o_ = [], []
    for i, (h, orange) in enumerate(vals):
        x = X - (len(vals) - 1) * 1.2 + i * 2.4
        for k in range(int(round(h))):
            (o_ if orange else g).append(((x, -2 + (k % 6) * 0.0, 0.25 + k * 0.5), (1.6, 1.6, 0.46)))
    if g: boxes("bars_haeuser", g, M["bar_g"], 0.03)
    if o_: boxes("bars_haeuser_o", o_, M["bar_o"], 0.03)

def set_pct(n_on, X=1400, n=100, cols=10, groups=None):
    for nm in ("pct_aus", "pct_an"):
        o = bpy.data.objects.get(nm)
        if o: bpy.data.objects.remove(o)
    a, b = [], []
    for k in range(n):
        r, c = divmod(k, cols); it = ((X - 4.5 + c, -6 - r, 0.25), (0.7, 0.7, 0.5))
        (b if k < n_on else a).append(it)
    if a: boxes("pct_aus", a, M["bar_g"], 0.03)
    if b: boxes("pct_an", b, M["pct_on"], 0.03)

def set_eiffel(n, X=1400):
    o = bpy.data.objects.get("eiffel")
    if o: bpy.data.objects.remove(o)
    it = []
    for k in range(n):
        cx, cy = X - 9 + (k % 12) * 1.5, 10 + (k // 12) * 1.5
        for j, (w, h) in enumerate(((0.9, 0.5), (0.6, 0.5), (0.35, 0.6), (0.15, 0.7))):
            it.append(((cx, cy, 0.25 + sum(x[1] for x in ((0.9, 0.5), (0.6, 0.5), (0.35, 0.6), (0.15, 0.7))[:j]) + h / 2 - 0.25), (w, w, h)))
    if it: boxes("eiffel", it, M["metal"], 0.01)

def build_rastplatz():
    """Rastplatz östlich der Autobahn (x 31..37): Reihen abgestellter Lkw, Figuren."""
    boxes("rp_platz", [((34, 2, 0.008), (6.5, 12, 0.01))], M["road"])
    boxes("rp_marks", [((34 + dx, 2 + y, 0.015), (0.03, 0.9, 0.003)) for dx in (-2.4, -0.8, 0.8, 2.4) for y in range(-5, 6)], M["lane"])
    rnd = random.Random(5); body = []
    for dx in (-1.6, 0, 1.6):
        for y in range(-5, 6):
            if rnd.random() < 0.15: continue
            body.append(((34 + dx, 2 + y * 0.95 - 0.12, 0.2), (0.28, 0.7, 0.3), 0)); body.append(((34 + dx, 2 + y * 0.95 + 0.35, 0.16), (0.28, 0.2, 0.26), 1))
    boxes("rp_lkw", body, [M["white"], M["orange"]], 0.015)
    boxes("rp_lampen", [((31, y, 0.5), (0.04, 0.04, 1.0)) for y in range(-3, 9, 3)], M["metal"])
    boxes("rp_lampenk", [((31.1, y, 1.0), (0.2, 0.08, 0.04)) for y in range(-3, 9, 3)], M["lamp"])
    ppl = []
    for _ in range(40):
        x, y = rnd.uniform(32, 36), rnd.uniform(-3, 7)
        ppl.append(((x, y, 0.09), (0.06, 0.06, 0.16), 0)); ppl.append(((x, y, 0.2), (0.05, 0.05, 0.05), 1))
    mat("person", (0.2, 0.22, 0.28, 1)); mat("kopf", (0.4, 0.3, 0.25, 1))
    STATE_OBJ["rp_people"] = boxes("rp_leute", ppl, [M["person"], M["kopf"]])
    boxes("rp_transparent", [((33.2, 2.4, 0.42), (0.02, 1.4, 0.3))], M["white"])
    ANCH["rastplatz"] = [Vector((34, -4.3, 0.6))]

def build_wasserwerk():
    mat("wasser", (0.05, 0.15, 0.3, 1), 0.3, 0.05)
    boxes("ww_becken", [((-38 + 2.2 * i, -6, 0.1), (2.0, 3.0, 0.2)) for i in range(3)], M["grey"], 0.02)
    boxes("ww_wasser", [((-38 + 2.2 * i, -6, 0.19), (1.8, 2.8, 0.02)) for i in range(3)], M["wasser"])
    boxes("ww_halle", [((-36, -2.2, 0.5), (4.5, 2.0, 1.0))], M["bld"], 0.03)
    boxes("ww_win", [((-37.5 + 0.6 * k, -3.21, 0.6), (0.25, 0.02, 0.2)) for k in range(6)], M["win"])

def build_haus_vorrat(X=300):
    """In der Küche (build_fridge): Vorratsregal, Wasserflaschen, zwei Putzeimer. Zustand vorrat 0..1, wasser 0..20."""
    mat("flasche", (0.6, 0.75, 0.9, 1), 0.0, 0.05); mat("eimer", (0.2, 0.35, 0.7, 1), rough=0.4)
    boxes("hv_regal", [((X - 1.5, 2.3, z), (1.2, 0.35, 0.03)) for z in (0.3, 0.7, 1.1, 1.5)] + [((X - 1.5 + sx, 2.3, 0.9), (0.03, 0.35, 1.8)) for sx in (-0.6, 0.6)], M["wood"] if "wood" in M else mat("wood", C["wood"]))
    rnd = random.Random(2); it = []
    for z in (0.32, 0.72, 1.12, 1.52):
        for k in range(8): it.append(dict(c=(X - 2.0 + k * 0.14, 2.3, z + 0.1), s=(0.11, 0.2, 0.18 + rnd.random() * 0.06), m=rnd.randrange(7), r=rnd.random()))
    STATE_OBJ["hv_items"] = it
    boxes("hv_eimer", [((X + 1.3, 1.6, 0.18), (0.3, 0.3, 0.36)), ((X + 1.7, 1.6, 0.18), (0.3, 0.3, 0.36))], M["eimer"], 0.05)
    ANCH["hv_regal"] = [Vector((X - 2.15, 2.1, 1.9)), Vector((X - 0.85, 2.1, 1.9)), Vector((X - 0.85, 2.1, 1.7)), Vector((X - 2.15, 2.1, 1.7))]

def set_vorrat(fill, wasser):
    for nm in ("hv_ware", "hv_flaschen"):
        o = bpy.data.objects.get(nm)
        if o: bpy.data.objects.remove(o)
    keep = [(i["c"], i["s"], i["m"]) for i in STATE_OBJ["hv_items"] if i["r"] < fill]
    if keep: boxes("hv_ware", keep, [M[f"prod{i}"] for i in range(7)], 0.01)
    fl = [((300 + 0.6 + (k % 5) * 0.13, 1.2 + (k // 5) * 0.13, 0.14), (0.1, 0.1, 0.28)) for k in range(int(wasser / 2))]
    if fl: boxes("hv_flaschen", fl, M["flasche"], 0.03)

def build_ladung(X=1500):
    boxes("ld_boden", [((X, 0, 0.3), (1.2, 4, 0.06)), ((X - 0.6, 0, 0.9), (0.04, 4, 1.2)), ((X, 2, 0.9), (1.2, 0.04, 1.2))], M["white"])
    it = []
    for k in range(5):
        y = -1.5 + k * 0.75
        it.append(((X, y, 0.36), (1.0, 0.7, 0.06), 0)); it.append(((X, y, 0.75), (0.95, 0.65, 0.7), 1 if k != 3 else 2))
    mat("ld_milch", (0.92, 0.92, 0.9, 1))
    boxes("ld_paletten", it, [M["wood"] if "wood" in M else mat("wood", C["wood"]), M["prod0"], M["ld_milch"]], 0.01)
    ANCH["ld_milch"] = [Vector((X + 0.5, 0.4, 1.12)), Vector((X + 0.5, 0.4 + 0.66, 1.12)), Vector((X + 0.5, 0.4 + 0.66, 0.4)), Vector((X + 0.5, 0.4, 0.4))]

def build_extra_town():
    # Mülltonnen an deinem Haus, Geldautomat am Markt, Figuren vor dem Markt / an der Tankstelle
    mat("tonne", (0.1, 0.2, 0.12, 1)); mat("atm", (0.3, 0.6, 0.9, 1), 2.0)
    boxes("muell", [((-10.9 + 0.22 * k, -9.0, 0.12), (0.18, 0.18, 0.24)) for k in range(4)], M["tonne"], 0.02)
    STATE_OBJ["muell_voll"] = boxes("muell_voll", [((-10.9 + 0.22 * k + 0.05, -9.25, 0.05), (0.14, 0.14, 0.1)) for k in range(6)] + [((-10.4, -9.3, 0.06), (0.3, 0.2, 0.12))], M["grey"], 0.03)
    boxes("atm_box", [((1.4, -9.33, 0.3), (0.3, 0.06, 0.5))], M["grey"]); STATE_OBJ["atm"] = boxes("atm_screen", [((1.4, -9.37, 0.38), (0.18, 0.01, 0.12))], M["atm"])
    ANCH["atm"] = [Vector((1.31, -9.38, 0.44)), Vector((1.49, -9.38, 0.44)), Vector((1.49, -9.38, 0.32)), Vector((1.31, -9.38, 0.32))]
    rnd = random.Random(3); ppl = []
    for _ in range(30):
        x, y = rnd.uniform(-1.5, 1.5), rnd.uniform(-10.4, -9.6); ppl.append(((x, y, 0.09), (0.06, 0.06, 0.16), 0)); ppl.append(((x, y, 0.2), (0.05, 0.05, 0.05), 1))
    if "person" not in M: mat("person", (0.2, 0.22, 0.28, 1)); mat("kopf", (0.4, 0.3, 0.25, 1))
    STATE_OBJ["markt_people"] = boxes("markt_leute", ppl, [M["person"], M["kopf"]])

def apply_state(st):
    def g(k, d): return st.get(k, d)
    emit("win", 7.0 * g("lights", 1.0)); emit("win_mine", 3.0 * g("mine", 1)); emit("hl", 30.0 * g("trucks", 1)); emit("lamp", 12.0 * g("lights", 1.0) ** 0.5)
    emit("shop", 4.0 * (0.25 if g("grey", 0) else 1.0) * g("lights", 1.0) ** 0.3); emit("sign", 6.0 * (0.0 if g("grey", 0) else 1.0))
    if "tape" in STATE_OBJ: STATE_OBJ["tape"].hide_render = not g("tape", 0)
    for k in ("lkw_body", "lkw_hl"):
        if k in STATE_OBJ: STATE_OBJ[k].hide_render = not g("lkw", 1)
    if "tor" in STATE_OBJ:
        o, z0 = STATE_OBJ["tor"]; o.location.z = 0.5 * g("door", 0)
    if "k_tuer" in STATE_OBJ:
        o = STATE_OBJ["k_tuer"]; a = g("door", 0)
        o.rotation_mode = "XYZ"; o.location = (0, 0, 0)
        piv = Vector((300 + 0.42, 1.73, 0)); o.matrix_world = __import__("mathutils").Matrix.Translation(piv) @ __import__("mathutils").Matrix.Rotation(-a * 1.9, 4, "Z") @ __import__("mathutils").Matrix.Translation(-piv)
        emit("flicht", 2.2 * a); STATE_OBJ["k_lamp"].data.energy = 20 * a
    if "fill" in st or "gap" in st: set_products(g("fill", 1.0), g("gap", 0))
    if "rfill" in st:
        for nm in STATE_OBJ.get("racks", {}): set_rack(nm, g("rfill", 1.0))
    if "bars" in st: set_bars(st["bars"])
    if "pct" in st: set_pct(st["pct"])
    if "eiffel" in st: set_eiffel(st["eiffel"])
    if "vorrat" in st or "wasser" in st: set_vorrat(g("vorrat", 0.0), g("wasser", 0))
    for k, key in (("rp_people", "people"), ("markt_people", "people"), ("muell_voll", "muell")):
        if k in STATE_OBJ: STATE_OBJ[k].hide_render = not g(key, 0 if key == "muell" else 1)
    if "fahrer" in STATE_OBJ:
        for o in STATE_OBJ["fahrer"]: o.hide_render = not g("driver", 1)
    if "atm" in STATE_OBJ: emit("atm", 2.0 * (1 - g("atm_off", 0)))
    if "pools" in STATE_OBJ: emit("pool", 0.35 * g("lights", 1.0))
    if "c_deckel" in STATE_OBJ: STATE_OBJ["c_deckel"].hide_render = g("cut", 0) > 0.5
    w = bpy.context.scene.world.node_tree.nodes["Background"]
    day = g("day", 0.0)
    w.inputs[0].default_value = tuple(C["night"][i] * (1 - day) + (0.35, 0.45, 0.6, 1)[i] * day for i in range(4)); w.inputs[1].default_value = 0.7 + 1.5 * day
    sun = bpy.data.objects["sonne"]; sun.data.energy = 0.9 + 4.0 * day; sun.data.color = (0.55 + 0.45 * day, 0.66 + 0.3 * day, 1.0 - 0.1 * day)

def setup_scene(W, H, samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(55), math.radians(8), math.radians(-35))); s = bpy.context.object; s.name = "sonne"
    s.data.angle = math.radians(6)
    build_town(); build_karte(); build_aisle(); build_fridge(); build_cut()
    build_detail(); build_rastplatz(); build_wasserwerk(); build_extra_town(); build_haus_vorrat(); set_vorrat(0.0, 0)
    build_racks("zlager", 700, "kisten"); build_racks("kuehl", 760, "weiss", light=(0.75, 0.88, 1.0)); build_racks("reserve", 820, "saecke")
    build_racks("apo", 880, "klein", rows=2, levels=3); build_racks("klinik", 940, "weiss", rows=2, levels=3)
    build_cab(); build_leitstand(); build_markt_cut(); build_bars(); build_ladung()
    r = sc.render; r.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.light_sampling_threshold = 0.02; r.resolution_x, r.resolution_y = W, H
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    sc.view_layers[0].use_pass_z = True
    return sc, cam

def look_at(cam, loc, tgt, lens):
    cam.location = Vector(loc); d = Vector(tgt) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens; cam.data.clip_start = 0.05; cam.data.clip_end = 400

def project(sc, cam, pts, W, H):
    out = []
    for p in pts:
        v = world_to_camera_view(sc, cam, Vector(p)); out.append([round(v.x * W, 1), round((1 - v.y) * H, 1), round(v.z, 3)])
    return out

def render(sc, path, kind="png", samples=None):
    r = sc.render
    if kind == "exr":
        r.image_settings.media_type = "MULTI_LAYER_IMAGE"; r.image_settings.file_format = "OPEN_EXR_MULTILAYER"
    else:
        r.image_settings.media_type = "IMAGE"; r.image_settings.file_format = "PNG"
    keep = sc.cycles.samples
    if samples: sc.cycles.samples = samples
    r.filepath = path; bpy.ops.render.render(write_still=True); sc.cycles.samples = keep

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("shots"); ap.add_argument("out")
    ap.add_argument("--w", type=int, default=1600); ap.add_argument("--h", type=int, default=900); ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--only", default="")
    a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:])
    os.makedirs(a.out, exist_ok=True)
    shots = json.load(open(a.shots)); only = set(a.only.split(",")) if a.only else None
    sc, cam = setup_scene(a.w, a.h, a.samples); DONE = {}
    for s in shots:
        if only and s["id"] not in only: continue
        base = os.path.join(a.out, s["id"])
        if os.path.exists(base + ".json"): continue
        key = json.dumps([s["cam"], s.get("A", {}), s.get("B"), sorted(s.get("anchors", []))], sort_keys=True)
        if key in DONE:   # gleiche Kamera + gleicher Zustand (Folge am selben Ort) -> Bilder wiederverwenden
            import shutil
            for suf in ("_A.png", "_B.png", "_Z.exr", ".json"):
                if os.path.exists(DONE[key] + suf): shutil.copy(DONE[key] + suf, base + suf)
            print("fertig", s["id"], "(kopiert)", flush=True); continue
        DONE[key] = base
        c = s["cam"]; look_at(cam, c["loc"], c["tgt"], c.get("lens", 50))
        apply_state(s.get("A", {})); render(sc, base + "_A.png")
        render(sc, base + "_Z.exr", "exr", samples=1)
        if s.get("B"): apply_state({**s.get("A", {}), **s["B"]}); render(sc, base + "_B.png")
        proj = {k: project(sc, cam, ANCH[k], a.w, a.h) for k in s.get("anchors", []) if k in ANCH}
        json.dump({"W": a.w, "H": a.h, "anchors": proj}, open(base + ".json", "w"))
        print("fertig", s["id"], flush=True)

if __name__ == "__main__":
    main()
