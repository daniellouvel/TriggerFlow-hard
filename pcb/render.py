from place import *
import re
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
PLANES = {"GND", "+3V3", "+5V", "+12V", "VISO_3V3", "VISO_GND"}
PWRSET = {f"{p}9{i}" for p in ("CN","Q","D","F") for i in range(1,7)} | {f"R{i}" for i in range(93,105)}
# classement par fonction, numérotation EasyEDA du 10/10
ESP = {"U101","D101","D102","U104","U102","J101","SW101","SW102","R106","R105","R107","R108","C101","C102","C104","C105","C106","C103","U103",
       "CN111","U116","C116","C121"}
I2C = {"U111","U112","U113","U114","C111","C112","C113","C114","C115","R111","R112","R113","R114","R115"}
ISO = {"U117","U118","C124","C125","C126","R118","R119"}
PWR = {"J112","F112","Q112","R116","R117","D112","U115","L112","D113","C117","C118","C119","C120","C122","C137",
       "U131","L131","D131","C131","C132","C133","C134","C135","C136","R131","R132","R133","R134","R135","U132","C123","D133","J131",
       "RELAY131","Q131","R136","R137","D132","J132"}
def block(ref):
    if ref in PWRSET or ref in PWR: return "pwr"
    if ref in ESP: return "esp"
    if ref in I2C: return "i2c"
    if ref in ISO: return "iso"
    m = re.match(r"([A-Z]+)(\d+)", ref); p, d = m.group(1), int(m.group(2))
    if 70 <= d <= 92: return "iso"
    return "ana"
COL = {"ana": ("#E1F5EE", "#0F6E56"), "iso": ("#EEEDFE", "#534AB7"), "pwr": ("#FAECE7", "#993C1D"),
       "esp": ("#F1EFE8", "#5F5E5A"), "i2c": ("#F1EFE8", "#5F5E5A")}
def pinxy(p):
    r, n = p.split('.')
    x, y, rot = P[r]
    if r == "U101":                     # module WROOM-1 tourné : antenne à gauche
        n = int(n)
        if n <= 14: xn, yn = -9.0, -5.15 + (n - 1) * 1.27
        elif n <= 26: xn, yn = -7.0 + (n - 15) * 1.27, 12.75
        elif n <= 40: xn, yn = 9.0, 11.36 - (n - 27) * 1.27
        else: xn, yn = 0.0, 2.0
        return (x + yn, y - xn)
    return (x, y)
def mst(pts):
    if len(pts) < 2: return []
    used, rest, e = [pts[0]], pts[1:], []
    while rest:
        best = min(((a, b) for a in used for b in rest), key=lambda ab: math.dist(ab[0], ab[1]))
        e.append(best); used.append(best[1]); rest.remove(best[1])
    return e
