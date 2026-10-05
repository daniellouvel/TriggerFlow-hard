# TriggerFlow — Architecture matérielle

Boîtier de déclenchement généraliste pour photographie haute vitesse : détection multi-capteurs, moteur de règles programmable, pilotage de sorties variées (flash, électrovannes, appareil photo, servo, relais) et d'appareils secteur via des prises Wi-Fi.

Contrôlable par **USB (PC)** et **Wi-Fi/BLE (application mobile)**.

Statut (05/10/2026) : **schéma complet et validé** dans EasyEDA (Blocs 1, 2, 3, 5, 5b, 8, 10, 12 servo, 13 relais et feuille ESP32) : netlist vérifiée net par net, ERC 0 erreur / 0 avertissement ; référence : `netlist/Netlist_Schematic1_2026-10-05.tel`. Moteur pas à pas, PWM lumière/servo et relais ×3 supprimés (prises Wi-Fi). Module capteur universel conçu (8 variantes). Implantation PCB v4 (175 × 125 mm, 4 couches) recalée sur la netlist de référence. Firmware non commencé.

---

## 1. Plateforme

- **MCU** : ESP32-S3-DevKitC-1, module WROOM-1-**N16R8** (16 Mo flash Quad, 8 Mo PSRAM Octal)
- **Cœurs** : dual-core Xtensa LX7, 240 MHz
- **Connectivité native** : Wi-Fi 2.4 GHz, Bluetooth LE, USB natif (device)
- Carte équipée de **2 ports USB-C** distincts sur le PCB :
  - Port USB-UART (pont série, GPIO 43/44) → programmation firmware / debug
  - Port USB natif (device, GPIO 19/20) → **contrôle PC** de l'application

## 2. Cahier des charges fonctionnel

