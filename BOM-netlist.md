# TriggerFlow — BOM & Netlist par bloc (pour saisie dans EasyEDA Pro)

Chaque bloc ci-dessous est pensé pour être ressaisi rapidement dans l'éditeur de schéma EasyEDA Pro : rechercher chaque référence dans le catalogue LCSC intégré, placer les symboles, relier selon la table de nets. Un bloc = un sous-schéma répété ×N selon le tableau.

---


## Bloc 1 — Entrée capteur (×6, un par canal)

### BOM

| Réf. | Composant | Valeur / partie | Répétition |
|---|---|---|---|
| U1 | MCP6S91 | PGA SPI, gain ×1 à ×32 | ×6 |
| U2 | TLV3501 | Comparateur rapide | ×6 |
| D1, D2 | BAT54S | Double diode Schottky (clamp) | ×6 |
| R1 | Résistance | 220-470 Ω (protection série) | ×6 |
| R2 | Résistance | 10 kΩ (hystérésis, vers entrée +) | ×6 |
| R3 | Résistance | 680 kΩ (hystérésis, feedback OUT→+, ≈50 mV) | ×6 |

### Netlist

| Net | Connecté à |
|---|---|
| SIG_IN_x | RJ45 pin (paire bleue) → R1 → nœud [D1 cathode / D2 anode] → MCP6S91 IN |
| MCP6S91_OUT_x | MCP6S91 OUT → TLV3501 (+) |
| VREF_x | MCP4728 DAC OUTx → TLV3501 (-) |
| TLV_OUT_x | TLV3501 OUT → GPIO natif ESP32-S3 (ISR) + R3 (feedback) |
| HYST_NODE_x | TLV3501 (+) → R2 (vers masse locale) + R3 (vers TLV_OUT_x) |
| SPI_SCK / SPI_MOSI / CS_x | Bus SPI commun (SCK/MOSI partagés, CS individuel depuis MCP23017) |
| GND_SIGNAL_x | RJ45 paire verte → masse signal (séparée de l'alim, cf. section connectique) |

### 1a. Pré-conditionnement selon le type de capteur (en amont du nœud SIG_IN_x)

**Micro électret**

| Réf. | Valeur | Rôle |
|---|---|---|
| R_bias | 4,7 kΩ | Polarisation de la capsule (Vcc → capsule) |
| C_couple | 1 µF | Découplage AC |
| R_mid1, R_mid2 | 100 kΩ chacune | Pont diviseur, recentre le signal à Vcc/2 |

Câblage : `+3.3V → R_bias → capsule(+) ; capsule(-) → GND ; capsule(+) → C_couple → [R_mid1 vers +3.3V, R_mid2 vers GND] → SIG_IN_x`

**Piézo**

| Réf. | Valeur | Rôle |
|---|---|---|
| R_bleed | 1 MΩ | Décharge continue du piézo (antiparallèle sur ses bornes) |
| C_couple, R_mid1, R_mid2 | Identiques au micro | Recentrage AC à Vcc/2 |

Câblage : `Piézo(+) → [R_bleed vers Piézo(-)/GND] → C_couple → [R_mid1 vers +3.3V, R_mid2 vers GND] → SIG_IN_x`

**Contact sec (en entrée)**

| Réf. | Valeur | Rôle |
|---|---|---|
| R_pullup | 10 kΩ | Tirage vers +3.3V, contact vers GND |

Câblage : `+3.3V → R_pullup → SIG_IN_x ; SIG_IN_x → contact externe → GND`. PGA réglé en gain ×1 (pas d'amplification nécessaire, signal déjà logique). Pas de condensateur de debounce matériel — anti-rebond géré en logiciel pour ne pas ralentir la détection.

**Laser** : voir Bloc 9 (module récepteur déporté, transimpédance).

---

## Bloc 2 — Sortie flash / caméra (opto + MOSFET)

### BOM

| Réf. | Composant | Valeur / partie | Répétition |
|---|---|---|---|
| U3 | 6N137 | Optocoupleur rapide (~50-100 ns) | ×4 (flash) + ×4 (focus/shutter caméra) = ×8 |
| Q1 | 2N7002 | MOSFET N logic-level, Vds 60V | ×8 |
| R4 | Résistance | 220-330 Ω (courant LED interne 6N137) | ×8 |
| R5 | Résistance | 10 kΩ (pull-up sortie collecteur ouvert) | ×8 |

### Netlist

| Net | Connecté à |
|---|---|
| GPIO_OUT_flash_x / GPIO_OUT_shutter_x | GPIO natif ESP32-S3 (gptimer/esp_timer) → R4 → anode LED 6N137 (cathode → GND logique) — flash ×4 + shutter ×2 |
| GPIO_OUT_focus_x | **Sortie MCP23017** (non critique en timing) → R4 → anode LED 6N137 — focus ×2 |
| VISO_3V3 | LDO dédié 3.3V isolé → R5 (pull-up) → collecteur 6N137 |
| OPTO_OUT_x | 6N137 sortie (collecteur ouvert) → grille Q1 |
| DRAIN_Q1 | Q1 drain → RJ45 broche signal (bleue = shutter/flash, verte = focus si connecteur caméra) |
| SOURCE_Q1 | Q1 source → retour dédié de la même paire (pas de masse commune partagée — chaque paire torsadée porte son propre signal+retour, cf. section 11 du README) |

**Note connecteur caméra (×2)** : chaque connecteur RJ45 caméra porte **2 circuits complets** de ce bloc — le **shutter** est piloté en GPIO natif (timing critique), le **focus** est piloté depuis le MCP23017 (non critique, cf. section 4 du README) — même circuit opto+MOSFET, source logique différente.

---

## Bloc 3 — Sortie électrovanne (×6)

### BOM

| Réf. | Composant | Valeur / partie | Répétition |
|---|---|---|---|
| Q1 | AO3400 | MOSFET N logic-level | ×6 |
| D1 | SS14 (Schottky) | 1A, ≥40V inverse (flyback) | ×6 |
| R1 | Résistance | 100-220 Ω (grille) | ×6 |
| R2 | Résistance | 10 kΩ (pull-down grille→source) | ×6 |

### Netlist

| Net | Connecté à |
|---|---|
| VALVE_PWR_x | +12V (rail vannes) → borne + électrovanne (via GX12) |
| VALVE_SW_x | Borne - électrovanne (via GX12) → drain Q1 + cathode... (D1 cathode vers +12V, anode vers ce nœud) |
| GPIO_VALVE_x | GPIO natif ESP32-S3 (gptimer, durée de pulse programmable) → R1 → grille Q1 |
| GATE_PD_x | Grille Q1 → R2 → source Q1 (pull-down, sécurité anti-ouverture accidentelle au boot) |
| GND_PWR | Source Q1 → masse rail 12V |

**Point de dimensionnement pour le bloc alimentation** : prévoir la capacité du bloc secteur externe pour un pire cas de plusieurs vannes activées simultanément (jusqu'à 6× le courant nominal d'une vanne si une règle du moteur les déclenche toutes ensemble).

---

## Bloc 4 — Driver moteur pas à pas (×1)

### BOM

| Réf. | Composant | Valeur / partie |
|---|---|---|
| Socket | Header femelle 2,54mm, 2×8 broches | Reçoit un module driver enfichable (format Pololu) |
| Driver | Module TMC2209 (recommandé, silencieux) — ou A4988/DRV8825, même pinout | — |
| C1 | Condensateur électrolytique | 100 µF, ≥25V, au plus près du module (VMOT/GND) |
| R1 | Résistance | 10 kΩ (pull-up RESET+SLEEP vers 3.3V) |
| MS1, MS2 | Câblage fixe (pont ou résistances de tirage) | Microstepping figé, pas piloté en logiciel |

### Netlist

| Net | Connecté à |
|---|---|
| VMOT | +12V (rail vannes/moteur) → module driver VMOT, C1+ |
| GND_PWR | Masse rail 12V → module driver GND, C1- |
| VDD_LOGIC | 3.3V (LDO analogique dédié) → module driver VDD |
| STEP | GPIO natif ESP32-S3 (LEDC/RMT) → module driver STEP |
| DIR | MCP23017 → module driver DIR |
| EN | MCP23017 → module driver EN (actif bas) |
| RESET_SLEEP | R1 (pull-up 3.3V) → module driver RESET + SLEEP (liés) |
| MOTOR_1A, 1B, 2A, 2B | Module driver → GX12 4 broches → moteur pas à pas |

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

## Bloc 7 — PWM lumière continue / servo (×1) — corrigé

**Correction d'architecture** : ce signal ne peut pas être généré par le MCP23017 (pas de PWM matériel). Il utilise le dernier GPIO natif disponible, via le périphérique LEDC de l'ESP32-S3 (PWM matériel, aucune charge CPU).

### BOM

| Réf. | Composant | Valeur / partie |
|---|---|---|
| Q1 | MOSFET N logic-level (AO3400) | Si pilotage lumière continue (charge résistive/LED puissance) |
| — | Connexion directe | Si pilotage servo (signal PWM 50Hz directement vers RJ45, alimentation servo séparée sur le rail 5V) |

### Netlist

| Net | Connecté à |
|---|---|
| GPIO_PWM | GPIO natif ESP32-S3 (LEDC) → grille Q1 (mode lumière) ou directement RJ45 signal (mode servo) |
| V5_SERVO | +5V rail → RJ45 alim servo (si mode servo) |

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
