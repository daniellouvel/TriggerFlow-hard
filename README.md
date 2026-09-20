# TriggerFlow — Architecture matérielle

Boîtier de déclenchement généraliste pour photographie haute vitesse : détection multi-capteurs, moteur de règles programmable, pilotage de sorties variées (flash, électrovannes, moteur pas à pas, contacts secs, appareil photo).

Contrôlable par **USB (PC)** et **Wi-Fi/BLE (application mobile)**.

Statut : cahier des charges fonctionnel et architecture matérielle figés. Schéma électronique détaillé et firmware non encore développés.

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
| Pilotage | Application mobile (Wi-Fi/BLE) **et** logiciel PC (USB) |
| Affichage local | Aucun (tout passe par l'app / le logiciel PC) |

## 3. Sorties

| Sortie | Quantité | Indépendance | Étage de puissance |
|---|---|---|---|
| Flash / obturateur (pulse simple) | 4 | Délai indépendant par canal | Optocoupleur |
| Électrovanne | 6 | Durée de pulse indépendante par canal | MOSFET + diode de roue libre (charge inductive) |
| Moteur pas à pas | 1 | STEP en natif, DIR/EN non critiques | Driver dédié (A4988 / DRV8825 / TMC2209) — pas de retour de position (rotation libre) |
| Déclenchement appareil photo | 2 sorties, **focus + obturation séparés** (4 contacts au total) | Timing indépendant | Optocoupleur par contact |
| Contact sec / relais générique | 3 | Non critique | Relais ou opto-triac |
| PWM lumière continue / servo | 1 | Non critique | MOSFET puissance ou alim dédiée régulée |

**Total : 16 sorties fonctionnelles.**

## 4. Classification des signaux : natif vs I2C/SPI

Principe directeur de l'architecture GPIO : **seul ce qui a une exigence de timing en µs reste en GPIO natif avec ISR/timer dédié** ; tout le reste (configuration, signaux lents) passe par un bus série (I2C/SPI) pour économiser les broches.

### 4.1 GPIO natifs (chemin critique)

| Fonction | GPIO natifs |
|---|---|
| 6 entrées capteurs (ISR) | 6 |
| 4 sorties flash | 4 |
| 6 sorties électrovannes | 6 |
| STEP moteur pas à pas | 1 |
| 2 sorties shutter caméra (déclenchement) | 2 |
| Bus I2C (SDA/SCL — DAC + expandeur) | 2 |
| Bus SPI (SCK/MOSI — vers les 6 PGA) | 2 |
| **Total natif** | **23 / ~25 GPIO propres disponibles** |

### 4.2 Périphériques I2C (non critique en timing)

```
ESP32-S3 (I2C : GPIO 8 = SDA, GPIO 9 = SCL)
   │
   ├── MCP4728 ×2 — DAC seuils comparateurs (8 canaux, 6 utilisés + 2 en réserve)
   └── MCP23017 — Expandeur 16 E/S
          ├── DIR + EN moteur pas à pas (2)
          ├── Contact sec / relais ×3 (3)
          ├── Focus caméra ×2 (2)
          ├── PWM lumière/servo (1)
          └── Chip Select des 6 MCP6S91 (6)
          ────────────────────────────────
          14 / 16 lignes utilisées
```

### 4.3 Chaîne d'entrée universelle (×6, identiques)

```
Connecteur capteur
   → Protection d'entrée (clamp diodes + résistance série)
   → Couplage AC/DC sélectionnable (micro/piézo = AC, photodiode/contact sec = DC)
   → MCP6S91 — Ampli à gain programmable SPI (gains ×1 à ×32, 8 pas)
   → TLV3501 — Comparateur avec hystérésis externe (résistances R1/R2), seuil piloté par DAC
   → GPIO natif ESP32-S3 (interruption)
```

- **TLV3501** choisi pour sa vitesse de propagation (~4.5 ns typ.) : totalement non limitant face à la latence ISR de l'ESP32 (~1-3 µs).
- **MCP6S91** : PGA mono-canal, SPI, gains +1/+2/+4/+5/+8/+10/+16/+32 V/V — un ampli dédié par entrée (pas de mutualisation) pour garantir que n'importe quelle combinaison de capteurs puisse fonctionner ensemble dans le moteur de règles.

## 5. Architecture logicielle (cœurs / tâches)

```
CORE 0 (PRO_CPU)                          CORE 1 (APP_CPU) — dédié chemin critique
─────────────────────                     ──────────────────────────────────────
• Pile Wi-Fi/BLE                          • ISR GPIO ×6 (entrées capteurs), IRAM_ATTR
• Serveur de contrôle USB (CDC)           • esp_timer (dispatch ISR) pour les 16 sorties,
• Tâche I2C → DAC / expandeur / PGA         délais indépendants par canal
• Tâche NVS / logging                     • Priorité maximale, xTaskCreatePinnedToCore(...,1)
• Moteur de règles (évaluation non-µs)    • Aucune tâche Wi-Fi/BLE épinglée ici
```

**Point clé** : l'ESP32-S3 ne dispose que de 4 `gptimer` matériels, insuffisant pour 16 sorties potentiellement indépendantes et simultanées. Solution retenue : le service **`esp_timer`** (timers logiciels haute résolution µs, dispatch en mode ISR pour éviter la latence de changement de contexte FreeRTOS), qui gère un nombre illimité d'alarmes virtuelles sur un seul timer matériel sous-jacent.

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
| Sorties totales | 12 max | 16 |
| Sorties flash indépendantes natives | 1 (accessoire externe pour plus) | 4 |
| Axe motorisé intégré | Aucun produit identifié n'en propose | Oui (moteur pas à pas) |
| Entrées reconfigurables | Fixes ou peu nombreuses | 6, gain/seuil logiciels |
| Contrôle sans fil | Oui chez MIOPS, non chez StopShot Studio (USB uniquement) | Oui (Wi-Fi/BLE) + USB |

### Fonctionnalités identifiées chez la concurrence, à considérer pour le firmware (aucun impact matériel)
- Mode "sorties désactivées" pour tester/calibrer sans risque de déclenchement accidentel (sécurité, notamment vannes + moteur)
- Fallback de contrôle local minimal (LED de statut) en cas de perte Wi-Fi/BLE sur le terrain
- Outils de mesure (vitesse de projectile entre 2 capteurs, latence de déclenchement de l'appareil) — réalisable en pur logiciel avec le matériel existant

## 9. Ouvert / non tranché

- Schéma électronique détaillé (valeurs R1/R2 hystérésis, choix MOSFET/driver stepper, dimensionnement alimentation)
- Type de connecteurs entrées/sorties (jack 3.5/6.35 mm vs bornier à vis)
- Connecteur d'alimentation secteur et tension de distribution interne (12V vs 5V selon vannes/moteur)
- Détail du moteur de règles (état de l'art : simple ET/OU vs langage de règles avec fenêtres temporelles/compteurs)
- Boîtier physique / mécanique (hors découpe façade USB-C déjà actée)
- Protocole de communication app/PC ↔ boîtier (USB CDC + Wi-Fi/BLE)
