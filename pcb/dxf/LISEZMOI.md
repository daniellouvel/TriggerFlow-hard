# DXF TriggerFlow pour EasyEDA Pro

Unité : mm. Origine DXF : coin AVANT gauche de la carte (Y vers l'arrière).
Le placement (`pcb/placement_TriggerFlow.csv`) a son origine au coin ARRIÈRE gauche, y vers l'avant :
Y_dxf = 125 − y_placement.

| Fichier | Contenu | Couche EasyEDA à choisir à l'import |
|---|---|---|
| TriggerFlow_1_contour.dxf | contour 175 × 125 mm (coins R2), fente sous l'antenne (12 × 24 mm), trous H1 et H5 Ø 3,2 non métallisés | Contour de carte (Board Outline) |
| TriggerFlow_2_trous_GND.dxf | repères de H2, H3, H4, H6, H7 (option) : perçage Ø 3,2, pastille Ø 6, dégagement Ø 7 | Document ; puis poser à chaque repère une pastille traversante Ø 3,2 / 6 mm reliée au net GND (ou un trou de fixation M3) |
| TriggerFlow_3_zones_interdites.dxf | zone antenne (x 58–86) et bande de 2 mm entre les broches 2 et 3 de U113 | Document ; puis tracer par-dessus des zones interdites (cuivre, toutes couches) |
| TriggerFlow_4_zones_document.dxf | zones du plan, barrière d'isolation, couloir de bus, rangée de vias de couture | Document (repères pour le routage) |
| TriggerFlow_5_couche3_plages.dxf | contours des plages de la couche 3 : VISO_3V3, +12V, +3V3, +5V | Document, ou Interne 2 comme guide ; puis créer les remplissages de cuivre par-dessus en leur donnant le bon net |

Ordre conseillé : 1 (contour) → 2 et 3 → 4 et 5 → mise à jour du PCB depuis le schéma → placement.
Après l'import, vérifier une cote connue (largeur 175 mm, H6 à 66 mm du bord gauche) avant de continuer.
La plage +3V3 du fichier 5 inclut la zone antenne : la zone interdite du fichier 3 doit la découper.
