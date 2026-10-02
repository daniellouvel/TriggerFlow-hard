# Méthode EasyEDA Pro + Claude Code (testée le 30/09 - 01/10/2026)

## Résultat
Le Bloc 2 (flash / caméra) a été généré dans EasyEDA Pro avec easyeda-copilot. Netlist exportée et vérifiée par comparaison avec la référence : conforme (seuls les noms de nets INPUT_A/B changent). Mise en page lisible, quelques retouches manuelles de textes à faire.

## Ce qui a marché
- Outils : extension EasyEda Copilot (biosshot) dans EasyEDA Pro application bureau (>= 3.2.149) + serveur MCP `easyeda-copilot` ajouté avec `claude mcp add --scope user easyeda-copilot -- npx easyeda-copilot-mcp`.
- Case « Allow interactive with external » cochée dans Extensions Manager > EasyEda Copilot > Config (et pour Run API Gateway).
- Menu Advanced > Copilot > MCP = interrupteur de recherche du serveur (scan stopped = arrêté, recliquer).
- Session Claude Code neuve (/clear ou /exit puis claude), projet EasyEDA vide, feuille de schéma active, aucun dialogue ouvert.
- Pièces données par référence LCSC explicite (jamais par nom : l'agent a posé un ESP32 et des AMS1117 à la place de l'optocoupleur).
- Consigne « au premier échec d'appel, arrête-toi et dis-moi lequel ».
- Vérification : exporter la netlist (menu Export) et la comparer soi-même. Ne JAMAIS se fier au résumé de l'agent (il a annoncé « généré ✓ » sans rien dessiner, et « netlist intacte » avant d'exécuter).

## Ce qui n'a pas marché
- Déplacer des composants avec SCH_PrimitiveComponent.modify : les fils et labels ne suivent pas, le schéma est cassé.
- easyeda-enhanced-schematic-skill (officiel) : place des cadres colorés mais superpose les textes ; à sortir du dossier ~/.claude/skills pour qu'il ne soit pas choisi.
- serveurs jlcmcp / easyeda-mcp-pro : pas d'outil de placement précis côté schéma. Désactiver les serveurs MCP EasyEDA quand on ne s'en sert pas.
- Mise en page automatique ou demande de réarrangement : toujours refaire à la souris (les fils suivent dans l'éditeur).

## Références LCSC vérifiées
| Pièce | Référence LCSC |
|---|---|
| HCPL2631 (DIP-8, onsemi) | C16384 |
| 2N7002 SOT-23 | C8545 |
| Résistance 270 Ohm 0603 | C22966 |
| Résistance 10 kOhm 0603 | C25804 |
| Résistance 220 Ohm 0603 | C22962 |
| AO3400A SOT-23 | C20917 |
| Diode SS14 SMA | C2480 |
Les références du doc « Bloc 3 - Sorties Électrovannes » (C160122, C25057, C25761) ne sont pas fiables : utiliser le tableau ci-dessus.

## Bloc 3 : attention
Le fichier sortie_electrovanne.kicad_sch d'origine a ses connexions cassées (résistances et grilles non reliées, diode court-circuitée). Refaire le bloc depuis la netlist voulue (voir la consigne dans la conversation du 01/10/2026) : GPIO -> 220 Ohm -> grille ; pull-down 10 kOhm grille -> GND ; source -> GND ; drain -> VALVE_OUT ; SS14 flyback (cathode V12, anode drain). Les descriptions « pull-up » du fichier d'origine sont erronées.

## Générateur KiCad
Reste la référence pour des schémas propres et vérifiés (claude/generateur/). Variante EasyEDA : EASYEDA=1 python3 build_project.py retire les champs cachés (Description, Datasheet, Footprint) qu'EasyEDA affiche à l'import.
