# TriggerFlow — BOM et netlists par bloc

État au **03/10/2026**. Référence : export netlist EasyEDA du 03/10/2026 (`Netlist_Schematic1_2026-10-03.tel`), vérifié net par net.
Numérotation : chiffre(s) de page + index (page 1 = voie 1 → R11, U11… ; page 9 = vannes ; page 10 = ESP32 / Bloc 8 ; page 11 = Blocs 5 et 5b). Quand une page dépasse 9 pièces d'un même type, la numérotation déborde (R100…R104 = vannes) : se fier au schéma, pas au numéro.

## État de validation

| Bloc | Contenu | État |
|---|---|---|
| 1 | 6 entrées capteur v3 (+ protection des lignes ID) | ✅ validé (6 voies) |
| 2 | 6 sorties isolées : 4 flash + appareil photo (focus, shutter) | ✅ validé (avec inverseurs et TVS) |
| 3 | 6 électrovannes + connecteurs | ✅ validé |
| 4 | Moteur pas à pas (module Pololu) | 📝 netlist prête, à saisir (page 12) |
| 5 | Alimentation 12 V → +12V / +5V / +3V3 | ✅ validé |
| 5b | Alimentation isolée VISO_3V3 / VISO_GND | ✅ validé |
| 6 | Relais ×3 | ❌ **supprimé** → prises Wi-Fi (voir fin du document) |
| 7 | PWM lumière / servo | 📝 netlist prête, à saisir (page 13) |
| 8 | Bus I2C : MCP23017, 2 × MCP4728, ADS7828, LED de statut | ✅ validé |
| 9 | Module capteur universel (carte déportée, 8 variantes) | 📝 schéma KiCad généré (`kicad/module_capteur/`) |
| 10 | Protection ESD des connecteurs | ✅ validé |
| 11 | PTC | intégrées dans chaque bloc (F11-61, F91-96, F121, F131) |
| ESP32 | Feuille U105 (YD-ESP32-S3 N16R8) | ✅ validé |

Méthode : schéma de référence → saisie EasyEDA Pro avec références LCSC → export netlist (.tel) → comparaison net par net.

---

## Feuille ESP32 — U105 (YD-ESP32-S3 N16R8, symbole ESP32-S3-DEVKITC-1)

Brochage du symbole : côté gauche 1-22 = rangée J1 ; côté droit 44 → 23 = rangée J3 (J3.k = broche 45-k).

| Broche U105 | GPIO | Net |
|---|---|---|
| 4, 5, 6, 7, 8, 9 | 4, 5, 6, 7, 15, 16 | TLV_OUT_1 … TLV_OUT_6 |
| 10 | 17 | FLASH_1_CMD |
| 11 | 18 | DAC2_LDAC (Bloc 8) |
| 12 / 15 | 8 / 9 | I2C_SDA / I2C_SCL |
| 16 | 10 | GPIO_VALVE_3 |
| 17 / 18 | 11 / 12 | SPI_MOSI / SPI_SCK |
| 19 | 13 | STEP |
| 20 | 14 | GPIO_PWM |
| 21 | 5V | via D101 (SS14) depuis +5V |
| 22, 23, 24, 44 | G | GND |
| 41, 40 | 1, 2 | GPIO_VALVE_1, GPIO_VALVE_2 |
| 39 | 42 | SHUTTER_CMD |
| 38 | 41 | FLASH_4_CMD |
| 36 | 39 | FLASH_3_CMD |
| 35 | 38 | GPIO_VALVE_4 |
| 29 | 48 | GPIO_VALVE_5 (pastille « RGB » de la carte laissée ouverte) |
| 28 | 47 | GPIO_VALVE_6 |
| 27 | 21 | FLASH_2_CMD |
| libres | 3V3 ×2, RST, 0, 3, 45, 46, 19, 20, 43, 44, 35-37, 40 | non connectées |

