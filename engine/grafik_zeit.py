"""Nur zu kurze 2D-Grafiken verlängern, alles andere bleibt wie geschnitten (Laurin 23.11.2026: „Davor war das Video wesentlich
besser, nur 2–3 Folien/Animationen waren zu schnell – meist 2D-animierte Sequenzen“).
Eine Grafik (kind "mo"; zusammenhängende Teile desselben Clips zählen zusammen) unter --unter s wird auf --ziel s verlängert.
Zeit kommt zuerst von danach (Grafik bleibt am Ende stehen, höchstens --max_nach s), dann von davor (Grafik kommt etwas früher).
Gebende Einstellung: die nächste Blender-/Clip-Einstellung mit Luft (behält ≥ --rest s, mit Text ≥ --rest_text s); Einstellungen
dazwischen rutschen nur (höchstens 4 weit, nie über eine andere Grafik hinweg). Satzzeiten und Gesamtlänge bleiben -> Ton synchron.
python3 engine/grafik_zeit.py plan.json plan_neu.json [--unter 3.5 --ziel 4.2]
Fallblatt-Tafeln unter --tafel_unter s werden genauso auf --tafel_ziel s verlängert.
Markiert "cut_head"/"cut_tail" (s) an gebenden Einstellungen und "grafik_neu" an verlängerten, für splice2.py."""
import json, argparse
ap = argparse.ArgumentParser(); ap.add_argument("plan"); ap.add_argument("out")
ap.add_argument("--unter", type=float, default=3.5); ap.add_argument("--ziel", type=float, default=4.2)
ap.add_argument("--rest", type=float, default=2.0); ap.add_argument("--rest_text", type=float, default=2.6); ap.add_argument("--max_nach", type=float, default=1.3)
ap.add_argument("--tafel_unter", type=float, default=1.6); ap.add_argument("--tafel_ziel", type=float, default=2.4)
a = ap.parse_args(); P = json.load(open(a.plan))
has_text = lambda p: any(f.get("type") in ("label", "tafel", "card") for f in p.get("fx", []))
def spare(p): return 0.0 if p.get("kind") == "mo" or p.get("grafik_neu") or any(f.get("type") == "tafel" for f in p.get("fx", [])) else max(0.0, round(p["dur"] - (a.rest_text if has_text(p) else a.rest), 3))
def take(idxs, need, head):
    got = 0.0
    for k in idxs:
        if k < 0 or k >= len(P) or P[k].get("kind") == "mo" or need - got < 0.05: break
        t = min(need - got, spare(P[k]))
        if t > 0.05:
            P[k]["dur"] = round(P[k]["dur"] - t, 3); key = "cut_head" if head else "cut_tail"; P[k][key] = round(P[k].get(key, 0) + t, 3); got += t
    return round(got, 3)
i = 0; log = []
while i < len(P):
    p = P[i]
    tafel = p.get("kind") != "mo" and "video" not in p and any(f.get("type") == "tafel" for f in p.get("fx", []))
    if tafel and p["dur"] < a.tafel_unter:      # Fallblatt-Tafel (Folie) zu kurz, um mitzulesen
        need = round(a.tafel_ziel - p["dur"], 3); g1 = take(range(i + 1, i + 5), need, True); g2 = take(range(i - 1, i - 5, -1), need - g1, False)
        p["dur"] = round(p["dur"] + g1 + g2, 3); p["grafik_neu"] = 1; log.append((p["id"], "Tafel", round(p["dur"] - g1 - g2, 2), p["dur"], f"nach +{g1}", f"vor +{g2}")); i += 1; continue
    if p.get("kind") != "mo": i += 1; continue
    j = i
    while j + 1 < len(P) and P[j + 1].get("video") == p.get("video"): j += 1
    tot = sum(P[k]["dur"] for k in range(i, j + 1))
    if tot < a.unter:
        need = round(a.ziel - tot, 3)
        g1 = take(range(j + 1, j + 5), min(need, a.max_nach), True); P[j]["dur"] = round(P[j]["dur"] + g1, 3)
        g2 = take(range(i - 1, i - 5, -1), need - g1, False); P[i]["dur"] = round(P[i]["dur"] + g2, 3)
        if g2: P[i]["lead"] = g2
        for k in range(i, j + 1): P[k]["grafik_neu"] = 1
        log.append((P[i]["id"], round(tot, 2), round(tot + g1 + g2, 2), f"nach +{g1}", f"vor +{g2}"))
    i = j + 1
json.dump(P, open(a.out, "w"), ensure_ascii=False, indent=1)
for l in log: print("verlängert", *l)
print(len(log), "Grafiken verlängert; Länge", round(sum(p["dur"] for p in P), 3))
