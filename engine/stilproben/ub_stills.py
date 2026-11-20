"""Unterbau-Mischform, Schritt 1: Standbilder der Miniaturwelt aus Blender (Licht an / Licht aus) plus echte Tiefe (Z-Pass).
python3 ub_stills.py OUTDIR"""
import sys, os, math
sys.path.insert(0, "/home/claude/repos/Unterbau-Pipeline/engine")
import bpy, miniwelt as mw
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
os.environ["ONLY"] = "1"
mw.scene_palette(OUT, 64, 36, 1)                       # baut die Szene, Wegwerf-Testbild
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080; sc.cycles.samples = 24
# mehr Stadt: zusaetzliche Haeuserzeilen mit Fenstern vorne
import random; random.seed(11)
m_b = bpy.data.materials["bld"]; m_win = bpy.data.materials["win"]
for _ in range(40):
    x, y = random.uniform(-10, 10), random.uniform(-6.2, -2.6)
    if x > 5.5 and y > -3.2: continue
    h = random.uniform(0.35, 0.9); mw.box("h2", (x, y, h / 2), (0.55, 0.55, h), m_b, 0.02)
    mw.box("w2", (x, y - 0.28, h * 0.6), (0.18, 0.01, 0.12), m_win, 0)
sc.frame_set(150)
cam = sc.camera; cam.animation_data_clear(); bpy.data.objects["tgt"].animation_data_clear()
cam.location = (-2, -21, 15); bpy.data.objects["tgt"].location = (0.5, 0.2, 0)
sc.camera.data.dof.use_dof = False
vl = sc.view_layers[0]; vl.use_pass_z = True
r = sc.render
def still(name, exr=False):
    if exr:
        r.image_settings.media_type = "MULTI_LAYER_IMAGE"; r.image_settings.file_format = "OPEN_EXR_MULTILAYER"; r.filepath = os.path.join(OUT, name + ".exr")
    else:
        r.image_settings.media_type = "IMAGE"; r.image_settings.file_format = "PNG"; r.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)
if not os.path.exists(os.path.join(OUT, "on.png")): still("on")
sc.cycles.samples = 1; still("depth", exr=True); sc.cycles.samples = 24
em = m_win.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; em.default_value = 0.0
bpy.data.materials["win"].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.025, 0.035, 1)
still("off")
print("fertig")
