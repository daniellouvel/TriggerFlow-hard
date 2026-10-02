# TriggerFlow — BOM & Netlist par bloc (pour saisie dans EasyEDA Pro)

Chaque bloc ci-dessous est pensé pour être ressaisi rapidement dans l'éditeur de schéma EasyEDA Pro : rechercher chaque référence dans le catalogue LCSC intégré, placer les symboles, relier selon la table de nets. Un bloc = un sous-schéma répété ×N selon le tableau.

---


## État de validation (02/10/2026)

| Bloc | État |
|---|---|
| 1 — Entrée capteur v3 | voie 1 validée (export .tel EasyEDA) ; voies 2 à 6 à copier et vérifier |
| 2 — Flash / caméra | une voie validée ; voies 2 et 3 à vérifier |
| 3 — Électrovannes | 6 canaux validés |
| 4 — Moteur pas à pas | proposition générée sous KiCad, non saisie |
| 7 — PWM lumière / servo | proposition générée sous KiCad, non saisie |
| 5, 5b, 6, 8 à 11 | description d'origine, non reprise |

Méthode : schéma de référence produit par le générateur KiCad, saisi dans EasyEDA Pro avec les références LCSC, puis netlist exportée (.tel) et comparée net par net à la référence.

---

## Bloc 1 — Entrée capteur v3 (×6, une voie par entrée)

**Statut** : voie 1 saisie dans EasyEDA et netlist (.tel) validée le 01/10/2026 par comparaison avec la référence. Voies 2 à 6 : à copier puis à vérifier par un export complet. La numérotation des voies suit le numéro de page EasyEDA.

Chaîne (tout signal capteur arrive en DC unipolaire 0–3,3 V) :
RJ45 4-5 → TVS + tirage 4,7 kΩ (JP101) + 1 MΩ → R101 2,2 kΩ → clamp BAT54S + 100 pF → MCP6S91 (VREF du PGA = GND) → TLV3501 avec hystérésis, seuil THR propre à la voie (filtré 1 kΩ / 100 nF) → TLV_OUT.
RJ45 1-2 : 5 V capteur via PTC. RJ45 7-8 : ligne ID (10 kΩ vers +3V3). RJ45 3-6 : GND.

Supprimés par rapport à la v2 : couplage AC (C105, JP104), polarisation Vcc/2 (R106, R107, R108, JP103), JP102 et le VREF partagé entre voies.

### Netlist (une voie, référence voie 1)

| Net | Broches |
|---|---|
| SENSOR_n | J101.4, J101.5, D102.2 (TVS), R104 (4,7 k vers JP101), R105 (1 M vers GND), R101.1 |
| CLAMP_n | R101.2, D101.3 (commun), C106 (100 pF vers GND), U101.2 (CH0) |
| MCP6S91_OUT | U101.1, R102.1 |
| HYST_NODE | R102.2, R103.1, U102.3 (+) |
| TLV_OUT_n | U102.6, R103.2 |
| THR_n → THR_F | THR_n → R109 (1 k) → C107 (100 nF vers GND), U102.2 (−) |
| V_SENS | J101.1, J101.2, F101 (PTC vers +5V), C108 (10 µF) |
| ID_n | J101.7, J101.8, R110 (10 k vers +3V3) |
| CS_n | U101.5 |
| SPI_MOSI, SPI_SCK (communs) | U101.6, U101.7 |
| +3V3 | U101.8, U102.7, D101.2, JP101, R110, découplage |
| GND | U101.3 (VREF du PGA), U101.4, U102.4, U102.8 (SHDN), D101.1, D102.1, R105, J101.3, J101.6, blindage J101, condensateurs |
| non connectées | U102.1, U102.5 |

Propres à chaque voie : SENSOR_n, CLAMP_n, CS_n, THR_n, TLV_OUT_n, ID_n, V_SENS. Communs aux 6 voies : SPI_MOSI, SPI_SCK, +3V3, +5V, GND. Après chaque copie, vérifier qu'aucune étiquette n'a gardé le suffixe d'une autre voie (EasyEDA fusionne les nets de même nom entre pages).

### BOM (une voie)

