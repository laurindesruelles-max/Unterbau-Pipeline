"""Unterbau-Miniaturwelt (Blender/bpy, kostenlos): Modell-Diorama von schräg oben im Unterbau-Look
(Nachtblau, ein oranger Akzent). Test-Szene "palette": Molkerei -> Zentrallager -> Supermarkt, ein Lkw fährt die Route,
hinter ihm leuchtet die Spur orange auf.

python3 engine/miniwelt.py palette <outdir> [w h samples]    -> outdir/f_0001.png ...
Render: Cycles CPU, wenige Samples + Denoiser. Immer mit setsid nohup im Hintergrund, nie zwei Blender parallel.
"""
import sys, math, os
import bpy
from mathutils import Vector

NAVY = (0.012, 0.03, 0.07, 1); GROUND = (0.03, 0.055, 0.1, 1); BLD = (0.16, 0.2, 0.27, 1)
WHITE = (0.75, 0.77, 0.8, 1); ORANGE = (1.0, 0.33, 0.05, 1); WARM = (1.0, 0.62, 0.3, 1); ROAD = (0.05, 0.07, 0.1, 1)

def mat(name, col, emit=0.0, rough=0.7):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = col; b.inputs["Emission Strength"].default_value = emit
    return m

def box(name, loc, size, m, bevel=0.04):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2); bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2
    o.data.materials.append(m); return o

def cyl(name, loc, r, h, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=32); o = bpy.context.object
    o.name = name; o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o

def windows(x, y, z, w, n, m, face="-y", d=0.0):
    for i in range(n):
        xx = x - w/2 + (i+0.5)*w/n
        box(f"win{x}{y}{i}", (xx, y+d, z), (w/n*0.5, 0.02, 0.18), m, bevel=0)

def curve(name, pts, depth, m):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(len(pts)-1)
    for p, c in zip(sp.points, pts): p.co = (c[0], c[1], c[2], 1)
    cu.bevel_depth = depth; cu.bevel_resolution = 2
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o)
    if m: cu.materials.append(m)
    return o

def smooth(pts, n=6):
    """Ecken der Route abrunden (Chaikin)."""
    for _ in range(n):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [tuple(0.75*a[i]+0.25*b[i] for i in range(3)), tuple(0.25*a[i]+0.75*b[i] for i in range(3))]
        out.append(pts[-1]); pts = out
    return pts

def truck(m_cab, m_box, m_dark):
    root = bpy.data.objects.new("truck", None); bpy.context.collection.objects.link(root)
    parts = [box("cab", (0.55, 0, 0.32), (0.32, 0.36, 0.42), m_cab, 0.03),
             box("trailer", (-0.12, 0, 0.36), (1.0, 0.38, 0.5), m_box, 0.02),
             box("glass", (0.715, 0, 0.42), (0.01, 0.3, 0.14), m_dark, 0)]
    for x in (0.55, 0.1, -0.4):
        for y in (-0.19, 0.19):
            w = cyl("wheel", (x, y, 0.09), 0.09, 0.07, m_dark); w.rotation_euler = (math.pi/2, 0, 0); parts.append(w)
    hl = box("headlight", (0.715, 0, 0.2), (0.01, 0.3, 0.04), mat("hl", WARM, 25), 0); parts.append(hl)
    for p in parts: p.parent = root
    root.scale = (1.15, 1.15, 1.15)
    return root

def pallet(x, y, z, m_wood, m_crate):
    box("pal", (x, y, z+0.03), (0.4, 0.4, 0.06), m_wood, 0.01)
    for i in range(2):
        for j in range(2):
            box("crate", (x-0.1+0.2*i, y-0.1+0.2*j, z+0.16), (0.18, 0.18, 0.2), m_crate, 0.01)

