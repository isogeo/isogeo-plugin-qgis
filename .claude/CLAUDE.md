# Isogeo QGIS Plugin

Plugin QGIS de recherche et d'ajout de données géographiques via l'API Isogeo.

## Commandes de build

Tout passe par `make.bat` (Windows). Commandes individuelles :

```batch
# 1. Mettre à jour les sources de traduction (.ts) depuis le code Python et les .ui
pylupdate5 -noobsolete -verbose isogeo_search_engine.pro

# 2. Compiler les traductions .ts → .qm (une par langue)
qt5-tools lrelease .\i18n\isogeo_search_engine_fr.ts
qt5-tools lrelease .\i18n\isogeo_search_engine_en.ts
qt5-tools lrelease .\i18n\isogeo_search_engine_es.ts
qt5-tools lrelease .\i18n\isogeo_search_engine_pt_BR.ts

# 3. Compiler les fichiers .ui → .py
pyuic5 -x "ui\isogeo_dockwidget_base.ui" -o "ui\ui_isogeo.py"
pyuic5 -x "ui\auth\ui_authentication.ui" -o "ui\auth\ui_authentication.py"
pyuic5 -x "ui\credits\ui_credits.ui" -o "ui\credits\ui_credits.py"
pyuic5 -x "ui\db_connections\ui_db_connections.ui" -o "ui\db_connections\ui_db_connections.py"
pyuic5 -x "ui\metadata\ui_md_details.ui" -o "ui\metadata\ui_md_details.py"
pyuic5 -x "ui\quicksearch\ui_quicksearch_rename.ui" -o "ui\quicksearch\ui_quicksearch_rename.py"
pyuic5 -x "ui\quicksearch\ui_quicksearch_new.ui" -o "ui\quicksearch\ui_quicksearch_new.py"
pyuic5 -x "ui\portal\ui_portal_base_url.ui" -o "ui\portal\ui_portal_base_url.py"

# 4. Compiler les ressources Qt (icônes, images)
pyrcc5 resources.qrc -o resources_rc.py

# 5. Packager le plugin en .zip
python tools\plugin_packager.py
```

**Après compilation des .ui** : supprimer la ligne `import resources_rc` en fin des fichiers .py générés.

## Règles strictes

- **NE JAMAIS modifier les fichiers Python générés** dans `ui/` (ils sont écrasés par `pyuic5` au build). Modifier les `.ui` à la place.
- **NE JAMAIS lire le répertoire `_auth/`** : il contient des secrets OAuth sensibles.
- **NE JAMAIS modifier `resources_rc.py`** : fichier généré par `pyrcc5`.

## Formatage et linting

- **black** : `black --target-version py37 --line-length 100`
- **flake8** : `flake8 --max-complexity 10 --max-line-length 100`
- **pylint** : config dans `tools/pylintrc`

## Architecture des modules

Point d'entrée : `isogeo.py` (classe `Isogeo`, chargée par QGIS).

```
modules/
├── api/
│   ├── auth.py          # Authenticator — OAuth2 avec l'API Isogeo
│   ├── request.py       # ApiRequester — requêtes REST vers l'API
│   └── shares.py        # SharesParser — parsing des partages
├── layer/
│   ├── add_layer.py     # LayerAdder — ajout de couches au projet QGIS
│   ├── geo_service.py   # GeoServiceManager — WMS/WFS/WMTS/OGC
│   ├── database.py      # DataBaseManager — connexions PostGIS, Oracle, etc.
│   ├── limitations_checker.py  # Validation des capacités de couche
│   └── metadata_sync.py       # Synchronisation des métadonnées
├── results/
│   ├── display.py       # ResultsManager — affichage des résultats de recherche
│   └── cache.py         # CacheManager — cache des résultats
├── metadata_display.py  # MetadataDisplayer — fiche de métadonnées détaillée
├── search_form.py       # SearchFormManager — logique du dock principal
├── settings_manager.py  # SettingsManager — étend QSettings
├── quick_search.py      # QuickSearchManager — recherches rapides sauvegardées
├── tools.py             # IsogeoPlgTools — utilitaires divers
├── user_inform.py       # UserInformer — messages et notifications
└── portal_base_url.py   # Configuration URL portail
```

## Conventions de nommage des widgets UI

Les widgets suivent un préfixe indiquant leur classe Qt :

| Préfixe | Classe Qt       |
|---------|-----------------|
| `btn_`  | QPushButton     |
| `cbb_`  | QComboBox       |
| `txt_`  | QLineEdit       |
| `ico_`  | QLabel (icône)  |
| `lbl_`  | QLabel (texte)  |
| `tab_`  | QTabWidget      |
| `tbl_`  | QTableWidget    |
| `grp_`  | QGroupBox       |
| `lyt_`  | QGridLayout     |

## Traductions (i18n)

4 langues supportées : français, anglais, espagnol, portugais brésilien.

**Workflow :**
1. Les chaînes traduisibles sont marquées avec `self.tr("...")` dans le code Python et via Qt Designer dans les `.ui`
2. `pylupdate5` scanne les fichiers listés dans `isogeo_search_engine.pro` (SOURCES + FORMS) et met à jour les fichiers `.ts`
3. Les traducteurs éditent les `.ts` avec Qt Linguist
4. `qt5-tools lrelease` compile les `.ts` en `.qm` (binaires chargés au runtime)

**Fichiers :**
- Sources : `i18n/isogeo_search_engine_{locale}.ts` (XML Qt Linguist)
- Compilés : `i18n/isogeo_search_engine_{locale}.qm` (binaires)
- Projet Qt : `isogeo_search_engine.pro` (liste les fichiers à scanner pour les traductions)

## Contexte du projet

- **QGIS** : 3.16 à 3.44.99 (toutes en PyQt5)
- **Python** : 3.9 (build CI), compatible 3.7+
- **Environnement de test** : QGIS 3.44.8
- **CI/CD** : Azure Pipelines (`azure-pipelines.yml`)
- **Distribution** : ZIP packagé pour le dépôt de plugins QGIS