| Réf | Valeur | Pièce | Boîtier | LCSC |
|---|---|---|---|---|
| U101 | PGA SPI | MCP6S91 | MSOP-8 | C627647 |
| U102 | Comparateur rapide | TLV3501AID | SOIC-8 | C43484 |
| D101 | Double Schottky | BAT54S | SOT-23 | C545549 |
| D102 | TVS 5 V bidirectionnelle | Nexperia PESD5V0S1BB,115 | SOD-523 | C97640 |
| R101 | 2,2 kΩ 1 % | 0603WAF2201T5E | 0603 | C4190 |
| R102, R110 | 10 kΩ 1 % | 0603WAF1002T5E | 0603 | C25804 |
| R103 | 680 kΩ 1 % | 0603WAF6803T5E | 0603 | C25822 |
| R104 | 4,7 kΩ | | 0603 | C23162 |
| R105 | 1 MΩ | | 0603 | C22935 |
| R109 | 1 kΩ 1 % | 0603WAF1001T5E | 0603 | C21190 (alt. C25585) |
| C101, C103, C107 | 100 nF | | 0603 | C14663 |
| C102, C104 | 1 µF | | 0603 | C5673 |
| C106 | 100 pF C0G 50 V | GRM1885C1H101JA01D | 0603 | C71664 |
| C108 | 10 µF X5R 25 V | CL21A106KAYNNNE | 0805 | C15850 |
| F101 | PTC 200 mA / 24 V | SMD1206P020TF | 1206 | C20984 |
| JP101 | 0 Ω (monté = tirage actif) | | 0603 | C21189 |
| J101 | RJ45 8P8C blindé, sans magnétiques (10 broches) | HanXia HX-RJ45 90 5631-1x1 | traversant | C25168869 |

21 composants par voie. Hystérésis : ΔV ≈ 3,3 V × 10 k / (10 k + 680 k) ≈ 48 mV. Courant capteur limité à 200 mA par port (PTC).

### Points ouverts

- 6 voies demandent 6 CS de PGA : vérifier les lignes libres du MCP23017 (sinon second MCP23017 ou décodeur 74HC138).
- 6 seuils THR (2 × MCP4728 = 8 canaux) et 6 lignes ID (ADC 8 canaux) : à câbler sur la feuille ESP32.
- 6 × 200 mA = 1,2 A au pire sur le +5V : à prévoir dans le Bloc 5.
- D102 recouvre en partie la protection RClamp0524P du Bloc 10 : n'en garder qu'une sur ces lignes.

---

## Bloc 2 — Sortie flash / caméra (HCPL-2631 + 2N7002, isolée)

**Statut** : une voie (2 canaux) validée le 01/10/2026 par export .tel EasyEDA. Le HCPL-2631 (double opto) remplace le 6N137 : un bloc = 2 canaux, instancié ×3 pour les 6 sorties (4 flash + 2 shutter). Voies 2 et 3 à vérifier par un export complet.

### Brochage HCPL-2631 DIP-8

1 A1 · 2 K1 · 3 K2 · 4 A2 · 5 GND sortie (VISO_GND) · 6 VO2 · 7 VO1 · 8 VCC (VISO_3V3)

### Netlist (une voie)

| Net | Broches |
|---|---|
| GPIO_A | R401.1 |
| GPIO_B | R402.1 |
| INPUT_A | R401.2, U401.1 |
| INPUT_B | R402.2, U401.4 |
| GND | U401.2, U401.3 |
| VISO_3V3 | U401.8, R403.1, R404.1 |
| VISO_GND | U401.5, Q401.2, Q402.2 |
| VO1_GATE | U401.7, R403.2, Q401.1 |
| VO2_GATE | U401.6, R404.2, Q402.1 |
| OUT_A | Q401.3 |
| OUT_B | Q402.3 |

### BOM (une voie)

| Réf | Valeur | Boîtier | LCSC |
|---|---|---|---|
| U401 | HCPL-2631 (onsemi) | DIP-8 | C16384 |
| R401, R402 | 270 Ω | 0603 | C22966 |
| R403, R404 | 10 kΩ | 0603 | C25804 |
| Q401, Q402 | 2N7002 | SOT-23 | C8545 |

### Points ouverts

