# TriggerFlow — Checklist de placement PCB

4 octobre 2026 (mise à jour d'après le placement réel) — export de la checklist « TriggerFlow — Checklist de placement PCB »

## Plan de zones (placement du 04/10)

Carte 175 × 125 mm, 4 couches, vue de dessus. Origine au coin arrière gauche, x vers la droite, y vers l'avant (bord arrière en haut). Cotes en mm, reprises du placement réel (`pcb/placement_TriggerFlow.csv`), à affiner une fois les empreintes confirmées. Positions des connecteurs données par leur **centre**.

| Zone | x (mm) | y (mm) | Contenu |
| --- | --- | --- | --- |
| Sorties isolées (VISO) | 0–99 | 0–40 | J71, J81-J84 (centres x = 17, 35, 53, 71, 89) ; TVS, 2N7002, 74LVC2G04 ; U114 au centre de l'îlot |
| Barrière d'isolation | 0–99 | y = 40 | U71, U81, U83 (HCPL-063L) et U113 (B0505S, sous J84, x = 90) à cheval ; ≥ 3 mm sans cuivre, toutes couches |
| Relais | 104–124 | 0–40 | J131 au bord arrière, K131, Q131, D131 |
| Alimentation 12 V → 5 V | 127–175 | 0–41 | J111 dans le coin, F111, Q111, D111, C112, U111 (languette en haut), D112, L111, C117 |
| ESP32-S3 DevKit (U105) | 1–70 | 44,5–72,5 | USB-C au bord gauche, rangée J1 vers l'avant ; D101 sous la carte |
| Zone antenne | 58–86 | 43,5–73 | sans cuivre sur les 4 couches ; fente fraisée ≈ 12 × 24 mm sous l'antenne (x 58–70, y 46–70) |
| Bus I2C (bloc 8) | 88–124 | 46–72 | U101 MCP23017, U102/U103 MCP4728, U104 ADS7828 |
| Couloir de bus | 0–124 | 73,5–81,5 | THR, CS, ID, TLV_OUT en couche 4 ; rangée de vias de couture côté analogique (y ≈ 81,6) |
| Servo 6 V | 127–175 | 44–69 | U121, L121, D121, C124, U122 ; C126 et J121 au bord droit |
| Vannes 2 × 3 | 127–175 | 71–115 | CN91-CN96 en 2 rangées miroir, rail +12V central |
| Entrées capteur ×6 | 0–124 | 82–125 | J11-J61 (centres x = 17, 35, 53, 79, 97, 115) ; une bande de 18 mm par voie |
| +3V3 et LED | 127–175 | 115–125 | U112 (AMS1117), C116, C111, CN101 au bord avant |

Trous M3 : H1 (4, 4) et H5 (101, 6) côté VISO en NPTH ; H2 (171, 4), H3 (4, 121), H4 (171, 121), H6 (66, 121) entre J31 et J41 ; H7 optionnel (124, 76).

## Partitionnement et chemins de courant

Analogique, numérique, puissance et isolé restent dans leurs zones ; aucun courant fort ne passe sous l'analogique.

- [ ] Couche 2 = GND plein, jamais coupée sous les bandes analogiques ni sous la zone I2C
- [ ] Couche 3 : +3V3 en grande plage continue sous la moitié gauche et le centre (entrées, ESP32, I2C) ; +12V limité au quart droit (alim, relais, servo, vannes) ; +5V en bandes étroites le long des bords (avant sous les RJ45 vers F11-F61, gauche vers la DevKit, bande verticale vers U112, tronçon sous la barrière vers U113) ; VISO_3V3 dans l'îlot
- [ ] Retours des vannes, du servo et du LM2596 vers J111 par le quart droit uniquement
- [ ] Une piste qui traverse une bande analogique passe en couche 4 et la croise à angle droit
- [ ] Chaque voie d'entrée suit l'ordre du signal : RJ45 → TVS/PTC → R16/BAT54S → MCP6S91 → TLV3501 → TLV\_OUT vers l'ESP32
- [ ] TLV\_OUT (fronts de 4,5 ns) ne longe jamais l'entrée CLAMP du PGA
- [ ] SPI, CS et SERVO\_PWM routés en couche 4, hors des bandes analogiques
- [ ] Pistes +12V, VALVE\_PWR, VALVE\_SW : ≥ 2 mm ou plages de cuivre
- [ ] Au moins 2 vias par source de MOSFET (Q91-Q96, Q131) vers la couche 2

## Antenne de l'ESP32

Sur la DevKit, l'USB et l'antenne sont aux deux bouts : l'USB va au bord gauche, l'antenne pointe vers le bus I2C, loin de l'avant.

- [ ] Zone x 58–86, y 43,5–73 sans cuivre sur les 4 couches, sans composant ni piste
- [ ] Fente fraisée dans la carte sous la partie antenne de la DevKit (environ 12 × 24 mm, à caler sur la carte réelle)
- [ ] Couloir de bus (y 73,5–81,5) entre l'antenne et les voies analogiques, rangée de vias de couture tous les 3 à 5 mm côté analogique
- [ ] Dans chaque voie, TLV3501 côté ESP32 et MCP6S91 côté connecteur : entrée du PGA à ≈ 18 mm de la zone antenne
- [ ] Aucun RJ45 blindé ni électrolytique à moins de 10 mm de l'antenne
- [ ] Si le boîtier est métallique : passer à une carte WROOM-1U avec antenne externe (u.FL) avant de router

## Empilement 4 couches

Dans l'empilement JLC 1,6 mm, les couches 3 et 4 sont proches (≈ 0,2 mm) et séparées des couches 1-2 par un noyau épais : une piste de couche 4 prend son retour de courant dans la couche 3, pas dans le plan GND.

- [ ] Empilement JLC04161H-7628 : L1 composants et signaux, L2 GND plein, L3 alimentations, L4 signaux longs
- [ ] Aucune piste de couche 4 ne traverse une frontière entre plages de la couche 3 ; sinon condensateur 100 nF entre les deux plages au point de croisement, ou passage en couche 1
- [ ] SERVO_PWM et GPIO_VALVE_1 à 6 : couche 4 sous le +3V3, via, puis couche 1 avant d'entrer dans la zone +12V
- [ ] GND coulé sur les zones libres des couches 1 et 4, relié à la couche 2 par des vias, aussi le long du bord de la carte
- [ ] Dans l'îlot isolé, même chose en VISO_GND, avec ses propres vias vers l'îlot VISO_GND de la couche 2

## Isolation VISO

Une seule barrière droite à y = 40 mm ; seuls les optos et le B0505S la traversent.

- [ ] Écart ≥ 3 mm entre cuivre GND et cuivre VISO, sur les 4 couches, tout le long de la barrière
- [ ] U71, U81, U83 (HCPL-063L) et U113 (B0505S) posés à cheval, broches côté ESP32 sous la barrière
- [ ] Bande sans cuivre sous U113 entre les broches 1-2 et 3-4 (fente fraisée optionnelle)
- [ ] Aucune piste, aucun via, aucun plan qui traverse la barrière en dehors de ces 4 composants
- [ ] Blindages des RJ45 J71 et J81-J84 non connectés
- [ ] Trous H1 et H5 en NPTH (non métallisés), à ≥ 3 mm de tout cuivre VISO
- [ ] Écart ≥ 3 mm entre la zone relais (GND) et l'îlot VISO
- [ ] Vérifier la distance de fuite réelle sous les HCPL-063L (boîtier SO-8) au regard de la norme IPC-2221B

## Découplage, puissance et thermique

Les deux LM2596 dissipent chacun 2 à 3 W dans le même coin : boucles courtes, cuivre sous les languettes, électrolytiques à distance.

- [ ] Chaque 100 nF à ≤ 2 mm de sa broche d'alimentation, via GND juste à côté du condensateur
- [ ] Filtre THR (R13/C11 et équivalents) collé à la broche 2 de chaque TLV3501
- [ ] Boucle C112 → U111 → D112 la plus courte possible ; idem C129/C122 → U121 → D121
- [ ] L111 et L121 orientées à 90° l'une de l'autre, à ≥ 10 mm
- [ ] Plage de cuivre et ≈ 15 vias thermiques sous la languette de U111 et de U121 (deux plans internes à traverser) ; couche 3 reliée au GND sous les régulateurs pour dissiper
- [ ] Électrolytiques C112, C117, C124, C126 à ≥ 5 mm des languettes des LM2596
- [ ] C126 (470 µF) collé à J121
- [ ] Dans chaque canal vanne, D9n entre CN9n et Q9n : boucle de roue libre ≤ 10 mm
- [ ] D101 (anti-retour USB) près de la broche 5V de la DevKit

## Mécanique et fixations

Onze RJ45 subissent un effort à chaque branchement : un trou de fixation près de chaque groupe de connecteurs, pas seulement aux coins.

- [ ] 6 trous M3 (H1 à H6), plus H7 au centre si la carte fléchit
- [ ] Zone d'exclusion de 7 mm de diamètre autour de chaque trou (tête de vis, entretoise)
- [ ] Décider si les trous GND (H2, H3, H4, H6) sont reliés à la masse du boîtier ; H1 et H5 jamais
- [ ] RJ45 alignés sur le bord, nez au ras ou en léger débord selon la façade
- [ ] Dégagement de 5 mm autour de CN91-CN96, J121 et J131 pour les doigts
- [ ] Rien de haut contre les connecteurs de vannes (C126, K131)
- [ ] Relever les hauteurs maximales : DevKit sur barrettes, relais, électrolytiques, LM2596 ; vérifier sous le couvercle
- [ ] Découpe de façade pour les deux USB-C de la DevKit (hauteur des barrettes femelles comprise)

## Fabrication, points de test et sérigraphie

Tout sur la face du dessus pour un assemblage JLC en simple face, le moins cher.

- [ ] Tous les CMS et tous les traversants (RJ45, borniers, barrettes) sur la face du dessus
- [ ] Composants polarisés orientés dans le même sens par zone (diodes, électrolytiques, CI)
- [ ] 3 repères optiques (fiducials) en coins opposés
- [ ] ≥ 0,5 mm entre tout cuivre et le bord de la carte
- [ ] Écarts entre zones d'encombrement selon IPC-7351 ; pas de CMS sous les zones de soudure des traversants
- [ ] Points de test : +12V, +5V, +3V3, VISO\_3V3, V\_SERVO, GND, VISO\_GND, I2C\_SDA/SCL, SPI\_MOSI/SCK, TLV\_OUT\_1 à 6
- [ ] Sérigraphie : V1 à V6 et + / − près de CN91-CN96, dans l'ordre des GX12 de façade
- [ ] Sérigraphie : « BASSE TENSION, 30 V max, jamais de 230 V » près de J131
- [ ] Sérigraphie : numéro de voie près de chaque RJ45, marquage de la zone isolée
- [ ] Empilement JLC standard 4 couches 1,6 mm, cuivre 1 oz

## À confirmer avant le placement réel

Les cotes du plan sont estimées ; ces données les figent.

- [ ] Empreinte exacte du RJ45 HanXia C25168869 (largeur supposée 16 mm, pas de 18 mm)
- [ ] Dimensions de la YD-ESP32-S3 N16R8, entraxe des rangées J1/J3, position de la broche 1, emplacement de l'antenne
- [ ] HX25003-2A : version droite ou coudée
- [ ] Boîtier : plastique ou métallique (décide de la WROOM-1U et du raccordement des trous à la masse)
- [ ] Choix du bornier J131 et de la barrette J121
- [x] Mise à jour de README.md et BOM-netlist.md sur GitHub (servo, relais, suppression des Blocs 4 et 7)
