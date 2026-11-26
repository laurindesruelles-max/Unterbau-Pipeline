"""Wortzeiten (words/wN.json) -> saetze.json [teil, start, ende, satz]. python3 mk_saetze.py WORK"""
import json, sys, re, os
W = sys.argv[1]; T = json.load(open(os.path.join(W, "v5/saetze_text.json"))); out = []
pos = {}
for k, s in T:
    w = json.load(open(os.path.join(W, f"words/w{k}.json")))["words"]; i = pos.get(k, 0); n = len(s.split())
    seg = w[i:i + n]; pos[k] = i + n
    assert [x["w"] for x in seg] == s.split(), (k, s, [x["w"] for x in seg])
    out.append([k, seg[0]["s"], seg[-1]["e"], s])
json.dump(out, open(os.path.join(W, "v5/saetze.json"), "w"), ensure_ascii=False, indent=0); print(len(out), "Sätze")
