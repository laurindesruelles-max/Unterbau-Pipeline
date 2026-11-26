"""Skript -> Sätze (Teil, Text) und Text-Dateien je Teil. python3 saetze_split.py script.md OUTDIR"""
import re, sys, json, os
src, out = sys.argv[1], sys.argv[2]
parts = re.split(r"^## Teil (\d+)\s*$", open(src).read(), flags=re.M)
S = []
for k in range(1, len(parts), 2):
    n = int(parts[k]); txt = " ".join(l.strip() for l in parts[k + 1].split("\n") if l.strip())
    open(os.path.join(out, f"text{n}.txt"), "w").write(txt + "\n")
    for s in re.split(r"(?<=[.?!])\s+", txt):
        if s: S.append([n, s])
json.dump(S, open(os.path.join(out, "saetze_text.json"), "w"), ensure_ascii=False, indent=0)
for i, (n, s) in enumerate(S): print(i, n, s)
