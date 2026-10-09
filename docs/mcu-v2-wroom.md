# TriggerFlow v2 — Feuille MCU : module ESP32-S3-WROOM-1-N16R8

Branche `v2-wroom`. La v1 (DevKit sur barrettes) reste sur `main` et l'étiquette `v1.0`.

## Fichiers du schéma

- `kicad/mcu_v2/mcu_wroom.kicad_sch` : feuille KiCad (A4) générée par `generateur/build_mcu.py`, aperçu `kicad/mcu_v2/apercu.png`.
- `kicad/easyeda/mcu_wroom.kicad_sch` : même feuille sans champs cachés, à importer dans EasyEDA Pro (copie « TriggerFlow v2 WROOM »).
- Netlist de la feuille vérifiée par calcul contre `pcb/netlist_v2_wroom.json` : 37 nets (avec les tirages I2C R114 / R115), aucun écart (la languette de U104 n'est pas une broche séparée du symbole KiCad ; elle est reliée à VO dans l'empreinte). Non ouverte dans KiCad 10 ni dans EasyEDA : ERC à faire.
- Les signaux vers les autres feuilles sont des étiquettes de net (TLV_OUT_1…, SPI_SCK, I2C_SDA, GPIO_VALVE_1…, FLASH_1_CMD…), comme dans les feuilles servo et relais.

## Numérotation EasyEDA (10/10/2026)

Le schéma EasyEDA « TriggerFlow v2 WROOM » a été renuméroté par EasyEDA (deux fois le 10/10). C'est cette numérotation qui fait foi : `pcb/netlist_v2_wroom.json` est l'export EasyEDA le plus récent (`pcb/netlist_v2_easyeda_2026-10-10.tel`), et le placement, la BOM-netlist, le README et la checklist l'utilisent. Correspondance vérifiée net par net à chaque renumérotation (0 écart). La feuille KiCad générée (`kicad/mcu_v2/`) garde la numérotation d'origine.

Changements volontaires faits dans EasyEDA : canal du USBLC6 inversé (D+ sur les broches 1/6, D− sur 3/4, équivalent) avec les nets USB_C_DP / USB_C_DN côté connecteur ; pastilles de test remplacées par la barrette U103 (1 GND, 2 TXD0, 3 RXD0) ; étiquettes V5_CAPT_1..6 entre PTC et RJ45 ; C87 (1 µF sur IO0) supprimé.

Les références des blocs 1 à 3 (entrées, sorties isolées, vannes) n'ont pas changé.

| Référence d'origine (docs du 06/10) | Numérotation actuelle |
|---|---|
| C101 | C111 |
| C102 | C112 |
| C103 | C113 |
| C104 | C114 |
| C105 | C115 |
| C111 | C116 |
| C112 | C117 |
| C113 | C118 |
| C114 | C119 |
| C115 | C120 |
| C116 | C121 |
| C117 | C122 |
| C118 | C137 |
| C119 | C124 |
| C120 | C125 |
| C121 | C126 |
| C122 | C131 |
| C123 | C132 |
| C124 | C133 |
| C125 | C134 |
| C126 | C135 |
| C127 | C136 |
| C128 | C123 |
| C141 | C103 |
| C142 | C101 |
| C143 | C102 |
| C144 | C104 |
| C145 | C105 |
| C146 | C106 |
| CN101 | CN111 |
| D101 | D101 |
| D111 | D112 |
| D112 | D113 |
| D121 | D131 |
| D122 | D132 |
| D123 | D133 |
| D141 | D102 |
| F111 | F112 |
| J111 | J112 |
| J121 | J131 |
| J122 | J132 |
| J141 | J101 |
| L111 | L112 |
| L121 | L131 |
| Q111 | Q112 |
| Q121 | Q131 |
| R105 | R111 |
| R106 | R112 |
| R107 | R113 |
| R108 | R114 |
| R109 | R115 |
| R111 | R116 |
| R112 | R117 |
| R113 | R118 |
| R114 | R119 |
| R121 | R131 |
| R122 | R132 |
| R123 | R133 |
| R124 | R134 |
| R125 | R135 |
| R126 | R136 |
| R127 | R137 |
| R141 | R107 |
| R142 | R108 |
| R143 | R106 |
| R144 | R105 |
| RELAY121 | RELAY131 |
| SW141 | SW101 |
| SW142 | SW102 |
| U101 | U111 |
| U102 | U112 |
| U103 | U113 |
| U104 | U114 |
| U105 | U101 |
| U111 | U115 |
| U112 | U116 |
| U113 | U117 |
| U114 | U118 |
| U121 | U131 |
| U122 | U132 |
| U141 | U104 |
| U142 | U102 |

