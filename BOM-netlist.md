# TriggerFlow — BOM et netlists par bloc

État au **05/10/2026**. Référence : export netlist EasyEDA du 05/10/2026 (`netlist/Netlist_Schematic1_2026-10-05.tel`), vérifié net par net, ERC EasyEDA : 0 erreur, 0 avertissement ; contrôle automatique : aucun net de voie (SENSOR, CLAMP, CS, THR, TLV_OUT, ID, GATE, VALVE…) mélangé entre deux voies.
Numérotation : chiffre(s) de page + index (page 1 = voie 1 → R11, U11… ; page 9 = vannes ; page 10 = ESP32 / Bloc 8 ; page 11 = Blocs 5 et 5b ; page 12 = sorties servo et relais). Quand une page dépasse 9 pièces d'un même type, la numérotation déborde (R100…R104 = vannes) : se fier au schéma, pas au numéro.

## État de validation

| Bloc | Contenu | État |
|---|---|---|
| 1 | 6 entrées capteur v3 (+ protection des lignes ID) | ✅ validé (6 voies) |
| 2 | 6 sorties isolées : 4 flash + appareil photo (focus, shutter) | ✅ validé (avec inverseurs et TVS) |
| 3 | 6 électrovannes + connecteurs | ✅ validé |
| 4 | Moteur pas à pas | ❌ **supprimé** (04/10) |
| 5 | Alimentation 12 V → +12V / +5V / +3V3 | ✅ validé |
| 5b | Alimentation isolée VISO_3V3 / VISO_GND | ✅ validé |
| 6 | Relais ×3 sur RJ45 | ❌ **supprimé** → prises Wi-Fi + 1 relais (Bloc 13) |
| 7 | PWM lumière / servo | ❌ **supprimé** (04/10) : lumière 12 V par une sortie vanne, servo dédié (Bloc 12) |
| 8 | Bus I2C : MCP23017, 2 × MCP4728, ADS7828, LED de statut | ✅ validé |
| 9 | Module capteur universel (carte déportée, 8 variantes) | 📝 schéma KiCad généré (`kicad/module_capteur/`) |
| 10 | Protection ESD des connecteurs | ✅ validé |
| 11 | PTC | intégrées dans chaque bloc (F11-61, F91-96) |
| 12 | Sortie servo, rail 6 V dédié | ✅ validé (page 12) |
| 13 | Sortie relais (contact sec) | ✅ validé (page 12) |
| PCB | Implantation 175 × 125 mm, 4 couches | 📝 placement v4 recalé sur la netlist du 05/10 (`pcb/`), checklist (`docs/pcb-checklist.md`) |
| ESP32 | Feuille U10 (YD-ESP32-S3 N16R8) | ✅ validé |

Méthode : schéma de référence → saisie EasyEDA Pro avec références LCSC → export netlist (.tel) → comparaison net par net.

---

## Feuille MCU v2 — U10 ESP32-S3-WROOM-1-N16R8 (branche v2-wroom)

Le module remplace la DevKit de la v1 ; chaque signal garde son GPIO. Détail complet (broches, nets, choix, BOM vérifiée) : [docs/mcu-v2-wroom.md](docs/mcu-v2-wroom.md).

GPIO réaffectés pour le placement (09/10) : chaque signal sort du côté du module qui fait face à sa destination.

| Broche module | GPIO | Net |
|---|---|---|
| 4 à 9 | 4, 5, 6, 7, 15, 16 | TLV_OUT_1 … TLV_OUT_6 |
| 10 / 11 | 17 / 18 | SPI_SCK / SPI_MOSI |
| 13 / 14 | 19 / 20 | USB_DN / USB_DP |
| 18 | 10 | DAC2_LDAC |
| 19 / 20 | 11 / 12 | I2C_SCL / I2C_SDA |
| 21, 22, 23, 24 | 13, 14, 21, 47 | GPIO_VALVE_6, 5, 4, 3 |
| 25 | 48 | SERVO_PWM |
| 27 | 0 | IO0_BOOT |
| 31 | 38 | SHUTTER_CMD |
| 32, 33, 34, 35 | 39, 40, 41, 42 | FLASH_1_CMD … FLASH_4_CMD |
| 36 / 37 | RXD0 / TXD0 | barrette U85 (broches 3 / 2) |
| 38 / 39 | 2 / 1 | GPIO_VALVE_1 / GPIO_VALVE_2 |
| 2 / 3 | — | 3V3_MCU / EN |
| 1, 40, 41 | — | GND |
| 12, 17 | 8, 9 | libres (réserve) |

