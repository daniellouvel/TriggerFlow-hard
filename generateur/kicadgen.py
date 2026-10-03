#!/usr/bin/env python3
"""Moteur de génération de feuilles KiCad (.kicad_sch v20260306) pour le projet TriggerFlow.

Usage : voir build_project.py. Un bloc = une fonction layout() qui appelle add/wire_abs/pwr/hl/lab/note/zone.
- Symboles : copiés du lib_symbols d'un fichier eeschema source (load_source).
- Fils : toujours tirés des positions de broches (Sym.pin).  sch_y = placed_y - sym_y.
- Jonctions : calculées automatiquement.
"""
import re, os, sys, uuid, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sexpdata
from kicad_net import parse, find, first, S, pin_pos

NS = uuid.UUID("7c1f2f0e-6f6e-4b53-9a0e-0d1c7a5f1000")
def U(name): return str(uuid.uuid5(NS, name))

DX, DY = 10.16, 0.0
ROOT_UUID = U("root")

f2 = lambda v: f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) > 1e-9 else "0"
def R2(v): return round(v + 0.0, 2)
def q(s): return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

# ------------------------------------------------------------------ état d'un bloc
LIB_BLOCKS, LIB_PINS, ORIG_PROPS = {}, {}, {}
CFG = {}
syms, wires, labels, hlabels, nocon, texts, rects = [], [], [], [], [], [], []
_pwr = [100]


def extract_blocks(text):
    """Blocs de symboles de lib_symbols (texte brut), en tenant compte des guillemets."""
    i = text.index("(lib_symbols")
    depth, j, blocks, in_str, start = 0, i, {}, False, None
    while j < len(text):
        c = text[j]
        if in_str:
            if c == "\\": j += 2; continue
            if c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif c == "(":
                depth += 1
                if depth == 2 and text.startswith('(symbol "', j):
                    start = j
            elif c == ")":
                if depth == 2 and start is not None:
                    blk = text[start:j + 1]
                    blocks[re.match(r'\(symbol "([^"]+)"', blk).group(1)] = blk
                    start = None
                depth -= 1
                if depth == 0: break
        j += 1
    return blocks


def load_source(path):
    """Charge symboles et propriétés d'un fichier eeschema existant."""
    text = open(path, encoding="utf-8").read()
    LIB_BLOCKS.clear(); LIB_PINS.clear(); ORIG_PROPS.clear()
    LIB_BLOCKS.update(extract_blocks(text))
    for name, blk in LIB_BLOCKS.items():
        node = sexpdata.loads(blk)
        LIB_PINS[name] = [(str(first(p, "number")[1]), float(first(p, "at")[1]), float(first(p, "at")[2]))
                          for sub in find(node, "symbol") for p in find(sub, "pin")]
    root = parse(path)
    for s in find(root, "symbol"):
        if not first(s, "lib_id"): continue
        props = collections.OrderedDict((p[1], p[2]) for p in find(s, "property"))
        ORIG_PROPS[props["Reference"]] = props


def configure(**kw):
    """pfx, digit0, n_inst, sheet_uuids, title, comment, uuid_name, pwr_start, date, rev"""
    CFG.clear(); CFG.update(kw)
    for l in (syms, wires, labels, hlabels, nocon, texts, rects): l.clear()
    _pwr[0] = kw.get("pwr_start", 100)


class Sym:
    def __init__(s, lib, ref, value, x, y, rot, ref_at=None, val_at=None, hide_val=False, hide_ref=False, justify=None, orig=None, mirror=None):
        s.mirror = mirror
        s.lib, s.ref, s.value, s.x, s.y, s.rot = lib, ref, value, R2(x + DX), R2(y + DY), rot
        s.ref_at, s.val_at, s.hide_val, s.hide_ref, s.justify, s.orig = ref_at, val_at, hide_val, hide_ref, justify, orig or ref
    def pin(s, num):
        for n, px, py in LIB_PINS[s.lib]:
            if n == str(num):
                return pin_pos(px, py, (s.x, s.y, s.rot), s.mirror)
        raise KeyError((s.ref, num))