## Principe

La DevKit est remplacée par le module qu'elle portait, **ESP32-S3-WROOM-1-N16R8**, soudé directement sur la carte. Chaque signal garde **le même GPIO** qu'en v1 : le firmware ne change pas. Seuls les numéros de broches du composant U101 changent.

Ce que la DevKit fournissait et qu'il faut maintenant ajouter : le 3,3 V du module, le reset, le bouton BOOT et le port USB.

Garder la version **N16R8** : dans les versions « …V » (R8V, R16V), GPIO47 et GPIO48 (vannes 5 et 6) passent en 1,8 V.

## Broches de U101 (module WROOM-1) — GPIO réaffectés pour le placement

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
| 36 / 37 | haut | RXD0 / TXD0 | RXD0 / TXD0 (barrette U103) | — |
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
| 5V_MCU | D101.1 (cathode, anode sur +5V), D102.1 (cathode, anode sur VBUS), U104.3 (VIN), C106.1 |
| VBUS | J101 A4, A9, B4, B9 ; D102.2 ; U102.5 |
| 3V3_MCU | U104.2 et languette (VOUT), U101.2, C101.1, C102.1, C104.1, C105.1, R107.1, R108.1 |
| EN | U101.3, R107.2, C103.1, SW101 (côté 1-2) |
| IO0_BOOT | U101.27, R108.2, SW102 (côté 1-2) |
| USB_DN | J101 A7 et B7, U102.1 et U102.6, U101.13 (IO19) |
| USB_DP | J101 A6 et B6, U102.3 et U102.4, U101.14 (IO20) |
| CC1 / CC2 | J101.A5 – R106.1 / J101.B5 – R105.1 |
| TXD0 / RXD0 | U101.37 – U103.2 / U101.36 – U103.3 (barrette dans la zone libre à droite des boutons, liaisons en couche Bottom) |
| GND | U101.1, 40, 41 ; U104.1 ; U102.2 ; J101 A1, A12, B1, B12 et blindage ; R106.2, R105.2 ; C103 à C106 (.2) ; SW101 et SW102 (côté 3-4) |

J101 SBU1 / SBU2 : non connectées. Le net V5_DEVKIT de la v1 devient 5V_MCU.

## Choix de conception