| Réf | Pièce | LCSC |
|---|---|---|
| U105 | Carte YD-ESP32-S3 N16R8 sur 2 barrettes femelles 1×22 (2,54 mm) | carte achetée à part (exclue de la BOM d'assemblage) |
| D101 | SS14, anode +5V → cathode U105.21 (anti-retour USB) | C2480 |
| R108, R109 | 4,7 kΩ, pull-ups I2C_SDA / I2C_SCL vers +3V3 | C23162 |

---

## Bloc 1 — Entrée capteur v3 (×6)

Référence voie 1 (voies 2 à 6 identiques, chiffre des dizaines = n° de voie). Signal attendu : continu 0–3,3 V, ≈ 0 V au repos.

| Net | Broches (voie 1) |
|---|---|
| SENSOR_1 | J11.4, J11.5, D13 (TVS), R12 (4,7 k → JP11 → +3V3), R17 (1 M → GND), R16.1 (2,2 k) |
| CLAMP | R16.2, D12.3 (BAT54S), C12 (100 pF → GND), U12.2 (CH0) |
| MCP6S91_OUT | U12.1, R15.1 (10 k) |
| HYST_NODE | R15.2, R18.1 (680 k), U11.3 (+) |
| TLV_OUT_1 | U11.6, R18.2, U105.4 |
| THR_1 → filtre | THR_1 (DAC) → R13 (1 k) → C11 (100 nF → GND) → U11.2 (−) |
| V_SENS | J11.1, J11.2, F11 (PTC 200 mA, depuis +5V), C13 (10 µF) |
| ID (connecteur) | J11.7, J11.8, R14 (10 k → +3V3), D11 (TVS → GND), R11.1 |
| ID_ADC_1 | R11.2 (1 k), U104.1 (ADS7828) |
| CS_1 | U12.5, U101.21 |
| SPI_MOSI / SPI_SCK (communs) | U12.6 / U12.7 |
| +3V3 | U11.7, U12.8, D12 (K), JP11, R14, découplages C14-C17 |
| GND | U11.4, U11.8 (SHDN), U12.3 (VREF du PGA), U12.4, D12 (A), D11, D13, R17, J11.3/.6/.9/.10 |
| non connectées | U11.1, U11.5 |

| Réf (voie 1) | Valeur / pièce | Boîtier | LCSC |
|---|---|---|---|
| U11 | TLV3501AID | SOIC-8 | C43484 |
| U12 | MCP6S91 | MSOP-8 | C627647 |
| D12 | BAT54S | SOT-23 | C545549 |
| D11, D13 | PESD5V0S1BB (TVS 5 V bidir.) | SOD-523 | C97640 |
| R11, R13 | 1 kΩ | 0603 | C21190 |
| R12 | 4,7 kΩ | 0603 | C23162 |
| R14, R15 | 10 kΩ | 0603 | C25804 |
| R16 | 2,2 kΩ | 0603 | C4190 |
| R17 | 1 MΩ | 0603 | C22935 |
| R18 | 680 kΩ | 0603 | C25822 |
| C11, C14, C15 | 100 nF | 0603 | C14663 |
| C12 | 100 pF C0G | 0603 | C71664 |
| C13 | 10 µF 25 V | 0805 | C15850 |
| C16, C17 | 1 µF | 0603 | C5673 |
| F11 | PTC 200 mA | 1206 | C20984 |
| JP11 | 0 Ω (monté = tirage actif) | 0603 | C21189 |
| J11 | RJ45 HanXia HX-RJ45 90 5631-1x1 (10 br.) | THT | C25168869 |

---

## Bloc 2 — Sorties isolées flash / appareil photo

Chaîne par sortie : `*_CMD` (ESP32) → 180 Ω → LED de l'opto HCPL-063L → sortie opto (pull-up 10 k VISO_3V3) → inverseur 74LVC2G04 → grille 2N7002 (pull-down 100 k) → drain sur le RJ45. Logique directe : CMD haut = sortie active ; CMD bas ou haute impédance (démarrage, plantage) = sortie bloquée.

| Sortie | Commande | Opto | Pull-up | Inverseur | Pull-down | MOSFET | TVS | Connecteur |
|---|---|---|---|---|---|---|---|---|
| FOCUS | FOCUS_CMD (MCP23017 GPA6) → R73 | U71 (1→7) | R71 | U72 (1A→1Y) | R72 | Q71 | D71 | J71.3 |
| SHUTTER | SHUTTER_CMD (GPIO42) → R74 | U71 (4→6) | R76 | U72 (2A→2Y) | R75 | Q72 | D72 | J71.4 |
| FLASH_1 | FLASH_1_CMD → R83 | U81 (1→7) | R81 | U82 (1A→1Y) | R82 | Q81 | D81 | J81.4 |
| FLASH_2 | FLASH_2_CMD → R84 | U81 (4→6) | R86 | U82 (2A→2Y) | R85 | Q82 | D82 | J82.4 |
| FLASH_3 | FLASH_3_CMD → R89 | U83 (1→7) | R87 | U84 (1A→1Y) | R88 | Q83 | D83 | J83.4 |
| FLASH_4 | FLASH_4_CMD → R90 | U83 (4→6) | R92 | U84 (2A→2Y) | R91 | Q84 | D84 | J84.4 |

Brochages : HCPL-063L SO-8 : 1 A1, 2 K1, 3 K2, 4 A2, 5 GND sortie, 6 VO2, 7 VO1, 8 VCC. 74LVC2G04 SOT-23-6 : 1 1A, 2 GND, 3 2A, 4 2Y, 5 VCC, 6 1Y.

| Net | Broches |
|---|---|
| GND (côté ESP32) | U71.2, U71.3, U81.2, U81.3, U83.2, U83.3 |
| VISO_3V3 | U71.8, U81.8, U83.8, U72.5, U82.5, U84.5, R71, R76, R81, R86, R87, R92, C71-C72, C81-C84 (.1), U114 (Bloc 5b) |
| VISO_GND | U71.5, U81.5, U83.5, U72.2, U82.2, U84.2, sources Q71-Q84, R72/R75/R82/R85/R88/R91, anodes D71-D84, J71.5, J71.6, J81.5 … J84.5, U113.3, U114.1 |

**Règles** : aucun composant entre GND et VISO_GND ; TVS cathode côté sortie, anode VISO_GND ; RJ45 de sortie : broches 1-2, 7-10 (et 3, 6 sur les flashs) non connectées, blindage non connecté.

| Réf | Pièce | Qté | LCSC |
|---|---|---|---|
| U71, U81, U83 | Broadcom HCPL-063L-500E (2 voies, 3,3 V, SO-8) | 3 | C188704 |
| U72, U82, U84 | TI SN74LVC2G04DBVR (SOT-23-6) | 3 | C10428 |
| Q71, Q72, Q81-Q84 | 2N7002 (SOT-23) | 6 | C8545 |
| R73, R74, R83, R84, R89, R90 | 180 Ω 0603 | 6 | C22828 |
| R71, R76, R81, R86, R87, R92 | 10 kΩ 0603 | 6 | C25804 |
| R72, R75, R82, R85, R88, R91 | 100 kΩ 0603 | 6 | C25803 |
| C71, C72, C81-C84 | 100 nF 0603 (VISO_3V3 / VISO_GND) | 6 | C14663 |
| D71, D72, D81-D84 | SMF24A (TVS 24 V, SOD-123FL) | 6 | C169430 |
| J71, J81-J84 | RJ45 HanXia 10 broches | 5 | C25168869 |

---

## Bloc 3 — Électrovannes (×6)

| Net (canal n) | Broches |
|---|---|
| GPIO_VALVE_n | résistance de grille 220 Ω (R93, R94, R95, R99, R100, R101) |
| GATE_n | Q9n.1, résistance 220 Ω, pull-down 10 kΩ (R96, R97, R98, R102, R103, R104) → GND |
| VALVE_SW_n | Q9n.3 (drain), D9n.2 (anode SS14), CN9n.2 (−) |
| VALVE_PWR_n | D9n.1 (cathode), F9n.2, CN9n.1 (+) |
| +12V | F91.1 … F96.1 |
| GND | Q9n.2 (source), pull-downs |

| Réf | Pièce | LCSC |
|---|---|---|
| Q91-Q96 | AO3400A (SOT-23) | C20917 |
| D91-D96 | SS14 (SMA) | C2480 |
| F91-F96 | Bourns MF-MSMF110/24X-2 (1,1 A / 24 V, 1812) | C210835 |
| 220 Ω ×6 | 0603 | C22962 |
| 10 kΩ ×6 | 0603 | C25804 |
| CN91-CN96 | connecteur 2 points HX25003-2A (pas 2,5 mm) | — |

Une sortie vanne libre peut piloter une charge 12 V DC (ruban LED, ventilateur, pompe, module relais 12 V) : 12 V, 1,1 A max, PWM possible, non isolée.

---

## Bloc 4 — Moteur pas à pas (page 12, à saisir)

Module Pololu (A4988 / DRV8825 / TMC2209) sur **deux barrettes 1×8 écartées de 12,7 mm**.

| Net | Broches |
|---|---|
| STEP_EN | J121.1 (EN), R121 (10 kΩ → +3V3), U101.2 (MCP23017 GPB1) |
| MS1 / MS2 / MS3 | J121.2 / .3 / .4 → JP121 / JP122 / JP123 → +3V3 |
| RST_SLP | J121.5 (RST) → JP124 → J121.6 (SLP) |
| STEP | J121.7, R122 (10 kΩ → GND), U105.19 (GPIO13) |
| DIR | J121.8, U101.1 (GPB0) |
| VMOT | J122.1, C121+ (100 µF), C122 (100 nF), F121.2 |
| +12V | F121.1 |
| MOT_2B / 2A / 1A / 1B | J122.3 / .4 / .5 / .6 → J123.1 … J123.4 |
| +3V3 | J122.7 (VDD), C123 (100 nF) |
| GND | J122.2, J122.8, C121−, C122, C123, R122 |

| Module | JP121 | JP122 | JP123 | JP124 | Résultat |
|---|---|---|---|---|---|
| TMC2209 | fermé | fermé | ouvert | **ouvert** | 1/16, stealthChop |
| A4988 | fermé | fermé | fermé | fermé | 1/16 |
| DRV8825 | ouvert | ouvert | fermé | fermé | 1/16 |

| Réf | Pièce | LCSC |
|---|---|---|
| J121, J122 | barrette femelle 1×8, 2,54 mm (BOOMELE) | C27438 |
| F121 | PTC 2 A / 16 V 1812 (SMD1812P200TF/16) | C545213 (alt. C20812) |
| C121 | 100 µF 35 V électrolytique CMS | C3339 (à vérifier) |
| C122, C123 | 100 nF 0603 | C14663 |
| R121, R122 | 10 kΩ 0603 | C25804 |
| JP121-JP124 | ponts de soudure 2 plots | — |
| J123 | bornier 4 points 5,08 mm (vers GX12 4 broches) | à choisir |

---

## Bloc 5 — Alimentation (validé)

Bloc secteur **12 V, 5 A minimum**.

| Net | Broches |
|---|---|
| VIN_RAW | J111.1, F111.1 |
| VIN_F | F111.2, Q111.5-8 (drain) |
| +12V | Q111.1-3 (source), R111, D111 (cathode), C112 (470 µF), 2 × 10 µF, 100 nF, U111.1 (VIN), F91-F96, (VMOT, V_ACC) |
| Q111_G | Q111.4, R111 (→ +12V), R112 (→ GND) : VGS ≈ −6 V |
| BUCK_SW | U111.2, L111.1, D112 (cathode) |
| +5V | L111.2, U111.4 (FB), C117 (330 µF), 100 nF, U112.3, 10 µF, D101, F11-F61, U113.2 |
| +3V3 | U112.2 + languette (4), C111 (10 µF) |
| GND | J111.2, R112, D111, D112 (anode), U111.3, U111.5 (ON/OFF), U111.6 (languette), U112.1, condensateurs |

| Réf | Pièce | LCSC |
|---|---|---|
| J111 | bornier KF128-5.08-2P | C474952 |
| F111 | fusible 6,3 A temporisé TLC TA3VT6.3 (2410) | C3014144 |
| Q111 | AO4407A (P-MOS 30 V 12 A, SOIC-8) | C16072 |
| R111, R112 | 10 kΩ 0603 | C25804 |
| D111 | SMBJ15A (TVS 600 W) | C83846 |
| C112 | 470 µF 25 V DMBJ RVT1E471M1010 | C970707 |
| 2 × 10 µF entrée, 10 µF AMS1117 entrée/sortie | 10 µF 25 V 0805 | C15850 |
| 100 nF ×2 | 0603 | C14663 |
| U111 | LM2596S-5.0 (UMW, TO-263-5) | C347421 |
| D112 | SS54 | C22452 |
| L111 | 33 µH 4,25 A SMDRI129-330MT | C2924828 |
| C117 | 330 µF 25 V low-ESR Panasonic EEE-FK1E331P (**pas de polymère** : instabilité du LM2596) | C178543 (alt. C970701) |
| U112 | AMS1117-3.3 | C6186 |

PCB : boucle C112-U111-D112 courte ; cuivre + vias sous la languette de U111 (~3 W) ; pistes 12 V ≥ 2 mm.

---

## Bloc 5b — Alimentation isolée (validé)

B0505S-1WR3 (5 V → 5 V isolé, non régulé, charge mini 20 mA) puis AMS1117-3.3 côté isolé (HCPL-063L : 2,7–3,6 V).

| Net | Broches |
|---|---|
| +5V / GND | U113.2 (VIN) / U113.1, condensateur d'entrée 10 µF |
| VISO_5V | U113.4 (+VO), C120 (10 µF), R113, U114.3 (VIN) |
| PRELOAD | R113 – R114 (2 × 220 Ω ≈ 11 mA) |
| VISO_3V3 | U114.2 + U114.4 (languette), C121 (10 µF) |
| VISO_GND | U113.3 (0V), C120, R114, U114.1, C121 |

| Réf | Pièce | LCSC |
|---|---|---|
| U113 | B0505S-1WR3 (SIP-4 : 1 GND, 2 VIN, 3 0V, 4 +VO) | C7465178 (EVISUN, alt. HI-LINK C5183119 ; Mornsun C131038 indisponible) |
| U114 | AMS1117-3.3 | C6186 |
| 3 × 10 µF | 0805 25 V | C15850 |
| R113, R114 | 220 Ω 0603 | C22962 |

PCB : bande sans cuivre (~2 mm) sous U113 entre les broches 1-2 et 3-4 ; plan VISO_GND séparé pour tout le côté isolé.

---

## Bloc 6 — Relais : supprimé

Remplacé par des **prises Wi-Fi** pour les appareils secteur (éclairage, petit compresseur…) et, si besoin, par les sorties vannes libres (charges 12 V DC ou module relais 12 V externe). Voir [docs/sorties-wifi.md](docs/sorties-wifi.md). Les lignes MCP23017 GPB2-GPB4 (ex-RELAY_1-3) restent en réserve.

---

## Bloc 7 — PWM lumière / servo (page 13, à saisir)

| Net | Broches |
|---|---|
| GPIO_PWM | U105.20 (GPIO14), R131.1 (220 Ω), U131.2 (A) |
| PWM_GATE | R131.2, Q131.1, R132 (10 kΩ → GND) |
| LIGHT_SW | Q131.3, D131 (anode), JP131 côté A |
| SERVO_Y | U131.4, R133.1 (220 Ω) |
| SERVO_SIG | R133.2, JP131 côté B |
| PWM_OUT | JP131 centre, J131.4, J131.5, D132 (cathode) |
| V_ACC_SEL | JP132 centre, F131.1 |
| V_ACC | F131.2, D131 (cathode), J131.1, J131.2 |
| +12V / +5V | JP132 côté A / côté B |
| +5V | U131.5, C131 (100 nF) |
| GND | Q131.2, U131.1 (OE), U131.3, R132, C131, D132 (anode), J131.3, J131.6 |
| libres | J131.7-10 |

Modes : lumière = JP131 sur A, JP132 sur +12V (ou +5V) ; servo = JP131 sur B, JP132 sur +5V. **Jamais JP132 sur +12V en mode servo** (sérigraphie).

| Réf | Pièce | LCSC |
|---|---|---|
| Q131 | AO3400A | C20917 |
| U131 | SN74AHCT1G125DBVR (1 OE, 2 A, 3 GND, 4 Y, 5 VCC) | C7484 |
| D131 | SS34 | C8678 (à vérifier) |
| D132 | SMF15A (TVS 15 V) | C123802 |
| F131 | PTC 1,1 A / 16 V Littelfuse 1812L110/16DR | C142746 |
| R131, R133 | 220 Ω 0603 | C22962 |
| R132 | 10 kΩ 0603 | C25804 |
| C131 | 100 nF 0603 | C14663 |
| J131 | RJ45 HanXia 10 broches | C25168869 |
| JP131, JP132 | ponts de soudure 3 plots | — |

---

## Bloc 8 — Bus I2C (validé)

| Composant | Adresse | Rôle |
|---|---|---|
| U101 MCP23017 (SSOP-28) | 0x20 (A0-A2 à GND) | GPA0-5 = CS_1-6, GPA6 = FOCUS_CMD, GPB0 = DIR, GPB1 = STEP_EN, GPB5 = LED de statut (R105 1 kΩ → CN101), RESET via R107 (10 k → +3V3) ; GPA7, GPB2-4, GPB6-7 libres |
| U102 MCP4728 | 0x60 | LDAC à GND ; VOUTA-D (6-9) = THR_1-4 |
| U103 MCP4728 | 0x61 (reprogrammée au 1er démarrage) | LDAC = DAC2_LDAC (GPIO18) + R106 10 k → GND ; VOUTA/B = THR_5/6 |
| U104 ADS7828 (TSSOP-16) | 0x48 (A0, A1 à GND) | CH0-5 = ID_ADC_1-6, CH6-7 et COM à GND, REF : C105 1 µF (référence interne 2,5 V) |

MCP4728 MSOP-10 : 1 VDD, 2 SCL, 3 SDA, 4 LDAC, 5 RDY, 6-9 VOUTA-D, 10 VSS (attention : symbole EasyEDA numéroté en miroir côté droit). Découplage C101-C104 (100 nF).

| Réf | Pièce | LCSC |
|---|---|---|
| U101 | MCP23017-E/SS | C506653 |
| U102, U103 | MCP4728-E/UN | C108207 |
| U104 | ADS7828E/250 | C701648 |
| R105 | 1 kΩ | C21190 |
| R106, R107 | 10 kΩ | C25804 |
| C101-C104 | 100 nF | C14663 |
| C105 | 1 µF | C5673 |
| CN101 | connecteur 2 points (LED de statut déportée, anode broche 1) | — |

---

## Bloc 9 — Module capteur universel (carte déportée)

Un seul PCB, 8 variantes par options de montage ; code ID = résistance R1. Schéma KiCad : `kicad/module_capteur/`.

| Code | R1 | Variante | Montage spécifique |
|---|---|---|---|
| 1 | 0 Ω | Contact sec | CN1, R14 1 k, R15 2,2 k, C11, JP5 |
| 2 | 220 Ω | Laser | D1 BPW34, U1, R5/R6/C4 (VBIAS), JP1, R7 = 10 k, C6 = 10 pF, JP3 |
| 3 | 510 Ω | Barrière IR (récepteur) | idem laser, R7 = 100 k |
| 4 | 910 Ω | Lumière ambiante | idem laser, R7 = 1 M |
| 5 | 1,5 kΩ | Son (micro électret) | M1, R10, C8, R9, VMID, JP2, U1 (gain 101), enveloppe U1B/D3/C10/R13, JP4 |
| 6 | 2,2 kΩ | Piézo | idem son avec CN2, R11, D2 (gain 11) |
| 7 | 3 kΩ | Mouvement PIR | module AM312 sur H1, R16 = 0 Ω, R15, C11, JP5 |
| 8 | 4,3 kΩ | Émetteur IR | D4 IR333C + R17 100 Ω (pas de sortie) |
| 9-12 | 6,2 k … 18 kΩ | réserve | — |

Pièces principales : TLV9062IDR C398355, BPW34 C85128, micro GMI6027P C529943, IR333C-A C5130, BAT54S C545549, RJ45 C25168869.

---

## Bloc 10 — Protection ESD (validé)

| Lignes | Protection |
|---|---|
| SENSOR (×6) | PESD5V0S1BB + 2,2 kΩ + BAT54S (Bloc 1) |
| ID (×6) | PESD5V0S1BB (D11 … D61) + 1 kΩ série vers l'ADC (R11 … R61) |
| V_SENS | PTC + 10 µF (absorbe une décharge 8 kV / 150 pF) |
| FOCUS, SHUTTER, FLASH_1-4 | SMF24A vers VISO_GND (D71, D72, D81-D84) |
| PWM_OUT | SMF15A vers GND (Bloc 7) |
| Vannes, moteur | diodes de roue libre / protections internes des modules |
| Entrée 12 V | SMBJ15A (Bloc 5) |

Pas de condensateur entre VISO_GND et GND (isolation conservée).

---

## Sorties Wi-Fi (remplacent le Bloc 6)

Prises connectées en réseau local, commandées par l'ESP32 (HTTP / MQTT, sans cloud) : éclairage, petit compresseur (prise ≥ 10 A), ventilateur… Non critiques (50–500 ms), envoyées avant ou après une séquence de déclenchement. Détails : [docs/sorties-wifi.md](docs/sorties-wifi.md).
