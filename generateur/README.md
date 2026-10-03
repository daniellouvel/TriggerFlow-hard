# Générateur de feuilles KiCad (.kicad_sch v20260306)

Scripts Python qui produisent des feuilles KiCad propres, avec fils tirés sur les positions réelles des broches, puis vérifient la netlist par géométrie.

| Fichier | Rôle |
|---|---|
| `kicadgen.py` | moteur : symboles, fils, jonctions, étiquettes, zones, sérialisation |
| `kicad_net.py` | relit un .kicad_sch et calcule la netlist (`python3 kicad_net.py feuille.kicad_sch`) |
| `render.py` | aperçu PNG approximatif (`python3 render.py feuille.kicad_sch apercu.png [a3]`) |
| `libextract.py` | extrait et aplatit des symboles des bibliothèques KiCad standard (paquet Ubuntu `kicad-symbols`) |
| `src_*.kicad_sch` | bibliothèques de symboles embarquées utilisées par chaque feuille |
| `bloc5.py` / `build_bloc5.py` | Bloc 5 — alimentation |
| `bloc5b.py` / `build_bloc5b.py` | Bloc 5b — alimentation isolée |
| `capteur.py` / `build_capteur.py` | module capteur universel |

Usage : `python3 build_bloc5.py sortie/` ; variante EasyEDA (sans champs cachés) : `EASYEDA=1 python3 build_bloc5.py sortie/`.
Dépendances : `pip install sexpdata matplotlib`.
Non vérifié : ouverture dans KiCad 10 et ERC (à faire côté utilisateur).