| Réf | Pièce | LCSC |
|---|---|---|
| U10 | ESP32-S3-WROOM-1-N16R8 | C2913202 |
| U26 | AMS1117-3.3 (3V3_MCU) | C6186 |
| U25 | USBLC6-2SC6 | C7519 |
| J10 | USB-C HRO TYPE-C-31-M-12 | C165948 |
| SW10, SW11 | TS-1187A-B-A-B (RESET, BOOT) | C318884 |
| D10, D19 | SS14 (+5V et VBUS vers 5V_MCU) | C2480 |
| R106, R107 | 10 kΩ (EN, IO0) | C25804 |
| R105, R10 | 5,1 kΩ (CC1, CC2) | C23186 |
| C86 | 1 µF (EN) | C5673 |
| C78 | 100 nF | C14663 |
| C10, C79, C80, C85 | 10 µF 0805 | C15850 |
| R79, R80 | 4,7 kΩ, pull-ups I2C vers +3V3 (inchangés) | C23162 |

---

## Bloc 1 — Entrée capteur v3 (×6)

Référence voie 1 (voies 2 à 6 identiques, chiffre des dizaines = n° de voie). Signal attendu : continu 0–3,3 V, ≈ 0 V au repos.

| Net | Broches (voie 1) |
|---|---|
| SENSOR_1 | J11.4, J11.5, D13 (TVS), R12 (4,7 k → JP11 → +3V3), R17 (1 M → GND), R16.1 (2,2 k) |
| CLAMP | R16.2, D12.3 (BAT54S), C12 (100 pF → GND), U12.2 (CH0) |
| MCP6S91_OUT | U12.1, R15.1 (10 k) |
| HYST_NODE | R15.2, R18.1 (680 k), U11.3 (+) |
| TLV_OUT_1 | U11.6, R18.2, U10.4 |
| THR_1 → filtre | THR_1 (DAC) → R13 (1 k) → C11 (100 nF → GND) → U11.2 (−) |
| V_SENS | J11.1, J11.2, F11 (PTC 200 mA, depuis +5V), C13 (10 µF) |
| ID (connecteur) | J11.7, J11.8, R14 (10 k → +3V3), D11 (TVS → GND), R11.1 |
| ID_ADC_1 | R11.2 (1 k), U24.1 (ADS7828) |
| CS_1 | U12.5, U19.21 |
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
| VISO_3V3 | U71.8, U81.8, U83.8, U72.5, U82.5, U84.5, R71, R76, R81, R86, R87, R92, C71-C72, C81-C84 (.1), U18 (Bloc 5b) |
| VISO_GND | U71.5, U81.5, U83.5, U72.2, U82.2, U84.2, sources Q71-Q84, R72/R75/R82/R85/R88/R91, anodes D71-D84, J71.5, J71.6, J81.5 … J84.5, U17.3, U18.1 |

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

Une sortie vanne libre peut piloter une charge 12 V DC (ruban LED, ventilateur, pompe, module relais 12 V) : 12 V, 1,1 A max, PWM possible, non isolée. **Lumière dimmable** : déclarer la sortie en mode « lumière » dans le firmware (LEDC ≈ 20 kHz ; 8 voies LEDC : 6 vannes 5 kHz + servo 50 Hz + lumière). Aucun matériel supplémentaire (câble adaptateur HX25003 : broche 1 = +12V, broche 2 = −).

---

## Bloc 4 — Moteur pas à pas : supprimé (04/10)

Usage jugé trop rare pour le coût (module Pololu, GX12 4 broches, 1,5 A sur le 12 V, firmware de rampes). GPIO13 réaffecté au servo (Bloc 12), DIR / STEP_EN du MCP23017 libérés. Une rotation continue se fera avec un contrôleur externe piloté par une sortie.

---

## Bloc 5 — Alimentation (validé)

Bloc secteur **12 V, 5 A minimum**.

