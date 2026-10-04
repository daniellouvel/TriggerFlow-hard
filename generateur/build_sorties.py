import os, sys
from mkbuild import build
import servo, relais
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_sorties"
build(servo, f"{OUT}/servo", "servo", "Sortie servo — rail 6 V dédié", "LM2596S-ADJ 6 V / 3 A coupable + buffer 74AHCT1G125",
      {"U121": "C347423", "L121": "C2924828", "D121": "C22452", "C124": "C178543", "C126": "C970707", "C129": "C15850", "C122": "C15850",
       "C123": "C14663", "C125": "C14663", "C127": "C14663", "R121": "C21190", "R123": "C25804", "R124": "C25804", "R125": "C22962",
       "U122": "C7484", "D122": "C97640"}, customs=["SN74AHCT1G125"], pwr_start=1200)
build(relais, f"{OUT}/relais", "relais", "Sortie relais — contact sec", "HF32F/012-ZS3 commandé par MCP23017 GPB2",
      {"K131": "C3633", "Q131": "C20917", "D131": "C2480", "R131": "C22962", "R132": "C25803"}, customs=["HF32F-012-ZS3"], pwr_start=1300)
