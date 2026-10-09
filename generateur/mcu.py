"""Feuille MCU v2 : module ESP32-S3-WROOM-1-N16R8 (U105), 3V3_MCU dédié, USB-C natif protégé, RESET / BOOT, console UART0.
GPIO réaffectés pour le placement (voir docs/mcu-v2-wroom.md) ; nets repris de pcb/netlist_v2_wroom.json."""
import json, os
from kicadgen import *
SRC = "src_mcu.kicad_sch"; FILE = "mcu_wroom.kicad_sch"
NETLIST = os.environ.get("NETLIST_V2", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb", "netlist_v2_wroom.json"))
def A(x, y): return (R2(x + DX), R2(y + DY))
def W(*pts): wire_abs(*[p if isinstance(p, tuple) and getattr(p, "_abs", False) else A(*p) for p in pts])
def G(x, y, rot=0): return add("power:GND", pwr_ref(), "GND", x, y, rot, hide_ref=True, hide_val=(rot != 0), val_at=(0, 3.81))
def gnd_below(pt, d=2.54):
    """fil vertical depuis un point absolu puis symbole GND"""
    wire_abs(pt, (pt[0], R2(pt[1] + d))); add("power:GND", pwr_ref(), "GND", R2(pt[0] - DX), R2(pt[1] + d - DY), 0, hide_ref=True, val_at=(0, 3.81))
def stub(pt, dx, net, ang):
    e = (R2(pt[0] + dx), pt[1]); wire_abs(pt, e); labels.append((net, e, ang))

def layout():
    t = json.load(open(NETLIST))
    pin_net = {}
    for n, ps in t["nets"].items():
        for p in ps:
            r, k = p.split(".")
            if r == "U105": pin_net[k] = n

    # ---------------- module ----------------
    u = add("RF_Module:ESP32-S3-WROOM-1", "U105", "ESP32-S3-WROOM-1-N16R8", 152.4, 93.98, 0,
            ref_at=(5.08, 29.21), val_at=(5.08, 31.75), justify="left")
    for k in [str(i) for i in range(3, 40)]:
        pt = u.pin(k); left = pt[0] < u.x
        net = pin_net.get(k)
        if net is None: nocon.append(pt); continue
        stub(pt, -5.08 if left else 5.08, net, 180 if left else 0)
    # 3V3 (broche 2) + découplage au plus près
    p2 = u.pin("2"); top = (p2[0], R2(p2[1] - 7.62)); wire_abs(p2, top)
    wire_abs(top, (R2(top[0] + 20.32), top[1])); labels.append(("3V3_MCU", top, 0))
    for ref, val, dx in (("C143", "100nF", 7.62), ("C142", "10uF", 15.24)):
        c = cap_v(ref, val, R2(top[0] + dx - DX), R2(top[1] + 3.81 - DY)); gnd_below(c.pin("2"))
    gnd_below(u.pin("1"))

    # ---------------- 3V3_MCU : D101 / D141 -> U141 ----------------
    add("power:+5V", pwr_ref(), "+5V", 27.94, 40.64, 0, hide_ref=True, val_at=(0, -3.81))
    d1 = add("Device:D_Schottky", "D101", "SS14", 38.1, 40.64, 180, ref_at=(0, -2.54), val_at=(0, 2.54))
    d2 = add("Device:D_Schottky", "D141", "SS14", 38.1, 50.8, 180, ref_at=(0, -2.54), val_at=(0, 2.54))
    W((27.94, 40.64)); wire_abs(A(27.94, 40.64), d1.pin("2"))
    wire_abs(A(27.94, 50.8), d2.pin("2")); labels.append(("VBUS", A(27.94, 50.8), 180))
    wire_abs(d1.pin("1"), A(48.26, 40.64), A(48.26, 50.8)); wire_abs(d2.pin("1"), A(48.26, 50.8))
    reg = add("Regulator_Linear:AMS1117-3.3", "U141", "AMS1117-3.3", 73.66, 45.72, 0, ref_at=(0, -5.08), val_at=(0, -7.62))
    wire_abs(A(48.26, 45.72), reg.pin("3")); labels.append(("5V_MCU", A(50.8, 45.72), 0))
    c146 = cap_v("C146", "10uF", 60.96, 49.53); gnd_below(c146.pin("2"))
    gnd_below(reg.pin("1"))
    wire_abs(reg.pin("2"), A(111.76, 45.72)); labels.append(("3V3_MCU", A(104.14, 45.72), 0))
    for ref, x in (("C144", 88.9), ("C145", 96.52)):
        c = cap_v(ref, "10uF", x, 49.53); gnd_below(c.pin("2"))

    # ---------------- RESET (EN) ----------------
    wire_abs(A(55.88, 71.12), A(101.6, 71.12)); labels.append(("EN", A(55.88, 71.12), 180))
    r = res_v("R141", "10k", 78.74, 67.31); wire_abs(r.pin("1"), A(78.74, 60.96)); labels.append(("3V3_MCU", A(78.74, 60.96), 90))
    c = cap_v("C141", "1uF", 88.9, 74.93); gnd_below(c.pin("2"))
    sw = add("Switch:SW_Push", "SW141", "RESET", 101.6, 76.2, 90, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")
    gnd_below(sw.pin("1"))
    # ---------------- BOOT (IO0) ----------------
    wire_abs(A(55.88, 93.98), A(101.6, 93.98)); labels.append(("IO0_BOOT", A(55.88, 93.98), 180))
    r = res_v("R142", "10k", 78.74, 90.17); wire_abs(r.pin("1"), A(78.74, 83.82)); labels.append(("3V3_MCU", A(78.74, 83.82), 90))
    sw = add("Switch:SW_Push", "SW142", "BOOT", 101.6, 99.06, 90, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")
    gnd_below(sw.pin("1"))
    # ---------------- console UART0 ----------------
    for ref, net, y in (("TP141", "TXD0", 111.76), ("TP142", "RXD0", 121.92)):
        tp = add("Connector:TestPoint", ref, net, 40.64, y, 0, ref_at=(2.54, -3.81), val_at=(2.54, -1.27), justify="left")
        wire_abs(tp.pin("1"), A(40.64, y + 2.54), A(55.88, y + 2.54)); labels.append((net, A(55.88, y + 2.54), 0))

    # ---------------- tirages I2C (vers +3V3, alimentation des circuits du bus) ----------------
    for ref, net, x in (("R108", "I2C_SDA", 76.2), ("R109", "I2C_SCL", 91.44)):
        rr = add("Device:R", ref, "4.7k", x, 118.11, 180, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left")   # broche 2 en haut
        add("power:+3V3", pwr_ref(), "+3V3", x, 111.76, 0, hide_ref=True, val_at=(0, -3.81)); wire_abs(rr.pin("2"), A(x, 111.76))
        wire_abs(rr.pin("1"), A(x, 125.73)); labels.append((net, A(x, 125.73), 270))

    # ---------------- USB-C natif ----------------
    j = add("Connector:USB_C_Receptacle_USB2.0_16P", "J141", "TYPE-C-31-M-12", 220.98, 63.5, 0, ref_at=(0, -27.94), val_at=(0, -25.4))
    e = add("Power_Protection:USBLC6-2SC6", "U142", "USBLC6-2SC6", 261.62, 66.04, 0, ref_at=(0, -10.16), val_at=(0, 10.16))
    # VBUS
    vb = j.pin("A4"); wire_abs(vb, (e.pin("5")[0], vb[1]), e.pin("5")); labels.append(("VBUS", (R2(vb[0] + 5.08), vb[1]), 0))
    # CC1 / CC2 -> 5,1 k -> GND
    for pinn, ref, off, rat in (("A5", "R143", 7.62, (0, -2.54)), ("B5", "R144", 17.78, (0, 2.54))):
        p = j.pin(pinn); rr = add("Device:R", ref, "5.1k", R2(p[0] + off - DX), R2(p[1] - DY), 90, ref_at=rat, val_at=(0, 6.35) if ref == "R144" else (0, -5.08))
        wire_abs(p, rr.pin("1" if rr.pin("1")[0] < rr.pin("2")[0] else "2"))
        far = rr.pin("2") if rr.pin("2")[0] > rr.pin("1")[0] else rr.pin("1")
        wire_abs(far, (R2(far[0] + 2.54), far[1])); add("power:GND", pwr_ref(), "GND", R2(far[0] + 2.54 - DX), R2(far[1] - DY), 90, hide_ref=True, hide_val=True)
    # D- (A7, B7) et D+ (A6, B6) : paires reliées, puis vers U142
    dm1, dm2, dp1, dp2 = j.pin("A7"), j.pin("B7"), j.pin("A6"), j.pin("B6")
    wire_abs(dm1, dm2); wire_abs(dp1, dp2)
    io1, io2 = e.pin("1"), e.pin("3")
    xm = R2(dm2[0] + 10.16); xp = R2(dp2[0] + 15.24)
    wire_abs(dm2, (xm, dm2[1]), (xm, io1[1]), io1); labels.append(("USB_DN", (R2(dm2[0] + 2.54), dm2[1]), 0))
    wire_abs(dp2, (xp, dp2[1]), (xp, io2[1]), io2); labels.append(("USB_DP", (R2(dp2[0] + 2.54), dp2[1]), 0))
    stub(e.pin("6"), 5.08, "USB_DN", 0); stub(e.pin("4"), 5.08, "USB_DP", 0)
    gnd_below(e.pin("2")); gnd_below(j.pin("A1")); gnd_below(j.pin("S1"))
    nocon.extend([j.pin("A8"), j.pin("B8")])

    # ---------------- zones et notes ----------------
    zone("1 · Alimentation 3V3_MCU", 20.32, 30.48, 116.84, 60.96 - 2.54)
    zone("2 · RESET, BOOT, console, tirages I2C", 20.32, 60.96, 116.84, 130.81)
    zone("3 · Module ESP32-S3-WROOM-1-N16R8", 119.38, 30.48, 199.39, 130.81)
    zone("4 · USB-C natif (IO19 / IO20)", 201.93, 30.48, 284.48, 101.6)
    note("Notes :\n"
         "• GPIO réaffectés pour le placement (v2) : TLV_OUT_1..6 = IO4-7, IO15, IO16 ; SPI SCK / MOSI = IO17 / IO18 ; I2C SCL / SDA = IO11 / IO12 ;\n"
         "  DAC2_LDAC = IO10 ; SERVO_PWM = IO48 ; vannes 1..6 = IO2, IO1, IO47, IO21, IO14, IO13 ; SHUTTER = IO38 ; FLASH_1..4 = IO39..IO42.\n"
         "• Non connectées : IO3, IO45, IO46 (démarrage), IO35-37 (PSRAM octale), IO8 et IO9 (réserve).\n"
         "• 5V_MCU par D101 (depuis +5V) ou D141 (depuis VBUS) : programmation par l'USB sans le 12 V ; l'USB n'alimente que le module.\n"
         "• U141 AMS1117-3.3 dédié au module (pointe Wi-Fi ≈ 355 mA) ; C142 + C143 au plus près de la broche 2 du module.\n"
         "• EN : 10 k / 1 µF (Espressif) + RESET ; BOOT maintenu + RESET = mode téléchargement. Console UART0 sur TP141 / TP142.\n"
         "• R108 / R109 : tirages I2C 4,7 k vers +3V3 (inchangés depuis la v1, rail des circuits du bus).\n"
         "• USB-C : CC1 / CC2 5,1 k vers GND (périphérique) ; USBLC6-2SC6 contre les décharges ; D+ / D- courtes, même longueur, sans via.",
         20.32, 137.16, 1.27)
