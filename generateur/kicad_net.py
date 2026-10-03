#!/usr/bin/env python3
"""Lecture d'un .kicad_sch (v20260306) et calcul de la netlist par géométrie.
Sert à (1) extraire la spec du Bloc 1 existant, (2) vérifier le fichier généré."""
import sys, math, collections
import sexpdata
from sexpdata import Symbol


def S(x):
    return x.value() if isinstance(x, Symbol) else x


def find(node, name):
    return [c for c in node if isinstance(c, list) and c and S(c[0]) == name]


def first(node, name):
    r = find(node, name)
    return r[0] if r else None


def parse(path):
    with open(path, encoding="utf-8") as f:
        return sexpdata.loads(f.read())


def lib_pins(root):
    """{lib_id: [(num, name, x, y, angle)]} en coordonnées symbole (Y vers le haut)."""
    out = {}
    libs = first(root, "lib_symbols")
    for sym in find(libs, "symbol"):
        lid = sym[1]
        pins = []
        for sub in find(sym, "symbol"):
            for p in find(sub, "pin"):
                at = first(p, "at")
                num = first(p, "number")[1]
                nm = first(p, "name")[1]
                pins.append((str(num), nm, float(at[1]), float(at[2]), float(at[3])))
        out[lid] = pins
    return out


def pin_pos(px, py, at, mirror):
    x, y, rot = at
    a = math.radians(rot)
    rx = px * math.cos(a) - py * math.sin(a)
    ry = px * math.sin(a) + py * math.cos(a)
    if mirror == "x":
        ry = -ry
    elif mirror == "y":
        rx = -rx
    return (round(x + rx, 2), round(y - ry, 2))  # sch_y = placed_y - sym_y


class UF:
    def __init__(s): s.p = {}
    def f(s, a):
        s.p.setdefault(a, a)
        while s.p[a] != a:
            s.p[a] = s.p[s.p[a]]
            a = s.p[a]
        return a
    def u(s, a, b): s.p[s.f(a)] = s.f(b)


def on_seg(pt, a, b):
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > 0.01:
        return False
    return min(x1, x2) - 0.01 <= x <= max(x1, x2) + 0.01 and min(y1, y2) - 0.01 <= y <= max(y1, y2) + 0.01


def analyse(path):
    root = parse(path)
    libs = lib_pins(root)
    uf = UF()
    comps, pinpts = [], []
    for s in find(root, "symbol"):
        lib = first(s, "lib_id")
        if not lib:
            continue
        lid = lib[1]
        at = first(s, "at")
        at = (float(at[1]), float(at[2]), float(at[3]))
        mir = first(s, "mirror")
        mir = S(mir[1]) if mir else None
        props = {p[1]: p[2] for p in find(s, "property")}
        ref, val = props.get("Reference"), props.get("Value")
        comps.append((ref, val, lid, at))
        for num, nm, px, py, _ in libs.get(lid, []):
            pinpts.append((ref, num, nm, lid, pin_pos(px, py, at, mir)))
    wires = []
    for w in find(root, "wire"):
        pts = first(w, "pts")
        a = tuple(round(float(v), 2) for v in first(pts, "xy")[1:3])
        b = tuple(round(float(v), 2) for v in find(pts, "xy")[1][1:3])
        wires.append((a, b))
        uf.u(a, b)
    juncs = [tuple(round(float(v), 2) for v in first(j, "at")[1:3]) for j in find(root, "junction")]
    # jonction ou extrémité posée sur un fil => connexion (T sans jonction = KiCad connecte l'extrémité seulement)
    endpoints = set(p for w in wires for p in w)
    for j in juncs:
        uf.f(j)
        for a, b in wires:
            if on_seg(j, a, b):
                uf.u(j, a)
    for (ref, num, nm, lid, p) in pinpts:
        uf.f(p)
        for a, b in wires:
            if on_seg(p, a, b):
                uf.u(p, a)
    labels = []
    for kind in ("label", "hierarchical_label", "global_label"):
        for l in find(root, kind):
            at = first(l, "at")
            p = (round(float(at[1]), 2), round(float(at[2]), 2))
            labels.append((kind, l[1], p))
            uf.f(p)
            for a, b in wires:
                if on_seg(p, a, b):
                    uf.u(p, a)
    nets = collections.defaultdict(lambda: {"pins": [], "names": set()})
    for (ref, num, nm, lid, p) in pinpts:
        nets[uf.f(p)]["pins"].append(f"{ref}.{num}")
    # noms : labels + power symbols
    for kind, name, p in labels:
        nets[uf.f(p)]["names"].add(name)
    for (ref, num, nm, lid, p) in pinpts:
        if lid.startswith("power:"):
            nets[uf.f(p)]["names"].add(lid.split(":")[1])
    # labels de même nom => même net
    byname = collections.defaultdict(list)
    for k, v in nets.items():
        for n in v["names"]:
            byname[n].append(k)
    merged = {}
    for n, ks in byname.items():
        for k in ks[1:]:
            uf.u(ks[0], k)
    final = collections.defaultdict(lambda: {"pins": set(), "names": set()})
    for k, v in nets.items():
        r = uf.f(k)
        final[r]["pins"] |= set(v["pins"])
        final[r]["names"] |= v["names"]
    return root, comps, pinpts, wires, juncs, labels, final


def report(path):
    root, comps, pinpts, wires, juncs, labels, nets = analyse(path)
    print(f"## {path}")
    print(f"composants={len([c for c in comps if not str(c[0]).startswith('#')])} fils={len(wires)} jonctions={len(juncs)} labels={len(labels)}")
    allpins = {f"{r}.{n}" for r, n, *_ in pinpts}
    connected = set()
    out = []
    for r, v in nets.items():
        pins = sorted(p for p in v["pins"] if not p.startswith("#PWR"))
        connected |= set(pins)
        names = "/".join(sorted(v["names"])) or "(sans nom)"
        if pins:
            out.append((names, pins))
    for names, pins in sorted(out):
        print(f"  NET {names:22s} {' '.join(pins)}")
    floating = sorted(p for p in allpins if not p.startswith("#PWR") and p not in connected)
    single = [(n, p) for n, p in out if len(p) < 2 and n == "(sans nom)"]
    print("  broches isolées:", floating)
    print("  nets à 1 broche sans nom:", single)
    return nets


if __name__ == "__main__":
    report(sys.argv[1])
