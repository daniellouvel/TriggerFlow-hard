"""DXF TriggerFlow pour EasyEDA Pro. Unité mm, origine au coin AVANT GAUCHE (convention DXF, Y vers le haut).
Conversion depuis le placement (origine arrière gauche, y vers l'avant) : Y_dxf = 125 - y."""
import ezdxf, math
from ezdxf import units
BW, BH, RC = 175.0, 125.0, 2.0
F = lambda x, y: (x, BH - y)                      # placement -> DXF

def new():
    d = ezdxf.new("R2010", setup=True); d.units = units.MM; d.header["$INSUNITS"] = 4; d.header["$MEASUREMENT"] = 1
    return d
def rrect(msp, x1, y1, x2, y2, r, layer):
    """Rectangle à coins arrondis en coordonnées placement, polyligne fermée avec bulges."""
    b = math.tan(math.radians(90) / 4)
    pts = [(x1 + r, y1, 0), (x2 - r, y1, b), (x2, y1 + r, 0), (x2, y2 - r, b), (x2 - r, y2, 0), (x1 + r, y2, b), (x1, y2 - r, 0), (x1, y1 + r, b)]
    # sens horaire en placement = anti-horaire en DXF après inversion de Y : bulge négatif
    msp.add_lwpolyline([(*F(x, y), 0, 0, -bb) for x, y, bb in pts], format="xyseb", close=True, dxfattribs={"layer": layer})
def rect(msp, x1, y1, x2, y2, layer):
    msp.add_lwpolyline([F(x1, y1), F(x2, y1), F(x2, y2), F(x1, y2)], close=True, dxfattribs={"layer": layer})
def poly(msp, pts, layer): msp.add_lwpolyline([F(*p) for p in pts], close=True, dxfattribs={"layer": layer})
def txt(msp, s, x, y, h, layer):
    msp.add_text(s, height=h, dxfattribs={"layer": layer}).set_placement(F(x, y), align=ezdxf.enums.TextEntityAlignment.TOP_LEFT)

HOLES = {"H1": (4, 4, "NPTH"), "H5": (101, 6, "NPTH"), "H2": (171, 4, "GND"), "H3": (4, 121, "GND"),
         "H4": (171, 121, "GND"), "H6": (66, 121, "GND")}   # H7 supprimé

# ---------- 1. contour + fente + trous non métallisés  -> couche Contour de carte ----------
d = new(); m = d.modelspace(); d.layers.add("CONTOUR", color=7)
rrect(m, 0, 0, BW, BH, RC, "CONTOUR")
# v2 : plus de fente, l'antenne du module est au bord gauche
for h, (x, y, k) in HOLES.items():
    if k == "NPTH": m.add_circle(F(x, y), 1.6, dxfattribs={"layer": "CONTOUR"})
d.saveas("TriggerFlow_1_contour.dxf")

# ---------- 2. repères des trous métallisés GND  -> couche Document (à remplacer par des pastilles) ----------
d = new(); m = d.modelspace(); d.layers.add("TROUS_GND", color=3)
for h, (x, y, k) in HOLES.items():
    if k.startswith("GND"):
        m.add_circle(F(x, y), 1.6, dxfattribs={"layer": "TROUS_GND"}); m.add_circle(F(x, y), 3.0, dxfattribs={"layer": "TROUS_GND"})
        m.add_circle(F(x, y), 3.5, dxfattribs={"layer": "TROUS_GND", "linetype": "DASHED"})
        txt(m, h + (" (option)" if "option" in k else ""), x + 4, y - 1, 1.5, "TROUS_GND")
d.saveas("TriggerFlow_2_trous_GND.dxf")

# ---------- 3. zones interdites (antenne, bande sous U113)  -> à convertir en zones interdites ----------
d = new(); m = d.modelspace(); d.layers.add("INTERDIT", color=1)
rect(m, 0, 43.5, 7, 68, "INTERDIT")                                 # antenne du module au bord : sans cuivre, toutes couches
rect(m, 0, 38.5, 99.4, 41.5, "INTERDIT")                            # barrière d'isolation
d.saveas("TriggerFlow_3_zones_interdites.dxf")

# ---------- 4. plan des zones (repères de routage)  -> couche Document ----------
d = new(); m = d.modelspace(); d.layers.add("ZONES", color=8); d.layers.add("BARRIERE", color=1)
Z = [("Sorties isolées VISO", 0, 0, 99, 40), ("Servo, relais, entrée 12V", 104, 0, 175, 43.5),
     ("U105 WROOM-1 (antenne <-)", 0.5, 45, 26, 63), ("USB-C J141", 0.5, 70.3, 8.3, 79.7), ("3V3_MCU, RESET, BOOT", 27, 44.5, 56, 72.5), ("Bus I2C", 88, 46, 124, 72), ("Couloir de bus (L4) + vias", 0, 73.5, 124, 81.5),
     ("Vannes 2x3", 127, 44, 175, 88), ("Entrées capteur x6", 0, 82, 124, 125), ("12V -> 5V, +3V3, LED", 124, 90, 175, 125)]
for t, x1, y1, x2, y2 in Z:
    rect(m, x1, y1, x2, y2, "ZONES"); txt(m, t, x1 + 1, y1 + 1, 1.8, "ZONES")
m.add_line(F(0, 40), F(99, 40), dxfattribs={"layer": "BARRIERE"})
rect(m, 0, 38.5, 99, 41.5, "BARRIERE"); txt(m, "Barrière isolation : 3 mm sans cuivre (sauf U71, U81, U83, U113)", 2, 36.2, 1.4, "BARRIERE")
for x in [1 + 3.5 * i for i in range(36)]: m.add_circle(F(x, 81.6), 0.3, dxfattribs={"layer": "ZONES"})   # rangée de vias de couture
d.saveas("TriggerFlow_4_zones_document.dxf")

# ---------- 5. découpage de la couche 3 (plages d'alimentation)  -> Interne 2 ----------
d = new(); m = d.modelspace()
for n, c in (("L3_VISO_3V3", 6), ("L3_+12V", 1), ("L3_+3V3", 4), ("L3_+5V", 2), ("L3_3V3_MCU", 5)): d.layers.add(n, color=c)
rect(m, 0.5, 0.5, 96.3, 38.5, "L3_VISO_3V3")
poly(m, [(104, 0.5), (174.5, 0.5), (174.5, 114.5), (146.5, 114.5), (146.5, 102), (127.5, 102), (127.5, 41.5), (104, 41.5)], "L3_+12V")   # v2 : jusqu'à l'entrée de U111 (coin avant droit)
poly(m, [(52, 45.5), (121, 45.5), (121, 117), (4, 117), (4, 74), (52, 74)], "L3_+3V3")
rect(m, 9, 45.5, 50, 72.5, "L3_3V3_MCU")          # rail du module (U141 -> U105)
poly(m, [(28, 42), (126.5, 42), (126.5, 103.5), (145, 103.5), (145, 116), (174.5, 116), (174.5, 124.5), (0.5, 124.5), (0.5, 118), (122, 118), (122, 44.5), (28, 44.5)], "L3_+5V")   # v2 : plus de bande gauche, tronçon prolongé jusqu'à D101 (x = 28)
for t, x, y in (("VISO_3V3", 40, 20), ("+12V", 150, 75), ("+3V3", 30, 100), ("+5V", 145, 120), ("3V3_MCU", 30, 60)): txt(m, t, x, y, 3, "L3_" + t)
d.saveas("TriggerFlow_5_couche3_plages.dxf")
print("ok")
