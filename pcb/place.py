"""Placement des composants TriggerFlow (carte 175 x 125 mm, 4 couches).
Origine : coin arrière gauche, x vers la droite, y vers l'avant (vers le bas sur le dessin). Cotes en mm.
Tailles = zones d'encombrement estimées (corps + pastilles), à recaler sur les empreintes réelles.
Repris de la conversation « Implémentation PCB optimisée » du 04/10/2026 (version v4).
Branche v2-wroom : module ESP32-S3-WROOM-1 (U101) au bord gauche, antenne au bord, USB-C natif (J101).
Numérotation EasyEDA (2e renumérotation du 10/10) : netlist_v2_wroom.json = export EasyEDA (netlist_v2_easyeda_2026-10-10.tel)."""
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
 "WIRELM-SMD_ESP32-S3-WROOM-1": (18.0, 25.5), "USB-C_SMD-TYPE-C-31-M-12": (9.4, 7.8), "SW-SMD_4P-L5.1-W5.1": (5.1, 5.1), "TP-1.5": (1.6, 1.6), "HDR-TH_3P-P2.54-V-M": (7.8, 2.8), "HDR-TH_2P-P2.54-V-M": (5.3, 2.8),
}
def size_of(fp):
    for k in sorted(FP, key=len, reverse=True):
        if k in fp: return FP[k]
    if "ESP32" in fp: return FP["DEVKIT"]
    raise KeyError(fp)

tel = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "netlist_v2_wroom.json")))
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
# module tourné de 90° : antenne au bord gauche (x = 0,5), broches 1-14 vers l'avant (TLV_OUT), 15-26 vers le bus I2C,
# 27-40 vers les optos (commandes flash, vannes 1-2-4)
put("U101", 13.25, 54.0, 90)
put("C101", 9.2, 65.7, 90); put("C102", 11.3, 65.5, 90)               # découplage au plus près de la broche 2 (3V3)
put("R107", 13.3, 65.5, 90); put("C103", 15.3, 65.5, 90)              # RC de EN (10 k / 1 µF)
put("J101", 4.4, 75.0, 90); put("U102", 12.0, 74.8)                   # USB-C au bord gauche, protection juste derrière
put("R106", 12.0, 78.6); put("R105", 15.2, 78.6)                      # CC1 / CC2 5,1 k
put("D102", 20.0, 70.5)                                               # VBUS -> 5V_MCU
put("D101", 31.0, 47.2)                                               # +5V -> 5V_MCU (via vers la bande +5V d'Inner2)
put("C106", 35.5, 51.5, 90); put("U104", 40.5, 50.0)                  # régulateur 3V3_MCU
put("C104", 46.0, 49.0, 90); put("C105", 48.4, 49.0, 90)
put("R108", 28.5, 52.0, 90)                                           # tirage de IO0
put("SW101", 33.0, 60.0); put("SW102", 41.0, 60.0)                    # RESET, BOOT
put("U103", 50.0, 66.0)                                                # barrette console UART0 1 x 3 (GND, TX, RX), non montée par JLC

# ---------------- bus I2C ----------------
put("U111", 113.0, 54.0); put("C111", 106.5, 55.0, 90); put("R113", 106.5, 58.5, 90); put("R111", 106.5, 51.5, 90)
put("U112", 95.0, 66.0); put("C112", 95.0, 69.5)
put("U113", 104.0, 66.0); put("C113", 104.0, 69.5); put("R112", 108.4, 66.0, 90)
put("U114", 117.0, 66.0); put("C114", 117.0, 70.3); put("C115", 121.8, 66.0, 90)
put("R114", 96.0, 50.0); put("R115", 96.0, 52.2)

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
# alimentation isolée (U117 hors de l'axe de l'antenne)
put("U117", 90, 40, 90); put("C124", 95.5, 44.5); put("C125", 94.6, 34.5, 90)
put("U118", 62.0, 28.0); put("C126", 67.5, 33.0, 90); put("R118", 96.5, 36.8, 90); put("R119", 98.0, 31.0, 90)

