"""Placement des composants TriggerFlow (carte 175 x 125 mm, 4 couches).
Origine : coin arrière gauche, x vers la droite, y vers l'avant (vers le bas sur le dessin). Cotes en mm.
Tailles = zones d'encombrement estimées (corps + pastilles), à recaler sur les empreintes réelles.
Repris de la conversation « Implémentation PCB optimisée » du 04/10/2026 (version v4)."""
import json, csv, math, collections, os

BW, BH = 175.0, 125.0
FP = {  # nom d'empreinte (préfixe) -> (largeur, hauteur) à rot 0
 "R0603": (2.6, 1.4), "C0603": (2.6, 1.4), "C0805": (3.2, 1.8), "F1206": (4.0, 2.0), "F1812": (5.4, 3.8),
 "F2410": (8.0, 3.5), "SOD-523": (2.2, 1.2), "SOD-123F": (4.0, 2.0), "SMA": (6.4, 3.0), "SMB": (6.6, 4.2),
 "SOT-23-6": (3.2, 3.2), "SOT-23-5": (3.2, 3.2), "SOT-23": (3.2, 3.0), "MSOP": (5.4, 3.6), "SOP-8": (6.6, 5.4),
 "SO-8": (6.6, 5.4), "SOIC-8": (6.6, 5.4), "TSSOP-16": (6.8, 5.4), "SSOP-28": (8.4, 10.4),
 "SOT-223": (6.9, 7.4), "TO-263": (10.5, 15.0), "IND": (13.0, 13.0), "CAP-SMD_BD10": (11.0, 11.0),
 "CAP-SMD_BD8": (9.0, 9.0), "CONN-TH_2P-P2.50": (8.0, 6.5), "KF128-5.08-2P": (10.5, 8.5), "KF128-5.08-3P": (15.8, 10.7),
 "RJ45-90": (16.3, 21.5), "DEVKIT": (69.0, 28.0), "B0505S": (12.0, 6.5), "PWRM": (12.0, 6.5), "HF32F": (21.0, 7.6), "HDR1x3": (7.8, 2.8),
}
def size_of(fp):
    for k in sorted(FP, key=len, reverse=True):
        if k in fp: return FP[k]
    if "ESP32" in fp: return FP["DEVKIT"]
    raise KeyError(fp)

tel = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "netlist_2026-10-05.json")))
comps = {r: fp for r, (fp, v) in tel["comps"].items()}
vals = {r: v for r, (fp, v) in tel["comps"].items()}
nets = {n: p for n, p in tel["nets"].items()}
# servo et relais présents dans la netlist du 05/10 (repères EasyEDA)

P = {}   # ref -> (x, y, rot)
def put(ref, x, y, rot=0): assert ref in comps, ref; P[ref] = (round(x, 2), round(y, 2), rot)

# ---------------- entrées capteur (6 bandes de 18 mm) ----------------
CX = [17, 35, 53, 79, 97, 115]
for n, cx in enumerate(CX, 1):
    put(f"J{n}1", cx, 114.25, 0)
    put(f"U{n}1", cx - 3.5, 86.0); put(f"R{n}5", cx + 1.6, 84.2); put(f"R{n}8", cx + 1.6, 86.2); put(f"R{n}3", cx + 1.6, 88.2)
    put(f"C{n}4", cx + 5.0, 84.2); put(f"C{n}6", cx + 5.0, 86.2); put(f"C{n}1", cx + 5.0, 88.2)
    put(f"U{n}2", cx - 3.5, 92.4); put(f"D{n}2", cx + 2.0, 92.4); put(f"C{n}2", cx + 5.0, 92.4, 90)
    put(f"C{n}5", cx + 7.4, 92.4, 90); put(f"C{n}7", cx - 7.9, 92.4, 90)
    put(f"R{n}6", cx - 4.5, 96.6); put(f"R{n}7", cx - 1.5, 96.6); put(f"R{n}2", cx + 1.5, 96.6)
    put(f"JP{n}1", cx + 4.5, 96.6); put(f"R{n}4", cx + 7.5, 96.6)
    put(f"F{n}1", cx - 6.4, 101.2); put(f"C{n}3", cx - 2.4, 101.2); put(f"D{n}3", cx + 0.9, 101.2)
    put(f"D{n}1", cx + 3.6, 101.2); put(f"R{n}1", cx + 7.2, 101.2)

# ---------------- ESP32 ----------------
put("U105", 35.5, 58.5, 0)           # USB-C côté x = 0, antenne côté x = 70
put("D101", 12.0, 65.0, 0)           # sous la DevKit (CMS bas), près de la broche 5V

# ---------------- bus I2C ----------------
put("U101", 113.0, 54.0); put("C101", 106.5, 55.0, 90); put("R107", 106.5, 58.5, 90); put("R105", 106.5, 51.5, 90)
put("U102", 95.0, 66.0); put("C102", 95.0, 69.5)
put("U103", 104.0, 66.0); put("C103", 104.0, 69.5); put("R106", 108.4, 66.0, 90)
put("U104", 117.0, 66.0); put("C104", 117.0, 70.3); put("C105", 121.8, 66.0, 90)
put("R108", 96.0, 50.0); put("R109", 96.0, 52.2)

