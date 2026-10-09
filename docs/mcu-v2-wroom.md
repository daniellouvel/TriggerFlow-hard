# TriggerFlow v2 — Feuille MCU : module ESP32-S3-WROOM-1-N16R8

Branche `v2-wroom`. La v1 (DevKit sur barrettes) reste sur `main` et l'étiquette `v1.0`.

## Principe

La DevKit est remplacée par le module qu'elle portait, **ESP32-S3-WROOM-1-N16R8**, soudé directement sur la carte. Chaque signal garde **le même GPIO** qu'en v1 : le firmware ne change pas. Seuls les numéros de broches du composant U105 changent.

Ce que la DevKit fournissait et qu'il faut maintenant ajouter : le 3,3 V du module, le reset, le bouton BOOT et le port USB.

Garder la version **N16R8** : dans les versions « …V » (R8V, R16V), GPIO47 et GPIO48 (vannes 5 et 6) passent en 1,8 V.

## Broches de U105 (module WROOM-1)

| Broche module | GPIO | Net | Broche DevKit v1 |
|---|---|---|---|
| 1, 40, 41 (pastille) | — | GND | 22, 23, 24, 44 |
| 2 | — | 3V3_MCU | (3V3 de la DevKit) |
| 3 | EN | EN | 3 (RST) |
| 4, 5, 6, 7, 8, 9 | 4, 5, 6, 7, 15, 16 | TLV_OUT_1 … TLV_OUT_6 | 4 à 9 |
| 10 | 17 | FLASH_1_CMD | 10 |
| 11 | 18 | GPIO18 (DAC2_LDAC) | 11 |
| 12 / 17 | 8 / 9 | I2C_SDA / I2C_SCL | 12 / 15 |
| 13 / 14 | 19 / 20 | USB_DN / USB_DP (USB natif) | 25 / 26 (libres en v1) |
| 18 | 10 | GPIO_VALVE_3 | 16 |
| 19 / 20 | 11 / 12 | SPI_MOSI / SPI_SCK | 17 / 18 |
| 21 | 13 | SERVO_PWM | 19 |
| 23 | 21 | FLASH_2_CMD | 27 |
| 24 / 25 | 47 / 48 | GPIO_VALVE_6 / GPIO_VALVE_5 | 28 / 29 |
| 27 | 0 | IO0_BOOT | 31 (libre en v1) |
| 31 | 38 | GPIO_VALVE_4 | 35 |
| 32 | 39 | FLASH_3_CMD | 36 |
| 34 | 41 | FLASH_4_CMD | 38 |
| 35 | 42 | SHUTTER_CMD | 39 |
| 36 / 37 | RXD0 / TXD0 | RXD0 / TXD0 (pastilles de test TP142 / TP141) | 42 / 43 |
| 38 / 39 | 2 / 1 | GPIO_VALVE_2 / GPIO_VALVE_1 | 40 / 41 |
| 15, 16, 22, 26, 28, 29, 30, 33 | 3, 46, 14, 45, 35, 36, 37, 40 | non connectées | — |

Broches de démarrage (IO0, IO3, IO45, IO46) : seul IO0 est utilisé, pour le bouton BOOT. IO35 à IO37 restent libres (PSRAM octale).

## Nouveaux nets

| Net | Broches |
|---|---|
| 5V_MCU | D101.1 (cathode, anode sur +5V), D141.1 (cathode, anode sur VBUS), U141.3 (VIN), C146.1 |
| VBUS | J141 A4, A9, B4, B9 ; D141.2 ; U142.5 |
| 3V3_MCU | U141.2 et languette (VOUT), U105.2, C142.1, C143.1, C144.1, C145.1, R141.1, R142.1 |
| EN | U105.3, R141.2, C141.1, SW141 (côté 1-2) |
| IO0_BOOT | U105.27, R142.2, SW142 (côté 1-2) |
| USB_DN | J141 A7 et B7, U142.1 et U142.6, U105.13 (IO19) |
| USB_DP | J141 A6 et B6, U142.3 et U142.4, U105.14 (IO20) |
| CC1 / CC2 | J141.A5 – R143.1 / J141.B5 – R144.1 |
| TXD0 / RXD0 | U105.37 – TP141 / U105.36 – TP142 |
| GND | U105.1, 40, 41 ; U141.1 ; U142.2 ; J141 A1, A12, B1, B12 et blindage ; R143.2, R144.2 ; C141 à C146 (.2) ; SW141 et SW142 (côté 3-4) |

J141 SBU1 / SBU2 : non connectées. Le net V5_DEVKIT de la v1 devient 5V_MCU.

## Choix de conception

