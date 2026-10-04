"""Sortie servo : rail 6 V dédié (LM2596S-ADJ depuis +12V, coupable par le MCP23017) + buffer 5 V du signal."""
from kicadgen import *
SRC = "src_servo.kicad_sch"; FILE = "sortie_servo.kicad_sch"
def A(x, y): return (R2(x + DX), R2(y + DY))
def W(*pts): wire_abs(*[A(*p) for p in pts])
def G(x, y, rot=0): return add("power:GND", pwr_ref(), "GND", x, y, rot, hide_ref=True, hide_val=(rot != 0), val_at=(0, 3.81))
def PW(kind, x, y, rot=0):
    return add(f"power:{kind}", pwr_ref(), kind, x, y, rot, hide_ref=True, val_at=(0, -3.81) if rot == 0 else (0, 3.81))
def dv(lib, ref, val, x, y): return add(lib, ref, val, x, y, 270, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")
def cpol(ref, val, x, y): return add("Device:C_Polarized", ref, val, x, y, 0, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")

def layout():
    # ---- entrée +12V et découplage
    PW("+12V", 27.94, 76.2); W((27.94, 76.2), (88.9, 76.2))
    for ref, val, x in (("C129", "10uF", 35.56), ("C122", "10uF", 43.18), ("C123", "100nF", 50.8)):
        cap_v(ref, val, x, 80.01); G(x, 83.82)
    u = add("Regulator_Switching:LM2596S-ADJ", "U121", "LM2596S-ADJ", 101.6, 78.74, 0, ref_at=(0, -8.89), val_at=(0, -6.35))
    G(101.6, 88.9); W((101.6, 86.36), (101.6, 88.9))
    # ON/OFF
    W((88.9, 81.28), (76.2, 81.28)); lab("SERVO_OFF", 76.2, 81.28, 180)
    res_v("R123", "10k", 81.28, 87.63); W((81.28, 81.28), (81.28, 83.82))
    PW("+3V3", 81.28, 93.98, 180); W((81.28, 91.44), (81.28, 93.98))
    # commutation
    W((114.3, 81.28), (123.19, 81.28)); lab("SERVO_SW", 119.38, 83.82)
    add("Device:L", "L121", "33uH 4A", 127.0, 81.28, 90, ref_at=(0, -5.08), val_at=(0, -2.54))
    dv("Device:D_Schottky", "D121", "SS54", 119.38, 88.9); W((119.38, 85.09), (119.38, 81.28))
    G(119.38, 95.25); W((119.38, 92.71), (119.38, 95.25))
    # sortie V_SERVO
    W((130.81, 81.28), (193.04, 81.28)); lab("V_SERVO", 182.88, 81.28)
    add("Device:R", "R122", "3.9k", 146.05, 77.47, 0, ref_at=(-2.54, -1.27), val_at=(-2.54, 1.27), justify="right")
    W((114.3, 76.2), (116.84, 76.2), (116.84, 73.66), (146.05, 73.66)); lab("SERVO_FB", 121.92, 73.66)
    res_h("R121", "1k", 153.67, 73.66); W((146.05, 73.66), (149.86, 73.66)); W((157.48, 73.66), (160.02, 73.66)); G(160.02, 73.66, 90)
    for ref, val, x, pol in (("C124", "330uF", 157.48, True), ("C125", "100nF", 167.64, False), ("C126", "470uF", 177.8, True)):
        (cpol if pol else cap_v)(ref, val, x, 85.09); G(x, 91.44); W((x, 88.9), (x, 91.44))
    j = add("Connector_Generic:Conn_01x03", "J121", "SERVO", 198.12, 81.28, 0, ref_at=(0, -5.08), val_at=(0, 5.08))
    W((193.04, 78.74), (190.5, 78.74)); G(190.5, 78.74, 180)
    # ---- signal
    add("TriggerFlow:SN74AHCT1G125", "U122", "SN74AHCT1G125", 127.0, 111.76, 0, ref_at=(7.62, -6.35), val_at=(7.62, 6.35), justify="left")
    W((119.38, 109.22), (99.06, 109.22)); lab("SERVO_PWM", 99.06, 109.22, 180)
    res_v("R124", "10k", 106.68, 113.03); G(106.68, 119.38); W((106.68, 116.84), (106.68, 119.38))
    W((119.38, 114.3), (114.3, 114.3), (114.3, 119.38)); G(114.3, 119.38)
    G(127.0, 119.38)
    PW("+5V", 127.0, 101.6); W((127.0, 104.14), (127.0, 101.6)); W((127.0, 101.6), (130.81, 101.6))
    chh = cap_h("C127", "100nF", 134.62, 101.6); W((138.43, 101.6), (140.97, 101.6)); G(140.97, 101.6, 90)
    res_h("R125", "220", 138.43, 111.76)
    W((142.24, 111.76), (190.5, 111.76), (190.5, 83.82), (193.04, 83.82)); lab("SERVO_SIG", 165.1, 111.76)
    add("Device:D_TVS", "D122", "PESD5V0S1BB", 182.88, 115.57, 90, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")
    G(182.88, 119.38)
    zone("Rail V_SERVO 6 V (LM2596S-ADJ depuis +12V)", 20.32, 58.42, 205.74, 97.79)
    zone("Signal servo", 91.44, 99.06, 205.74, 127.0)
    note("Notes :\n"
         "• V_SERVO = 1,23 V × (1 + R122 / R121) = 1,23 × (1 + 3,9k / 1k) ≈ 6,0 V ; 3 A max (limitation interne du LM2596).\n"
         "• SERVO_OFF (MCP23017 GPB3) : haut ou haute impédance (R123 vers +3V3) = rail coupé ; bas = servo alimenté.\n"
         "• SERVO_PWM (GPIO13, LEDC 50 Hz) ; R124 maintient l'entrée basse au démarrage ; U122 sort un signal 5 V, R125 220 Ω série.\n"
         "• J121 : 1 = GND, 2 = V_SERVO, 3 = signal (brochage servo standard). D122 : TVS sur le signal.\n"
         "• C124 : électrolytique low-ESR, pas de polymère (stabilité du LM2596). C126 470 µF au plus près de J121.\n"
         "• PCB : boucle C129/C122-U121-D121 courte, cuivre et vias sous la languette de U121.",
         20.32, 134.62, 1.27)
