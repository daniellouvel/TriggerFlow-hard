# Bonnes pratiques PCB — TriggerFlow v2 (4 couches)

Document de référence issu de la conception TriggerFlow v2. S'applique à tout PCB 4 couches avec convertisseurs à découpage, bus analogiques et signaux mixtes.

---

## 1. Raisonnement en 4 couches

**Avant tout jugement de placement ou de routage, identifier la couche concernée.**

| Couche | Rôle | Ce qui y passe |
|---|---|---|
| Top (L1) | signaux, pistes locales | pistes courtes, composants, bus de signaux |
| Inner1 (L2) | GND plein continu | plan de retour pour tous les signaux |
| Inner2 (L3) | plages d'alimentation | +12V, +5V, +3V3, 3V3_MCU, VISO_3V3 |
| Bottom (L4) | signaux longs | bus horizontaux (couloir), pistes de distribution |

Un condensateur de découplage ou d'entrée/sortie se connecte à la plage Inner2 par un via court. Il n'a pas besoin d'une piste de surface pour rejoindre une alimentation distante. **Ne pas déplacer un composant pour raccourcir une piste de surface si le via vers Inner2 suffit.**

---

## 2. Convertisseurs à découpage (LM2596, MP2307, similaires)

- **Piste SW (nœud de commutation) ≤ 8 mm**, largeur ≥ 1 mm, couche Top. C'est la piste la plus critique : elle rayonne si elle est longue. **Mesurer avec l'outil de mesure avant de déplacer.**
- **Condensateurs d'entrée** collés à la broche IN, alimentés par Inner2 via des vias courts.
- **Condensateurs de sortie** : le plus grand (electrolytique) en premier après l'inductance, puis les autres par valeur décroissante.
- **Inductance** : broche 1 (nœud SW) face à U, broche 2 (sortie) face aux condensateurs de sortie.
- **Diode flyback** entre le nœud SW et GND, aussi proche que possible du nœud SW.
- **Via thermique** sous la languette de U (TO-263) : minimum 4 vias vers le plan GND Inner1.
- **Diviseur FB** (R116/R117) en dessous du circuit, proches de la broche FB.

---

## 3. Découplage des circuits intégrés

- **100 nF en premier**, le plus proche de la broche VCC, bord à bord ≤ 2 mm. Via GND collé à sa pastille GND.
- **10 µF ou 1 µF** juste derrière le 100 nF.
- Le courant de découplage fait la boucle : broche VCC → condensateur → via GND → plan Inner1 → broche GND. **Plus la boucle est petite, mieux ça filtre.**
- Avec un plan GND à 0,2 mm sous Top (4 couches), la boucle est très courte si le via est collé à la pastille GND du condensateur.
- **Pas de piste longue entre la broche VCC et le condensateur** : la piste doit aller VCC → condensateur → broche, pas l'inverse.

---

## 4. Couloir de bus analogique

- **Bande de 8 mm sans aucun composant** entre le MCU et les voies d'entrée (y = 73,5 à 81,5 mm dans TriggerFlow).
- Vérifier avec une zone interdite (Prohibited Region, type Component uniquement).
- **Pistes horizontales en couche Bottom** (L4), au-dessus de la plage +3V3 d'Inner2 (retour de courant propre).
- **Pistes verticales (entrées/descentes) en couche Top**, vias 0,2/0,4 mm aux changements de couche.
- **Ordre des lignes** (de haut en bas) : TLV_OUT, SPI, CS — piste de garde GND — ID_ADC, THR.
- **Piste de garde GND** (ligne 9 sur 18) : 0,30 mm de large, vias GND tous les 10 mm.
- **Pas entre lignes** : 0,45 mm (centre à centre), pistes 0,15 mm, écart 0,30 mm.
- **Vias de couture GND** : y ≈ 82 mm, pas de 3 à 4 mm, 0,3/0,6 mm standard.
- Les commandes EV ne passent **jamais** par le couloir : elles longent la barrière d'isolation au-dessus.

---

## 5. Barrière d'isolation galvanique

- **≥ 3 mm sans cuivre sur toutes les couches** entre le côté GND et le côté VISO.
- Règle Net-Net dans EasyEDA : classe VISO vs reste → espacement 3 mm.
- Seuls les composants d'isolation (HCPL-063L, B0505S, U117) traversent la barrière.
- **Aucune piste, aucun plan, aucun via** ne traverse la barrière entre les deux domaines.

