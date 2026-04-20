# Code Review depuis le commit $ARGUMENTS

Effectue une code review approfondie de tous les changements introduits depuis le commit `$ARGUMENTS` jusqu'à HEAD, **commit `$ARGUMENTS` inclus**.

La base de comparaison est le parent de `$ARGUMENTS` (soit `$ARGUMENTS~1`), ce qui fait entrer `$ARGUMENTS` lui-même dans le périmètre de la review.

---

## Étape 0 — Analyse parallèle par module

1. Découvrir dynamiquement la structure du dépôt via Glob :
   - Lister les sous-dossiers directs de `modules/` (Glob `modules/*/`)
   - Lister les fichiers `.py` directement dans `modules/` (Glob `modules/*.py`) et à la racine (Glob `*.py`)
   - Lister les fichiers `.ui` (Glob `**/*.ui`)
   - Lister les fichiers de traduction `.ts` (Glob `i18n/*.ts`)
   - Ne jamais coder en dur la liste des modules

2. Regrouper les fichiers modifiés par périmètre, puis lancer un agent en parallèle par groupe :
   - Un agent par sous-dossier direct de `modules/` contenant au moins un fichier modifié (ex. `modules/api/`, `modules/layer/`, `modules/results/`)
   - Un agent pour les fichiers `.py` à la racine et dans `modules/` directement (dont `isogeo.py`) s'ils sont modifiés
   - Un agent pour les fichiers `.ui` et `.ts` s'ils sont modifiés

   Chaque agent doit :
   - Lire le diff et le fichier complet de chaque fichier modifié dans son périmètre
   - Identifier bugs, problèmes de compatibilité Qt5/Qt6, lacunes de type annotations, problèmes de style (sévérité : high / medium / low)
   - Retourner les findings sous forme structurée : fichier, ligne, sévérité, description

3. Une fois tous les agents terminés, effectuer une **passe de synthèse** dans le contexte principal :
   - Fusionner les findings de tous les modules
   - Vérifier les impacts croisés entre modules (ex. changement dans un sous-module `api/` consommé par `layer/`)
   - Dédupliquer et prioriser avant de passer aux étapes suivantes

---

## Étape 1 — Cartographie des changements

Exécute les commandes suivantes :

```bash
git diff --name-only $ARGUMENTS~1 HEAD
git diff $ARGUMENTS~1 HEAD --stat
git log $ARGUMENTS~1..HEAD --oneline
```

Identifie tous les fichiers modifiés. Exclusion stricte : ne jamais ouvrir ni lire les fichiers du répertoire `_auth/` (secrets OAuth sensibles).

---

## Étape 2 — Lecture des diffs et des fichiers complets

Pour chaque fichier modifié :

1. Lis le diff exact : `git diff $ARGUMENTS~1 HEAD -- <fichier>`
2. Lis le fichier complet dans sa version actuelle pour avoir le contexte

---

## Étape 3 — Analyse des effets de bord (priorité absolue)

C'est l'étape la plus importante. Pour **chaque** fonction, méthode, classe ou constante modifiée :

1. Recherche toutes ses occurrences dans l'ensemble du dépôt (pas seulement les fichiers modifiés) :
   - Utilise Grep pour chercher le nom dans tous les fichiers `.py` et `.ui`
   - Lis chaque fichier appelant pour comprendre comment il utilise l'élément modifié

2. Analyse si la modification peut provoquer une régression :
   - Changement de paramètres (ajout, suppression, valeurs par défaut modifiées)
   - Changement du format de retour ou des données émises (signaux Qt, dict, liste)
   - Changement de comportement aux limites (valeurs None, listes vides, réponse API vide, couche invalide)
   - Changement d'effet de bord implicite (état UI modifié, signal émis, couche ajoutée/supprimée)

3. Si un signal Qt est modifié, vérifier que les types et le nombre d'arguments déclarés dans `pyqtSignal(...)` sont toujours compatibles avec tous les slots connectés à ce signal dans le dépôt

---

## Étape 4 — Analyse approfondie par critère

Pour chaque fichier modifié ET chaque fichier identifié en étape 3, analyse selon les critères suivants :

### Bugs et robustesse

- Erreurs de logique, off-by-one, conditions inversées
- Cas limites non gérés : réponse API vide ou en erreur, couche invalide, CRS absent, géométrie nulle, résultat de recherche vide
- Exceptions mal capturées ou avalées silencieusement
- Fuites de ressources : connexions PostGIS/Oracle ouvertes, handles QGIS non libérés

### Compatibilité Qt5 / Qt6 et QGIS 3.x / 4.x

- Utilisation de constantes Qt entières dépréciées (ex. `Qt.AlignLeft`) au lieu des enums namespaced (ex. `Qt.AlignmentFlag.AlignLeft`)
- Imports `from PyQt5` au lieu de `from qgis.PyQt` (non portable)
- Méthodes ou classes supprimées entre PyQt5 et PyQt6 (ex. `QVariant`, `exec_()` → `exec()`)
- Usage de `pyqtSignal` / `pyqtSlot` vs `Signal` / `Slot`
- Vérifier la cohérence avec les patterns de compatibilité déjà en place dans le code existant

### Effets de bord et régressions UI