- Logique inversée (LED allumée = sortie basse = Q bloqué) : à gérer côté firmware.
- Courant LED ≈ (3,3 V − 1,5 V) / 270 Ω ≈ 7 mA : à confirmer avec la datasheet.
- Ne jamais relier GND et VISO_GND.
- Le 2N7002 (60 V) ne supporte pas la tension de synchro de certains flashs anciens (plusieurs centaines de volts).

---

## Bloc 3 — Sortie électrovanne (×6)

**Statut** : 6 canaux validés le 01/10/2026 par export .tel EasyEDA. Le fichier `sortie_electrovanne.kicad_sch` d'origine avait des connexions cassées (résistances et grilles non reliées, diode court-circuitée) et des descriptions « pull-up » erronées : il ne fait plus référence.

### Netlist (canal n)

| Net | Broches |
|---|---|
| GPIO_VALVE_n | R(2n−1).1 |
| GATE_n | Q70n.1, R(2n−1).2, R(2n) (pull-down) |
| GND | Q70n.2 (source), R(2n) |
| VALVE_SW_n | Q70n.3 (drain), D70n.2 (anode), borne « − » de la vanne |
| VALVE_PWR_n | D70n.1 (cathode), F70n.1, borne « + » de la vanne |
| +12V | F70n.2 |

Canal n : résistance de grille R(2n−1) = 220 Ω (R701, R703 … R711), pull-down R(2n) = 10 kΩ (R702, R704 … R712). Seuls GND et +12V sont communs ; chaque canal a ses 4 nets propres. Erreur déjà rencontrée à la copie : les grilles des canaux 5 et 6 avaient gardé GATE_2 / GATE_3.

### BOM (par canal)

| Réf | Valeur | Boîtier | LCSC |
|---|---|---|---|
| R 220 Ω (grille) | 220 Ω | 0603 | C22962 |
| R 10 kΩ (pull-down) | 10 kΩ | 0603 | C25804 |
| Q70n | AO3400A (G=1, S=2, D=3) | SOT-23 | C20917 |
| D70n | SS14 (cathode côté VALVE_PWR) | SMA | C2480 |
| F70n | Bourns MF-MSMF110/24X-2 (1,1 A / 2,2 A / 24 V) | 1812 | C210835 (alt. Littelfuse 1812L110/33MR : C142747) |

Ne pas utiliser le MF-R110 (traversant, non confirmé sur LCSC) ni les références C160122, C25057, C25761 d'une ancienne version de ce document.

**Dimensionnement** : prévoir dans le Bloc 5 le pire cas de 6 vannes ouvertes simultanément (≈ 3 A à 12 V).

### Points ouverts

- Connecteur vanne GX12 : 2 ou 4 broches ?
- Affectation GPIO_VALVE_n ↔ broches ESP32-S3 (feuille principale).

---

## Bloc 4 — Driver moteur pas à pas (×1)

**Statut** : proposition du 01/10/2026, feuille générée sous KiCad (netlist calculée sans broche isolée). Pas encore saisie ni validée dans EasyEDA.

Corrections par rapport à la version précédente : un module Pololu s'enfiche dans **deux barrettes 1×8** écartées de 12,7 mm (pas une 2×8) ; le TMC2209 n'a pas exactement le brochage de l'A4988 (SPREAD/CLK), donc la pull-up RESET/SLEEP est remplacée par un cavalier JP804 ; ajout d'une pull-up sur EN (moteur coupé au boot) et d'une pull-down sur STEP.

### Netlist

| Net | Broches |
|---|---|
| STEP | GPIO natif (LEDC/RMT), J801.7, R802 (10 kΩ vers GND) |
| DIR | MCP23017, J801.8 |
| STEP_EN | MCP23017, J801.1, R801 (10 kΩ vers +3V3) |
| MS1, MS2, MS3 | J801.2, J801.3, J801.4 → JP801, JP802, JP803 vers +3V3 |
| RST_SLP | J801.5 ↔ JP804 ↔ J801.6 |
| VMOT | +12V → F801 → J802.1, C801+ (100 µF), C802 (100 nF) |
| GND | J802.2, J802.8, C801−, C802, C803, R802 |
| MOT_2B, MOT_2A, MOT_1A, MOT_1B | J802.3 à J802.6 → J803 (vers le GX12 4 broches) |
| +3V3 | J802.7 (VDD/VIO), C803 (100 nF), R801, cavaliers |

