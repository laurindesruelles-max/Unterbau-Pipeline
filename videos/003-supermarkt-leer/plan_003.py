"""Aus bilddrehbuch.json die Render-Liste (shots.json, engine/stadt.py) und den Compositing-Plan (plan.json, engine/stadtcomp.py).
python3 plan_003.py bilddrehbuch.json OUTDIR [--max-i N]
Kamera je Schauplatz (SETS) + kleine Variation je Einstellung, damit kein Bild zweimal vorkommt."""
import json, sys, os, hashlib, argparse

SETS = {   # loc, tgt, lens, A-Zustand, Anker
 "haus_kueche":      ((-12.9, -10.6, 0.8), (-12.1, -8.7, 0.6), 42, {"mine": 1}, ["haus"]),
 "kuehlschrank":     ((299.2, -1.4, 1.5), (300.0, 2.0, 0.95), 28, {"door": 0}, []),
 "markt_regal_voll": ((200.15, -5.8, 1.35), (201.0, 1.4, 0.7), 30, {"fill": 1, "gap": 0}, ["milchfach"]),
 "autobahn_nacht":   ((-14, -24, 3.0), (-4, -16, 0), 35, {"trucks": 1}, ["route_autobahn"]),
 "stadt_total":      ((-4, -30, 16), (0, -1, 0), 40, {"lights": 1, "trucks": 1}, ["route_autobahn", "haus", "tafel", "uhr"]),
 "karte_de":         ((0, 178, 18), (0, 200, 0), 45, {}, ["de_staedte", "de_HHH", "de_HDO", "de_DOK", "de_KF", "de_FN", "de_NM", "de_FS", "de_SM", "de_HL", "de_LB", "de_HHB", "de_LN"]),
 "rathaus_uhr":      ((0.6, 4.0, 1.4), (0, 7.5, 2.0), 50, {}, ["uhr"]),
 "bahnhof_tafel":    ((-7.4, 4.4, 1.25), (-8, 7.1, 1.25), 42, {}, ["tafel"]),
 "notreserve_aussen":((-17.5, -19.5, 3.2), (-22, -11.5, 0.5), 40, {"lights": 0.3}, ["notreserve"]),
 "querschnitt_stadt":((397, -8, 0.8), (400, 0, -0.4), 40, {"cut": 0}, ["cut"]),
}
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
        sp = SPEC.get((e["i"], k), {}); st = sp.get("set", e["set"])
        if st not in SETS: print("FEHLT Set", st, "für", e["i"]); continue
        loc, tgt, lens, A, anc = SETS[st]
        if "cam" in sp: loc, tgt, lens = sp["cam"]
        sid = f"s{n:03d}"
        if "cam" not in sp: loc = jitter(sid, loc, 0.6)
        shots.append({"id": sid, "set": st, "cam": {"loc": list(loc), "tgt": list(tgt), "lens": lens}, "A": {**A, **sp.get("A", {})},
                      "B": sp.get("B"), "anchors": anc})
        plan.append({"id": sid, "dur": e["sek"], "move": sp.get("move", "push"), "trans": sp.get("trans", "diff"),
                     "t_trans": sp.get("t_trans", [0.2, 0.8]), "fx": sp.get("fx", []), "anim": e["animation"], "i": e["i"]})
    json.dump(shots, open(os.path.join(a.out, "shots.json"), "w"), indent=0)
    json.dump(plan, open(os.path.join(a.out, "plan.json"), "w"), indent=0, ensure_ascii=False)
    print(len(shots), "Einstellungen,", round(sum(p["dur"] for p in plan), 1), "s")

if __name__ == "__main__":
    main()
