"""Construction générique d'une feuille autonome (A4/A3) avec symboles TriggerFlow personnalisés."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kicadgen as K
from libextract import full

def pin(num, name, x, y, ang, typ="passive", ln=2.54):
    return f'(pin {typ} line (at {x} {y} {ang}) (length {ln}) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))'

def box(name, ref, val, w, h, pins, desc, fp=""):
    o = f'(symbol "TriggerFlow:{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
    o += f' (property "Reference" "{ref}" (at 0 {h+1.27} 0) (effects (font (size 1.27 1.27))))\n'
    o += f' (property "Value" "{val}" (at 0 {-h-1.27} 0) (effects (font (size 1.27 1.27))))\n'
    o += f' (property "Footprint" "{fp}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    o += ' (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    o += f' (property "Description" "{desc}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
    o += f' (symbol "{name}_0_1" (rectangle (start {-w} {h}) (end {w} {-h}) (stroke (width 0.254) (type default)) (fill (type background))))\n'
    o += f' (symbol "{name}_1_1" ' + ' '.join(pins) + '))'
    return o

def write_src(path, libsyms, customs):
    o = '(kicad_sch\n\t(version 20260306)\n\t(lib_symbols\n'
    for lib, n in libsyms: o += '\t\t' + full(lib, n) + '\n'
    for c in customs: o += '\t\t' + c + '\n'
    open(path, 'w').write(o + '\t)\n)\n')

def build(m, out, name, title, comment, lcsc, customs=(), paper="A4", pwr_start=0):
    os.makedirs(out, exist_ok=True)
    sheet = K.U(name + "-sheet")
    K.load_source(m.SRC)
    K.configure(pfx=name + "-", n_inst=1, sheet_uuids=[sheet], title=title, comment=comment, uuid_name=name,
                pwr_start=pwr_start, keep_refs=True, paper=paper, easyeda=bool(os.environ.get("EASYEDA")))
    for r, c in lcsc.items(): K.ORIG_PROPS[r] = {"LCSC": c}
    m.layout()
    s = K.build_child(); own = K.U(name)
    s = s.replace(f"/{K.ROOT_UUID}/{sheet}", f"/{own}")
    s = s.replace("\t(embedded_fonts no)\n)", "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)")
    open(f"{out}/{m.FILE}", "w", encoding="utf-8").write(s)
    base = m.FILE.replace(".kicad_sch", "")
    open(f"{out}/{base}.kicad_pro", "w").write('{\n  "meta": {"filename": "%s.kicad_pro", "version": 3},\n  "sheets": [["%s", "Root"]]\n}\n' % (base, own))
    if customs:
        lib = "(kicad_symbol_lib\n\t(version 20260306)\n\t(generator \"kicad_symbol_editor\")\n\t(generator_version \"10.0\")\n"
        for c in customs:
            lib += "\t" + K.LIB_BLOCKS[f"TriggerFlow:{c}"].replace(f'(symbol "TriggerFlow:{c}"', f'(symbol "{c}"', 1) + "\n"
        open(f"{out}/TriggerFlow.kicad_sym", "w").write(lib + ")\n")
        open(f"{out}/sym-lib-table", "w").write('(sym_lib_table\n\t(version 7)\n\t(lib (name "TriggerFlow")(type "KiCad")(uri "${KIPRJMOD}/TriggerFlow.kicad_sym")(options "")(descr "Symboles TriggerFlow"))\n)\n')
    print(m.FILE, len(K.syms), "symboles", len(K.wires), "fils", len(K.compute_junctions()), "jonctions")
