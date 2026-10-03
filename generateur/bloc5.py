"""Bloc 5 — Alimentation : 12 V secteur -> fusible, anti-inversion, TVS -> +12V ; LM2596S-5.0 -> +5V ; AMS1117-3.3 -> +3V3."""
from kicadgen import *

SRC = "src_bloc5.kicad_sch"
FILE = "alimentation.kicad_sch"

def P12(x, y):  return add("power:+12V", pwr_ref(), "+12V", x, y, 0, hide_ref=True, val_at=(0, -3.81))
def P5(x, y):   return add("power:+5V", pwr_ref(), "+5V", x, y, 0, hide_ref=True, val_at=(0, -3.81))
def P33(x, y):  return add("power:+3V3", pwr_ref(), "+3V3", x, y, 0, hide_ref=True, val_at=(0, -3.81))
def G(x, y):    return add("power:GND", pwr_ref(), "GND", x, y, 0, hide_ref=True, val_at=(0, 3.81))
def cap(ref, val, x, y, pol=False):
    return add("Device:C_Polarized" if pol else "Device:C", ref, val, x, y, 0, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")
def dv(lib, ref, val, x, y):   # diode verticale, cathode en haut
    return add(lib, ref, val, x, y, 270, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")

def layout():
    Y = 76.2
    # ---- 1. Entrée et protections -------------------------------------------------------
    j = add("Connector:Screw_Terminal_01x02", "J501", "12V_IN", 25.4, Y, 0, mirror="y",
            ref_at=(0, -5.08), val_at=(0, 7.62))
    f = add("Device:Fuse", "F501", "6.3A T", 40.64, Y, 90, ref_at=(0, -2.54), val_at=(0, 2.54))
    q = add("Transistor_FET:FDS9435A", "Q501", "AO4407A", 55.88, Y + 2.54, 90, ref_at=(-7.62, 5.08), val_at=(-7.62, 7.62), justify="right")
    wire_abs(j.pin(1), f.pin(1)); lab("VIN_RAW", 31.75, Y)
    wire_abs(f.pin(2), q.pin(5)); lab("VIN_F", 45.72, Y)
    g1 = G(33.02, 86.36); wire_abs(j.pin(2), (33.02 + DX, j.pin(2)[1]), g1.pin(1))
    # pont de grille
    r2 = res_v("R502", "10k", 55.88, 92.71)
    wire_abs(q.pin(4), r2.pin(1))
    g2 = G(55.88, 100.33); wire_abs(r2.pin(2), g2.pin(1))
    r1 = res_v("R501", "10k", 66.04, 81.28)
    wire_abs(r1.pin(1), (66.04 + DX, Y + DY))
    wire_abs(r1.pin(2), (66.04 + DX, 86.36 + DY), (55.88 + DX, 86.36 + DY))
    lab("Q501_G", 58.42, 86.36)
    # TVS
    d1 = dv("Device:D_Zener", "D501", "SMBJ15A", 81.28, 83.82)
    wire_abs(d1.pin(1), (81.28 + DX, Y + DY))
    g3 = G(81.28, 91.44); wire_abs(d1.pin(2), g3.pin(1))
    wire_abs(q.pin(1), (139.7 + DX, Y + DY))
    P12(96.52, Y)

    # ---- 2. +5V : LM2596S-5.0 ----------------------------------------------------------
    c1 = cap("C501", "470u", 116.84, 83.82, True)
    c7 = cap("C507", "10u", 124.46, 83.82)
    c8 = cap("C508", "10u", 132.08, 83.82)
    c2 = cap("C502", "100n", 139.7, 83.82)
    for c in (c1, c7, c8, c2):
        wire_abs(c.pin(1), (c.pin(1)[0], Y + DY))
        gg = G(c.x - DX, 91.44); wire_abs(c.pin(2), gg.pin(1))
    u = add("Regulator_Switching:LM2596S-5", "U501", "LM2596S-5.0", 157.48, 81.28, 0, ref_at=(-10.16, -8.89), val_at=(0, -8.89))
    wire_abs((139.7 + DX, Y + DY), (144.78 + DX, Y + DY), (144.78 + DX, u.pin(1)[1]), u.pin(1))
    wire_abs(u.pin(5), (143.51 + DX, u.pin(5)[1]), (143.51 + DX, 91.44 + DY))
    g4 = G(143.51, 91.44)
    g5 = G(157.48, 93.98); wire_abs(u.pin(3), g5.pin(1))
    sw = (175.26 + DX, u.pin(2)[1])
    wire_abs(u.pin(2), sw)
    lab("BUCK_SW", 170.18, u.pin(2)[1] + 0)
    l = add("Device:L", "L501", "33uH 4A", 181.61, u.pin(2)[1], 90, ref_at=(0, -2.54), val_at=(0, 2.54))
    wire_abs(sw, l.pin(1))
    d2 = dv("Device:D_Schottky", "D502", "SS54", 175.26, 91.44)
    wire_abs(d2.pin(1), sw)
    g6 = G(175.26, 99.06); wire_abs(d2.pin(2), g6.pin(1))
    Y5 = u.pin(2)[1]
    c3 = cap("C503", "330u", 193.04, 91.44, True)
    c4 = cap("C504", "100n", 203.2, 91.44)
    wire_abs(l.pin(2), (226.06 + DX, Y5))
    for c in (c3, c4):
        wire_abs(c.pin(1), (c.pin(1)[0], Y5))
        gg = G(c.x - DX, 99.06); wire_abs(c.pin(2), gg.pin(1))
    wire_abs(u.pin(4), (190.5 + DX, u.pin(4)[1]), (190.5 + DX, Y5))
    P5(209.55, Y5)

    # ---- 3. +3V3 : AMS1117-3.3 ---------------------------------------------------------
    c5 = cap("C505", "10u", 218.44, 91.44)
    wire_abs(c5.pin(1), (c5.pin(1)[0], Y5)); g7 = G(218.44, 99.06); wire_abs(c5.pin(2), g7.pin(1))
    v = add("Regulator_Linear:AMS1117-3.3", "U502", "AMS1117-3.3", 233.68, Y5 - 0, 0, ref_at=(0, -6.35), val_at=(0, -3.81))
    wire_abs((226.06 + DX, Y5), v.pin(3))
    g8 = G(233.68, 99.06); wire_abs(v.pin(1), g8.pin(1))
    c6 = cap("C506", "10u", 248.92, 91.44)
    wire_abs(v.pin(2), (254.0 + DX, Y5))
    wire_abs(c6.pin(1), (c6.pin(1)[0], Y5)); g9 = G(248.92, 99.06); wire_abs(c6.pin(2), g9.pin(1))
    P33(254.0, Y5)

    # ---- zones & notes ------------------------------------------------------------------
    zone("1 · Entrée 12 V et protections", 15.24, 55.88, 109.22, 106.68)
    zone("2 · +5V : LM2596S-5.0 (3 A)", 111.76, 55.88, 212.09, 106.68)
    zone("3 · +3V3 : AMS1117-3.3", 214.63, 55.88, 264.16, 106.68)
    note("+12V → vannes (V_VALVE), moteur (VMOT via F801),\nlumière (V_ACC via JP902)", 66.04, 63.5, 1.27)
    note("Notes :\n"
         "• Bloc secteur 12 V, 5 A minimum (60 W). J501 : bornier vers la prise jack de façade.\n"
         "• F501 : fusible CMS 6,3 A temporisé (2410), protège contre un court-circuit franc ; chaque sortie a sa PTC.\n"
         "• Q501 (AO4407A, canal P) : anti-inversion de polarité sans chute. Pont R501/R502 : VGS ≈ -6 V (limite ±25 V).\n"
         "• D501 (SMBJ15A) après Q501 : écrête les surtensions à 24,4 V, ne conduit jamais en cas d'inversion.\n"
         "• C503 : électrolytique aluminium low-ESR (pas de polymère : ESR trop faible = instabilité du LM2596).\n"
         "• C501 : 470 µF 25 V. C503 : 330 µF 25 V low-ESR (Panasonic FK). C507, C508 (10 µF 25 V céramique) au plus près de VIN : absorbent le courant d'entrée pulsé.\n"
         "• U501 : LM2596S-5.0, FB relié au +5V après L501 (version fixe), ON/OFF à GND (toujours actif).\n"
         "• PCB : boucle C501-U501-D502 la plus courte possible ; cuivre et vias sous la languette de U501 (≈ 3 W).\n"
         "• U502 : AMS1117-3.3 alimenté par le +5V, ≈ 100 mA. Pistes 12 V : 2 mm minimum ou zone de cuivre.",
         15.24, 116.84, 1.27)
