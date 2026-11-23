"""Ruhiger Schnitt (Laurin 23.11.2026: „zu viele Animationen hintereinander bzw. zu kurz – man kam nicht hinterher“).
Fasst zu kurze Einstellungen mit den folgenden zusammen, ohne Ton oder Satzzeiten zu verschieben:
Einstellung mit Text/Zahl/Grafik >= MIN_TEXT s, sonst >= MIN_BILD s. Titel-/Kapitelkarten werden nie geschluckt.
python3 engine/ruhig.py plan.json plan_ruhig.json [--text 4.0 --bild 2.5]"""
import json, sys, argparse
ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--text", type=float, default=4.0); ap.add_argument("--bild", type=float, default=2.5)
a = ap.parse_args(); P = json.load(open(a.inp))
def has_text(e): return e.get("kind") == "mo" or any(f["type"] in ("label", "tafel", "card") for f in e.get("fx", []))
def is_card(e): return any(isinstance(k, str) for k in e.get("keys", []))
out, dropped = [], []
def absorb(e, nx):
    e["dur"] = round(e["dur"] + nx["dur"], 3); e["keys"] = list(e.get("keys", [])) + list(nx.get("keys", []))
    e["ids"] = e.get("ids", [e["id"]]) + nx.get("ids", [nx["id"]])
# 1) vorwärts: nur Einstellungen OHNE Text schlucken (eine Fortsetzung derselben Grafik/desselben Clips zählt als ohne)
i = 0
while i < len(P):
    e = dict(P[i]); i += 1
    need = a.text if has_text(e) else a.bild
    while e["dur"] < need and i < len(P) and not is_card(P[i]) and not is_card(e):
        nx = P[i]; same = nx.get("video") and nx.get("video") == e.get("video")
        if has_text(nx) and not same: break
        absorb(e, nx); i += 1
    out.append(e)
# 2) rückwärts: Text-Einstellung beginnt früher und nimmt der vorigen Einstellung ohne Text Zeit weg
for k in range(1, len(out)):
    e, pv = out[k], out[k - 1]
    if has_text(e) and e["dur"] < a.text and not has_text(pv) and not is_card(pv) and not is_card(e):
        take = min(a.text - e["dur"], pv["dur"] - a.bild)
        if take > 0.3:
            pv["dur"] = round(pv["dur"] - take, 3); e["dur"] = round(e["dur"] + take, 3); e["lead"] = round(take, 3)
PRUEFEN = []
def carry(dst, src, at, total=None):
    """Text der weichenden Einstellung als Einblendung auf die bleibende übernehmen (nichts geht verloren)."""
    total = total or (dst["dur"] + src["dur"])
    if dst.get("kind") == "mo": PRUEFEN.append(dst["id"])   # Grafik hat oft eigene Überschrift oben -> Standbild ansehen, ggf. Einblendung weglassen
    for f in src.get("fx", []):
        if f.get("type") == "label": t = dict(f, t0=round((at + 0.1 * src["dur"]) / total, 3)); t.pop("anchor", None); t["pos"] = [800, 90]; dst.setdefault("fx", []).append(t)
        if f.get("type") == "tafel": dst.setdefault("fx", []).append({"type": "label", "text": " · ".join(f["texts"]), "pos": [800, 90], "t0": round((at + 0.1 * src["dur"]) / total, 3)})
    dst["fx"] = [g for g in dst.get("fx", []) if g.get("type") != "label"] + [g for g in dst.get("fx", []) if g.get("type") == "label"][-1:]   # höchstens eine Einblendung gleichzeitig
# 3) zwei Text-Einstellungen, beide zu kurz: die reine Einblendung (Label/Tafel im Bild) weicht der Grafik
k = 0
while k + 1 < len(out):
    e, nx = out[k], out[k + 1]
    if has_text(e) and has_text(nx) and (e["dur"] < 3.0 or nx["dur"] < 3.0) and e["dur"] + nx["dur"] <= 7.0 and not is_card(e) and not is_card(nx):
        if e.get("kind") == "mo" and nx.get("kind") != "mo":
            carry(e, nx, e["dur"]); dropped.append((nx["id"], "-> als Einblendung übernommen")); absorb(e, nx); del out[k + 1]; continue
        if nx.get("kind") == "mo" and e.get("kind") != "mo":
            for f in nx.get("fx", []):
                if f.get("type") == "label": f["t0"] = round((e["dur"] + f.get("t0", 0.15) * nx["dur"]) / (e["dur"] + nx["dur"]), 3)
            carry(nx, e, 0.0, e["dur"] + nx["dur"]); dropped.append((e["id"], "-> als Einblendung übernommen"))
            nx["dur"] = round(nx["dur"] + e["dur"], 3); nx["keys"] = e["keys"] + nx["keys"]; nx["ids"] = e.get("ids", [e["id"]]) + nx.get("ids", [nx["id"]]); nx["lead"] = round(nx.get("lead", 0) + e["dur"], 3); del out[k]; continue
    k += 1
# 4) kurze Einstellung ohne Text vor einer Text-Einstellung: weicht, die Text-Einstellung beginnt früher
k = 0
while k + 1 < len(out):
    e, nx = out[k], out[k + 1]
    if not has_text(e) and e["dur"] < a.bild and not is_card(e) and not is_card(nx) and nx["dur"] + e["dur"] <= 8.0:
        nx["dur"] = round(nx["dur"] + e["dur"], 3); nx["keys"] = e["keys"] + nx["keys"]; nx["ids"] = e.get("ids", [e["id"]]) + nx.get("ids", [nx["id"]])
        nx["lead"] = round(nx.get("lead", 0) + e["dur"], 3)
        for f in nx.get("fx", []):
            if f.get("type") == "label": f["t0"] = round((e["dur"] + f.get("t0", 0.15) * (nx["dur"] - e["dur"])) / nx["dur"], 3)
        del out[k]; continue
    k += 1
# zu kurze Reste ohne Nachfolger: an die vorige Einstellung hängen
k = 1
while k < len(out):
    if out[k]["dur"] < 1.8 and not is_card(out[k]) and not is_card(out[k - 1]):
        out[k - 1]["dur"] = round(out[k - 1]["dur"] + out[k]["dur"], 3); out[k - 1]["keys"] += out[k]["keys"]; del out[k]
    else: k += 1
# gleiche Szene hintereinander = eine durchgehende Fahrt
k = 0
while k < len(out):
    j = k
    while j + 1 < len(out) and "video" not in out[k] and "video" not in out[j + 1] and out[j + 1].get("set") == out[k].get("set"): j += 1
    tot = sum(out[q]["dur"] for q in range(k, j + 1)); acc = 0.0
    for q in range(k, j + 1):
        if "video" in out[q]: continue
        out[q].update(run_k=q - k, run_len=j - k + 1, run_u=[acc / tot, (acc + out[q]["dur"]) / tot]); acc += out[q]["dur"]
    k = j + 1
json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=0)
d = sorted(x["dur"] for x in out)
print(len(P), "->", len(out), "Einstellungen; Median", d[len(d) // 2], "s; Text unter", a.text, "s:", sum(1 for x in out if has_text(x) and x["dur"] < a.text))
for x in dropped: print("weggefallen:", x)
if PRUEFEN: print("PRÜFEN (Einblendung auf 2D-Grafik übernommen – Standbild ansehen, bei Überlappung weglassen):", ", ".join(PRUEFEN))
