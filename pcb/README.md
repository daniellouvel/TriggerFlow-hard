# Implantation PCB TriggerFlow (v4, 04/10/2026)

> Branche **v2-wroom** : placement avec le module WROOM-1 (305 composants). Netlist d'entrée `netlist_v2_wroom.json` = **export EasyEDA du 10/10** (`netlist_v2_easyeda_2026-10-10.tel`), numérotation EasyEDA (U10 = module, U15 = LM2596 5 V, U13 = LM2596 servo… correspondance complète dans `docs/mcu-v2-wroom.md`). `mcu_v2.py` (ancienne netlist construite depuis la v1) n'écrit plus que `netlist_v2_ancienne_numerotation.json`. Zoom de la zone module : `zoom_mcu_v2.png`.

Placement des **287 composants** en v1, **305** en v2 (export EasyEDA de référence du 05/10, servo et relais compris, sans moteur ni PWM) sur une carte **175 × 125 mm, 4 couches**. Repère : origine au coin arrière gauche, x vers la droite, y vers l'avant. Tailles = encombrements estimés, à recaler sur les vraies empreintes.

![Placement complet](placement_complet.png)

| Fichier | Rôle |
|---|---|
| `placement_TriggerFlow.csv` | référence, valeur, empreinte, X, Y, rotation, face, bloc (séparateur `;`) + trous M3 |
| `place.py` | positions de chaque composant |
| `check.py` | contrôle : chevauchements, bords, zone antenne, barrière d'isolation, trous M3 |
| `render.py` | dessin du placement et du chevelu (hors plans GND / alimentations) + 3 zooms |
| `export_csv.py` | régénère le CSV |
| `netlist_2026-10-05.json` | netlist de référence (export EasyEDA du 05/10) |

Usage : `python3 check.py && python3 render.py && python3 export_csv.py` (dépendance : matplotlib).

## Empilement (JLC 4 couches, JLC04161H-7628, 1,6 mm, cuivre 1 oz)

