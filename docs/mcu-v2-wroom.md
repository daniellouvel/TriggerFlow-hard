# TriggerFlow v2 — Feuille MCU : module ESP32-S3-WROOM-1-N16R8

Branche `v2-wroom`. La v1 (DevKit sur barrettes) reste sur `main` et l'étiquette `v1.0`.

## Principe

La DevKit est remplacée par le module qu'elle portait, **ESP32-S3-WROOM-1-N16R8**, soudé directement sur la carte. Chaque signal garde **le même GPIO** qu'en v1 : le firmware ne change pas. Seuls les numéros de broches du composant U105 changent.

Ce que la DevKit fournissait et qu'il faut maintenant ajouter : le 3,3 V du module, le reset, le bouton BOOT et le port USB.

Garder la version **N16R8** : dans les versions « …V » (R8V, R16V), GPIO47 et GPIO48 (vannes 5 et 6) passent en 1,8 V.

## Broches de U105 (module WROOM-1) — GPIO réaffectés pour le placement

Les GPIO de la v1 ont été **réaffectés** (accord du 09/10 : sans impact pour le firmware, qui n'utilise qu'une table de broches par version). Le module étant tourné (antenne à gauche), chaque signal sort du côté qui fait face à sa destination :

- **bas** (broches 1-14, vers les entrées capteur) : TLV_OUT, SPI, USB ;
- **droite** (broches 15-26, vers le bus I2C, le servo et les vannes) : I2C, DAC2_LDAC, SERVO_PWM, vannes 3 à 6 ;
- **haut** (broches 27-40, vers les optocoupleurs) : SHUTTER, FLASH_1 à 4, console UART, vannes 1 et 2.

Sur chaque côté, l'ordre des broches suit l'ordre des destinations pour que les pistes ne se croisent pas (en haut : SHUTTER vers U71 la plus proche, puis FLASH_1/2 vers U81, FLASH_3/4 vers U83, vannes 1/2 en dernier par la bande libre le long de la barrière).

| Broche module | Côté | GPIO v2 | Net | GPIO v1 |
|---|---|---|---|---|
| 1, 40, 41 (pastille) | — | — | GND | — |
| 2 | bas | — | 3V3_MCU | — |
| 3 | bas | EN | EN | — |
| 4, 5, 6, 7, 8, 9 | bas | 4, 5, 6, 7, 15, 16 | TLV_OUT_1 … TLV_OUT_6 | inchangé |
| 10 | bas | 17 | SPI_SCK | 12 |
| 11 | bas | 18 | SPI_MOSI | 11 |
| 12 | bas | 8 | libre (réserve) | I2C_SDA |
| 13 / 14 | bas | 19 / 20 | USB_DN / USB_DP | — |
| 15, 16 | droite | 3, 46 | non connectées (démarrage) | — |
| 17 | droite | 9 | libre (réserve) | I2C_SCL |
| 18 | droite | 10 | DAC2_LDAC (ancien net GPIO18) | 18 |
| 19 / 20 | droite | 11 / 12 | I2C_SCL / I2C_SDA | 9 / 8 |
| 21, 22, 23, 24 | droite | 13, 14, 21, 47 | GPIO_VALVE_6, 5, 4, 3 | 47, 48, 38, 10 |
| 25 | droite | 48 | SERVO_PWM | 13 |
| 26 | droite | 45 | non connectée (démarrage) | — |
| 27 | haut | 0 | IO0_BOOT | — |
| 28, 29, 30 | haut | 35, 36, 37 | non connectées (PSRAM octale) | — |
| 31 | haut | 38 | SHUTTER_CMD | 42 |
| 32, 33 | haut | 39, 40 | FLASH_1_CMD, FLASH_2_CMD | 17, 21 |
| 34, 35 | haut | 41, 42 | FLASH_3_CMD, FLASH_4_CMD | 39, 41 |
| 36 / 37 | haut | RXD0 / TXD0 | RXD0 / TXD0 (TP142 / TP141, à gauche) | — |
| 38 / 39 | haut | 2 / 1 | GPIO_VALVE_1 / GPIO_VALVE_2 | 1 / 2 |

Table de broches à reprendre dans le firmware v2 :

```c
// TriggerFlow v2 (module WROOM-1) — à comparer avec la table v1 (DevKit)
#define PIN_TLV_OUT_1 4   #define PIN_TLV_OUT_2 5   #define PIN_TLV_OUT_3 6
#define PIN_TLV_OUT_4 7   #define PIN_TLV_OUT_5 15  #define PIN_TLV_OUT_6 16
#define PIN_SPI_SCK   17  #define PIN_SPI_MOSI  18
#define PIN_I2C_SDA   12  #define PIN_I2C_SCL   11  #define PIN_DAC2_LDAC 10
#define PIN_SERVO_PWM 48
#define PIN_VALVE_1 2  #define PIN_VALVE_2 1  #define PIN_VALVE_3 47
#define PIN_VALVE_4 21 #define PIN_VALVE_5 14 #define PIN_VALVE_6 13
#define PIN_SHUTTER 38 #define PIN_FLASH_1 39 #define PIN_FLASH_2 40
#define PIN_FLASH_3 41 #define PIN_FLASH_4 42
```

Broches de démarrage (IO0, IO3, IO45, IO46) : seul IO0 est utilisé, pour le bouton BOOT. IO35 à IO37 restent libres (PSRAM octale). IO39 à IO42 sont aussi les broches JTAG externes, inutilisées puisque le JTAG passe par l'USB.

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
| TXD0 / RXD0 | U105.37 – TP141 / U105.36 – TP142 (pastilles à gauche du module, liaison en couche Bottom sous les pistes des vannes 1-2) |
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
- Colonne de droite reprise de l'implantation EasyEDA du 09/10 : servo, relais et entrée 12 V à l'arrière ; vannes au milieu ; 12 V → 5 V et +3V3 dans le coin avant droit, avec la boucle de découpage de U111 compacte (C112 au-dessus de l'entrée, C113-C115 et D112 collés aux broches, L111 à moins de 10 mm).
- Bus I2C (U101 à U104) hors du couloir de bus, R108 / R109 près de U101.
- Zone antenne interdite au cuivre sur les 4 couches : x 0 à 7, y 43,5 à 68 mm (repère du placement). Plus de fente fraisée.
- J141 au bord gauche sous la zone antenne (y 70,3 à 79,7), U142 juste derrière, R143 / R144 à côté.
- U141, D101, C144 à C146, R142, SW141 et SW142 dans la zone libérée par la DevKit (x 27 à 56).
- Inner2 : nouvelle plage **3V3_MCU** (x 9 à 50, y 45,5 à 72,5) ; la plage +3V3 commence à x = 52 au-dessus du couloir de bus ; la bande gauche du +5V disparaît et le tronçon sous la barrière est prolongé jusqu'à D101 (x = 28) ; la plage **+12V** descend jusqu'à l'entrée de U111 (coin avant droit) et le **+5V** occupe le bas du coin (sortie de L111, C117, U112).

## Points à vérifier

- Orientation réelle de l'empreinte EasyEDA du module (position de la broche 1 et de l'antenne) avant de figer la rotation.
- Distance entre l'antenne et le blindage de l'USB-C (≈ 7 mm) : acceptable, à surveiller si la portée Wi-Fi est faible.
- Lignes USB_DP / USB_DN : courtes, de même longueur, sans via, au-dessus du plan GND d'Inner1.
- La zone x 56 à 88 de l'ancienne antenne est maintenant libre : la carte pourrait rétrécir dans une version suivante.
