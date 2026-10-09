import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkbuild import build, write_src
import mcu
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_mcu"
if not os.path.exists(mcu.SRC):
    write_src(mcu.SRC, [("Device", "R"), ("Device", "C"), ("Device", "D_Schottky"), ("power", "+5V"), ("power", "GND"),
                        ("RF_Module", "ESP32-S3-WROOM-1"), ("Regulator_Linear", "AMS1117-3.3"), ("Power_Protection", "USBLC6-2SC6"),
                        ("Connector", "USB_C_Receptacle_USB2.0_16P"), ("Switch", "SW_Push"), ("Connector", "TestPoint")], [])
build(mcu, OUT, "mcu_v2", "MCU v2 — ESP32-S3-WROOM-1-N16R8", "Module soudé, 3V3_MCU dédié, USB-C natif, RESET / BOOT",
      {"U105": "C2913202", "U141": "C6186", "U142": "C7519", "J141": "C165948", "SW141": "C318884", "SW142": "C318884",
       "D101": "C2480", "D141": "C2480", "R141": "C25804", "R142": "C25804", "R143": "C23186", "R144": "C23186",
       "C141": "C5673", "C143": "C14663", "C142": "C15850", "C144": "C15850", "C145": "C15850", "C146": "C15850"},
      paper="A4", pwr_start=1400)
print("ok", OUT)
