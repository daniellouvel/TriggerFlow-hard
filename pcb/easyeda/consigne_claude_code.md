# Consigne à donner à Claude Code (session neuve, easyeda-copilot actif, PCB TriggerFlow ouvert sur une copie)

Exécute le script `triggerflow_plans_et_zones.js` dans l'éditeur PCB EasyEDA Pro, en deux temps :
1. D'abord avec `DRY_RUN = true` : montre-moi la ligne « Calibration » (1 mm doit valoir 39,37 unités si l'API est en mil, échelles X et Y égales en valeur absolue).
2. Si la calibration est cohérente, passe `DRY_RUN = false` et exécute. Montre-moi le journal complet (lignes OK / ÉCHEC).
Au premier appel d'API qui échoue ou n'existe pas (par exemple `eda.pcb_PrimitivePad.getAll` ou le format du polygone), arrête-toi et dis-moi lequel, sans improviser de contournement.
Ne modifie rien d'autre dans le projet.