- Un signal Qt connecté dans le point d'entrée ou dans le gestionnaire de formulaire émet-il toujours les mêmes types et nombre d'arguments qu'attendu par les slots connectés ?
- Un widget renommé ou supprimé dans un `.ui` est-il encore référencé dans le code Python ?
- La logique d'affichage des résultats reste-t-elle cohérente avec les données retournées par l'API ?
- Les traductions (`self.tr(...)`) couvrent-elles les nouveaux textes visibles par l'utilisateur ?

### Performance et réactivité QGIS

- Opérations longues exécutées dans le thread principal (gel de l'interface) — devraient passer par `QgsTask` ou un worker
- Requêtes REST répétées dans une boucle qui pourraient être factorisées
- Chargement en mémoire de données volumineuses qui pourraient être streamées
- Reconnexion de signaux dans des boucles (risque d'accumulation de connexions)

### Qualité du code

- Duplication de logique (DRY)
- Abstractions prématurées ou code qui gagnerait à être factorisé
- Complexité inutile — existe-t-il une formulation plus simple ?
- Variables, fonctions ou imports inutilisés
- Nombres ou chaînes magiques sans constante nommée

### Formalisme Python

- Respect des conventions PEP8 et formatage black (`--line-length 100`)
- Respect des limites flake8 (`--max-complexity 10`, `--max-line-length 100`)
- Type hints manquants sur les nouvelles fonctions/méthodes
- Docstrings absentes ou non mises à jour après modification
- Organisation des imports (stdlib / third-party / local)

### Logging et observabilité

- Les nouveaux chemins de code sont-ils loggés à un niveau approprié via `logger` ?
- Les erreurs sont-elles loggées avec suffisamment de contexte (identifiant de ressource, type d'erreur) ?
- Aucun token OAuth, identifiant ou donnée sensible n'est loggé en clair

### Traductions

- Les nouvelles chaînes visibles par l'utilisateur sont-elles marquées `self.tr("...")` ?
- Les fichiers `.ts` sont-ils cohérents avec les changements de code (sinon noter qu'un `pylupdate5` est nécessaire) ?

---

## Étape 5 — Vérifications actives

Si un constat mérite d'être étayé, consulte la documentation en ligne :

- **PyQGIS Developer Cookbook** (`https://docs.qgis.org/latest/en/docs/pyqgis_developer_cookbook/`) — recettes et patterns courants
- **QGIS API Python/C++** (`https://qgis.org/api/`) — vérifier l'existence et les paramètres d'une méthode QGIS
- **PyQt6 vs PyQt5 differences** (`https://www.riverbankcomputing.com/static/Docs/PyQt6/pyqt5_differences.html`) — incompatibilités entre versions
- **QGIS changelog** (`https://changelog.qgis.org/`) — vérifier si une API a été dépréciée ou supprimée dans une version donnée

Cite tes sources dans le rapport (URL + version consultée).

---

## Étape 6 — Rédaction du rapport

### Liens cliquables vers le code (obligatoire)

Chaque constat doit inclure des liens cliquables vers les lignes de code concernées, au format markdown :

```text
[nom_fichier.py:42](chemin/relatif/depuis/racine/nom_fichier.py#L42)
[nom_fichier.py:42-51](chemin/relatif/depuis/racine/nom_fichier.py#L42)
```

Ces chemins sont **relatifs depuis l'emplacement du fichier de rapport** (`.claude/reviews/`), donc ils remontent deux niveaux avec `../../` :

```text
[add_layer.py:115](../../modules/layer/add_layer.py#L115)
[display.py:270](../../modules/results/display.py#L270)
[isogeo.py:88](../../isogeo.py#L88)
```

Pour chaque constat :

1. Citer le lien cliquable vers la ou les lignes concernées
2. Montrer l'extrait de code avec un bloc `python` (entouré de lignes vides pour respecter MD031)
3. Expliquer le problème et proposer un fix si applicable

### Structure du rapport

```markdown
# Code Review — <sha_court>..HEAD

## Résumé

- Commits couverts : [liste git log --oneline]
- Fichiers directement modifiés : N
- Fichiers analysés pour effets de bord : M
- Constats : X critique(s), Y avertissement(s), Z suggestion(s)

## Fichiers directement modifiés

### `chemin/du/fichier.py`

**Changements :** résumé en 1-2 phrases de ce qui a changé

---

**[CRITIQUE]** Titre court du problème

Contexte à [fichier.py:42-51](chemin/fichier.py#L42) :

\```python
# extrait de code concerné
\```

Explication du problème et de sa sévérité. Fix suggéré si applicable.

---

**[AVERTISSEMENT]** ...

---

### `autre/fichier.py`

...

## Aucun constat

Fichiers analysés sans constat :

- [fichier1.py](chemin/fichier1.py)
- [fichier2.py](chemin/fichier2.py)
```

Niveaux de sévérité :

- **[CRITIQUE]** : bug avéré, régression, incompatibilité Qt5/Qt6 bloquante, fuite de ressource — doit être corrigé avant merge
- **[AVERTISSEMENT]** : comportement fragile, risque latent, dégradation de performance significative, traduction manquante — fortement recommandé de corriger
- **[SUGGESTION]** : amélioration de lisibilité, factorisation, formalisme — facultatif mais souhaitable

---

## Étape 7 — Sauvegarde du rapport

Sauvegarde le rapport dans un fichier :

```text
.claude/reviews/review-<sha_court>-<YYYY-MM-DD>.md
```

Crée le dossier `.claude/reviews/` s'il n'existe pas, puis affiche le rapport complet dans la conversation.
