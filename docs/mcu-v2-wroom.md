# TriggerFlow v2 — Feuille MCU : module ESP32-S3-WROOM-1-N16R8

Branche `v2-wroom`. La v1 (DevKit sur barrettes) reste sur `main` et l'étiquette `v1.0`.

## Fichiers du schéma

- `kicad/mcu_v2/mcu_wroom.kicad_sch` : feuille KiCad (A4) générée par `generateur/build_mcu.py`, aperçu `kicad/mcu_v2/apercu.png`.
- `kicad/easyeda/mcu_wroom.kicad_sch` : même feuille sans champs cachés, à importer dans EasyEDA Pro (copie « TriggerFlow v2 WROOM »).
- Netlist de la feuille vérifiée par calcul contre `pcb/netlist_v2_wroom.json` : 37 nets (avec les tirages I2C R79 / R80), aucun écart (la languette de U26 n'est pas une broche séparée du symbole KiCad ; elle est reliée à VO dans l'empreinte). Non ouverte dans KiCad 10 ni dans EasyEDA : ERC à faire.
- Les signaux vers les autres feuilles sont des étiquettes de net (TLV_OUT_1…, SPI_SCK, I2C_SDA, GPIO_VALVE_1…, FLASH_1_CMD…), comme dans les feuilles servo et relais.

## Numérotation EasyEDA du 10/10/2026

Le schéma EasyEDA « TriggerFlow v2 WROOM » a été renuméroté (annotation automatique). C'est cette numérotation qui fait foi : `pcb/netlist_v2_wroom.json` est l'export EasyEDA du 10/10 (`pcb/netlist_v2_easyeda_2026-10-10.tel`), et le placement, la BOM-netlist, le README et la checklist l'utilisent. Correspondance vérifiée net par net (tous les nets identiques après renommage, hors changements volontaires ci-dessous). La feuille KiCad générée (`kicad/mcu_v2/`) garde l'ancienne numérotation.

Changements volontaires faits dans EasyEDA : canal du USBLC6 inversé (D+ sur les broches 1/6, D− sur 3/4, équivalent) avec les nets USB_C_DP / USB_C_DN côté connecteur ; pastilles TP141/TP142 remplacées par la barrette U85 (1 GND, 2 TXD0, 3 RXD0) ; étiquettes V5_CAPT_1..6 entre PTC et RJ45.

**À corriger dans le schéma : supprimer C87** (1 µF entre IO0_BOOT et GND) : il retarde IO0 autant que EN et peut faire démarrer le module en mode programmation.

| Ancienne réf. | Nouvelle réf. |
|---|---|
| C101 | C73 |
| CN101 | CN11 |
| C102 | C74 |
| C103 | C75 |
| C104 | C76 |
| C105 | C77 |
| C111 | C39 |
| C112 | C40 |
| C113 | C48 |
| C114 | C49 |
| C115 | C50 |
| C116 | C58 |
| C117 | C59 |
| C118 | C60 |
| C119 | C68 |
| C120 | C69 |
| C121 | C70 |
| C122 | C18 |
| C123 | C19 |
| C124 | C20 |
| C125 | C28 |
| C126 | C29 |
| C127 | C30 |
| C128 | C38 |
| C141 | C86 |
| C142 | C10 |
| C143 | C78 |
| C144 | C79 |
| C145 | C80 |
| C146 | C85 |
| D101 | D10 |
| D111 | D17 |
| D112 | D18 |
| D121 | D14 |
| D122 | D15 |
| D123 | D16 |
| D141 | D19 |
| F111 | F12 |
| J111 | J12 |
| J121 | J13 |
| J122 | J14 |
| J141 | J10 |
| L111 | L12 |
| L121 | L13 |
| Q111 | Q12 |
| Q121 | Q13 |
| R105 | R70 |
| R106 | R77 |
| R107 | R78 |
| R108 | R79 |
| R109 | R80 |
| R111 | R50 |
| R112 | R59 |
| R113 | R60 |
| R114 | R69 |
| R121 | R19 |
| RELAY121 | RELAY13 |
| R122 | R20 |
| R123 | R29 |
| R124 | R30 |
| R125 | R39 |
| R126 | R40 |
| R127 | R49 |
| R141 | R106 |
| R142 | R107 |
| R143 | R105 |
| R144 | R10 |
| SW141 | SW10 |
| SW142 | SW11 |
| U101 | U19 |
| U102 | U20 |
| U103 | U23 |
| U104 | U24 |
| U105 | U10 |
| U111 | U15 |
| U112 | U16 |
| U113 | U17 |
| U114 | U18 |
| U121 | U13 |
| U122 | U14 |
| U141 | U26 |
| U142 | U25 |