- **3V3_MCU dédié** : U104 AMS1117-3.3 (même pièce que U116) alimenté par 5V_MCU, séparé du +3V3 de l'électronique analogique. Le module tire jusqu'à 355 mA en émission Wi-Fi d'après la fiche JLC ; dissipation de U104 ≈ (4,55 − 3,3) × 0,36 ≈ 0,45 W en pointe, à dissiper par la languette (plage 3V3_MCU d'Inner2).
- **Deux sources pour 5V_MCU, par diodes SS14** : le +5V de la carte (D101, comme en v1) et le VBUS de l'USB (D102). Le module peut ainsi être programmé par l'USB sans le bloc 12 V, et l'USB n'alimente jamais le reste de la carte. Après la diode, 5V_MCU ≈ 4,55 V : la marge de chute de l'AMS1117 (≈ 1,1 V à pleine charge) reste juste. Si le Wi-Fi se montre instable, remplacer D101 et D102 par des diodes à plus faible tension de seuil ou passer à un régulateur à faible chute.
- **Découplage** : C101 (10 µF) + C102 (100 nF) collés à la broche 2 ; C104 + C105 (2 × 10 µF) en sortie de U104 ; C106 (10 µF) en entrée.
- **EN** : R107 10 kΩ vers 3V3_MCU + C103 1 µF vers GND (valeurs recommandées par Espressif) ; SW101 RESET vers GND.
- **IO0** : R108 10 kΩ vers 3V3_MCU ; SW102 BOOT vers GND. Maintenir BOOT puis appuyer sur RESET force le mode téléchargement.
- **USB** : un seul port USB-C, sur l'USB natif (IO19 / IO20). La v1 en avait deux (pont série + USB natif). La programmation passe par l'USB-Serial/JTAG intégré. Si le firmware utilise l'USB natif pour le contrôle PC, on reprogramme avec BOOT + RESET, et la console série reste accessible sur la barrette U103 (GND, TX, RX) avec un adaptateur 3,3 V. R106 / R105 (5,1 kΩ) déclarent la carte comme périphérique USB-C. U102 protège les deux lignes et VBUS contre les décharges.
- **Supprimés** : la DevKit et ses deux barrettes femelles. D101 reste (même rôle : +5V vers l'alimentation du microcontrôleur).

## BOM de la feuille MCU v2

| Réf. | Pièce | Boîtier | LCSC | Catégorie JLC |
|---|---|---|---|---|
| U101 | ESP32-S3-WROOM-1-N16R8 | SMD 25,5 × 18 mm | C2913202 | Extended (à confirmer sur la fiche) |
| U104 | AMS1117-3.3 | SOT-223 | C6186 | (déjà dans la BOM v1, U116) |
| U102 | USBLC6-2SC6 | SOT-23-6 | C7519 | à vérifier |
| J101 | HRO TYPE-C-31-M-12 (16 broches) | SMD | C165948 | Extended |
| SW101, SW102 | TS-1187A-B-A-B (5,1 × 5,1 mm) | SMD | C318884 | Basic |
| D101, D102 | SS14 | SMA | C2480 | (déjà dans la BOM v1) |
| R107, R108 | 10 kΩ | 0603 | C25804 | (déjà dans la BOM v1) |
| R106, R105 | 5,1 kΩ | 0603 | C23186 | Basic |
| C103 | 1 µF | 0603 | C5673 | (déjà dans la BOM v1) |
| C102 | 100 nF | 0603 | C14663 | (déjà dans la BOM v1) |
| C101, C104, C105, C106 | 10 µF | 0805 | C15850 | (déjà dans la BOM v1) |
| U103 | barrette mâle 1 × 3, pas 2,54 mm (1 GND, 2 TXD0, 3 RXD0) | traversant | C5383112 | non montée (Add into BOM : No) |

Les numéros LCSC de U101, U102, J101, SW101/142 et R106/144 ont été vérifiés sur les fiches JLC / LCSC le 06/10/2026. Les autres sont repris de la BOM v1 exportée d'EasyEDA.

## Implantation (voir `pcb/`)

- U101 tourné de 90° : **antenne au bord gauche** (x = 0,5 à 6,8 mm), broches 1 à 14 vers les entrées capteur, 15 à 26 vers le bus I2C, 27 à 40 vers les optocoupleurs.
- Colonne de droite reprise de l'implantation EasyEDA du 09/10 : servo, relais et entrée 12 V à l'arrière ; vannes au milieu ; 12 V → 5 V et +3V3 dans le coin avant droit, avec la boucle de découpage de U115 compacte (C117 au-dessus de l'entrée, C118-C120 et D113 collés aux broches, L112 à moins de 10 mm).
- Bus I2C (U111 à U114) hors du couloir de bus, R114 / R115 près de U111.
- Zone antenne interdite au cuivre sur les 4 couches : x 0 à 7, y 43,5 à 68 mm (repère du placement). Plus de fente fraisée.
- J101 au bord gauche sous la zone antenne (y 70,3 à 79,7), U102 juste derrière, R106 / R105 à côté.
- U104, D101, C104 à C106, R108, SW101 et SW102 dans la zone libérée par la DevKit (x 27 à 56).
- Inner2 : nouvelle plage **3V3_MCU** (x 9 à 50, y 45,5 à 72,5) ; la plage +3V3 commence à x = 52 au-dessus du couloir de bus ; la bande gauche du +5V disparaît et le tronçon sous la barrière est prolongé jusqu'à D101 (x = 28) ; la plage **+12V** descend jusqu'à l'entrée de U115 (coin avant droit) et le **+5V** occupe le bas du coin (sortie de L112, C122, U116).

## Points à vérifier

- Orientation réelle de l'empreinte EasyEDA du module (position de la broche 1 et de l'antenne) avant de figer la rotation.
- Distance entre l'antenne et le blindage de l'USB-C (≈ 7 mm) : acceptable, à surveiller si la portée Wi-Fi est faible.
- Lignes USB_DP / USB_DN : courtes, de même longueur, sans via, au-dessus du plan GND d'Inner1.
- La zone x 56 à 88 de l'ancienne antenne est maintenant libre : la carte pourrait rétrécir dans une version suivante.
