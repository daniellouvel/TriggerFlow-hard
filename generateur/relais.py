"""Sortie relais : HF32F/012-ZS3 (bobine 12 V) commandé par le MCP23017 (GPB2) via AO3400A."""
from kicadgen import *
SRC = "src_relais.kicad_sch"; FILE = "sortie_relais.kicad_sch"
def A(x, y): return (R2(x + DX), R2(y + DY))
def W(*pts): wire_abs(*[A(*p) for p in pts])
def G(x, y): return add("power:GND", pwr_ref(), "GND", x, y, 0, hide_ref=True, val_at=(0, 3.81))

def layout():
    k = add("TriggerFlow:HF32F-012-ZS3", "K131", "HF32F/012-ZS3", 139.7, 76.2, 0, ref_at=(0, -10.16), val_at=(0, -7.62))
    W((114.3, 73.66), (130.81, 73.66))
    add("power:+12V", pwr_ref(), "+12V", 121.92, 73.66, 0, hide_ref=True, val_at=(0, -3.81))
    add("Device:D_Schottky", "D131", "SS14", 114.3, 76.2, 270, ref_at=(-2.54, -1.27), val_at=(-2.54, 1.27), justify="right")
    W((114.3, 72.39), (114.3, 73.66))
    W((114.3, 80.01), (114.3, 81.28), (124.46, 81.28))
    W((130.81, 78.74), (124.46, 78.74), (124.46, 88.9)); lab("RELAY_DRV", 124.46, 85.09)
    add("Transistor_FET:AO3400A", "Q131", "AO3400A", 121.92, 93.98, 0, ref_at=(5.08, -1.27), val_at=(5.08, 1.27), justify="left")
    G(124.46, 101.6); W((124.46, 99.06), (124.46, 101.6))
    res_h("R131", "220", 109.22, 93.98); W((113.03, 93.98), (116.84, 93.98))
    W((105.41, 93.98), (100.33, 93.98)); lab("RELAY_CMD", 100.33, 93.98, 180)
    res_v("R132", "100k", 114.3, 97.79); G(114.3, 104.14); W((114.3, 101.6), (114.3, 104.14))
    add("Connector_Generic:Conn_01x03", "J131", "RELAIS", 175.26, 76.2, 0, ref_at=(0, -5.08), val_at=(0, 5.08))
    for y, net in ((73.66, "RELAY_COM"), (76.2, "RELAY_NO"), (78.74, "RELAY_NC")):
        W((148.59, y), (170.18, y))
    lab("RELAY_COM", 150.5, 73.66); lab("RELAY_NO", 150.5, 76.2); lab("RELAY_NC", 150.5, 78.74)
    zone("Sortie relais (contact sec)", 88.9, 58.42, 190.5, 109.22)
    note("Notes :\n"
         "• RELAY_CMD = MCP23017 GPB2 ; R132 maintient le relais ouvert au démarrage. D131 : roue libre de la bobine.\n"
         "• J131 : 1 = COM, 2 = NO (travail), 3 = NC (repos). Contact 3 A / 30 V DC — basse tension uniquement, jamais de 230 V.\n"
         "• Numéros de broches de K131 : à câbler d'après les NOMS du symbole EasyEDA de la C3633 (bobine, COM, NO, NC).",
         88.9, 116.84, 1.27)