### Cavaliers selon le module

| Module | JP801 (MS1) | JP802 (MS2) | JP803 (MS3) | JP804 | Résultat |
|---|---|---|---|---|---|
| TMC2209 | fermé | fermé | ouvert | **ouvert** | 1/16, stealthChop |
| A4988 | fermé | fermé | fermé | fermé | 1/16 |
| DRV8825 | ouvert | ouvert | fermé | fermé | 1/16 |

### BOM

| Réf | Pièce | LCSC |
|---|---|---|
| J801, J802 | Barrette femelle 1×8, 2,54 mm, traversante | C27438 |
| C801 | 100 µF 35 V électrolytique SMD 6,3×7,7 | C3339 |
| C802, C803 | 100 nF 0603 | C14663 |
| R801, R802 | 10 kΩ 0603 | C25804 |
| F801 | PTC 2 A / 16 V, 1812 (SMD1812P200TF/16) | C545213 |
| JP801 à JP804 | Pont de soudure 2 plots | — |
| J803 | Connecteur 4 broches vers le GX12 (bornier ou XH) | à choisir |

---

## Bloc 5 — Alimentation (buck 12V→5V + LDO 3.3V dédié)

### BOM

| Réf. | Composant | Valeur / partie |
|---|---|---|
| F1 | Fusible rapide + porte-fusible | 5A |
| C_bulk | Condensateur électrolytique | 470 µF, ≥25V |
| Buck | Module LM2596 préfabriqué, ajustable | Réglé sortie 5V, 3A |
| U (LDO) | AMS1117-3.3 | 1A |
| C1, C2 | Céramique | 100 nF (découplage local) |
| C3 | Tantale/électrolytique | 10 µF (stabilité sortie LDO) |

### Netlist

| Net | Connecté à |
|---|---|
| V12_IN | GX12/16 (entrée alim) → F1 → C_bulk → rail 12V |
| V12_RAIL | C_bulk+ → électrovannes (×6, GX12), VMOT driver stepper, entrée buck |
| V5_RAIL | Sortie buck LM2596 → DevKitC-1 (pin 5V), servo/relais 5V si utilisés, entrée LDO |
| V3V3_ANALOG | Sortie AMS1117-3.3 → TLV3501 ×6, MCP6S91 ×6, MCP4728 ×2, MCP23017, ADS78xx |
| GND_STAR | Point de masse unique — sépare masse puissance (vannes/moteur) et masse signal (analogique), reliées uniquement à ce nœud |

**Budget de courant** (à affiner selon le matériel réel) : ~9-10A/12V en pire cas théorique (6 vannes + moteur simultanés) ; dimensionnement recommandé du bloc secteur externe : 6-8A/12V (72-96W) pour un usage réaliste.

---

## Bloc 5b — Alimentation isolée pour le rail Viso des 6N137

### BOM

| Réf. | Composant | Valeur / partie |
|---|---|---|
| ISO1 | B0505S-1W | Convertisseur DC-DC isolé 5V→5V, 1W, ~1kV d'isolement |
| LDO2 | AMS1117-3.3 | 1A, dérive le 3.3V isolé depuis la sortie de ISO1 |
| C1, C2 | 100nF + 1µF | Découplage entrée/sortie (règle standard) |

### Netlist

| Net | Connecté à |
|---|---|
| V5_RAIL | Sortie buck LM2596 → entrée ISO1 |
| VISO_5V | Sortie isolée ISO1 → entrée LDO2 |
| VISO_3V3 | Sortie LDO2 → Vcc des 8× 6N137 (avec découplage 100nF+1µF par CI) |
| GND_ISO | Masse isolée, distincte de GND_STAR (masse principale) — ne se rejoint nulle part sur le PCB, c'est le principe même de l'isolation |

---

## Bloc 6 — Contact sec / relais (×3)

### BOM

| Réf. | Composant | Valeur / partie | Répétition |
|---|---|---|---|
| Q1 | BC847 (NPN) | — | ×3 |
| R1 | Résistance | 1 kΩ (base) | ×3 |
| D1 | 1N4148 (flyback) | — | ×3 |
| Relais | Relais signal 5V, contact sec | — | ×3 |