## Principe

La DevKit est remplacée par le module qu'elle portait, **ESP32-S3-WROOM-1-N16R8**, soudé directement sur la carte. Chaque signal garde **le même GPIO** qu'en v1 : le firmware ne change pas. Seuls les numéros de broches du composant U10 changent.

Ce que la DevKit fournissait et qu'il faut maintenant ajouter : le 3,3 V du module, le reset, le bouton BOOT et le port USB.

Garder la version **N16R8** : dans les versions « …V » (R8V, R16V), GPIO47 et GPIO48 (vannes 5 et 6) passent en 1,8 V.

## Broches de U10 (module WROOM-1) — GPIO réaffectés pour le placement

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
| 36 / 37 | haut | RXD0 / TXD0 | RXD0 / TXD0 (barrette U85) | — |
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
| 5V_MCU | D10.1 (cathode, anode sur +5V), D19.1 (cathode, anode sur VBUS), U26.3 (VIN), C85.1 |
| VBUS | J10 A4, A9, B4, B9 ; D19.2 ; U25.5 |
| 3V3_MCU | U26.2 et languette (VOUT), U10.2, C10.1, C78.1, C79.1, C80.1, R106.1, R107.1 |
| EN | U10.3, R106.2, C86.1, SW10 (côté 1-2) |
| IO0_BOOT | U10.27, R107.2, SW11 (côté 1-2) |
| USB_DN | J10 A7 et B7, U25.1 et U25.6, U10.13 (IO19) |
| USB_DP | J10 A6 et B6, U25.3 et U25.4, U10.14 (IO20) |
| CC1 / CC2 | J10.A5 – R105.1 / J10.B5 – R10.1 |
| TXD0 / RXD0 | U10.37 – U85.2 / U10.36 – U85.3 (barrette dans la zone libre à droite des boutons, liaisons en couche Bottom) |
| GND | U10.1, 40, 41 ; U26.1 ; U25.2 ; J10 A1, A12, B1, B12 et blindage ; R105.2, R10.2 ; C86 à C85 (.2) ; SW10 et SW11 (côté 3-4) |

J10 SBU1 / SBU2 : non connectées. Le net V5_DEVKIT de la v1 devient 5V_MCU.

## Choix de conception