| Net | Broches |
|---|---|
| VIN_RAW | J12.1, F12.1 |
| VIN_F | F12.2, Q12.5-8 (drain) |
| +12V | Q12.1-3 (source), R50, D17 (cathode), C40 (470 µF), 2 × 10 µF, 100 nF, U15.1 (VIN), F91-F96, U13.1 (servo), bobine K131 (relais) |
| Q12_G | Q12.4, R50 (→ +12V), R59 (→ GND) : VGS ≈ −6 V |
| BUCK_SW | U15.2, L12.1, D18 (cathode) |
| +5V | L12.2, U15.4 (FB), C59 (330 µF), 100 nF, U16.3, 10 µF, D10, F11-F61, U17.2 |
| +3V3 | U16.2 + languette (4), C39 (10 µF) |
| GND | J12.2, R59, D17, D18 (anode), U15.3, U15.5 (ON/OFF), U15.6 (languette), U16.1, condensateurs |

| Réf | Pièce | LCSC |
|---|---|---|
| J12 | bornier KF128-5.08-2P | C474952 |
| F12 | fusible 6,3 A temporisé TLC TA3VT6.3 (2410) | C3014144 |
| Q12 | AO4407A (P-MOS 30 V 12 A, SOIC-8) | C16072 |
| R50, R59 | 10 kΩ 0603 | C25804 |
| D17 | SMBJ15A (TVS 600 W) | C83846 |
| C40 | 470 µF 25 V DMBJ RVT1E471M1010 | C970707 |
| 2 × 10 µF entrée, 10 µF AMS1117 entrée/sortie | 10 µF 25 V 0805 | C15850 |
| 100 nF ×2 | 0603 | C14663 |
| U15 | LM2596S-5.0 (UMW, TO-263-5) | C347421 |
| D18 | SS54 | C22452 |
| L12 | 33 µH 4,25 A SMDRI129-330MT | C2924828 |
| C59 | 330 µF 25 V low-ESR Panasonic EEE-FK1E331P (**pas de polymère** : instabilité du LM2596) | C178543 (alt. C970701) |
| U16 | AMS1117-3.3 | C6186 |

PCB : boucle C40-U15-D18 courte ; cuivre + vias sous la languette de U15 (~3 W) ; pistes 12 V ≥ 2 mm.

---

## Bloc 5b — Alimentation isolée (validé)

B0505S-1WR3 (5 V → 5 V isolé, non régulé, charge mini 20 mA) puis AMS1117-3.3 côté isolé (HCPL-063L : 2,7–3,6 V).

| Net | Broches |
|---|---|
| +5V / GND | U17.2 (VIN) / U17.1, condensateur d'entrée 10 µF |
| VISO_5V | U17.4 (+VO), C69 (10 µF), R60, U18.3 (VIN) |
| PRELOAD | R60 – R69 (2 × 220 Ω ≈ 11 mA) |
| VISO_3V3 | U18.2 + U18.4 (languette), C70 (10 µF) |
| VISO_GND | U17.3 (0V), C69, R69, U18.1, C70 |

| Réf | Pièce | LCSC |
|---|---|---|
| U17 | B0505S-1WR3 (SIP-4 : 1 GND, 2 VIN, 3 0V, 4 +VO) | C7465178 (EVISUN, alt. HI-LINK C5183119 ; Mornsun C131038 indisponible) |
| U18 | AMS1117-3.3 | C6186 |
| 3 × 10 µF | 0805 25 V | C15850 |
| R60, R69 | 220 Ω 0603 | C22962 |

PCB : bande sans cuivre (~2 mm) sous U17 entre les broches 1-2 et 3-4 ; plan VISO_GND séparé pour tout le côté isolé.

---

## Bloc 6 — Relais ×3 : supprimé

Remplacé par des **prises Wi-Fi** sur le réseau créé par l'ESP32 (éclairage, petit compresseur…), par les sorties vannes libres (charges 12 V DC, lumière dimmable, module relais 12 V externe) et par **une sortie relais embarquée** (Bloc 13). Voir [docs/sorties-wifi.md](docs/sorties-wifi.md).

---

## Bloc 7 — PWM lumière / servo : supprimé (04/10)