# ======== colonne de droite, reprise de l'implantation EasyEDA du 09/10 (servo et relais à l'arrière, 5 V à l'avant) ========
# ---------------- entrée 12 V (coin arrière droit) ----------------
put("J112", 162, 4.5); put("F112", 171.5, 16.5, 90); put("R116", 163, 16.5); put("R117", 163, 18.7)
put("Q112", 171, 27, 90); put("D112", 163, 27, 90)

# ---------------- relais ----------------
put("J132", 147, 5.5); put("RELAY131", 147, 24, 90); put("D132", 154.5, 24, 90)
put("Q131", 139.5, 22); put("R136", 139.5, 17.5, 90); put("R137", 139.5, 26.5, 90)

# ---------------- servo 6 V (languette de U131 à gauche, broches vers L131 et les condensateurs) ----------------
put("J131", 116, 5.5); put("C136", 130.5, 7)                           # bornier servo et 470 µF au bord arrière
put("U131", 113, 34, 90); put("L131", 129.5, 31); put("C134", 123, 18.5); put("C135", 131, 16.5)
put("D131", 123, 41.6); put("C131", 128, 40.5); put("C132", 131.8, 40.5); put("C133", 135.2, 40.5)
put("R131", 107, 42.2); put("R132", 110.4, 42.2); put("R133", 113.8, 42.2)
put("U132", 116, 15); put("R135", 112, 15, 90); put("R134", 110.2, 15, 90); put("D133", 108.5, 15, 90); put("C123", 116, 18.6)

# ---------------- vannes 2 x 3 (connecteurs vers l'extérieur du bloc, rail 12 V au milieu) ----------------
VX = [134, 150, 166]
VR = {1: ("R93", "R96"), 2: ("R94", "R97"), 3: ("R95", "R98"), 4: ("R99", "R102"), 5: ("R100", "R103"), 6: ("R101", "R104")}
DY = -27.75
for i, cx in enumerate(VX):
    a_, b_ = i + 1, i + 4
    put(f"CN9{a_}", cx, 75.5 + DY); put(f"Q9{a_}", cx - 4, 82 + DY); put(f"D9{a_}", cx + 3.5, 82 + DY)
    put(VR[a_][0], cx - 5.5, 86.5 + DY); put(VR[a_][1], cx - 5.5, 88.6 + DY); put(f"F9{a_}", cx + 3.5, 88.5 + DY)
    put(f"F9{b_}", cx + 3.5, 97.5 + DY); put(VR[b_][0], cx - 5.5, 97.4 + DY); put(VR[b_][1], cx - 5.5, 99.5 + DY)
    put(f"Q9{b_}", cx - 4, 104 + DY); put(f"D9{b_}", cx + 3.5, 104 + DY); put(f"CN9{b_}", cx, 110.5 + DY, 180)

# ---------------- 12 V -> 5 V (coin avant droit), boucle de découpage compacte ----------------
# U115 tourné : broches vers la gauche (C118-C120 et D113 collés), languette au bord droit ; C117 au-dessus de l'entrée
put("U115", 166, 108, 90); put("C117", 152, 96.8)
put("C118", 155.5, 105); put("C119", 155.5, 107.3); put("C120", 155.5, 109.5); put("D113", 151.5, 108.5, 90)
put("L112", 141.5, 109.3); put("C122", 130, 109); put("C137", 130, 115.3, 90)

# ---------------- +3V3 (U116) et LED ----------------
put("C121", 137.6, 120.5, 90); put("U116", 144, 120.5); put("C116", 149.8, 120.5, 90); put("CN111", 157.5, 121.75)

HOLES = {"H1": (4, 4, "NPTH"), "H5": (101, 6, "NPTH"), "H2": (171, 4, "GND"), "H3": (4, 121, "GND"),
         "H4": (171, 121, "GND"), "H6": (66, 121, "GND")}  # H7 (124, 76) supprimé : il coupait la bande +5V d'Inner2
KEEPOUT_ANT = (0, 43.5, 7, 68)          # antenne du module au bord : sans cuivre, toutes couches
BARRIER = (0, 38.5, 99, 41.5)           # seuls les composants à cheval
STRADDLE = {"U71", "U81", "U83", "U117"}

def rect(ref):
    x, y, rot = P[ref]; w, h = size_of(comps[ref])
    if rot in (90, 270): w, h = h, w
    return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