# ---------------- sorties isolées ----------------
ISO = [("J71", 17), ("J81", 35), ("J82", 53), ("J83", 71), ("J84", 89)]
for j, cx in ISO: put(j, cx, 10.75, 180)
put("Q71", 13, 25); put("Q72", 21, 25); put("D71", 13, 28.8); put("D72", 21, 28.8)
put("R72", 9, 25, 90); put("R75", 25, 25, 90); put("U72", 17, 32.2); put("C72", 17, 28.6, 90)
put("R71", 14, 34.8, 90); put("R76", 20, 34.8, 90); put("U71", 17, 40, 90); put("C71", 17, 35.0)
put("R73", 12.6, 42.6); put("R74", 21.4, 42.6)
def pair(ux, qa, qb, xa, xb, ra, rb, pa, pb, ca, cb, inv, opto, rin_a, rin_b):
    put(qa, xa, 25); put(qb, xb, 25); put(f"D{qa[1:]}", xa, 28.5); put(f"D{qb[1:]}", xb, 28.5)
    put(ra, xa - 4, 25, 90); put(rb, xb + 4, 25, 90)
    put(inv, ux, 32.2); put(cb, ux, 28.6, 90); put(pa, ux - 3, 34.8, 90); put(pb, ux + 3, 34.8, 90)
    put(opto, ux, 40, 90); put(ca, ux, 35.0); put(rin_a, ux - 4.4, 42.6); put(rin_b, ux + 4.4, 42.6)
pair(44, "Q81", "Q82", 35, 53, "R82", "R85", "R81", "R86", "C81", "C82", "U82", "U81", "R83", "R84")
pair(80, "Q83", "Q84", 71, 89, "R88", "R91", "R87", "R92", "C83", "C84", "U84", "U83", "R89", "R90")
# alimentation isolée (U113 hors de l'axe de l'antenne)
put("U113", 90, 40, 90); put("C119", 95.5, 44.5); put("C120", 94.6, 34.5, 90)
put("U114", 62.0, 28.0); put("C121", 67.5, 33.0, 90); put("R113", 96.5, 36.8, 90); put("R114", 98.0, 31.0, 90)

# ---------------- relais ----------------
put("J122", 114, 5.7); put("RELAY121", 114, 23.2, 90); put("D122", 120.5, 22, 90)
put("Q121", 108, 35); put("R127", 104.8, 35, 90); put("R126", 108, 38.6)

# ---------------- alimentation 12 V -> 5 V ----------------
# flux : J111 -> F111 -> Q111 -> D111 -> C112 -> U111 (languette en haut, broches en bas) -> D112 / L111 -> C117
put("J111", 161, 4.5); put("F111", 153, 6, 90); put("Q111", 146, 6); put("R111", 146, 10.4); put("R112", 146, 12.2)
put("D111", 139, 7, 90); put("C112", 133, 18); put("U111", 150, 22)
put("C113", 143.5, 32, 90); put("C114", 143.5, 35.6, 90); put("C115", 143.5, 39, 90); put("D112", 149.5, 33, 90)
put("L111", 162, 33.5); put("C117", 170, 22); put("C118", 153.3, 38.5, 90)

# ---------------- servo 6 V ----------------
put("C123", 131.5, 50, 90); put("C122", 131.5, 54, 90); put("C124", 131.5, 57.6, 90)
put("U121", 141, 52); put("D121", 143, 62.5); put("L121", 153, 51.5); put("R123", 148.5, 61, 90); put("R122", 148.5, 64.4, 90)
put("R121", 136.5, 62.5, 90); put("C125", 155, 63); 
put("C127", 166.5, 65.3); put("J121", 169.15, 51.4, 90); put("U122", 161.5, 52.0, 0); put("R125", 162.0, 49.0, 0); put("D123", 162.0, 54.5, 0); put("C128", 162.0, 56.5, 0); put("R124", 162.0, 47.0, 0); put("C126", 162.0, 58.5, 0)

# ---------------- vannes 2 x 3 ----------------
VX = [135, 151, 167]
VR = {1: ("R93", "R96"), 2: ("R94", "R97"), 3: ("R95", "R98"), 4: ("R99", "R102"), 5: ("R100", "R103"), 6: ("R101", "R104")}
for i, cx in enumerate(VX):
    a, b = i + 1, i + 4
    put(f"CN9{a}", cx, 75.5); put(f"Q9{a}", cx - 4, 82); put(f"D9{a}", cx + 3.5, 82)
    put(VR[a][0], cx - 5.5, 86.5); put(VR[a][1], cx - 5.5, 88.6); put(f"F9{a}", cx + 3.5, 88.5)
    put(f"F9{b}", cx + 3.5, 97.5); put(VR[b][0], cx - 5.5, 97.4); put(VR[b][1], cx - 5.5, 99.5)
    put(f"Q9{b}", cx - 4, 104); put(f"D9{b}", cx + 3.5, 104); put(f"CN9{b}", cx, 110.5, 180)

# ---------------- +3V3 et LED ----------------
put("C116", 128.6, 119.5, 90); put("U112", 134, 119.5); put("C111", 140, 119.5, 90); put("CN101", 151, 121.75)

HOLES = {"H1": (4, 4, "NPTH"), "H5": (101, 6, "NPTH"), "H2": (171, 4, "GND"), "H3": (4, 121, "GND"),
         "H4": (171, 121, "GND"), "H6": (66, 121, "GND"), "H7": (124, 76, "GND (option)")}
KEEPOUT_ANT = (58, 43.5, 86, 73)        # sans cuivre, toutes couches
BARRIER = (0, 38.5, 99, 41.5)           # seuls les composants à cheval
STRADDLE = {"U71", "U81", "U83", "U113"}

def rect(ref):
    x, y, rot = P[ref]; w, h = size_of(comps[ref])
    if rot in (90, 270): w, h = h, w
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
