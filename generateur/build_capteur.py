import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as K, capteur as m
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_capteur"
os.makedirs(OUT, exist_ok=True)
sheet = K.U("capteur-sheet")
K.load_source(m.SRC)
K.configure(pfx="cap-", n_inst=1, sheet_uuids=[sheet], title="Module capteur universel",
            comment="Un PCB, 8 variantes : contact, laser, barrière IR, lumière, son, piézo, PIR, émetteur IR",
            uuid_name="capteur", pwr_start=0, keep_refs=True, paper="A3", easyeda=bool(os.environ.get("EASYEDA")))
LCSC = {"U1": "C398355", "D1": "C85128", "M1": "C529943", "D4": "C5130", "D2": "C545549", "D3": "C545549", "J1": "C25168869",
        "C1": "C15850", "C2": "C14663", "C4": "C14663", "C5": "C14663", "C10": "C14663", "C11": "C14663",
        "C3": "C5673", "C7": "C5673", "C8": "C5673", "C9": "C5673",
        "R3": "C25804", "R4": "C25804", "R5": "C25804", "R11": "C25804", "R13": "C25804", "R12": "C25803", "R9": "C22935",
        "R10": "C4190", "R15": "C4190", "R14": "C21190", "R6": "C22962",
        "JP1": "C21189", "JP2": "C21189", "JP3": "C21189", "JP4": "C21189", "JP5": "C21189", "R16": "C21189"}
for r, c in LCSC.items(): K.ORIG_PROPS[r] = {"LCSC": c}
m.layout()
s = K.build_child()
own = K.U("capteur")
s = s.replace(f"/{K.ROOT_UUID}/{sheet}", f"/{own}")
s = s.replace("\t(embedded_fonts no)\n)", "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)")
open(f"{OUT}/{m.FILE}", "w", encoding="utf-8").write(s)
open(f"{OUT}/module_capteur.kicad_pro", "w").write('{\n  "meta": {"filename": "module_capteur.kicad_pro", "version": 3},\n  "sheets": [["%s", "Root"]]\n}\n' % own)
open(f"{OUT}/TriggerFlow.kicad_sym", "w").write("(kicad_symbol_lib\n\t(version 20260306)\n\t(generator \"kicad_symbol_editor\")\n\t(generator_version \"10.0\")\n\t"
    + K.LIB_BLOCKS["TriggerFlow:TLV9062"].replace('(symbol "TriggerFlow:TLV9062"', '(symbol "TLV9062"', 1) + "\n\t"
    + K.LIB_BLOCKS["TriggerFlow:RJ45_10P"].replace('(symbol "TriggerFlow:RJ45_10P"', '(symbol "RJ45_10P"', 1) + "\n)\n")
open(f"{OUT}/sym-lib-table", "w").write('(sym_lib_table\n\t(version 7)\n\t(lib (name "TriggerFlow")(type "KiCad")(uri "${KIPRJMOD}/TriggerFlow.kicad_sym")(options "")(descr "Symboles TriggerFlow"))\n)\n')
print(len(K.syms), "symboles", len(K.wires), "fils", len(K.compute_junctions()), "jonctions")