La lumière 12 V dimmable passe par une sortie vanne (même étage AO3400A + diode + PTC 1,1 A) ; le servo a sa sortie dédiée (Bloc 12). Plus de cavaliers de mode ni de risque de 12 V sur le servo. GPIO14 libre, un RJ45 de moins.

---

## Bloc 8 — Bus I2C (validé)

| Composant | Adresse | Rôle |
|---|---|---|
| U19 MCP23017 (SSOP-28) | 0x20 (A0-A2 à GND) | GPA0-5 = CS_1-6, GPA6 = FOCUS_CMD, **GPB2 = RELAY_CMD** (Bloc 13), **GPB3 = SERVO_OFF** (Bloc 12), GPB5 = LED de statut (R70 1 kΩ → CN11), RESET via R78 (10 k → +3V3) ; GPA7, GPB0-1, GPB4, GPB6-7 libres |
| U20 MCP4728 | 0x60 | LDAC à GND ; VOUTA-D (6-9) = THR_1-4 |
| U23 MCP4728 | 0x61 (reprogrammée au 1er démarrage) | LDAC = DAC2_LDAC (GPIO10 en v2, GPIO18 en v1) + R77 10 k → GND ; VOUTA/B = THR_5/6 |
| U24 ADS7828 (TSSOP-16) | 0x48 (A0, A1 à GND) | CH0-5 = ID_ADC_1-6, CH6-7 et COM à GND, REF : C77 1 µF (référence interne 2,5 V) |

MCP4728 MSOP-10 : 1 VDD, 2 SCL, 3 SDA, 4 LDAC, 5 RDY, 6-9 VOUTA-D, 10 VSS (attention : symbole EasyEDA numéroté en miroir côté droit). Découplage C73-C76 (100 nF).

| Réf | Pièce | LCSC |
|---|---|---|
| U19 | MCP23017-E/SS | C506653 |
| U20, U23 | MCP4728-E/UN | C108207 |
| U24 | ADS7828E/250 | C701648 |
| R70 | 1 kΩ | C21190 |
| R77, R78 | 10 kΩ | C25804 |
| C73-C76 | 100 nF | C14663 |
| C77 | 1 µF | C5673 |
| CN11 | connecteur 2 points (LED de statut déportée, anode broche 1) | — |

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
| SERVO_SIG | PESD5V0S1BB D15 (Bloc 12) + 220 Ω série |
| Vannes | diodes de roue libre SS14 / diode interne de l'AO3400A |
| Relais | contacts isolés de la bobine (aucune protection nécessaire) |
| Entrée 12 V | SMBJ15A (Bloc 5) |

Pas de condensateur entre VISO_GND et GND (isolation conservée).

---

## Bloc 12 — Sortie servo, rail 6 V dédié (validé, page 12)

LM2596S-ADJ alimenté par le +12V : V_SERVO = 1,23 V × (1 + R29 / R20) = 1,23 × (1 + 3,9 k / 1 k) ≈ **6,0 V, 3 A** (limitation interne, pas de PTC). Rail coupable par le MCP23017 : servo **hors tension au démarrage** tant que le firmware n'a pas fixé sa position. Repères = export EasyEDA du 05/10 (les feuilles KiCad de `kicad/sortie_servo/` utilisent une numérotation antérieure).

| Net | Broches |
|---|---|
| +12V | U13.1 (VIN), C18, C19 (10 µF), C20 (100 nF) |
| SERVO_SW | U13.2, L13.1, D14 (cathode, SS54) |
| V_SERVO | L13.2, R29 (3,9 kΩ), C28+ (330 µF), C29 (100 nF), C30+ (470 µF), J13.2 |
| SERVO_FB | U13.4, R29, R20 (1 kΩ → GND) |
| SERVO_OFF | U13.5 (ON/OFF), R19 (10 kΩ → +3V3), U19.4 (GPB3) — haut / haute impédance = coupé |
| SERVO_PWM | U10.19 (GPIO13, LEDC 50 Hz), R30 (10 kΩ → GND), U14.2 (A) |
| (sans nom) | U14.4 (Y), R39 (220 Ω) |
| (sans nom) | R39, D16 (TVS), J13.3 (signal) |
| +5V | U14.5 (VCC), C38 (100 nF) |
| GND | U13.3, U13 languette, R20, D14 anode, C18-C38, U14.1 (OE), U14.3, R30, D16, J13.1 |

