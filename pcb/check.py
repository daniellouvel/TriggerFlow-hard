from place import *
miss = sorted(set(comps) - set(P)); extra = sorted(set(P) - set(comps))
print("non placés:", miss); print("inconnus:", extra)
R = {r: rect(r) for r in P}
def ov(a, b, m=0.2): return a[0] < b[2] + m and b[0] < a[2] + m and a[1] < b[3] + m and b[1] < a[3] + m
under_devkit_ok = set()
bad = []
refs = sorted(R)
for i, a in enumerate(refs):
    for b in refs[i + 1:]:
        if {a, b} & {"U101"} and ({a, b} - {"U101"}) <= under_devkit_ok: continue
        if ov(R[a], R[b]): bad.append((a, b))
print("chevauchements:", bad)
out = [r for r, q in R.items() if q[0] < 0.5 or q[1] < 0 or q[2] > BW - 0.5 or q[3] > BH]
print("hors carte:", out)
ka = [r for r, q in R.items() if r != "U101" and ov(q, KEEPOUT_ANT, 0)]
print("dans zone antenne:", ka)
kb = [r for r, q in R.items() if r not in STRADDLE and ov(q, BARRIER, 0)]
print("sur la barrière:", kb)
kh = [(r, h) for h, (hx, hy, _) in HOLES.items() for r, q in R.items() if ov(q, (hx - 3.5, hy - 3.5, hx + 3.5, hy + 3.5), 0)]
print("trous:", kh)
print(len(P), "composants placés")
