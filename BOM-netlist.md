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
| GPIO_OUT_x | GPIO natif ESP32-S3 → R4 → anode LED 6N137 (cathode → GND logique) |
| VISO_3V3 | LDO dédié 3.3V isolé → R5 (pull-up) → collecteur 6N137 |
| OPTO_OUT_x | 6N137 sortie (collecteur ouvert) → grille Q1 |
| DRAIN_Q1 | Q1 drain → RJ45 broche signal (bleue = shutter/flash, verte = focus si connecteur caméra) |
| SOURCE_Q1 | Q1 source → RJ45 masse commune |

**Note connecteur caméra (×2)** : chaque connecteur RJ45 caméra porte **2 circuits complets** de ce bloc (un pour focus, un pour shutter), partageant une seule masse commune côté RJ45.

---

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

## Blocs restants à documenter (au fur et à mesure de l'avancement)

- Alimentation (buck 12V→5V + LDO 3.3V dédié analogique)
- Contact sec / relais ×3
- PWM lumière continue / servo ×1
- Bus I2C complet (MCP4728 ×2, MCP23017, ADS78xx) — adressage et connexions