def P(x, y): return (R2(x + DX), R2(y + DY))
def add(lib, ref, value, x, y, rot=0, **kw):
    s = Sym(lib, ref, value, x, y, rot, **kw); syms.append(s); return s
def wire(*pts):
    pts = [P(*p) for p in pts]
    for a, b in zip(pts, pts[1:]):
        if a != b: wires.append((a, b))
def wire_abs(*pts):
    pts = [(R2(p[0]), R2(p[1])) for p in pts]
    for a, b in zip(pts, pts[1:]):
        if a != b: wires.append((a, b))

# ------------------------------------------------------------------ composants usuels
R_FP = "Device:R"; C_FP = "Device:C"; JP = "Jumper:SolderJumper_2_Open"
PWR3 = "power:+3V3"; GND = "power:GND"

def pwr_ref():
    _pwr[0] += 1
    return f"#PWR{_pwr[0]}"
def pwr(kind, x, y, rot=0):
    """kind : '3V3', 'GND' ou nom d'un symbole power: (ex. 'VISO_3V3')."""
    lib = {"3V3": PWR3, "GND": GND}.get(kind, f"power:{kind}")
    up = lib in (PWR3,) or kind.endswith("3V3")
    value = {"3V3": "+3V3"}.get(kind, kind)
    return add(lib, pwr_ref(), value, x, y, rot, hide_ref=True, val_at=(0, -3.81) if up else (0, 3.81))

def res_v(ref, val, x, y, **kw):
    return add(R_FP, ref, val, x, y, 0, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left", **kw)
def res_h(ref, val, x, y, **kw):
    return add(R_FP, ref, val, x, y, 90, ref_at=(0, -2.54), val_at=(0, 2.54), **kw)
def cap_v(ref, val, x, y, **kw):
    return add(C_FP, ref, val, x, y, 0, ref_at=(2.54, -1.27), val_at=(2.54, 1.27), justify="left", **kw)
def cap_h(ref, val, x, y, **kw):
    return add(C_FP, ref, val, x, y, 90, ref_at=(0, -3.81), val_at=(0, 3.81), **kw)
def jp_v(ref, x, y, **kw):
    return add(JP, ref, "SolderJumper_2_Open", x, y, 90, ref_at=(2.54, 0), hide_val=True, justify="left", **kw)
def jp_h(ref, x, y, **kw):
    return add(JP, ref, "SolderJumper_2_Open", x, y, 0, ref_at=(0, -2.54), hide_val=True, **kw)

def hl(name, x, y, angle, shape): hlabels.append((name, P(x, y), angle, shape))
def lab(name, x, y, angle=0): labels.append((name, P(x, y), angle))
def note(text, x, y, size=1.27, bold=False): texts.append((text, P(x, y), size, bold))
def zone(title, x1, y1, x2, y2):
    rects.append((P(x1, y1), P(x2, y2)))
    note(title, x1 + 2.54, y1 + 2.54, 2.0, True)

# ------------------------------------------------------------------ jonctions
def compute_junctions():
    pins = collections.Counter()
    for s in syms:
        for p in {pin_pos(px, py, (s.x, s.y, s.rot), getattr(s, 'mirror', None)) for n, px, py in LIB_PINS[s.lib]}:
            pins[p] += 1
    ends = collections.Counter()
    for a, b in wires:
        ends[a] += 1; ends[b] += 1
    j = []
    for p in set(pins) | set(ends):
        n = pins[p] + ends[p]
        for a, b in wires:
            if p in (a, b): continue
            (x, y), (x1, y1), (x2, y2) = p, a, b
            if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) < 0.01 and min(x1, x2) - .01 <= x <= max(x1, x2) + .01 and min(y1, y2) - .01 <= y <= max(y1, y2) + .01:
                n += 2
        if n >= 3: j.append(p)
    return sorted(j)