### Netlist

| Net | Connecté à |
|---|---|
| MCP23017_OUT_x | MCP23017 → R1 → base Q1 |
| RELAY_COIL | +5V → bobine relais → collecteur Q1 (D1 en antiparallèle sur la bobine, cathode +5V) |
| GND_LOGIC | Émetteur Q1 → GND |
| CONTACT_NO/NC/COM | Contact du relais → RJ45 (signal externe, isolé galvaniquement) |

---

## Bloc 7 — PWM lumière continue / servo (×1)

**Statut** : proposition du 01/10/2026, feuille générée sous KiCad (netlist calculée sans broche isolée). Pas encore saisie ni validée dans EasyEDA.

Signal sur le dernier GPIO natif (LEDC, PWM matériel). Mode lumière : MOSFET côté masse. Mode servo : buffer 74AHCT1G125 alimenté en 5 V (entrée 3,3 V, sortie 5 V franche). Deux cavaliers 3 plots empêchent de sélectionner les deux modes à la fois.

### Netlist

| Net | Broches |
|---|---|
| GPIO_PWM | GPIO natif (LEDC), R901.1, U901.2 (A) |
| GATE_PWM | R901.2 (220 Ω), Q901.1, R902 (10 kΩ vers GND) |
| LIGHT_SW | Q901.3 (drain), D901 anode, JP901 côté A |
| SERVO_SIG | U901.4 (Y) → R903 (220 Ω) → JP901 côté B |
| PWM_OUT | JP901 centre, RJ45 broches 4 et 5 |
| V_ACC_SEL | JP902 centre → F901.1 |
| V_ACC | F901.2, D901 cathode, RJ45 broches 1 et 2 |
| +12V / +5V | JP902 côté A / côté B |
| +5V | U901.5 (VCC), C901 (100 nF) |
| GND | Q901.2, U901.1 (OE), U901.3, R902, C901, RJ45 broches 3 et 6 |
| non connectées | RJ45 broches 7 et 8 (réservées) |

Modes : lumière = JP901 sur A, JP902 sur +12V (ou +5V) ; servo = JP901 sur B, JP902 sur +5V. **Ne jamais laisser JP902 sur +12V en mode servo** (à sérigraphier).

### BOM

| Réf | Pièce | LCSC |
|---|---|---|
| Q901 | AO3400A | C20917 |
| U901 | SN74AHCT1G125DBVR, SOT-23-5 | C7484 |
| D901 | SS34 | C8678 |
| F901 | PTC 1,1 A / 16 V, 1812 (1812L110/16DR) | C142746 |
| R901, R903 | 220 Ω 0603 | C22962 |
| R902 | 10 kΩ 0603 | C25804 |
| C901 | 100 nF 0603 | C14663 |
| JP901, JP902 | Pont de soudure 3 plots | — |

---

## Bloc 8 — Adressage du bus I2C

| Puce | Adresse I2C | Configuration |
|---|---|---|
| MCP4728 #1 | 0x60 (défaut usine) | — |
| MCP4728 #2 | 0x61 | Reprogrammation d'adresse en EEPROM (procédure MCP4728, une fois au premier flash) |
| MCP23017 | 0x20 | Broches A0/A1/A2 → GND |
| ADS78xx | 0x48 | Broche ADDR → GND |

---

## Bloc 9 — Module capteur laser (récepteur, déporté en bout de câble RJ45)

### BOM

| Réf. | Composant | Valeur / partie |
|---|---|---|
| PD1 | BPW34 (photodiode PIN) | Polarisée en inverse (cathode → +3.3V) |
| U1 | OPA380 (ampli transimpédance) | Bande passante ~90 MHz |
| Rf | Résistance | 100 kΩ - 1 MΩ (gain, à ajuster en test selon distance/puissance laser) |
| Cf | Condensateur céramique | 2-10 pF (stabilité) |
| Filtre optique (option) | Filtre IR passe-long >700nm | Recommandé en usage extérieur, accordé sur la longueur d'onde du laser émetteur |

### Netlist