- **3V3_MCU dédié** : U141 AMS1117-3.3 (même pièce que U112) alimenté par 5V_MCU, séparé du +3V3 de l'électronique analogique. Le module tire jusqu'à 355 mA en émission Wi-Fi d'après la fiche JLC ; dissipation de U141 ≈ (4,55 − 3,3) × 0,36 ≈ 0,45 W en pointe, à dissiper par la languette (plage 3V3_MCU d'Inner2).
- **Deux sources pour 5V_MCU, par diodes SS14** : le +5V de la carte (D101, comme en v1) et le VBUS de l'USB (D141). Le module peut ainsi être programmé par l'USB sans le bloc 12 V, et l'USB n'alimente jamais le reste de la carte. Après la diode, 5V_MCU ≈ 4,55 V : la marge de chute de l'AMS1117 (≈ 1,1 V à pleine charge) reste juste. Si le Wi-Fi se montre instable, remplacer D101 et D141 par des diodes à plus faible tension de seuil ou passer à un régulateur à faible chute.
- **Découplage** : C142 (10 µF) + C143 (100 nF) collés à la broche 2 ; C144 + C145 (2 × 10 µF) en sortie de U141 ; C146 (10 µF) en entrée.
- **EN** : R141 10 kΩ vers 3V3_MCU + C141 1 µF vers GND (valeurs recommandées par Espressif) ; SW141 RESET vers GND.
- **IO0** : R142 10 kΩ vers 3V3_MCU ; SW142 BOOT vers GND. Maintenir BOOT puis appuyer sur RESET force le mode téléchargement.
- **USB** : un seul port USB-C, sur l'USB natif (IO19 / IO20). La v1 en avait deux (pont série + USB natif). La programmation passe par l'USB-Serial/JTAG intégré. Si le firmware utilise l'USB natif pour le contrôle PC, on reprogramme avec BOOT + RESET, et la console série reste accessible sur TP141 / TP142 avec un adaptateur 3,3 V. R143 / R144 (5,1 kΩ) déclarent la carte comme périphérique USB-C. U142 protège les deux lignes et VBUS contre les décharges.
- **Supprimés** : la DevKit et ses deux barrettes femelles. D101 reste (même rôle : +5V vers l'alimentation du microcontrôleur).

## BOM de la feuille MCU v2

| Réf. | Pièce | Boîtier | LCSC | Catégorie JLC |
|---|---|---|---|---|
| U105 | ESP32-S3-WROOM-1-N16R8 | SMD 25,5 × 18 mm | C2913202 | Extended (à confirmer sur la fiche) |
| U141 | AMS1117-3.3 | SOT-223 | C6186 | (déjà dans la BOM v1, U112) |
| U142 | USBLC6-2SC6 | SOT-23-6 | C7519 | à vérifier |
| J141 | HRO TYPE-C-31-M-12 (16 broches) | SMD | C165948 | Extended |
| SW141, SW142 | TS-1187A-B-A-B (5,1 × 5,1 mm) | SMD | C318884 | Basic |
| D101, D141 | SS14 | SMA | C2480 | (déjà dans la BOM v1) |
| R141, R142 | 10 kΩ | 0603 | C25804 | (déjà dans la BOM v1) |
| R143, R144 | 5,1 kΩ | 0603 | C23186 | Basic |
| C141 | 1 µF | 0603 | C5673 | (déjà dans la BOM v1) |
| C143 | 100 nF | 0603 | C14663 | (déjà dans la BOM v1) |
| C142, C144, C145, C146 | 10 µF | 0805 | C15850 | (déjà dans la BOM v1) |
| TP141, TP142 | pastilles de test Ø 1,5 mm | — | — | pas de pièce |

Les numéros LCSC de U105, U142, J141, SW141/142 et R143/144 ont été vérifiés sur les fiches JLC / LCSC le 06/10/2026. Les autres sont repris de la BOM v1 exportée d'EasyEDA.

## Implantation (voir `pcb/`)

- U105 tourné de 90° : **antenne au bord gauche** (x = 0,5 à 6,8 mm), broches 1 à 14 vers les entrées capteur, 15 à 26 vers le bus I2C, 27 à 40 vers les optocoupleurs.
- Zone antenne interdite au cuivre sur les 4 couches : x 0 à 7, y 43,5 à 68 mm (repère du placement). Plus de fente fraisée.
- J141 au bord gauche sous la zone antenne (y 70,3 à 79,7), U142 juste derrière, R143 / R144 à côté.
- U141, D101, C144 à C146, R142, SW141 et SW142 dans la zone libérée par la DevKit (x 27 à 56).
- Inner2 : nouvelle plage **3V3_MCU** (x 9 à 50, y 45,5 à 72,5) ; la plage +3V3 commence à x = 52 au-dessus du couloir de bus ; la bande gauche du +5V disparaît et le tronçon sous la barrière est prolongé jusqu'à D101 (x = 28).

## Points à vérifier

- Orientation réelle de l'empreinte EasyEDA du module (position de la broche 1 et de l'antenne) avant de figer la rotation.
- Distance entre l'antenne et le blindage de l'USB-C (≈ 7 mm) : acceptable, à surveiller si la portée Wi-Fi est faible.
- Lignes USB_DP / USB_DN : courtes, de même longueur, sans via, au-dessus du plan GND d'Inner1.
- La zone x 56 à 88 de l'ancienne antenne est maintenant libre : la carte pourrait rétrécir dans une version suivante.
