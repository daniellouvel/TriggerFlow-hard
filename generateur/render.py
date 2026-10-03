#!/usr/bin/env python3
"""Rendu approximatif d'un .kicad_sch (contrôle visuel de la mise en page)."""
import sys, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from kicad_net import parse, find, first, S, pin_pos

def tf(px, py, at, mirror=None):
    return pin_pos(px, py, at, mirror)

def xy(n): return float(n[1]), float(n[2])

def render(path, out, paper=(297, 210)):
    root = parse(path)
    libs = {}
    for sym in find(first(root, "lib_symbols"), "symbol"):
        libs[sym[1]] = sym
    fig, ax = plt.subplots(figsize=(16.5, 11.7))
    ax.set_xlim(0, paper[0]); ax.set_ylim(paper[1], 0); ax.set_aspect("equal")
    ax.add_patch(Rectangle((5, 5), paper[0] - 10, paper[1] - 10, fill=False, ec="#800", lw=0.8))
    # zones
    for r in find(root, "rectangle"):
        a = xy(first(r, "start")); b = xy(first(r, "end"))
        ax.add_patch(Rectangle(a, b[0] - a[0], b[1] - a[1], fill=False, ec="#888", ls="--", lw=0.8))
    for t in find(root, "text"):
        at = first(t, "at"); size = float(first(first(first(t, "effects"), "font"), "size")[1])
        ax.text(float(at[1]), float(at[2]), t[1].replace("\\n", "\n"), fontsize=size * 4.2, va="top", ha="left", color="#444",
                fontweight="bold" if first(first(first(t, "effects"), "font"), "bold") else "normal")
    for w in find(root, "wire"):
        pts = find(first(w, "pts"), "xy")
        ax.plot([float(pts[0][1]), float(pts[1][1])], [float(pts[0][2]), float(pts[1][2])], color="#080", lw=1.4)
    for j in find(root, "junction"):
        x, y = xy(first(j, "at")); ax.add_patch(Circle((x, y), 0.6, color="#080"))
    for n in find(root, "no_connect"):
        x, y = xy(first(n, "at")); ax.plot([x - 0.8, x + 0.8], [y - 0.8, y + 0.8], "b", lw=1); ax.plot([x - 0.8, x + 0.8], [y + 0.8, y - 0.8], "b", lw=1)
    for s in find(root, "symbol"):
        lib = first(s, "lib_id")
        if not lib: continue
        a = first(s, "at"); at = (float(a[1]), float(a[2]), float(a[3]))
        mi = first(s, "mirror"); mi = S(mi[1]) if mi else None
        tf = lambda px, py, at, _m=mi: pin_pos(px, py, at, _m)
        ls = libs[lib[1]]
        for sub in find(ls, "symbol"):
            for g in find(sub, "rectangle"):
                s1 = xy(first(g, "start")); e1 = xy(first(g, "end"))
                pts = [tf(s1[0], s1[1], at), tf(e1[0], s1[1], at), tf(e1[0], e1[1], at), tf(s1[0], e1[1], at)]
                ax.add_patch(Polygon(pts, fill=False, ec="#a00", lw=1.2))
            for g in find(sub, "polyline"):
                pts = [tf(float(p[1]), float(p[2]), at) for p in find(first(g, "pts"), "xy")]
                ax.add_patch(Polygon(pts, fill=False, closed=False, ec="#a00", lw=1.2))
            for g in find(sub, "circle"):
                c = xy(first(g, "center")); r = float(first(g, "radius")[1]); p = tf(c[0], c[1], at)
                ax.add_patch(Circle(p, r, fill=False, ec="#a00", lw=1.2))
            for g in find(sub, "arc"):
                pts = [tf(*xy(first(g, k)), at) for k in ("start", "mid", "end")]
                ax.plot([p[0] for p in pts], [p[1] for p in pts], color="#a00", lw=1.2)
            for p in find(sub, "pin"):
                pa = first(p, "at"); ln = float(first(p, "length")[1]); ang = float(pa[3])
                px, py = float(pa[1]), float(pa[2])
                q = (px + ln * math.cos(math.radians(ang)), py + ln * math.sin(math.radians(ang)))
                p0 = tf(px, py, at); p1 = tf(q[0], q[1], at)
                ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#a00", lw=1.0)
                ax.plot(*p0, "s", ms=2.5, color="#a00")
        for p in find(s, "property"):
            if p[1] not in ("Reference", "Value"): continue
            if any(S(c[0]) == "hide" for c in p if isinstance(c, list)): continue
            pa = first(p, "at"); just = first(first(p, "effects"), "justify")
            ha = "left" if just and "left" in [S(x) for x in just[1:]] else "right" if just and "right" in [S(x) for x in just[1:]] else "center"
            ax.text(float(pa[1]), float(pa[2]), p[2], fontsize=6.5, color="#066", ha=ha, va="center")
    for kind in ("label", "hierarchical_label"):
        for l in find(root, kind):
            at = first(l, "at"); ang = float(at[3])
            ha = "right" if ang == 180 else "left"
            x, y = float(at[1]), float(at[2])
            rot = 90 if ang == 90 else 0
            ax.text(x - (0.6 if rot else 0), y - (0.6 if kind == "label" and not rot else 0), l[1], fontsize=7, color="#00a" if kind == "label" else "#a50", ha=ha,
                    va="bottom" if kind == "label" and not rot else "center", fontweight="bold", rotation=rot, rotation_mode="anchor")
            if kind == "hierarchical_label": ax.plot(x, y, "D", ms=3, color="#a50")
    ax.set_title(path.split("/")[-1])
    fig.savefig(out, dpi=110, bbox_inches="tight"); print("écrit", out)

if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], (420, 297) if len(sys.argv) > 3 else (297, 210))