# ------------------------------------------------------------------ sérialisation d'une feuille
def inst_ref(ref, k):
    if CFG.get("keep_refs"): return ref
    m = re.match(r"^([A-Za-z#]+)(\d)(\d+)$", ref)
    return f"{m.group(1)}{CFG.get('digit0', 1) + k - 1}{m.group(3)}"

def fx(size=1.27, justify=None, hide=False, bold=False):
    out = ""
    if hide: out += "\t\t\t(hide yes)\n"
    out += "\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size %s %s)\n" % (size, size)
    if bold: out += "\t\t\t\t\t(bold yes)\n"
    out += "\t\t\t\t)\n"
    if justify: out += "\t\t\t\t(justify %s)\n" % justify
    out += "\t\t\t)\n"
    return out

def prop(name, val, x, y, a, hide=False, justify=None):
    return "\t\t(property %s %s\n\t\t\t(at %s %s %s)\n%s\t\t)\n" % (q(name), q(val), f2(x), f2(y), f2(a), fx(1.27, justify, hide))

def strip_props(block, keep=("Reference", "Value")):
    """Variante EasyEDA : retire les champs (property ...) sauf Reference/Value (EasyEDA ignore l'attribut « hide »)."""
    out, i = "", 0
    while True:
        j = block.find("(property ", i)
        if j < 0: out += block[i:]; break
        m = re.match(r'\(property "([^"]*)"', block[j:])
        d, k = 0, j
        while True:
            if block[k] == "(": d += 1
            elif block[k] == ")":
                d -= 1
                if d == 0: break
            k += 1
        if m.group(1) in keep: out += block[i:k + 1]
        else:
            out += block[i:j].rstrip("\t ")
            if out.endswith("\n") and k + 1 < len(block) and block[k + 1] == "\n": k += 1
        i = k + 1
    return out

def sym_block(s, idx):
    pfx = CFG.get("pfx", "")
    o = ORIG_PROPS.get(s.orig, {})
    out = "\t(symbol\n\t\t(lib_id %s)\n\t\t(at %s %s %s)\n%s\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(uuid %s)\n" % (
        q(s.lib), f2(s.x), f2(s.y), f2(s.rot), ("\t\t(mirror %s)\n" % s.mirror) if getattr(s,'mirror',None) else "", q(U(f"{pfx}sym{idx}")))
    ta = 0 if s.rot in (0, 180) else 90
    ra = s.ref_at or (0, 0); va = s.val_at or (0, 0)
    # KiCad retourne le texte (et inverse l'alignement) quand le symbole est tourné de 90°
    flip = {"left": "right", "right": "left"}
    jj = flip.get(s.justify, s.justify) if s.rot == 90 else s.justify
    out += prop("Reference", s.ref, s.x + ra[0], s.y + ra[1], ta, s.hide_ref, jj)
    out += prop("Value", s.value, s.x + va[0], s.y + va[1], ta, s.hide_val, jj)
    for k in (() if CFG.get("easyeda") else ("Footprint", "Datasheet", "Description")):
        v = o.get(k)
        if v is None:
            m = re.search(r'\(property "%s" "([^"]*)"' % k, LIB_BLOCKS[s.lib])
            v = m.group(1) if m else ""
        out += prop(k, v, s.x, s.y, 0, True)
    for k, v in ({} if CFG.get("easyeda") else o).items():
        if k not in ("Reference", "Value", "Footprint", "Datasheet", "Description"):
            out += prop(k, v, s.x, s.y, 0, True)
    for n, _, _ in LIB_PINS[s.lib]:
        out += "\t\t(pin %s\n\t\t\t(uuid %s)\n\t\t)\n" % (q(n), q(U(f"{pfx}pin{idx}-{n}")))
    out += "\t\t(instances\n\t\t\t(project \"TriggerFlow\"\n"
    for k in range(1, CFG["n_inst"] + 1):
        out += "\t\t\t\t(path %s\n\t\t\t\t\t(reference %s)\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n" % (
            q(f"/{ROOT_UUID}/{CFG['sheet_uuids'][k-1]}"), q(inst_ref(s.ref, k)))
    out += "\t\t\t)\n\t\t)\n\t)\n"
    return out

