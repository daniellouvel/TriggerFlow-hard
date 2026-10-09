# TriggerFlow — Checklist de placement PCB

4 octobre 2026 (mise à jour d'après le placement réel) — export de la checklist « TriggerFlow — Checklist de placement PCB »

## Plan de zones (placement du 04/10)

Carte 175 × 125 mm, 4 couches, vue de dessus. Origine au coin arrière gauche, x vers la droite, y vers l'avant (bord arrière en haut). Cotes en mm, reprises du placement réel (`pcb/placement_TriggerFlow.csv`), à affiner une fois les empreintes confirmées. Positions des connecteurs données par leur **centre**.

| Zone | x (mm) | y (mm) | Contenu |
| --- | --- | --- | --- |
| Sorties isolées (VISO) | 0–99 | 0–40 | J71, J81-J84 (centres x = 17, 35, 53, 71, 89) ; TVS, 2N7002, 74LVC2G04 ; U18 au centre de l'îlot |
| Barrière d'isolation | 0–99 | y = 40 | U71, U81, U83 (HCPL-063L) et U17 (B0505S, sous J84, x = 90) à cheval ; ≥ 3 mm sans cuivre, toutes couches |
| Servo, relais, entrée 12 V | 104–175 | 0–43,5 | bord arrière : J13 (servo) + C30, J14 (relais), J12 (12 V) ; RELAY13, Q13, D15 ; U13 (languette à gauche) + L13, C28, D14 ; F12, Q12, D17 au bord droit |
| Module ESP32-S3-WROOM-1 (U10, v2) | 0,5–26 | 45–63 | tourné de 90°, antenne au bord gauche, broches 1-14 vers l'avant |
| USB-C J10, U25 (v2) | 0,5–16 | 70–80 | USB natif protégé, CC1 / CC2 5,1 k |
| 3V3_MCU, RESET, BOOT (v2) | 27–56 | 44,5–72,5 | U26, D10, D19, SW10, SW11 |
| Zone antenne (v2) | 0–7 | 43,5–68 | sans cuivre sur les 4 couches ; plus de fente |
| Bus I2C (bloc 8) | 88–124 | 46–72 | U19 MCP23017, U20/U23 MCP4728, U24 ADS7828 |
| Couloir de bus | 0–124 | 73,5–81,5 | THR, CS, ID, TLV_OUT en couche 4 ; rangée de vias de couture côté analogique (y ≈ 81,6) |
| Vannes 2 × 3 | 127–175 | 44–88 | CN91-CN93 (y ≈ 48) et CN94-CN96 (y ≈ 83) vers l'extérieur, rail +12V au milieu ; D9n entre CN9n et Q9n |
| Entrées capteur ×6 | 0–124 | 82–125 | J11-J61 (centres x = 17, 35, 53, 79, 97, 115) ; une bande de 18 mm par voie |
| 12 V → 5 V, +3V3, LED | 124–175 | 90–125 | U15 tourné (broches à gauche, languette au bord droit), C40 au-dessus de l'entrée, C48-C50 et D18 collés aux broches, L12 et C59 à gauche ; U16, C58, C39, CN11 au bord avant |

Trous M3 : H1 (4, 4) et H5 (101, 6) côté VISO en NPTH ; H2 (171, 4), H3 (4, 121), H4 (171, 121), H6 (66, 121) entre J31 et J41 ; H7 supprimé (il coupait la bande +5V d'Inner2).

## Partitionnement et chemins de courant

Analogique, numérique, puissance et isolé restent dans leurs zones ; aucun courant fort ne passe sous l'analogique.

- [ ] Couche 2 = GND plein, jamais coupée sous les bandes analogiques ni sous la zone I2C
- [ ] Couche 3 : +3V3 au centre et à l'avant (entrées, I2C) ; v2 : plage 3V3_MCU sous le module et U26 ; +12V limité au quart droit (alim, relais, servo, vannes) ; +5V en bandes étroites le long des bords (avant sous les RJ45 vers F11-F61, bande verticale de 4,5 mm vers U16, tronçon sous la barrière vers U17 et D10) ; v2 : plus de bande gauche ; VISO_3V3 dans l'îlot
- [ ] Retours des vannes, du servo et du LM2596 vers J12 par le quart droit uniquement
- [ ] Une piste qui traverse une bande analogique passe en couche 4 et la croise à angle droit
- [ ] Chaque voie d'entrée suit l'ordre du signal : RJ45 → TVS/PTC → R16/BAT54S → MCP6S91 → TLV3501 → TLV\_OUT vers l'ESP32
- [ ] TLV\_OUT (fronts de 4,5 ns) ne longe jamais l'entrée CLAMP du PGA
- [ ] SPI, CS et SERVO\_PWM routés en couche 4, hors des bandes analogiques
- [ ] Pistes +12V, VALVE\_PWR, VALVE\_SW : ≥ 2 mm ou plages de cuivre
- [ ] Au moins 2 vias par source de MOSFET (Q91-Q96, Q13) vers la couche 2

## Antenne de l'ESP32 (v2 : module au bord)

En v2, l'antenne du module est au bord gauche de la carte, comme le recommande Espressif. Le problème de la v1 (antenne vers l'intérieur, près des voies analogiques) disparaît.

- [ ] Zone x 0–7, y 43,5–68 sans cuivre sur les 4 couches, sans composant ni piste
- [ ] Partie antenne du module (x 0,5–6,8) au ras du bord, rien au-delà
- [ ] Aucun composant métallique (USB-C, électrolytique) à moins de 5 mm de la zone antenne ; J10 est à ≈ 2 mm de la zone et ≈ 7 mm de l'antenne : à surveiller
- [ ] Plan GND d'Inner1 plein sous le corps du module (hors antenne), avec de nombreux vias sous la pastille centrale (broche 41)
- [ ] Couloir de bus (y 73,5–81,5) entre le module et les voies analogiques, rangée de vias de couture côté analogique
- [ ] Si le boîtier est métallique : module WROOM-1U-N16R8 (C3013946) à antenne externe u.FL

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
- [ ] U71, U81, U83 (HCPL-063L) et U17 (B0505S) posés à cheval, broches côté ESP32 sous la barrière
- [ ] Bande sans cuivre sous U17 entre les broches 1-2 et 3-4 (fente fraisée optionnelle)
- [ ] Aucune piste, aucun via, aucun plan qui traverse la barrière en dehors de ces 4 composants
- [ ] Blindages des RJ45 J71 et J81-J84 non connectés
- [ ] Trous H1 et H5 en NPTH (non métallisés), à ≥ 3 mm de tout cuivre VISO
- [ ] Écart ≥ 3 mm entre la zone relais (GND) et l'îlot VISO
- [ ] Vérifier la distance de fuite réelle sous les HCPL-063L (boîtier SO-8) au regard de la norme IPC-2221B

## Découplage, puissance et thermique

Les deux LM2596 dissipent chacun 2 à 3 W dans le même coin : boucles courtes, cuivre sous les languettes, électrolytiques à distance.

- [ ] Chaque 100 nF à ≤ 2 mm de sa broche d'alimentation, via GND juste à côté du condensateur
- [ ] Filtre THR (R13/C11 et équivalents) collé à la broche 2 de chaque TLV3501
- [ ] Boucle C40 → U15 → D18 la plus courte possible, L12 à moins de 10 mm de la broche SW de U15 ; idem C18/C19/C20 → U13 → D14 et L13
- [ ] L12 et L13 orientées à 90° l'une de l'autre, à ≥ 10 mm
- [ ] Plage de cuivre et ≈ 15 vias thermiques sous la languette de U15 et de U13 (deux plans internes à traverser) ; couche 3 reliée au GND sous les régulateurs pour dissiper
- [ ] Électrolytiques C40, C59, C28, C30 à ≥ 5 mm des languettes des LM2596
- [ ] C30 (470 µF) au plus près de J13
- [ ] Dans chaque canal vanne, D9n entre CN9n et Q9n : boucle de roue libre ≤ 10 mm
- [ ] v2 : C10 + C78 collés à la broche 2 (3V3) du module ; C79 / C80 en sortie de U26 ; R106 / C86 près de EN
- [ ] v2 : USB_DP / USB_DN courtes, de même longueur, sans via, au-dessus d'Inner1 ; U25 entre J10 et le module

## Mécanique et fixations

Onze RJ45 subissent un effort à chaque branchement : un trou de fixation près de chaque groupe de connecteurs, pas seulement aux coins.

- [ ] 6 trous M3 (H1 à H6) ; H7 supprimé, il coupait la bande +5V d'Inner2
- [ ] Zone d'exclusion de 7 mm de diamètre autour de chaque trou (tête de vis, entretoise)
- [ ] Décider si les trous GND (H2, H3, H4, H6) sont reliés à la masse du boîtier ; H1 et H5 jamais
- [ ] RJ45 alignés sur le bord, nez au ras ou en léger débord selon la façade
- [ ] Dégagement de 5 mm autour de CN91-CN96, J13 et J14 pour les doigts
- [ ] Rien de haut contre les connecteurs de vannes (C30, RELAY13)
- [ ] Relever les hauteurs maximales : relais, électrolytiques, LM2596 (v2 : plus de DevKit sur barrettes) ; vérifier sous le couvercle
- [ ] Découpe de façade pour l'USB-C J10 au bord gauche (v2 : un seul port)

## Fabrication, points de test et sérigraphie

Tout sur la face du dessus pour un assemblage JLC en simple face, le moins cher.

- [ ] Tous les CMS et tous les traversants (RJ45, borniers, barrettes) sur la face du dessus
- [ ] Composants polarisés orientés dans le même sens par zone (diodes, électrolytiques, CI)
- [ ] 3 repères optiques (fiducials) en coins opposés
- [ ] ≥ 0,5 mm entre tout cuivre et le bord de la carte
- [ ] Écarts entre zones d'encombrement selon IPC-7351 ; pas de CMS sous les zones de soudure des traversants
- [ ] Points de test : +12V, +5V, +3V3, VISO\_3V3, V\_SERVO, GND, VISO\_GND, I2C\_SDA/SCL, SPI\_MOSI/SCK, TLV\_OUT\_1 à 6
- [ ] Sérigraphie : V1 à V6 et + / − près de CN91-CN96, dans l'ordre des GX12 de façade
- [ ] Sérigraphie : « BASSE TENSION, 30 V max, jamais de 230 V » près de J14
- [ ] Sérigraphie : numéro de voie près de chaque RJ45, marquage de la zone isolée
- [ ] Empilement JLC standard 4 couches 1,6 mm, cuivre 1 oz

## À confirmer avant le placement réel

Les cotes du plan sont estimées ; ces données les figent.

- [ ] Empreinte exacte du RJ45 HanXia C25168869 (largeur supposée 16 mm, pas de 18 mm)
- [ ] Empreinte EasyEDA du module WROOM-1 : position de la broche 1 et de l'antenne, pour fixer la rotation
- [ ] HX25003-2A : version droite ou coudée
- [ ] Boîtier : plastique ou métallique (décide de la WROOM-1U et du raccordement des trous à la masse)
- [x] Borniers J13 (servo) et J14 (relais) : KF128-5.08-3P-AA, C474953
- [x] Mise à jour de README.md et BOM-netlist.md sur GitHub (servo, relais, suppression des Blocs 4 et 7)
