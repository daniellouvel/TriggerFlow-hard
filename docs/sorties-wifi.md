# Sorties Wi-Fi — prises connectées (remplacent le Bloc 6 « relais »)

Décision du 03/10/2026 (révisée le 04/10) : les 3 sorties relais sur RJ45 sont supprimées ; **une seule sortie relais** est conservée sur bornier (Bloc 13). Les usages prévus (éclairage, petit compresseur) sont des appareils **secteur sans contrainte de timing** : ils sont pilotés par des prises connectées Wi-Fi commandées par l'ESP32 en réseau local.

## Pourquoi

- **Sécurité** : aucun 230 V dans le boîtier ; la commutation secteur est faite par un appareil déjà certifié.
- **Souplesse** : nombre de sorties non limité, pas de câble supplémentaire vers le boîtier.
- **Carte simplifiée** : 3 relais, 3 transistors, 3 RJ45 en moins (12 RJ45 au lieu de 15) ; lignes MCP23017 GPB2-GPB4 libérées.

## Matériel recommandé

| Usage | Prise | Remarque |
|---|---|---|
| Éclairage | Shelly Plug S, Shelly 1 / 1PM (encastré), ou prise Tuya reflashée Tasmota / ESPHome | API locale obligatoire (sans cloud) |
| Petit compresseur | Prise **≥ 10 A** (Shelly Plug S 10 A / 2 500 W, Shelly 1PM 16 A) | Moteur : fort appel de courant au démarrage |

## Réseau : l'ESP32 crée son propre Wi-Fi

L'ESP32 fonctionne en **point d'accès (SoftAP)** : il crée le réseau « TriggerFlow » et sert de serveur DHCP. Les prises s'y connectent directement, **sans box ni routeur : fonctionne partout**, y compris en extérieur (là où il y a une prise de courant pour l'appareil commandé). Le téléphone de l'utilisateur rejoint le même réseau pour l'application web. En option, mode AP + STA : connexion simultanée à la box domestique quand elle est disponible (mises à jour).
Limites : 4 clients par défaut, ~10 en configuration ; portée de quelques dizaines de mètres.

## Commande depuis l'ESP32

- Réseau local uniquement (réseau de l'ESP32), adresses IP fixes attribuées par le DHCP de l'ESP32 (ou mDNS).
- Shelly (Gen1) : `GET http://<ip>/relay/0?turn=on|off` ; Shelly Gen2/Plus : `GET http://<ip>/rpc/Switch.Set?id=0&on=true|false`.
- Tasmota : `GET http://<ip>/cm?cmnd=Power%20On|Off` ; ou MQTT (`cmnd/<topic>/POWER`).
- ESPHome : API REST du serveur web embarqué ou MQTT.
- Variante possible : passer par un serveur Home Assistant (API REST locale) si l'installation en dispose.

## Contraintes firmware

- **Latence 50–500 ms, variable** : réservé aux actions non critiques (allumer / éteindre avant ou après une séance, couper l'éclairage d'ambiance avant une prise au flash…).
- Les commandes sont envoyées **avant ou après** une séquence de déclenchement, **jamais pendant** : l'activité Wi-Fi (cœur 0) peut ajouter de la gigue aux interruptions du cœur 1.
- Gestion des erreurs : délai d'attente court (≈ 1 s), retour d'état affiché dans l'application, pas de blocage du moteur de règles si une prise ne répond pas.

## Besoins qui ne passent pas par une prise Wi-Fi

| Besoin | Solution |
|---|---|
| Charge 12 V DC (ruban LED, ventilateur, pompe, électrovanne en plus) | une **sortie vanne libre** : 12 V, 1,1 A (PTC), PWM possible, non isolée, broche 1 = +12V, broche 2 = commutée à la masse |
| Contact sec basse tension (entrée d'un autre appareil) | **module relais 12 V** du commerce branché sur une sortie vanne libre |
| Contact isolé basse tension DC, polarisé (≤ 24 V, quelques centaines de mA) | une sortie flash libre (Bloc 2, isolée) |
| Timing précis (< 1 ms) | sorties de la carte uniquement (flash, vannes, servo) |
| Contact sec embarqué, sans configuration réseau | **sortie relais** de la carte (Bloc 13, HF32F, 3 A / 30 V DC, basse tension uniquement) |
| Lumière 12 V dimmable | une **sortie vanne libre** en mode « lumière » (PWM ≈ 20 kHz, 1,1 A max) |