- **3V3_MCU dédié** : U26 AMS1117-3.3 (même pièce que U16) alimenté par 5V_MCU, séparé du +3V3 de l'électronique analogique. Le module tire jusqu'à 355 mA en émission Wi-Fi d'après la fiche JLC ; dissipation de U26 ≈ (4,55 − 3,3) × 0,36 ≈ 0,45 W en pointe, à dissiper par la languette (plage 3V3_MCU d'Inner2).
- **Deux sources pour 5V_MCU, par diodes SS14** : le +5V de la carte (D10, comme en v1) et le VBUS de l'USB (D19). Le module peut ainsi être programmé par l'USB sans le bloc 12 V, et l'USB n'alimente jamais le reste de la carte. Après la diode, 5V_MCU ≈ 4,55 V : la marge de chute de l'AMS1117 (≈ 1,1 V à pleine charge) reste juste. Si le Wi-Fi se montre instable, remplacer D10 et D19 par des diodes à plus faible tension de seuil ou passer à un régulateur à faible chute.
- **Découplage** : C10 (10 µF) + C78 (100 nF) collés à la broche 2 ; C79 + C80 (2 × 10 µF) en sortie de U26 ; C85 (10 µF) en entrée.
- **EN** : R106 10 kΩ vers 3V3_MCU + C86 1 µF vers GND (valeurs recommandées par Espressif) ; SW10 RESET vers GND.
- **IO0** : R107 10 kΩ vers 3V3_MCU ; SW11 BOOT vers GND. Maintenir BOOT puis appuyer sur RESET force le mode téléchargement.
- **USB** : un seul port USB-C, sur l'USB natif (IO19 / IO20). La v1 en avait deux (pont série + USB natif). La programmation passe par l'USB-Serial/JTAG intégré. Si le firmware utilise l'USB natif pour le contrôle PC, on reprogramme avec BOOT + RESET, et la console série reste accessible sur la barrette U85 (GND, TX, RX) avec un adaptateur 3,3 V. R105 / R10 (5,1 kΩ) déclarent la carte comme périphérique USB-C. U25 protège les deux lignes et VBUS contre les décharges.
- **Supprimés** : la DevKit et ses deux barrettes femelles. D10 reste (même rôle : +5V vers l'alimentation du microcontrôleur).

## BOM de la feuille MCU v2

| Réf. | Pièce | Boîtier | LCSC | Catégorie JLC |
|---|---|---|---|---|
| U10 | ESP32-S3-WROOM-1-N16R8 | SMD 25,5 × 18 mm | C2913202 | Extended (à confirmer sur la fiche) |
| U26 | AMS1117-3.3 | SOT-223 | C6186 | (déjà dans la BOM v1, U16) |
| U25 | USBLC6-2SC6 | SOT-23-6 | C7519 | à vérifier |
| J10 | HRO TYPE-C-31-M-12 (16 broches) | SMD | C165948 | Extended |
| SW10, SW11 | TS-1187A-B-A-B (5,1 × 5,1 mm) | SMD | C318884 | Basic |
| D10, D19 | SS14 | SMA | C2480 | (déjà dans la BOM v1) |
| R106, R107 | 10 kΩ | 0603 | C25804 | (déjà dans la BOM v1) |
| R105, R10 | 5,1 kΩ | 0603 | C23186 | Basic |
| C86 | 1 µF | 0603 | C5673 | (déjà dans la BOM v1) |
| C78 | 100 nF | 0603 | C14663 | (déjà dans la BOM v1) |
| C10, C79, C80, C85 | 10 µF | 0805 | C15850 | (déjà dans la BOM v1) |
| U85 | barrette mâle 1 × 3, pas 2,54 mm (1 GND, 2 TXD0, 3 RXD0) | traversant | C5383112 | non montée (Add into BOM : No) |

Les numéros LCSC de U10, U25, J10, SW10/142 et R105/144 ont été vérifiés sur les fiches JLC / LCSC le 06/10/2026. Les autres sont repris de la BOM v1 exportée d'EasyEDA.

## Implantation (voir `pcb/`)

- U10 tourné de 90° : **antenne au bord gauche** (x = 0,5 à 6,8 mm), broches 1 à 14 vers les entrées capteur, 15 à 26 vers le bus I2C, 27 à 40 vers les optocoupleurs.
- Colonne de droite reprise de l'implantation EasyEDA du 09/10 : servo, relais et entrée 12 V à l'arrière ; vannes au milieu ; 12 V → 5 V et +3V3 dans le coin avant droit, avec la boucle de découpage de U15 compacte (C40 au-dessus de l'entrée, C48-C50 et D18 collés aux broches, L12 à moins de 10 mm).
- Bus I2C (U19 à U24) hors du couloir de bus, R79 / R80 près de U19.
- Zone antenne interdite au cuivre sur les 4 couches : x 0 à 7, y 43,5 à 68 mm (repère du placement). Plus de fente fraisée.
- J10 au bord gauche sous la zone antenne (y 70,3 à 79,7), U25 juste derrière, R105 / R10 à côté.
- U26, D10, C79 à C85, R107, SW10 et SW11 dans la zone libérée par la DevKit (x 27 à 56).
- Inner2 : nouvelle plage **3V3_MCU** (x 9 à 50, y 45,5 à 72,5) ; la plage +3V3 commence à x = 52 au-dessus du couloir de bus ; la bande gauche du +5V disparaît et le tronçon sous la barrière est prolongé jusqu'à D10 (x = 28) ; la plage **+12V** descend jusqu'à l'entrée de U15 (coin avant droit) et le **+5V** occupe le bas du coin (sortie de L12, C59, U16).

## Points à vérifier

- Orientation réelle de l'empreinte EasyEDA du module (position de la broche 1 et de l'antenne) avant de figer la rotation.
- Distance entre l'antenne et le blindage de l'USB-C (≈ 7 mm) : acceptable, à surveiller si la portée Wi-Fi est faible.
- Lignes USB_DP / USB_DN : courtes, de même longueur, sans via, au-dessus du plan GND d'Inner1.
- La zone x 56 à 88 de l'ancienne antenne est maintenant libre : la carte pourrait rétrécir dans une version suivante.
