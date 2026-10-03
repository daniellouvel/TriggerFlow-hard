import os, sys, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as K, bloc5 as m
OUT = sys.argv[1] if len(sys.argv) > 1 else "out_bloc5"
os.makedirs(OUT, exist_ok=True)
sheet = K.U("bloc5-sheet")
K.load_source(m.SRC)
K.configure(pfx="b5-", digit0=5, n_inst=1, sheet_uuids=[sheet], title="Bloc 5 — Alimentation",
            comment="12 V secteur -> +12V, +5V (LM2596S-5.0), +3V3 (AMS1117-3.3)", uuid_name="bloc5", pwr_start=500,
            easyeda=bool(os.environ.get("EASYEDA")))
LCSC = {"Q501": "C16072", "D501": "C83846", "U501": "C347421", "D502": "C22452", "U502": "C6186",
        "R501": "C25804", "R502": "C25804", "C502": "C14663", "C504": "C14663", "C505": "C15850", "C506": "C15850", "C507": "C15850", "C508": "C15850",
        "L501": "C2924828", "C501": "C970707", "F501": "C3014144", "J501": "C474952", "C503": "C178543"}
for r, c in LCSC.items():
    K.ORIG_PROPS[r] = {"LCSC": c}
m.layout()
s = K.build_child()
own = K.U("bloc5")
s = s.replace(f"/{K.ROOT_UUID}/{sheet}", f"/{own}")
s = s.replace("\t(embedded_fonts no)\n)", "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)")
open(f"{OUT}/{m.FILE}", "w", encoding="utf-8").write(s)
pro = '{\n  "meta": {"filename": "alimentation.kicad_pro", "version": 3},\n  "sheets": [["%s", "Root"]]\n}\n' % own
open(f"{OUT}/alimentation.kicad_pro", "w").write(pro)
print(len(K.syms), "symboles", len(K.wires), "fils", len(K.compute_junctions()), "jonctions")
