Lance le script de vérification de compatibilité QGIS et génère un rapport markdown.

## Instructions

1. Exécute le script :
   ```
   python tools/qgis_compatibility_checker.py --severity info --format markdown --output tools/compatibility_report.md $ARGUMENTS
   ```
   `$ARGUMENTS` contient les arguments optionnels passés par l'utilisateur (ex: `--min-version 3.28 --max-version 3.40`).

2. Lis le fichier `tools/compatibility_report.md` généré et affiche son contenu à l'utilisateur.

3. Si des erreurs ou warnings sont trouvés, propose des pistes de correction pour chaque finding.