def build_child():
    pfx = CFG.get("pfx", "")
    o = "(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n\t(generator_version \"10.0\")\n"
    o += "\t(uuid %s)\n\t(paper %s)\n\t(title_block\n\t\t(title %s)\n\t\t(date %s)\n\t\t(rev %s)\n\t\t(company \"TriggerFlow\")\n\t\t(comment 1 %s)\n\t)\n" % (
        q(U(CFG["uuid_name"])), q(CFG.get("paper","A4")), q(CFG["title"]), q(CFG.get("date", "2026-09-30")), q(CFG.get("rev", "A")), q(CFG["comment"]))
    o += "\t(lib_symbols\n"
    used = []
    for s in syms:
        if s.lib not in used: used.append(s.lib)
    for name in used: o += "\t\t" + (strip_props(LIB_BLOCKS[name]) if CFG.get("easyeda") else LIB_BLOCKS[name]) + "\n"
    o += "\t)\n"
    for i, s in enumerate(syms): o += sym_block(s, i)
    for i, (a, b) in enumerate(wires):
        o += "\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            f2(a[0]), f2(a[1]), f2(b[0]), f2(b[1]), q(U(f"{pfx}wire{i}")))
    for i, p in enumerate(compute_junctions()):
        o += "\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid %s)\n\t)\n" % (f2(p[0]), f2(p[1]), q(U(f"{pfx}junc{i}")))
    for i, p in enumerate(nocon):
        o += "\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid %s)\n\t)\n" % (f2(p[0]), f2(p[1]), q(U(f"{pfx}nc{i}")))
    for i, (name, p, a) in enumerate(labels):
        o += "\t(label %s\n\t\t(at %s %s %s)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s bottom)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            q(name), f2(p[0]), f2(p[1]), f2(a), "right" if a == 180 else "left", q(U(f"{pfx}label{i}")))
    for i, (name, p, a, shape) in enumerate(hlabels):
        just = "right" if a == 180 else "left"
        o += "\t(hierarchical_label %s\n\t\t(shape %s)\n\t\t(at %s %s %s)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            q(name), shape, f2(p[0]), f2(p[1]), f2(a), just, q(U(f"{pfx}hlabel{i}")))
    for i, (p1, p2) in enumerate(rects):
        o += "\t(rectangle\n\t\t(start %s %s)\n\t\t(end %s %s)\n\t\t(stroke\n\t\t\t(width 0.254)\n\t\t\t(type dash)\n\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            f2(p1[0]), f2(p1[1]), f2(p2[0]), f2(p2[1]), q(U(f"{pfx}rect{i}")))
    for i, (t, p, size, bold) in enumerate(texts):
        o += "\t(text %s\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n%s\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            q(t), f2(p[0]), f2(p[1]), size, size, "\t\t\t\t(bold yes)\n" if bold else "", q(U(f"{pfx}text{i}")))
    o += "\t(embedded_fonts no)\n)\n"
    return o