| Net | Connecté à |
|---|---|
| V3V3_CAPTEUR | RJ45 paire orange (alim capteur) → cathode PD1 |
| PD_SIGNAL | Anode PD1 → entrée (-) OPA380, Rf/Cf en contre-réaction |
| SIG_OUT | Sortie OPA380 → RJ45 paire bleue (signal, vers MCP6S91 côté boîtier) |
| GND_SIGNAL | RJ45 paire verte → masse module |

**Émetteur** : module laser IR (780-850nm) du commerce, Classe 1/2, alimentation autonome indépendante du boîtier (pas de connecteur dédié — hors périmètre RJ45/GX12).

---

## Bloc 10 — Protection ESD sur les connecteurs RJ45 (×16)

### BOM

| Réf. | Composant | Répétition |
|---|---|---|
| U_ESD | RClamp0524P (protection ESD multi-lignes, 4 canaux) | ×16 (un par connecteur RJ45) |

### Netlist

| Net | Connecté à |
|---|---|
| RJ45_PAIRS_x | Chaque connecteur RJ45 → RClamp0524P (4 lignes) → reste du circuit (R1 protection, MCP6S91, etc.) |
| GND_ESD | RClamp0524P → masse locale (signal ou puissance selon le connecteur) |

**Placement** : au plus près de chaque connecteur, avant tout autre composant — première ligne de défense contre les décharges électrostatiques, en complément des diodes BAT54S déjà prévues sur le Bloc 1 (qui protègent contre les surtensions plus lentes).

---

## Bloc 11 — Fusibles réarmables (PTC) par canal de puissance

### BOM

| Réf. | Composant | Valeur | Répétition |
|---|---|---|---|
| PTC1-6 | Polyfuse réarmable (ex : MF-R110) | 1,1A hold | ×6 (une par électrovanne) |
| PTC7 | Polyfuse réarmable | 2A hold | ×1 (moteur pas à pas) |

### Netlist

| Net | Connecté à |
|---|---|
| V12_VALVE_x | Rail 12V → PTC1-6 → alimentation de chaque électrovanne (Bloc 3) |
| V12_MOTOR | Rail 12V → PTC7 → VMOT du driver moteur (Bloc 4) |

**Rôle** : isole un défaut (court-circuit) sur un seul canal sans couper l'ensemble du boîtier — le fusible global F1 (Bloc 5) reste la protection de dernier recours sur l'ensemble du rail 12V.

---

## Découplage — règle générale à appliquer sur tous les CI

Chaque circuit intégré alimenté a **deux condensateurs en parallèle** au plus près de sa broche Vcc/GND (non listés individuellement dans les netlists ci-dessus pour ne pas les alourdir, mais obligatoires au routage) : un **100 nF céramique** (filtre le bruit haute fréquence — commutation SPI, fronts rapides des comparateurs) et un **1 µF** (céramique ou tantale, filtre les variations plus lentes/appels de courant plus soutenus) :

| CI | Découplage local (×2) | Rail |
|---|---|---|
| TLV3501 ×6 | 100 nF + 1 µF | 3.3V analogique dédié |
| MCP6S91 ×6 | 100 nF + 1 µF | 3.3V analogique dédié |
| MCP4728 ×2 | 100 nF + 1 µF | 3.3V analogique dédié |
| MCP23017 | 100 nF + 1 µF | 3.3V analogique dédié |
| ADS78xx | 100 nF + 1 µF | 3.3V analogique dédié |
| OPA380 (module laser) | 100 nF + 1 µF | 3.3V (RJ45 alim capteur) |
| 6N137 ×8 | 100 nF + 1 µF (côté Viso) | 3.3V isolé dédié |
| Driver stepper | 100 nF + 1 µF (VDD logique), en plus de C1=100µF déjà prévu sur VMOT | 3.3V + 12V |

**Filtrage global additionnel** : +1× 10 µF tantale/électrolytique en sortie du LDO AMS1117-3.3 (rail analogique), +1× 10 µF en sortie du régulateur isolé dédié aux 6N137 (rail Viso), en complément des 100nF locaux déjà comptés dans le bloc alimentation.

---

## Tous les blocs sont maintenant documentés (11/11 + découplage)

Reste à router le PCB principal + le petit module récepteur laser (carte fille déportée) dans EasyEDA Pro.
