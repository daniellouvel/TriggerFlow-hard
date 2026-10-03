"""Bloc 5b — Alimentation isolée VISO_3V3 / VISO_GND : B0505S-1WR3 (5 V -> 5 V isolé) + AMS1117-3.3."""
from kicadgen import *
SRC = "src_bloc5b.kicad_sch"; FILE = "alim_isolee.kicad_sch"
def A(x, y): return (R2(x + DX), R2(y + DY))
def W(*pts): wire_abs(*[A(*p) for p in pts])
def G(x, y): return add("power:GND", pwr_ref(), "GND", x, y, 0, hide_ref=True, val_at=(0, 3.81))

def layout():
    u = add("TriggerFlow:B0505S-1WR3", "U121", "B0505S-1WR3", 101.6, 76.2, 0, ref_at=(0, -7.62), val_at=(0, 7.62))
    # primaire
    W((91.44, 73.66), (66.04, 73.66))
    add("power:+5V", pwr_ref(), "+5V", 66.04, 73.66, 0, hide_ref=True, val_at=(0, -3.81))
    cap_v("C121", "10uF", 76.2, 77.47); W((76.2, 81.28), (76.2, 83.82)); G(76.2, 83.82)
    W((91.44, 78.74), (86.36, 78.74), (86.36, 83.82)); G(86.36, 83.82)
    # secondaire
    W((111.76, 73.66), (152.4, 73.66)); lab("VISO_5V", 139.7, 73.66)
    cap_v("C122", "10uF", 121.92, 77.47)
    res_v("R121", "220", 134.62, 77.47); res_v("R122", "220", 134.62, 88.9)
    W((134.62, 81.28), (134.62, 85.09)); lab("PRELOAD", 134.62, 83.82)
    add("Regulator_Linear:AMS1117-3.3", "U122", "AMS1117-3.3", 160.02, 73.66, 0, ref_at=(0, -6.35), val_at=(0, -3.81))
    W((167.64, 73.66), (185.42, 73.66)); lab("VISO_3V3", 177.8, 73.66)
    cap_v("C123", "10uF", 175.26, 77.47)
    # bus VISO_GND
    W((111.76, 78.74), (116.84, 78.74), (116.84, 96.52))
    W((116.84, 96.52), (175.26, 96.52)); lab("VISO_GND", 142.24, 96.52)
    for x, y in ((121.92, 81.28), (134.62, 92.71), (160.02, 81.28), (175.26, 81.28)):
        W((x, y), (x, 96.52))
    zone("Côté primaire (+5V / GND)", 55.88, 55.88, 100.33, 104.14)
    zone("Côté isolé (VISO_5V / VISO_3V3 / VISO_GND)", 102.87, 55.88, 193.04, 104.14)
    note("Notes :\n"
         "• U121 B0505S-1WR3 : non régulé, charge minimale 20 mA (10 %). R121 + R122 (440 Ω) ≈ 11 mA + U122 + optos ≥ 20 mA.\n"
         "• U122 AMS1117-3.3 côté isolé : VISO_3V3 stable (HCPL-063L : 2,7 à 3,6 V). Languette SOT-223 = VOUT (VISO_3V3).\n"
         "• Charge côté isolé < 40 mA (3 HCPL-063L, 3 74LVC2G04, pull-ups) ; module 200 mA max.\n"
         "• Aucun composant entre GND et VISO_GND. PCB : bande sans cuivre (≈ 2 mm) sous U121 entre broches 1-2 et 3-4 ;\n"
         "  plan VISO_GND séparé pour tout le côté isolé (Bloc 2). C121 côté entrée, C122 / C123 au plus près.\n"
         "• VISO_3V3 et VISO_GND : mêmes noms que sur les feuilles du Bloc 2 (raccordement par étiquette).",
         55.88, 114.3, 1.27)