# ------------------------------------------------------------------ racine
def build_root(blocks):
    """blocks : liste de dict(file, name, pfx, n_inst, sheet_uuids, ins, outs, row_y, shared)"""
    o = "(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n\t(generator_version \"10.0\")\n"
    o += "\t(uuid %s)\n\t(paper \"A3\")\n\t(title_block\n\t\t(title \"TriggerFlow\")\n\t\t(date \"2026-09-30\")\n\t\t(rev \"A\")\n\t\t(company \"TriggerFlow\")\n\t\t(comment 1 \"Racine : entrées capteur et sorties flash/caméra\")\n\t)\n\t(lib_symbols)\n" % q(ROOT_UUID)
    sheet_w = 50.8
    wires_r, labels_r, page, n = [], [], 1, 0
    for b in blocks:
        ins, outs = b["ins"], b["outs"]
        sheet_h = 12.7 + 5.08 * (max(len(ins), len(outs)) - 1) + 7.62
        for k in range(1, b["n_inst"] + 1):
            page += 1
            sx, sy = 50.8 + (k - 1) * 114.3, b["row_y"]
            o += "\t(sheet\n\t\t(at %s %s)\n\t\t(size %s %s)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n\t\t(fields_autoplaced yes)\n\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill\n\t\t\t(color 0 0 0 0.0000)\n\t\t)\n\t\t(uuid %s)\n" % (
                f2(sx), f2(sy), f2(sheet_w), f2(sheet_h), q(b["sheet_uuids"][k - 1]))
            o += "\t\t(property \"Sheetname\" %s\n\t\t\t(at %s %s 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left bottom)\n\t\t\t)\n\t\t)\n" % (q(f"{b['name']}_{k}"), f2(sx), f2(sy - 0.7))
            o += "\t\t(property \"Sheetfile\" %s\n\t\t\t(at %s %s 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left top)\n\t\t\t)\n\t\t)\n" % (q(b["file"]), f2(sx), f2(sy + sheet_h + 0.7))
            pins = [(nm, sh, (sx, sy + 7.62 + i * 5.08), 180) for i, (nm, sh) in enumerate(ins)] + \
                   [(nm, sh, (sx + sheet_w, sy + 7.62 + i * 5.08), 0) for i, (nm, sh) in enumerate(outs)]
            for nm, sh, (px, py), ang in pins:
                just = "left" if ang == 180 else "right"
                o += "\t\t(pin %s %s\n\t\t\t(at %s %s %s)\n\t\t\t(uuid %s)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify %s)\n\t\t\t)\n\t\t)\n" % (
                    q(nm), sh, f2(px), f2(py), f2(ang), q(U(f"sp{b['pfx']}{k}-{nm}")), just)
                net = nm if nm in b.get("shared", ()) else f"{nm}_{k}"
                qx = px - 7.62 if ang == 180 else px + 7.62
                wires_r.append(((qx, py), (px, py)))
                labels_r.append((net, (qx, py), ang))
            o += "\t\t(instances\n\t\t\t(project \"TriggerFlow\"\n\t\t\t\t(path %s\n\t\t\t\t\t(page %s)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n" % (q(f"/{ROOT_UUID}"), q(str(page)))
    for i, (a, b2) in enumerate(wires_r):
        o += "\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            f2(a[0]), f2(a[1]), f2(b2[0]), f2(b2[1]), q(U(f"rwire{i}")))
    for i, (name, p, ang) in enumerate(labels_r):
        just = "right bottom" if ang == 180 else "left bottom"
        o += "\t(label %s\n\t\t(at %s %s %s)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n\t\t(uuid %s)\n\t)\n" % (
            q(name), f2(p[0]), f2(p[1]), f2(ang), just, q(U(f"rlabel{i}")))
    o += "\t(sheet_instances\n\t\t(path \"/\"\n\t\t\t(page \"1\")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n"
    return o

def build_kicad_sym(src_blocks):
    blk = src_blocks["TriggerFlow:MCP6S91"].replace('(symbol "TriggerFlow:MCP6S91"', '(symbol "MCP6S91"', 1)
    return "(kicad_symbol_lib\n\t(version 20260306)\n\t(generator \"kicad_symbol_editor\")\n\t(generator_version \"10.0\")\n\t" + blk + "\n)\n"

def build_pro(block_sheets):
    return json.dumps({"meta": {"filename": "TriggerFlow.kicad_pro", "version": 3},
                       "schematic": {"drawing": {"default_line_thickness": 6.0}},
                       "sheets": [[ROOT_UUID, "Root"]] + block_sheets, "text_variables": {}}, indent=2, ensure_ascii=False)
