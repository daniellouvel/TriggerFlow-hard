import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as K, bloc5b as m
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_bloc5b"
os.makedirs(OUT, exist_ok=True)
sheet = K.U("bloc5b-sheet")
K.load_source(m.SRC)
K.configure(pfx="b5b-", n_inst=1, sheet_uuids=[sheet], title="Bloc 5b — Alimentation isolée", keep_refs=True,
            comment="+5V -> B0505S-1WR3 (isolé) -> AMS1117-3.3 -> VISO_3V3 / VISO_GND", uuid_name="bloc5b", pwr_start=520,
            easyeda=bool(os.environ.get("EASYEDA")))
for r, c in {"U121": "C7465178", "U122": "C6186", "C121": "C15850", "C122": "C15850", "C123": "C15850", "R121": "C22962", "R122": "C22962"}.items():
    K.ORIG_PROPS[r] = {"LCSC": c}
m.layout()
s = K.build_child(); own = K.U("bloc5b")
s = s.replace(f"/{K.ROOT_UUID}/{sheet}", f"/{own}")
s = s.replace("\t(embedded_fonts no)\n)", "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)")
open(f"{OUT}/{m.FILE}", "w", encoding="utf-8").write(s)
open(f"{OUT}/alim_isolee.kicad_pro", "w").write('{\n  "meta": {"filename": "alim_isolee.kicad_pro", "version": 3},\n  "sheets": [["%s", "Root"]]\n}\n' % own)
open(f"{OUT}/TriggerFlow.kicad_sym", "w").write("(kicad_symbol_lib\n\t(version 20260306)\n\t(generator \"kicad_symbol_editor\")\n\t(generator_version \"10.0\")\n\t"
    + K.LIB_BLOCKS["TriggerFlow:B0505S-1WR3"].replace('(symbol "TriggerFlow:B0505S-1WR3"', '(symbol "B0505S-1WR3"', 1) + "\n)\n")
open(f"{OUT}/sym-lib-table", "w").write('(sym_lib_table\n\t(version 7)\n\t(lib (name "TriggerFlow")(type "KiCad")(uri "${KIPRJMOD}/TriggerFlow.kicad_sym")(options "")(descr "Symboles TriggerFlow"))\n)\n')
print(len(K.syms), "symboles", len(K.wires), "fils", len(K.compute_junctions()), "jonctions")