| Paramètre | Valeur retenue |
|---|---|
| Canaux d'entrée (capteurs) | 6, génériques et reconfigurables (gain + seuil logiciels) |
| Types de capteurs supportés | Son, laser/optique, piézo, contact sec — adaptables via un front-end universel |
| Utilisation des entrées | Rarement simultanées ; les 6 canaux existent surtout pour la flexibilité de branchement, pas pour du traitement massivement parallèle en continu |
| Logique inter-canaux | Moteur de règles programmable (ET / OU / conditions avancées), pas de simple mapping 1:1 figé |
| Précision de déclenchement | ±10 µs ou mieux |
| Plage de délai programmable | De la µs à plusieurs secondes, résolution constante |
| Alimentation | Secteur (pas de contrainte de consommation) |
| Pilotage | USB (PC), Wi-Fi (page web servie par le boîtier et/ou app mobile), Bluetooth LE (contrôle de proximité / mode secours) |
| Affichage local | Aucun (tout passe par l'app / le logiciel PC) |

## 3. Sorties

| Sortie | Quantité | Indépendance | Étage de puissance |
|---|---|---|---|
| Flash (pulse simple) | 4 | Délai indépendant par canal | Opto HCPL-063L + inverseur 74LVC2G04 + 2N7002, côté isolé (VISO) |
| Déclenchement appareil photo | 1 prise, **focus + shutter séparés** (2 contacts) | Timing indépendant | Idem flash (isolé) |
| Électrovanne | 6 | Durée de pulse indépendante par canal | AO3400A + diode de roue libre SS14, PTC 1,1 A |
| Servo | 1 | Non critique (LEDC 50 Hz) | Rail 6 V / 3 A dédié (LM2596S-ADJ depuis le 12 V, coupable), signal par buffer 74AHCT1G125 5 V |
| Relais (contact sec) | 1 | Non critique (MCP23017) | HF32F/012-ZS3, 1RT 3 A / 30 V DC, basse tension uniquement |
| **Prises Wi-Fi (secteur)** | illimité | Non critique (50–500 ms) | Prises connectées commandées en local (HTTP/MQTT) — voir section 3.1 |

**Total sur la carte : 14 sorties** (4 flash + 2 caméra + 6 vannes + servo + relais). Supprimés : moteur pas à pas (Bloc 4), PWM lumière/servo (Bloc 7), relais ×3 sur RJ45 (Bloc 6). Une **lumière 12 V dimmable** se branche sur une sortie vanne libre (même étage MOSFET, PWM ≈ 20 kHz par le firmware, 1,1 A max) : rien à ajouter côté matériel.

### 3.1 Sorties Wi-Fi (remplacent les relais)

Les appareils secteur sans contrainte de timing (éclairage, petit compresseur, ventilateur, pompe…) sont pilotés par des **prises connectées Wi-Fi** commandées par l'ESP32 sur **son propre réseau** (point d'accès SoftAP avec DHCP : sans box, utilisable partout) :
- prises recommandées : Shelly Plug S / Shelly 1PM, ou prises Tuya reflashées Tasmota / ESPHome (API locale HTTP ou MQTT, sans cloud) ; **≥ 10 A pour le compresseur** (appel de courant au démarrage) ;
- aucun 230 V dans le boîtier (sécurité, pas de certification secteur à porter) ; nombre de sorties non limité ;
- latence 50–500 ms et variable : réservé au non critique. Les commandes sont envoyées **avant ou après** une séquence de déclenchement, jamais pendant (l'activité Wi-Fi ajoute de la gigue aux interruptions) ;
Pour un contact sec basse tension : la **sortie relais** de la carte (Bloc 13), ou un module relais 12 V sur une sortie vanne libre ; pour une charge 12 V DC (ruban LED, ventilateur, pompe) : directement sur une sortie vanne (12 V, 1,1 A, PWM possible, non isolée).
Détails : [docs/sorties-wifi.md](docs/sorties-wifi.md).

## 4. Classification des signaux : natif vs I2C/SPI

Principe directeur de l'architecture GPIO : **seul ce qui a une exigence de timing en µs reste en GPIO natif avec ISR/timer dédié** ; tout le reste (configuration, signaux lents) passe par un bus série (I2C/SPI) pour économiser les broches.

### 4.1 GPIO natifs (chemin critique) — affectation validée

Carte : **YD-ESP32-S3 N16R8** (copie de la DevKitC-1, même brochage ; pastille « RGB » laissée **ouverte** : GPIO48 libre). Aucune broche réservée ni de strapping utilisée (0, 3, 45, 46, 19, 20, 43, 44, 35-37 libres).

| Signal | GPIO | Broche symbole U105 |
|---|---|---|
| TLV_OUT_1 … TLV_OUT_6 (entrées, ISR) | 4, 5, 6, 7, 15, 16 | 4 à 9 |
| FLASH_1_CMD, FLASH_2_CMD, FLASH_3_CMD, FLASH_4_CMD | 17, 21, 39, 41 | 10, 27, 36, 38 |
| SHUTTER_CMD | 42 | 39 |
| GPIO_VALVE_1 … GPIO_VALVE_6 | 1, 2, 10, 38, 48, 47 | 41, 40, 16, 35, 29, 28 |
| SERVO_PWM (LEDC 50 Hz) | 13 | 19 |
| libre (réserve) | 14 | 20 |
| I2C_SDA / I2C_SCL | 8 / 9 | 12 / 15 |
| SPI_MOSI / SPI_SCK (PGA) | 11 / 12 | 17 / 18 |
| DAC2_LDAC (programmation adresse du 2e MCP4728) | 18 | 11 |
| **Total** | **24 utilisés** | GPIO14 et GPIO40 libres |

Alimentation : 5V de la carte via D101 (SS14, anti-retour USB) ; broches 3V3 de la carte non connectées (le 3,3 V périphérique vient du Bloc 5).

### 4.2 Périphériques I2C (non critique en timing)

```
ESP32-S3 (I2C : GPIO 8 = SDA, GPIO 9 = SCL, pull-ups 4,7 kΩ R108/R109)
   │
   ├── MCP23017 (0x20) — expandeur 16 E/S
   │      ├── GPA0-5 : CS_1 … CS_6 des 6 MCP6S91
   │      ├── GPA6   : FOCUS_CMD
   │      ├── GPB2   : RELAY_CMD (sortie relais)
   │      ├── GPB3   : SERVO_OFF (coupure du rail servo)
   │      ├── GPB5   : LED de statut (déportée, CN101)
   │      └── GPA7, GPB0-1, GPB4, GPB6-7 : réserve
   ├── MCP4728 #1 (0x60) — seuils THR_1 … THR_4 (LDAC à GND)
   ├── MCP4728 #2 (0x61, reprogrammée via LDAC = GPIO18) — THR_5, THR_6
   └── ADS7828 (0x48) — lecture des 6 lignes ID (ID_ADC_1 … 6)
```

### 4.3 Chaîne d'entrée universelle (×6, identiques) — v3

```
RJ45 (4-5 signal, 1-2 alim 5 V via PTC 200 mA, 7-8 ID, 3-6 GND)
   → TVS PESD5V0S1BB + tirage 4,7 kΩ optionnel (JP) + 1 MΩ vers GND
   → 2,2 kΩ série + écrêteur BAT54S + 100 pF
   → MCP6S91 — PGA SPI (gain ×1 à ×32), VREF = GND
   → TLV3501 — comparateur, hystérésis ≈ 48 mV (10 k / 680 k), seuil THR_n par DAC (filtré 1 k / 100 nF)
   → GPIO natif ESP32-S3 (interruption)
Ligne ID : tirage 10 kΩ vers +3V3, TVS, 1 kΩ série → ADS7828
```

- Signal attendu : **continu, unipolaire 0–3,3 V, ≈ 0 V au repos** (le couplage AC et la polarisation Vcc/2 de la v2 sont supprimés ; la mise en forme est faite dans le module capteur).
- **TLV3501** : ~4,5 ns, non limitant face à la latence ISR (~1-3 µs). **MCP6S91** : un PGA par entrée.

## 5. Architecture logicielle (cœurs / tâches)

```
CORE 0 (PRO_CPU)                          CORE 1 (APP_CPU) — dédié chemin critique
─────────────────────                     ──────────────────────────────────────
• Pile Wi-Fi/BLE                          • ISR GPIO ×6 (entrées capteurs), IRAM_ATTR
• Serveur de contrôle USB (CDC)           • esp_timer (dispatch ISR) pour toutes les sorties,
• Tâche I2C → DAC / expandeur / PGA         délais indépendants par canal
• Tâche NVS / logging                     • Priorité maximale, xTaskCreatePinnedToCore(...,1)
• Moteur de règles (évaluation non-µs)    • Aucune tâche Wi-Fi/BLE épinglée ici
```

**Point clé** : l'ESP32-S3 ne dispose que de 4 `gptimer` matériels, insuffisant pour 13 sorties potentiellement indépendantes et simultanées. Solution retenue : le service **`esp_timer`** (timers logiciels haute résolution µs, dispatch en mode ISR pour éviter la latence de changement de contexte FreeRTOS), qui gère un nombre illimité d'alarmes virtuelles sur un seul timer matériel sous-jacent.

## 6. Mémoire

| Ressource | Usage prévu |
|---|---|
| Flash 16 Mo | NVS (presets seuils/délais/règles), OTA double-slot, firmware, LittleFS (logs horodatés) |
| PSRAM 8 Mo Octal | Non-critique uniquement : buffers réseau, historique de déclenchements — **jamais** de code/donnée du chemin temps réel (latence d'accès variable) |

## 7. Contraintes GPIO de la carte N16R8 (rappel)

- **GPIO 26-37** : indisponibles (bus interne flash/PSRAM Octal — non sortis sur le module WROOM)
- **GPIO 33-34** : non sortis sur le module, à ne jamais adresser même en logiciel
- **GPIO 0, 3, 45, 46** : broches de strapping — utilisables prioritairement en sortie, prudence en entrée
- **GPIO 19-20** : réservées USB natif (contrôle PC)
- **GPIO 43-44** : réservées USB-UART (programmation/debug)
- Tout code du chemin critique (ISR, callbacks `esp_timer`) doit être marqué `IRAM_ATTR` pour éviter les cache-miss flash

## 8. Comparatif marché (état à date de rédaction)

| Aspect | Marché (StopShot Studio = référence haut de gamme) | TriggerFlow |
|---|---|---|
| Sorties totales | 12 max | 14 + prises Wi-Fi |
| Sorties flash indépendantes natives | 1 (accessoire externe pour plus) | 4 |
| Axe motorisé intégré | Aucun produit identifié n'en propose | Servo dédié (rail 6 V), pas d'axe pas à pas |
| Entrées reconfigurables | Fixes ou peu nombreuses | 6, gain/seuil logiciels |
| Contrôle sans fil | Oui chez MIOPS, non chez StopShot Studio (USB uniquement) | Oui (Wi-Fi/BLE) + USB |

### Fonctionnalités confirmées au cahier des charges (logiciel, aucun impact matériel)
- **Mode "sorties désactivées"** : verrou logiciel global (armé/désarmé) évalué par le moteur de règles avant tout déclenchement. Décision actée : **désarmement logiciel uniquement via app/PC**, pas d'interrupteur physique de sécurité en façade.
- **Outils de mesure** : vitesse de projectile (calculée à partir des timestamps de deux entrées capteur sur une même trajectoire) et latence de déclenchement de l'appareil photo. Repose entièrement sur l'infrastructure de timestamping déjà prévue par les ISR — aucun composant supplémentaire.

### Point encore ouvert
- Fallback de contrôle local minimal (LED de statut) en cas de perte Wi-Fi/BLE sur le terrain — non tranché

## 9. Performance et budget de latence

### 9.1 Chaîne de latence (hors propagation physique du signal capteur)

| Étage | Latence typique |
|---|---|
| TLV3501 (comparateur) | ~5-7 ns |
| MCP6S91 (PGA, bande passante 1-18 MHz selon gain) | ~350 ns à gain faible ; **non vérifié à gain ×32** (la bande passante chute avec le gain — pourrait approcher 1-2 µs, à confirmer au datasheet avant routage, surtout sur les canaux à fort gain type micro) |
| Interruption GPIO ESP32-S3 | ~1-3 µs |
| Callback `esp_timer` (dispatch ISR) | voir 9.2 |
| Sortie GPIO physique | ~1-3 µs |
| **Total chemin électronique** | **~2 à 10 µs**, conforme à l'objectif ±10 µs |

### 9.2 Contrainte technique vérifiée sur `esp_timer`

- Mode `ESP_TIMER_ISR` : plancher d'environ **20 µs** pour un timer one-shot (tout délai demandé en dessous est en pratique dispatché à ~20 µs).
- Timer périodique : période minimale d'environ **50 µs** (inadapté aux signaux périodiques rapides : on utilise LEDC/RMT).

**Décisions d'architecture qui en découlent :**
- **Signaux périodiques (servo 50 Hz, PWM des vannes / lumière)** : sur LEDC (périphérique matériel dédié), jamais sur `esp_timer`.
- **Délais de déclenchement (flash/vannes/shutter)** : architecture hybride — délai < ~20 µs routé vers l'un des 4 `gptimer` matériels natifs (précision garantie, sans plancher), délai ≥ ~20 µs routé vers `esp_timer` (nombre de canaux illimité). Choix fait dynamiquement par le firmware selon le délai demandé.

### 9.3 Point de validation en phase de test (non tranché sur plan)
- Impact réel du trafic Wi-Fi/BLE sur le jitter des ISR du Core 1 : pas de chiffre garanti par la documentation Espressif, dépend du trafic au moment T. Mitigé par l'épinglage Core 1 dédié et le réglage du niveau de priorité d'interruption d'`esp_timer` (1 à 3). **À mesurer à l'oscilloscope sur le premier prototype**, jitter entrée→sortie avec Wi-Fi actif vs coupé.

### 9.4 Exemple d'application — impact du choix de capteur sur la précision finale
Cas : carabine à air comprimé, plomb à ~250 m/s.
- **Capteur son** : le délai de propagation acoustique (343 m/s) domine très largement le budget — à 30 cm du canon, le plomb a déjà parcouru ~22 cm avant déclenchement, contre <1 mm imputable à l'électronique. Le placement du capteur compte infiniment plus que la précision électronique pour ce cas d'usage.
- **Capteur laser (photodiode PIN + transimpédance)** : élimine le délai de propagation, ramène le déplacement du plomb pendant le délai de déclenchement à ~0,5-1,25 mm (inférieur au diamètre du plomb). Le facteur limitant devient alors la **durée d'éclair du flash** lui-même, pas l'électronique de déclenchement.
- Conclusion générale : pour les capteurs son, privilégier les cas où la source sonore est proche du sujet photographié ; pour les projectiles très rapides, privilégier systématiquement une détection optique (laser/photodiode) plutôt qu'acoustique.

## 11. Connectique — RJ45 généralisé

Connecteurs **RJ45 blindés 10 broches HanXia HX-RJ45 90 5631-1x1 (LCSC C25168869)** pour toutes les liaisons faible courant ; vannes, servo, relais et alimentation sur connecteurs dédiés.

**11 connecteurs RJ45 au total** : 6 entrées capteur + 4 flash + 1 appareil photo (focus + shutter). Les RJ45 « contact sec » (Bloc 6) et PWM (Bloc 7) sont supprimés ; le servo (barrette 3 points) et le relais (bornier COM / NO / NC) ont leurs propres connecteurs.

### Brochage

| Broches | Entrées capteur (×6) | Flash (×4) | Appareil photo (×1) |
|---|---|---|---|
| 1-2 | V_SENS 5 V (PTC 200 mA) | non connectées | non connectées |
| 3 | GND | non connectée | **FOCUS** |
| 4 | Signal capteur | **FLASH_n** (drain 2N7002) | **SHUTTER** |
| 5 | Signal capteur | **VISO_GND** (retour) | VISO_GND (retour shutter) |
| 6 | GND | non connectée | VISO_GND (retour focus) |
| 7-8 | ID (code du capteur) | non connectées | non connectées |
| 9-10 (blindage) | GND | **non connectées** | **non connectées** |

- Sorties flash / appareil photo : chaque signal est dans la même paire que son retour ; **retour sur VISO_GND, jamais sur GND** ; blindage non connecté (sinon la façade métallique relierait VISO_GND à GND) ; câble UTP conseillé.
- Polarité côté flash : broche 4 = + de la synchro, broche 5 = −. TVS SMF24A sur chaque sortie : flashs jusqu'à 24 V de synchro (au-delà : adaptateur type Safe-Sync).

### Auto-détection du type de capteur

Résistance de codage entre ID (7-8) et la masse dans le module capteur, tirage 10 kΩ vers 3,3 V sur la carte, lecture par l'ADS7828 (référence interne 2,5 V). **12 codes fiables** dans le pire cas (tolérances 1 %, rail ±3 %, décalage de masse 40 mV) :

| Code | R_ID | Code | R_ID |
|---|---|---|---|
| 1 | 0 Ω | 7 | 3 kΩ |
| 2 | 220 Ω | 8 | 4,3 kΩ |
| 3 | 510 Ω | 9 | 6,2 kΩ |
| 4 | 910 Ω | 10 | 8,2 kΩ |
| 5 | 1,5 kΩ | 11 | 12 kΩ |
| 6 | 2,2 kΩ | 12 | 18 kΩ |

Ligne ouverte (lecture pleine échelle) = aucun capteur. Affectation des codes aux variantes du module capteur universel : voir BOM-netlist.md, Bloc 9.

## 13. Connecteurs vannes, servo, relais et alimentation

### Connecteurs puissance (hors RJ45) — famille GX12

Choix retenu : **connecteurs circulaires aviation GX12** pour les vannes et l'alimentation, en remplacement du JST-XH envisagé initialement — plus robustes pour un usage en façade manipulé sur le terrain (verrouillage à vis, tenue ~3-5A par broche selon variante, bien au-dessus du besoin), alors que le JST-XH est plutôt pensé pour du câblage interne de carte.

| Élément | Connecteur | Notes |
|---|---|---|
| Électrovanne (×6) | GX12 2 broches | +/- alimentation vanne |
| Servo | bornier 3 points 5,08 mm KF128 (C474953) | 1 = GND, 2 = V_SERVO 6 V, 3 = signal (rallonge servo à câbler) |
| Relais | bornier 3 points 5,08 mm KF128 (C474953) | COM / NO / NC, basse tension uniquement |
| Alimentation générale (entrée DC) | GX12 ou GX16 selon courant total | Voir section alimentation ci-dessous |

**Périmètre délibérément limité** : le GX12 reste réservé aux connecteurs de puissance. Les 11 connecteurs signal (entrées capteur + sorties flash / appareil photo) restent en **RJ45** (voir section 11) — meilleur compromis coût/disponibilité de câbles préfabriqués/qualité de signal (paires torsadées) pour du faible courant, l'étanchéité renforcée du GX12 n'étant pas jugée nécessaire pour ces liaisons dans l'usage prévu. Bénéfice supplémentaire : les deux familles de connecteurs sont physiquement incompatibles entre elles, ce qui empêche tout branchement erroné (vanne sur un port capteur, par exemple).

### Architecture d'alimentation (Bloc 5 et 5b, validés)

Alimentation externe : **bloc secteur 12 V, 5 A minimum (60 W)**, pas de 230 V dans le boîtier.

```
Bloc secteur 12 V → J111 → F111 (6,3 A T) → Q111 AO4407A (anti-inversion) → +12V
                                                  D111 SMBJ15A (TVS)        │
      ┌───────────────────────────────────────────────────────────────────┤
      ▼                                                                    ▼
  vannes (F91-96), relais (K131), U121 LM2596S-ADJ          U111 LM2596S-5.0 → +5V (3 A)
  → V_SERVO 6 V / 3 A (coupable, servo)                     ├→ DevKit (via D101), capteurs (F11-61), buffer servo
                                                             ├→ U112 AMS1117-3.3 → +3V3 (électronique)
                                                             └→ U113 B0505S-1WR3 (isolé) → U114 AMS1117-3.3 → VISO_3V3 / VISO_GND
                                                                                         (sorties flash / appareil photo)
```

- Le 3,3 V de la carte ESP32 n'alimente que le module ; tout le reste est sur +3V3 (U112).
- Le côté isolé (VISO) n'a **aucun conducteur commun** avec GND : il protège l'ESP32 et les entrées analogiques des perturbations des flashs, évite les boucles de masse entre boîtier, appareil photo et flashs secteur.

## 14. Synoptique général du montage

Plutôt qu'un seul diagramme complet (illisible avec autant de blocs), voici la même architecture découpée en 4 schémas simples, chacun centré sur une seule idée.

### 14.1 Vue d'ensemble

```
   Alimentation 12V DC (bloc secteur externe)
                  │
                  ▼
   ┌─────────────────────────────────┐
   │   ESP32-S3-DevKitC-1 (N16R8)     │
   │                                  │
   │   Core 0 : réseau / contrôle     │
   │   Core 1 : temps réel (critique) │
   └────────────┬─────────────┬───────┘
                │             │
                ▼             ▼
      6 entrées capteurs   14 sorties + prises Wi-Fi
      (connecteurs RJ45)   (RJ45 pour le signal,
                            GX12 pour la puissance)
```

### 14.2 Chaîne d'une entrée capteur (répétée ×6, identique)

```
Capteur          Ampli à gain        Comparateur         ESP32-S3
(RJ45)     →     programmable   →    + seuil réglable →  (interruption,
                  MCP6S91 (SPI)       TLV3501              Core 1)
                                      + DAC (I2C)
```

### 14.3 Qui parle à qui sur les bus de configuration

```
                         ┌── MCP4728 ×2  → seuils des 6 comparateurs
ESP32-S3 ── I2C ──┼── MCP23017    → focus caméra, CS des PGA, relais,
                         │              coupure servo, LED de statut
                         └── ADS78xx    → lecture ID des capteurs (auto-détection)

ESP32-S3 ── SPI ──── 6× MCP6S91  → réglage du gain de chaque entrée
```

*(Ces bus ne portent que de la configuration — rien ne transite dessus pendant un déclenchement, donc aucun impact sur la précision temporelle.)*

### 14.4 Les sorties, groupées par nature

```
Core 1 (temps réel, GPIO natif)          Expandeur I2C (non critique)
─────────────────────────────            ────────────────────────────
4× Flash            (RJ45, isolé)         1× Relais (bornier, contact sec)
1× Caméra focus+shutter (RJ45, isolé)    Prises Wi-Fi secteur (réseau de l'ESP32)
6× Électrovanne      (GX12)
1× Servo             (rail 6 V dédié, LEDC 50 Hz)
```

**Ce qu'il faut retenir de ces 4 schémas** :
- Le chemin capteur → déclenchement (14.2 + 14.4 colonne de gauche) est le seul qui doit rester ultra-rapide — tout le reste (14.3) ne fait que régler des paramètres, jamais pendant une prise.
- Deux familles de connecteurs bien séparées : RJ45 pour tout ce qui est signal, GX12 pour tout ce qui est puissance — impossible de les confondre en branchant.

## 15. Ouvert / non tranché

- **Schéma** : terminé (référence du 05/10). Points restants : R123 3,9 kΩ (C23018 en rupture, secours 39 k / 10 k), D101 = SS14 C2480 à confirmer, barrettes 1×22 de la carte ESP32.
- **Vérifications** : écartement réel des rangées de la YD-ESP32-S3 ; empreintes réelles (RJ45, DevKit, relais) avant de figer le placement.
- **PCB** (voir `pcb/` et `docs/pcb-checklist.md`) : cotes réelles du RJ45 HanXia C25168869 et de la DevKit, orientation broche 1 des empreintes, boîtier plastique ou métallique (métallique → WROOM-1U à antenne externe, à décider avant routage), raccordement des trous de fixation à la masse.
- **Connecteur vanne** : HX25003-2A droit ou coudé ; GX12 de façade (2 ou 4 broches).
- **Bande passante MCP6S91 à gain ×32** à confirmer à la datasheet.
- **Limite connue** : au-delà de 4 sorties simultanées à délai < 20 µs, plancher `esp_timer` (~20 µs).
- **Module capteur universel** : saisie EasyEDA et PCB (schéma KiCad dans `kicad/module_capteur/`).
- **Firmware** : moteur de règles, protocole USB CDC / web / BLE, Wi-Fi en point d'accès + pilotage des prises, mode « lumière » des sorties vannes, servo (coupure SERVO_OFF au démarrage), lecture ID et presets par variante, reprogrammation d'adresse du 2e MCP4728.
- **Mécanique** : boîtier, façade (11 RJ45, 6 GX12, entrée 12 V, servo, relais, 2 USB-C).

## 16. Implantation PCB

Carte **175 × 125 mm, 4 couches** (JLC 1,6 mm, 1 oz) : couche 1 composants et signaux courts, couche 2 **GND plein** (îlot VISO séparé), couche 3 plages d'alimentation (+12V au quart droit, +3V3 au centre, +5V en bandes le long des bords), couche 4 signaux longs.

Zones : sorties isolées au bord arrière gauche (barrière d'isolation à y = 40 mm, seuls les 3 HCPL-063L et le B0505S la traversent, ≥ 3 mm sans cuivre sur toutes les couches) ; relais et alimentation au bord arrière droit ; ESP32 à gauche avec l'USB-C au bord et l'antenne vers l'intérieur (zone sans cuivre + fente) ; bus I2C au centre ; couloir de bus de 8 mm en couche 4 ; servo et vannes (2 rangées de 3) à droite ; 6 entrées capteur au bord avant (bandes de 18 mm). Placement de 287 composants vérifié par script (chevauchements, zone antenne, barrière, trous M3).

Détails, fichier de positions et scripts : [pcb/README.md](pcb/README.md) ; checklist : [docs/pcb-checklist.md](docs/pcb-checklist.md).
