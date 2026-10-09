/**
 * TriggerFlow : plans internes et zones interdites (EasyEDA Pro, API PCB bêta).
 * À exécuter dans l'éditeur PCB ouvert, sur une COPIE du projet.
 *
 * Cotes en mm, repère des DXF : origine au coin AVANT gauche, Y vers l'ARRIÈRE.
 * Le script calibre lui-même unité, origine et sens des axes à partir des 5 pastilles GND
 * (H3 (4;4), H6 (66;4), H4 (171;4), H2 (171;121) ; H7 doit être supprimée avant, elle couperait la bande +5V).
 *
 * Ce qu'il fait :
 *  1. supprime les remplissages existants sur Inner1 et Inner2 ;
 *  2. Inner1 : GND (polygone sans l'îlot) + VISO_GND (îlot), 3 mm d'écart ;
 *  3. Inner2 : VISO_3V3, +12V, +3V3, +5V (un seul polygone, bande verticale élargie à 4,5 mm) ;
 *  4. zones interdites toutes couches : antenne, barrière d'isolation, cercles R 4,8 mm autour de H1 et H5.
 */
const DRY_RUN = false;          // true : calcule et affiche sans rien créer
const KEEP_ISLANDS = true;      // true tant que le schéma n'est pas importé (sinon les plages sans pastille disparaissent)

const L = (typeof EPCB_LayerId !== 'undefined') ? EPCB_LayerId : {};
const LAYER = { INNER_1: L.INNER_1 ?? 15, INNER_2: L.INNER_2 ?? 16, MULTI: L.MULTI ?? 12 };
const RT = (typeof EPCB_PrimitiveRegionRuleType !== 'undefined') ? EPCB_PrimitiveRegionRuleType : {};
const NO_WIRES = RT.NO_WIRES ?? 5, NO_FILLS = RT.NO_FILLS ?? 6, NO_POURS = RT.NO_POURS ?? 7, NO_PLANES = RT.NO_INNER_ELECTRICAL_LAYERS ?? 8;
const KEEPOUT = [NO_WIRES, NO_FILLS, NO_POURS, NO_PLANES].concat(RT.NO_VIAS !== undefined ? [RT.NO_VIAS] : []);

// ---------- 1. calibration sur les pastilles GND ----------
const pads = (await eda.pcb_PrimitivePad.getAll()).filter(p => p.getState_Net && p.getState_Net() === 'GND');
const P = pads.map(p => ({ x: p.getState_X(), y: p.getState_Y() }));
if (P.length < 4) throw new Error(`Calibration impossible : ${P.length} pastilles GND trouvées (4 attendues au minimum).`);
const near = (a, b) => Math.abs(a - b) < 1;           // en unités API
const front = P.find(p => P.filter(q => near(q.y, p.y)).length >= 3);   // rangée H3 / H6 / H4 (y = 4 mm)
if (!front) throw new Error('Rangée H3 / H6 / H4 introuvable : vérifie les pastilles GND.');
const row = P.filter(q => near(q.y, front.y)).sort((a, b) => a.x - b.x);
const H3 = row[0], H4 = row[row.length - 1];
const H2 = P.filter(q => !near(q.y, front.y)).sort((a, b) => Math.abs(b.x - H4.x) > Math.abs(a.x - H4.x) ? -1 : 1)[0];
const sx = (H4.x - H3.x) / (171 - 4), sy = (H2.y - H4.y) / (121 - 4);
const ox = H3.x - 4 * sx, oy = H3.y - 4 * sy;
const T = (x, y) => [ox + x * sx, oy + y * sy];
console.log(`Calibration : 1 mm = ${sx.toFixed(4)} unités en X, ${sy.toFixed(4)} en Y ; origine API = (${ox.toFixed(1)} ; ${oy.toFixed(1)})`);
if (Math.abs(Math.abs(sx) - Math.abs(sy)) > 0.01 * Math.abs(sx)) throw new Error('Échelles X et Y différentes : calibration douteuse, arrêt.');

