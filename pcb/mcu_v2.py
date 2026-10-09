#!/usr/bin/env python3
"""TriggerFlow v2 : remplace la DevKit (U105, 44 broches sur barrettes) par le module ESP32-S3-WROOM-1-N16R8.
Part de la netlist de référence v1 (netlist_2026-10-05.json) et écrit netlist_v2_wroom.json.
Même GPIO pour chaque signal : le firmware ne change pas. Seuls les numéros de broches de U105 changent."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
t = json.load(open(os.path.join(HERE, "netlist_2026-10-05.json")))

# broche DevKit (symbole ESP32-S3-DEVKITC-1) -> GPIO, puis GPIO -> broche du module WROOM-1
DEVKIT_GPIO = {4: 4, 5: 5, 6: 6, 7: 7, 8: 15, 9: 16, 10: 17, 11: 18, 12: 8, 13: 3, 14: 46, 15: 9, 16: 10, 17: 11, 18: 12,
               19: 13, 20: 14, 41: 1, 40: 2, 39: 42, 38: 41, 37: 40, 36: 39, 35: 38, 34: 37, 33: 36, 32: 35, 31: 0,
               30: 45, 29: 48, 28: 47, 27: 21, 26: 20, 25: 19}
WROOM_PIN = {4: 4, 5: 5, 6: 6, 7: 7, 15: 8, 16: 9, 17: 10, 18: 11, 8: 12, 19: 13, 20: 14, 3: 15, 46: 16, 9: 17, 10: 18,
             11: 19, 12: 20, 13: 21, 14: 22, 21: 23, 47: 24, 48: 25, 45: 26, 0: 27, 35: 28, 36: 29, 37: 30, 38: 31,
             39: 32, 40: 33, 41: 34, 42: 35, 2: 38, 1: 39}          # + 1 GND, 2 3V3, 3 EN, 36 RXD0, 37 TXD0, 40/41 GND

# v2 : GPIO réaffectés pour le placement (chaque signal sort du côté du module qui fait face à sa destination)
#  bas (vers les entrées)  : TLV_OUT_1..6 = IO4, 5, 6, 7, 15, 16 ; SPI_SCK = IO17 ; SPI_MOSI = IO18 ; IO8 libre
#  droite (bus I2C, servo, vannes) : SERVO_PWM = IO48 ; GPIO_VALVE_3..6 = IO47, 21, 14, 13 ; I2C_SDA = IO12 ;
#                                    I2C_SCL = IO11 ; DAC2_LDAC = IO10 ; IO9 libre
#  haut (vers les optos)   : SHUTTER = IO38 ; FLASH_1..4 = IO39, 40, 41, 42 ; GPIO_VALVE_1 = IO2 ; GPIO_VALVE_2 = IO1
GPIO_V2 = {"TLV_OUT_1": 4, "TLV_OUT_2": 5, "TLV_OUT_3": 6, "TLV_OUT_4": 7, "TLV_OUT_5": 15, "TLV_OUT_6": 16,
           "SPI_SCK": 17, "SPI_MOSI": 18, "SERVO_PWM": 48, "GPIO_VALVE_3": 47, "GPIO_VALVE_4": 21,
           "GPIO_VALVE_5": 14, "GPIO_VALVE_6": 13, "I2C_SDA": 12, "I2C_SCL": 11, "DAC2_LDAC": 10,
           "SHUTTER_CMD": 38, "FLASH_1_CMD": 39, "FLASH_2_CMD": 40, "FLASH_3_CMD": 41, "FLASH_4_CMD": 42,
           "GPIO_VALVE_1": 2, "GPIO_VALVE_2": 1}
RENAME = {"GPIO18": "DAC2_LDAC"}
nets = {}
for n, pins in t["nets"].items():
    n2 = RENAME.get(n, n)
    out = [p for p in pins if not p.startswith("U105.")]
    if n2 in GPIO_V2: out.append(f"U105.{WROOM_PIN[GPIO_V2[n2]]}")
    nets[n2] = out
nets["5V_MCU"] = [p for p in nets.pop("V5_DEVKIT") if p != "U105.21"]   # D101.1 (cathode)

comps = dict(t["comps"])
comps["U105"] = ["WIRELM-SMD_ESP32-S3-WROOM-1", "ESP32-S3-WROOM-1-N16R8"]
NEW = {  # réf : (empreinte, valeur, LCSC)
 "U141": ("SOT-223-3_L6.5-W3.4-P2.30-LS7.0-BR", "AMS1117-3.3", "C6186"),
 "U142": ("SOT-23-6", "USBLC6-2SC6", "C7519"),
 "J141": ("USB-C_SMD-TYPE-C-31-M-12", "TYPE-C-31-M-12", "C165948"),
 "SW141": ("SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL-2", "TS-1187A-B-A-B (RESET)", "C318884"),
 "SW142": ("SW-SMD_4P-L5.1-W5.1-P3.70-LS6.5-TL-2", "TS-1187A-B-A-B (BOOT)", "C318884"),
 "D141": ("SMA_L4.2-W2.6-LS5.0-RD_1", "SS14", "C2480"),
 "R141": ("R0603", "10kΩ", "C25804"), "R142": ("R0603", "10kΩ", "C25804"),
 "R143": ("R0603", "5.1kΩ", "C23186"), "R144": ("R0603", "5.1kΩ", "C23186"),
 "C141": ("C0603", "1uF", "C5673"), "C143": ("C0603", "100nF", "C14663"),
 "C142": ("C0805", "10uF", "C15850"), "C144": ("C0805", "10uF", "C15850"),
 "C145": ("C0805", "10uF", "C15850"), "C146": ("C0805", "10uF", "C15850"),
 "TP141": ("TP-1.5", "TXD0 (console UART0)", "—"), "TP142": ("TP-1.5", "RXD0 (console UART0)", "—"),
}
for r, (fp, v, lcsc) in NEW.items(): comps[r] = [fp, v]

add = {
 "5V_MCU": ["D141.1", "U141.3", "C146.1"],
 "VBUS": ["J141.A4", "J141.A9", "J141.B4", "J141.B9", "D141.2", "U142.5"],
 "3V3_MCU": ["U141.2", "U141.4", "U105.2", "C142.1", "C143.1", "C144.1", "C145.1", "R141.1", "R142.1"],
 "EN": ["U105.3", "R141.2", "C141.1", "SW141.1", "SW141.2"],
 "IO0_BOOT": ["U105.27", "R142.2", "SW142.1", "SW142.2"],
 "USB_DN": ["J141.A7", "J141.B7", "U142.1", "U142.6", "U105.13"],
 "USB_DP": ["J141.A6", "J141.B6", "U142.3", "U142.4", "U105.14"],
 "CC1": ["J141.A5", "R143.1"], "CC2": ["J141.B5", "R144.1"],
 "TXD0": ["U105.37", "TP141.1"], "RXD0": ["U105.36", "TP142.1"],
 "GND": ["U105.1", "U105.40", "U105.41", "U141.1", "U142.2", "J141.A1", "J141.A12", "J141.B1", "J141.B12",
         "J141.SH", "R143.2", "R144.2", "C141.2", "C142.2", "C143.2", "C144.2", "C145.2", "C146.2", "SW141.3", "SW141.4",
         "SW142.3", "SW142.4"],
}
for n, p in add.items(): nets[n] = nets.get(n, []) + p
json.dump({"comps": comps, "nets": nets, "lcsc_new": {r: v[2] for r, v in NEW.items()}},
          open(os.path.join(HERE, "netlist_v2_wroom.json"), "w"), ensure_ascii=False, indent=1)
u = sorted({int(p.split(".")[1]) for ps in nets.values() for p in ps if p.startswith("U105.")})
print("U105 broches utilisées :", u)
print("composants :", len(comps), "| nets :", len(nets))