| Couche | Contenu |
|---|---|
| 1 (dessus) | composants et signaux, dont les signaux analogiques courts |
| 2 | **GND plein**, sans aucune piste (sauf l'îlot VISO_GND séparé) ; jamais coupé sous les bandes analogiques ni sous l'I2C |
| 3 | plages d'alimentation : **+12V** limité au quart droit (alim, servo, relais, vannes) ; **+3V3** au centre et à l'avant (à partir de x = 52 au-dessus du couloir de bus) ; **3V3_MCU** sous le module et son régulateur (x 9–50, y 45,5–72,5) ; **+5V** en bandes étroites (avant sous les RJ45, bande verticale vers U16, tronçon sous la barrière prolongé jusqu'à D10) ; **VISO_3V3** dans l'îlot |
| 4 (dessous) | signaux longs : SPI, CS, I2C, SERVO_PWM, commandes des vannes, TLV_OUT |

Une piste de couche 4 prend son retour dans la couche 3 (noyau épais entre L2 et L3) : elle ne traverse jamais une frontière entre plages de la couche 3 (sinon condensateur de couture 100 nF ou passage en couche 1). Une piste qui doit entrer dans la zone 12 V change donc de couche avant la frontière (ex. SERVO_PWM : couche 4 puis via et couche 1 jusqu'à U14). Une piste qui traverse une bande analogique passe en couche 4, à angle droit.

## Zones (bord arrière en haut)

| Zone | x (mm) | y (mm) | Contenu |
|---|---|---|---|
| Sorties isolées (VISO) | 0–99 | 0–40 | J71, J81-J84 au bord arrière ; TVS, 2N7002, 74LVC2G04, HCPL-063L |
| Barrière d'isolation | 0–99 | y = 40 | seuls U71, U81, U83, U17 à cheval ; ≥ 3 mm sans cuivre sur les 4 couches |
| Servo, relais, entrée 12 V | 104–175 | 0–43,5 | bord arrière : J13 (servo) + C30, J14 (relais), J12 (12 V) ; RELAY13, Q13, D15 ; U13 (languette à gauche) + L13, C28, D14 ; F12, Q12, D17 au bord droit |
| Module ESP32-S3-WROOM-1 (v2) | 0,5–26 | 45–63 (U10 tourné de 90°) | antenne au bord gauche (x 0,5–6,8) ; broches 1-14 vers l'avant |
| USB-C J10 + U25 | 0,5–16 | 70–80 | USB natif, protection USBLC6, CC 5,1 k |
| 3V3_MCU, RESET, BOOT | 27–56 | 44,5–72,5 | U26 AMS1117, D10 / D19, SW10 / SW11 |
| Zone antenne | 0–7 | 43,5–68 | sans cuivre sur les 4 couches (v2 : plus de fente) |
| Bus I2C | 88–124 | 46–72 | U19 MCP23017, U20/U23 MCP4728, U24 ADS7828 |
| Couloir de bus | 0–124 | 73,5–81,5 | THR / CS / ID / TLV_OUT en couche 4 ; rangée de vias de couture côté analogique |
| Vannes 2 × 3 | 127–175 | 44–88 | CN91-CN93 (y ≈ 48) et CN94-CN96 (y ≈ 83) vers l'extérieur, rail +12V au milieu ; D9n entre CN9n et Q9n |
| Entrées capteur ×6 | 0–124 | 82–125 | J11-J61 au bord avant (x = 17, 35, 53, 79, 97, 115), bande de 18 mm par voie |
| 12 V → 5 V, +3V3, LED | 124–175 | 90–125 | U15 tourné (broches à gauche, languette au bord droit), C40 au-dessus de l'entrée, C48-C50 et D18 collés aux broches, L12 et C59 à gauche ; U16, C58, C39, CN11 au bord avant |

**Trous M3** : H1 (4, 4) et H5 (101, 6) côté VISO en **NPTH** (jamais reliés à la masse) ; H2 (171, 4), H3 (4, 121), H4 (171, 121), H6 (66, 121) en GND ; H7 supprimé (sa pastille coupait la bande +5V d'Inner2). Exclusion de 7 mm de diamètre autour de chaque trou.

## Règles clés appliquées au placement

- Chaque voie d'entrée suit le trajet du signal : RJ45 → TVS/PTC → R16 / BAT54S / C12 → MCP6S91 → TLV3501 → TLV_OUT vers la rangée J1 de l'ESP32. TLV_OUT (fronts de 4,5 ns) ne longe jamais l'entrée CLAMP du PGA ; filtre THR (R13/C11) collé à la broche 2 du TLV3501.
- Découplages à ≤ 2 mm de leur broche, via GND juste à côté.
- Boucles de découpage courtes (C40 → U15 → D18 ; C18/C19 → U13 → D14), ≈ 15 vias thermiques sous les languettes de U15 et U13 (deux plans internes à traverser), électrolytiques à ≥ 5 mm des languettes, L12 et L13 à 90° et ≥ 10 mm.
- Pistes +12V, VALVE_PWR, VALVE_SW ≥ 2 mm ou plages ; ≥ 2 vias par source de MOSFET (Q91-Q96, Q13) vers la couche 2.
- Isolation : aucune piste, via ou plan ne traverse la barrière hors U71/U81/U83/U17 ; bande sans cuivre sous U17 ; blindages J71/J81-J84 non connectés ; ≥ 3 mm entre la zone relais (GND) et l'îlot VISO.
- Tout sur la face du dessus (assemblage JLC simple face) ; 3 fiducials ; ≥ 0,5 mm entre cuivre et bord.
- Points de test : +12V, +5V, +3V3, 3V3_MCU, VISO_3V3, V_SERVO, GND, VISO_GND, I2C_SDA/SCL, SPI_MOSI/SCK, TLV_OUT_1 à 6 ; console UART0 sur la barrette U85 (GND, TX, RX) (v2).
- Sérigraphie : V1 à V6 et + / − près de CN91-CN96 ; « BASSE TENSION, 30 V max, jamais de 230 V » près de J14 ; numéro de voie près de chaque RJ45 ; marquage de la zone isolée.

Checklist complète à cocher : [docs/pcb-checklist.md](../docs/pcb-checklist.md).

## Changements par rapport au plan de zones initial

- Couloir de bus de 8 mm (y 73,5–81,5) à la place de la bande de garde : les 24 liaisons THR, CS, ID et TLV_OUT y passent en couche 4. L'ESP32 remonte de 3 mm.
- U17 (B0505S) déplacé sous J84 : il était dans l'axe de l'antenne.
- U18 au centre de l'îlot isolé (alimente les trois optos répartis sur toute la largeur).
- Servo et relais repris avec les repères EasyEDA du 05/10 : J13 et J14 sont des borniers KF128 3P (15,8 × 10,7 mm) ; J13 recentré (x = 169,15), L13 décalé à x = 153, petits composants du servo replacés en colonne à x ≈ 162, C30 (470 µF) sous J13, RELAY13 descendu à y = 23,2, J14 à y = 5,7.

## Encore approximatif / à confirmer

- Empreinte exacte du RJ45 HanXia C25168869 (largeur supposée 16 mm, pas de 18 mm), dimensions du relais, orientation réelle de l'empreinte du module (broche 1, antenne).
- Rotation 0 = orientation par défaut de l'empreinte : vérifier la broche 1 sur la bibliothèque réelle.
- Dégagement autour des connecteurs de vannes de la 1re rangée ≈ 1,5 mm entre C30 et CN93 (5 mm visés) : à reprendre avec les vraies empreintes.
- Boîtier plastique ou métallique (métallique → module WROOM-1U-N16R8 C3013946 à antenne externe u.FL, à décider avant routage).
- Application dans EasyEDA Pro : saisie manuelle ou Claude Code + easyeda-copilot lisant le CSV (déplacer une empreinte sur le PCB ne casse pas les liaisons).