const poly = pts => { const a = pts.map(([x, y]) => T(x, y)); const src = [a[0][0], a[0][1], 'L']; a.slice(1).forEach(([x, y]) => src.push(x, y)); return eda.pcb_MathPolygon.createPolygon(src); };
const circle = (cx, cy, r) => { const [x, y] = T(cx, cy); return eda.pcb_MathPolygon.createPolygon(['CIRCLE', x, y, Math.abs(r * sx)]); };
const rect = (x1, y1, x2, y2) => poly([[x1, y1], [x2, y1], [x2, y2], [x1, y2]]);

// ---------- 2. géométrie (mm, repère DXF) ----------
const POURS = [
  // Inner1
  { net: 'GND', layer: LAYER.INNER_1, name: 'L2_GND', shape: () => poly([[0.5, 0.5], [174.5, 0.5], [174.5, 124.5], [99.4, 124.5], [99.4, 83.5], [0.5, 83.5]]) },
  { net: 'VISO_GND', layer: LAYER.INNER_1, name: 'L2_VISO_GND', shape: () => rect(0.5, 86.5, 96.3, 124.5) },
  // Inner2
  { net: 'VISO_3V3', layer: LAYER.INNER_2, name: 'L3_VISO_3V3', shape: () => rect(0.5, 86.5, 96.3, 124.5) },
  { net: '+12V', layer: LAYER.INNER_2, name: 'L3_+12V', shape: () => poly([[104, 124.5], [174.5, 124.5], [174.5, 17], [127.5, 17], [127.5, 83.5], [104, 83.5]]) },
  { net: '+3V3', layer: LAYER.INNER_2, name: 'L3_+3V3', shape: () => rect(4, 8, 121, 79.5) },
  { net: '+5V', layer: LAYER.INNER_2, name: 'L3_+5V', shape: () => poly([[84, 83], [126.5, 83], [126.5, 15.5], [174.5, 15.5], [174.5, 0.5], [0.5, 0.5], [0.5, 80.5], [3, 80.5], [3, 7], [122, 7], [122, 80.5], [84, 80.5]]) },
];
const REGIONS = [
  { name: 'Interdit_antenne', shape: () => rect(58, 52, 86, 81.5) },
  { name: 'Interdit_barriere_isolation', shape: () => rect(0, 83.5, 99.4, 86.5) },
  { name: 'Interdit_H1_3mm', shape: () => circle(4, 121, 4.8) },
  { name: 'Interdit_H5_3mm', shape: () => circle(100.965, 119, 4.8) },
];

// ---------- 3. exécution ----------
if (DRY_RUN) { console.log('DRY_RUN : rien n\'est créé.'); POURS.concat(REGIONS).forEach(o => console.log(o.name)); }
else {
  for (const lay of [LAYER.INNER_1, LAYER.INNER_2]) {
    const old = await eda.pcb_PrimitivePour.getAll(undefined, lay);
    if (old.length) { await eda.pcb_PrimitivePour.delete(old.map(o => o.getState_PrimitiveId())); console.log(`Supprimé ${old.length} remplissage(s) sur la couche ${lay}`); }
  }
  for (const p of POURS) {
    const r = await eda.pcb_PrimitivePour.create(p.net, p.layer, p.shape(), 'solid', KEEP_ISLANDS, p.name, 1, undefined, true);
    console.log(r ? `OK  ${p.name}` : `ÉCHEC ${p.name} (le net « ${p.net} » existe-t-il sur le PCB ?)`);
  }
  for (const g of REGIONS) {
    const r = await eda.pcb_PrimitiveRegion.create(LAYER.MULTI, g.shape(), KEEPOUT, g.name);
    console.log(r ? `OK  ${g.name}` : `ÉCHEC ${g.name}`);
  }
  console.log('Terminé : relancer le remplissage de tous les cuivres, puis Design → Check DRC.');
}