---

## 6. Antenne Wi-Fi (module WROOM-1)

- **Zone sans cuivre sur toutes les couches** sous l'antenne : x = 0 à 7 mm depuis le bord gauche.
- Meilleure solution : découpe fraisée dans le PCB sous l'antenne (aucun substrat FR4 sous l'antenne).
- Si découpe : aucune zone interdite nécessaire sous la découpe, mais garder 0,5 mm entre les pastilles du module et le bord de la découpe.
- **Aucun composant** dans la zone x = 0 à 7 mm. Vérifier avec le DRC.

---

## 7. Connecteur USB-C SMD

- L'**ouverture du connecteur doit dépasser du bord de la carte** de 0,5 à 1 mm pour permettre le branchement du câble.
- Les pastilles de fixation EH (blindage) doivent être reliées au GND.
- Les broches CC1 et CC2 : 5,1 kΩ vers GND (rôle périphérique USB).
- Paires D+/D− : pistes courtes, même longueur, sans via si possible.

---

## 8. Placement général

- **Mesurer avant de déplacer.** Une piste qui semble longue à l'écran peut être dans les normes (ex. piste SW à 5,5 mm).
- **Composants satellites au plus près de leur CI** : condensateurs de découplage, résistances de grille, diodes flyback.
- **Boucles de puissance compactes** : entrée → condensateurs d'entrée → CI → inductance → condensateurs de sortie, dans cet ordre physique sur la carte.
- **Ordre logique du courant** visible sur le PCB : de la source vers la charge, sans retours en arrière.
- **Connecteurs au bord de la carte**, broches vers l'extérieur.
- **Composants traversants** (borniers, barrettes) : Add into BOM: No si montés à la main.
- **Vérifier l'orientation des composants polarisés** (condensateurs electrolytiques, diodes, MOSFETs) dans l'aperçu de placement JLC avant la commande.

---

## 9. Règles de largeur de pistes

| Type de piste | Largeur minimale |
|---|---|
| Signaux bus (couloir) | 0,15 mm |
| Signaux ordinaires | 0,20 mm |
| +3V3, 3V3_MCU, VISO_3V3 | 0,60 mm |
| +5V, sortie convertisseur | 1,00 mm |
| Nœud SW (convertisseur) | 1,00 mm (≤ 8 mm de long) |
| +12V, pistes de puissance | 1,50 à 2,00 mm |
| Entrée 12V (J112 → Q112) | 2,00 mm minimum |

---

## 10. DRC et vérifications finales

- Lancer le DRC **avant le remplissage GND** (Top et Bottom), pour voir clairement les erreurs.
- Remplissages GND Top et Bottom : **en dernier**, après tout le routage.
- Vias de couture le long de la barrière d'isolation : **après le routage**, avant les remplissages.
- Vérifier dans l'aperçu JLC que la **broche 1 de chaque CI** est au bon endroit (point rouge).
- **Ne pas relancer Annotate Designator** après avoir validé la numérotation.
- Exporter la netlist après chaque modification majeure du schéma et comparer à la référence.

## 11. Retrait du cuivre par rapport au bord de la carte

Minimum JLCPCB (cartes détourées par fraisage, d'après leur tableau des capacités, à confirmer sur la page officielle avant commande) :

| Cuivre | Minimum JLC | Valeur à utiliser |
|---|---|---|
| Couches externes (Top, Bottom) : pistes, remplissages GND | 0,25 mm | **0,5 mm** |
| Couches internes (Inner1 GND, Inner2 plages) | 0,40 mm | **0,5 mm** |
| Séparation en V-cut | 0,45 mm | non utilisé ici |

- La règle par défaut d'EasyEDA (copperThickness1oz) impose 0,3 mm entre le contour et les objets de la couche ; on prend 0,5 mm pour garder de la marge sur toutes les couches.
- Les plages d'Inner2 de TriggerFlow sont à 0,5 mm du bord (DXF) ; les remplissages GND Top et Bottom doivent respecter la même valeur.
- Exceptions voulues : pastilles des connecteurs au bord (USB-C, RJ45) et trous de fixation, qui restent à l'intérieur du contour mais peuvent s'en approcher ; le DRC les signale s'ils passent sous 0,3 mm.

---

*Document créé le 14/10/2026 — projet TriggerFlow v2*
*À mettre à jour au fil des sessions.*