J13 : bornier 3 points — 1 = GND, 2 = V_SERVO (6 V), 3 = signal (rallonge servo à câbler).

| Réf | Pièce | LCSC |
|---|---|---|
| U13 | LM2596S-ADJ (UMW, TO-263-5) | C347423 |
| L13 | 33 µH 4,25 A SMDRI129-330MT | C2924828 |
| D14 | SS54 | C22452 |
| C28 | 330 µF 25 V low-ESR Panasonic EEE-FK1E331P (pas de polymère) | C178543 (alt. C970701) |
| C30 | 470 µF 25 V DMBJ RVT1E471M1010 | C970707 |
| C18, C19 | 10 µF 25 V 0805 | C15850 |
| C20, C29, C38 | 100 nF 0603 | C14663 |
| R20 | 1 kΩ 1 % | C21190 |
| R29 | 3,9 kΩ 1 % UNI-ROYAL 0603WAF3901T5E | C23018 (rupture constatée le 05/10 ; secours : R29 = 39 kΩ C23153 + R20 = 10 kΩ C25804, même rapport, R20/R29 collées à U13.4) |
| R19, R30 | 10 kΩ | C25804 |
| R39 | 220 Ω | C22962 |
| U14 | SN74AHCT1G125DBVR (1 OE, 2 A, 3 GND, 4 Y, 5 VCC) | C7484 |
| D16 | PESD5V0S1BB | C97640 |
| J13 | bornier KEFA KF128-5.08-3P-AA | C474953 |

---

## Bloc 13 — Sortie relais, contact sec (validé, page 12)

| Net | Broches |
|---|---|
| RELAY_CMD | U19.3 (GPB2), R40 (220 Ω) |
| (grille) | R40, Q13.1, R49 (100 kΩ → GND, relais ouvert au démarrage) |
| (bobine −) | Q13.3 (drain), RELAY13.2, D15 anode |
| +12V | RELAY13.1 (bobine +), D15 cathode (SS14, roue libre) |
| GND | Q13.2 (source), R49 |
| RELAY_COM | RELAY13.5 (contact mobile), J14.1 |
| RELAY_NO | RELAY13.4, J14.2 |
| RELAY_NC | RELAY13.3, J14.3 |

Brochage COM / NO / NC vérifié sur le symbole LCSC de la C3633 (lame au repos sur le contact NC).

| Réf | Pièce | LCSC |
|---|---|---|
| RELAY13 | HONGFA HF32F/012-ZS3 (bobine 12 V, 1RT, 3 A) | C3633 |
| Q13 | AO3400A | C20917 |
| D15 | SS14 | C2480 |
| R40 | 220 Ω | C22962 |
| R49 | 100 kΩ | C25803 |
| J14 | bornier KEFA KF128-5.08-3P-AA | C474953 |

Contact 3 A / 30 V DC — **basse tension uniquement, jamais de 230 V** (sérigraphie près de J14).

---

## Bilan 12 V (sans moteur)

Vannes 3 A + servo ≈ 1,8 A (à pleine charge, sous 6 V) + +5V ≈ 1,5 A + relais 30 mA : bloc secteur **12 V 5 A** suffisant, 6 A pour la marge si vannes et servo forcent ensemble.

---

## Implantation PCB

Carte 175 × 125 mm, 4 couches (GND plein en couche 2, alimentations en couche 3). Placement v4 des 287 composants, règles et zones : [pcb/README.md](pcb/README.md) ; checklist : [docs/pcb-checklist.md](docs/pcb-checklist.md).

---

## Sorties Wi-Fi (remplacent le Bloc 6)

Prises connectées commandées par l'ESP32 sur **son propre réseau Wi-Fi** (point d'accès SoftAP, DHCP intégré : fonctionne sans box, partout), en HTTP / MQTT local : éclairage, petit compresseur (prise ≥ 10 A), ventilateur… Non critiques (50–500 ms), envoyées avant ou après une séquence de déclenchement. Détails : [docs/sorties-wifi.md](docs/sorties-wifi.md).