def render(out, view=(0, BW, 0, BH), scale=1.0, labels=True, rats=True):
    w = (view[1]-view[0]); h = (view[3]-view[2])
    fig, ax = plt.subplots(figsize=(w/175*16*scale, h/175*16*scale))
    ax.set_xlim(view[0]-2, view[1]+2); ax.set_ylim(view[3]+2, view[2]-2); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0, 0), BW, BH, boxstyle="round,pad=0,rounding_size=2", fill=False, ec="#444", lw=1.2))
    zones = [((0,0,99,40),"#EEEDFE","Sorties isolées (VISO)"), ((104,0,175,43.5),"#FAECE7","Servo · relais · entrée 12 V"),
             ((127,44,175,88),"#FAECE7","Vannes 2 × 3"), ((124,90,175,125),"#FAECE7","12 V → 5 V · +3V3"),
             ((0,82,124,125),"#E1F5EE","Entrées capteur ×6"), ((88,46,124,72),"#F1EFE8","Bus I2C"), ((27,44.5,56,72.5),"#F1EFE8","3V3_MCU")]
    for (x1,y1,x2,y2),c,t in zones:
        ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fc=c,ec="none",alpha=0.55,zorder=0))
    ax.add_patch(Rectangle((0,73.5),124,8,fc="none",ec="#888",ls=(0,(3,2)),lw=0.8)); ax.plot([1,123],[81.6,81.6],color="#888",lw=0.6,ls=(0,(0.6,1.4)))
    ax.text(16,77.5,"couloir des bus THR / CS / ID / TLV_OUT (couche 4) · rangée de vias de couture côté analogique",fontsize=5*scale,color="#666",va="center",clip_on=True)
    x1,y1,x2,y2 = KEEPOUT_ANT; ax.add_patch(Rectangle((x1,y1),x2-x1,y2-y1,fc="none",ec="#E24B4A",ls=(0,(4,2)),lw=1))
    ax.text(3.5,69.6,"antenne",fontsize=4.5*scale,color="#A32D2D",ha="center",clip_on=True)
    ax.plot([0,99],[40,40],color="#A32D2D",lw=1.2,ls=(0,(5,3)))
    for hname,(hx,hy,kind) in HOLES.items():
        ax.add_patch(Circle((hx,hy),1.6,fc="white",ec="#333",lw=0.8,ls="--" if kind=="NPTH" else "-"))
        ax.add_patch(Circle((hx,hy),3.5,fc="none",ec="#999",lw=0.5,ls=":")); ax.text(hx,hy+5.2,hname,clip_on=True,fontsize=4.5*scale,ha="center",color="#333")
    for r,(x,y,rot) in P.items():
        q = rect(r); fc, ec = COL[block(r)]
        if r == "U101":
            ax.add_patch(Rectangle((q[0],q[1]),q[2]-q[0],q[3]-q[1],fc=fc,ec=ec,lw=0.9,zorder=4))
            ax.add_patch(Rectangle((q[0],q[1]),6.3,q[3]-q[1],fc="none",ec=ec,hatch="////",lw=0.5,zorder=4))
            for k in range(1, 41):
                px, py = pinxy(f"U101.{k}"); ax.add_patch(Circle((px, py), 0.35, fc=ec, ec="none", zorder=5))
            ax.text(x+3,y,"U101\nWROOM-1",fontsize=5.5*scale,ha="center",va="center",color=ec,clip_on=True); continue
        ax.add_patch(Rectangle((q[0],q[1]),q[2]-q[0],q[3]-q[1],fc=fc,ec=ec,lw=0.5,zorder=4))
        if labels:
            fs = 3.2*scale if (q[2]-q[0])*(q[3]-q[1]) < 12 else 4.5*scale
            ax.text(x,y,r,clip_on=True,fontsize=fs,ha="center",va="center",color=ec,zorder=5,rotation=90 if rot in (90,270) and (q[3]-q[1])>(q[2]-q[0]) and fs<4 else 0)
    if rats:
        for n,pins in nets.items():
            if n in PLANES: continue
            pts = list(dict.fromkeys(pinxy(p) for p in pins if p.split('.')[0] in P))
            for a,b in mst(pts): ax.plot([a[0],b[0]],[a[1],b[1]],color="#185FA5",lw=0.35,alpha=0.7,zorder=6)
    for (x1,y1,x2,y2),c,t in zones:
        if x2-x1>15: ax.text(x1+1,y1+1.8,t,clip_on=True,fontsize=6*scale,color="#444",weight="bold",va="top",zorder=7)
    fig.savefig(out,dpi=220,bbox_inches="tight",facecolor="white"); plt.close(fig)
if __name__ == "__main__":
    render("placement_complet.png")
    render("zoom_entree_voie1.png", view=(6,46,80,126), scale=2.6, rats=True)
    render("zoom_isole_alim.png", view=(0,100,0,48), scale=1.6)
    render("zoom_puissance.png", view=(100,175,0,125), scale=1.4)
    render("zoom_servo.png", view=(125,175,40,72), scale=2.4)
    tot = 0
    for n,pins in nets.items():
        if n in PLANES: continue
        pts=list(dict.fromkeys(pinxy(p) for p in pins if p.split('.')[0] in P))
        tot += sum(math.dist(a,b) for a,b in mst(pts))
    print("longueur ratsnest (signaux, hors plans) :", round(tot), "mm")