def scene_palette(out, W=1280, H=720, samples=10):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; fps = 25; N = 15*fps
    sc.frame_start, sc.frame_end = 1, N; sc.render.fps = fps
    m_g, m_b, m_w, m_r = mat("ground", GROUND, rough=0.9), mat("bld", BLD), mat("white", WHITE), mat("road", ROAD, rough=0.5)
    m_win, m_or, m_dark = mat("win", WARM, 6), mat("orange", ORANGE, 0, 0.4), mat("dark", (0.01, 0.01, 0.015, 1), rough=0.3)
    m_trail = mat("trail", ORANGE, 12); m_wood = mat("wood", (0.35, 0.22, 0.12, 1))
    # Boden: große Platte (Diorama-Sockel) + leichte Kante
    box("base", (0, 0, -0.15), (22, 13, 0.3), m_g, 0.08)
    # Molkerei (links hinten): Halle + 3 Silos
    box("molk", (-7.5, 3.2, 0.6), (2.6, 1.8, 1.2), m_b); box("molk_roof", (-7.5, 3.2, 1.23), (2.7, 1.9, 0.06), m_w, 0.01)
    for i in range(3): cyl("silo", (-9.3, 2.4+0.75*i, 1.1), 0.32, 2.2, m_w)
    windows(-7.5, 2.29, 0.7, 2.2, 6, m_win)
    # Zentrallager (Mitte): flach + riesig, Laderampen mit Licht
    box("lager", (0.5, 2.9, 0.55), (5.5, 3.0, 1.1), m_b); box("lager_roof", (0.5, 2.9, 1.13), (5.6, 3.1, 0.06), m_w, 0.01)
    for i in range(8): box(f"dock{i}", (-1.9+i*0.68, 1.38, 0.35), (0.4, 0.04, 0.5), m_win, 0)
    # Supermarkt (rechts vorn): Gebäude + oranges Band als einziger Akzent
    box("markt", (7.6, -0.6, 0.5), (2.8, 2.0, 1.0), m_b); box("markt_band", (7.6, -1.62, 0.85), (2.8, 0.05, 0.16), m_or, 0)
    box("markt_roof", (7.6, -0.6, 1.03), (2.9, 2.1, 0.06), m_w, 0.01); windows(7.6, -1.62, 0.4, 2.4, 5, m_win)
    # ein paar Wohnhäuser + Bäume als Füllung
    import random; random.seed(3)
    for _ in range(26):
        x, y = random.uniform(-10, 10), random.uniform(-6, 6)
        if abs(y-(0.6-0.25*x)) < 1.4 or (abs(x-0.5) < 3.4 and abs(y-2.9) < 2.2) or (x < -5.5 and y > 1.6) or (x > 5.5 and y > -3.2 and y < 1): continue
        h = random.uniform(0.3, 0.7); box("haus", (x, y, h/2), (0.5, 0.5, h), m_b, 0.02)
        if random.random() < 0.5: box("hw", (x, y-0.26, h*0.6), (0.14, 0.01, 0.1), m_win, 0)
    # Straße: Molkerei -> Lager-Rampe -> Supermarkt
    route = smooth([(-6.0, 2.0, 0.02), (-4.8, 1.0, 0.02), (-2.6, 0.7, 0.02), (-0.5, 0.75, 0.02), (1.6, 0.75, 0.02),
                    (3.6, 0.2, 0.02), (5.0, -1.4, 0.02), (6.2, -2.4, 0.02), (7.4, -2.4, 0.02)])
    road = curve("road", [(x, y, 0.0) for x, y, _ in route], 0, None); road.data.extrude = 0.28; road.data.materials.append(m_r)
    trail = curve("trail", [(x, y, 0.03) for x, y, _ in route], 0.035, m_trail)
    trail.data.bevel_factor_mapping_end = "SPLINE"
    path = curve("path", route, 0, None); path.data.path_duration = N; path.hide_render = True
    # Paletten: eine an der Molkerei (die "unsere" ist), viele im Lager-Vorplatz
    pallet(-6.3, 2.7, 0, m_wood, m_w)
    for i in range(5): pallet(-1.8+i*0.55, 1.05, 0, m_wood, m_w)
    # Lkw folgt der Route, hält an der Lager-Rampe
    tr = truck(m_or, m_w, m_dark)
    c = tr.constraints.new("FOLLOW_PATH"); c.target = path; c.use_curve_follow = True; c.use_fixed_location = True; c.forward_axis = "FORWARD_X"
    keys = [(1, 0.0), (int(1.2*fps), 0.0), (int(6*fps), 0.47), (int(8.5*fps), 0.47), (int(13.5*fps), 1.0), (N, 1.0)]
    for f, v in keys:
        c.offset_factor = v; c.keyframe_insert("offset_factor", frame=f)
        trail.data.bevel_factor_end = v; trail.data.keyframe_insert("bevel_factor_end", frame=f)
    for fc in list(tr.animation_data.action.fcurves) + list(trail.data.animation_data.action.fcurves) if hasattr(tr.animation_data.action, "fcurves") else []:
        for k in fc.keyframe_points: k.interpolation = "BEZIER"; k.easing = "AUTO"
    # Licht: kaltes Mondlicht + Welt nachtblau
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(10), math.radians(-40)))
    sun = bpy.context.object; sun.data.energy = 1.6; sun.data.color = (0.55, 0.68, 1.0); sun.data.angle = math.radians(8)
    bpy.ops.object.light_add(type="AREA", location=(0, -4, 9)); a = bpy.context.object; a.data.energy = 900; a.data.size = 14; a.data.color = (0.5, 0.6, 0.9)
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = NAVY
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    # Kamera: orthografisch-ähnlich (lange Brennweite), langsame Fahrt + leichtes Mitschwenken
    cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 60; cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
    cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 2.2
    foc = bpy.data.objects.new("focus", None); sc.collection.objects.link(foc); cam_d.dof.focus_object = foc
    tgt = bpy.data.objects.new("tgt", None); sc.collection.objects.link(tgt)
    t = cam.constraints.new("TRACK_TO"); t.target = tgt; t.track_axis = "TRACK_NEGATIVE_Z"; t.up_axis = "UP_Y"
    shots = [(1, (-12, -22, 17), (-4.0, 1.2, 0)), (int(6*fps), (-5, -23, 16), (0.0, 0.8, 0)), (N, (3, -22, 15), (5.0, -1.0, 0))]
    for f, cl, tl in shots:
        cam.location = cl; cam.keyframe_insert("location", frame=f); tgt.location = tl; tgt.keyframe_insert("location", frame=f)
    fc_ = foc.constraints.new("COPY_LOCATION"); fc_.target = tr
    # Render
    r = sc.render; r.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; r.resolution_x, r.resolution_y = W, H; r.film_transparent = False
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    r.image_settings.file_format = "PNG"; r.filepath = os.path.join(out, "f_")
    sc.frame_step = int(os.environ.get("STEP", "1"))
    first = os.environ.get("ONLY")
    if first:
        sc.frame_set(int(first)); r.filepath = os.path.join(out, f"test_{first}.png"); bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)

if __name__ == "__main__":
    a = sys.argv[1:]; os.makedirs(a[1], exist_ok=True)
    W, H, S = (int(a[2]), int(a[3]), int(a[4])) if len(a) > 4 else (1280, 720, 10)
    {"palette": scene_palette}[a[0]](a[1], W, H, S)
