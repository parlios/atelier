# Décision 0002 — Initialisation Git et publication privée sur GitHub

- **Date :** 18 juillet 2026
- **Statut :** acceptée
- **Portée :** versionnement et publication du projet Atelier

## Contexte

Atelier était fonctionnel, interface refondue, tests au vert, mais non versionné. L'application est privée, mono-utilisateur, avec une base SQLite locale et des fichiers de configuration (.env) qui ne doivent jamais être publiés. Git et SSH GitHub étaient déjà configurés globalement dans l'environnement Hermes V2.

## Décisions

- Dépôt Git local dans la racine d'Atelier (`/home/maxime/projects/apps/atelier`)
- Branche principale `main`
- Dépôt GitHub privé `parlios/atelier`
- Authentification et remote par SSH uniquement
- Aucun remote HTTPS avec token
- `.env`, `.venv/`, `.local/` et SQLite exclus du versionnement
- Fichiers statiques sources sous `static/atelier/` versionnés
- Fichiers générés par `collectstatic` exclus
- `.env.example` versionné avec valeurs fictives uniquement
- Vérification des fichiers indexés avant chaque commit important
- `git add -f` interdit pour contourner une exclusion de sécurité
- Push forcé interdit sauf décision explicite et documentée

## Exclusions Git

Le fichier `.gitignore` a été complété pour exclure :

- `.env` et fichiers `.env.*` (sauf `.env.example`)
- `.venv/`, `venv/`
- `.local/`
- `db.sqlite3`, `*.sqlite3`, `*.sqlite`
- `__pycache__/`, `*.py[cod]`
- caches Python (`.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`)
- couverture (`.coverage`, `htmlcov/`)
- Node.js (`node_modules/`)
- builds et distributions
- fichiers d'éditeur (`.vscode/`, `.idea/`, `*.swp`, `*.swo`)
- fichiers système (`.DS_Store`, `Thumbs.db`)
- journaux (`*.log`)
- clés privées (`*.pem`, `*.key`)

## Conséquences positives

- Historique complet du projet versionné
- Sauvegarde distante privée sur GitHub
- Traçabilité de toutes les évolutions
- Possibilité de branches et de revues
- Meilleure sécurité des données locales et sensibles
- Base prête pour les futures intégrations et automatisations (Hermes, CI, déploiement)

## Limites et risques

- GitHub ne remplace pas les sauvegardes locales ou les snapshots WSL
- Les exclusions Git doivent continuer à être vérifiées lors de chaque ajout sensible
- Un secret commité resterait dans l'historique même après suppression — nécessiterait une rotation
- Le dépôt distant ne contient pas la base SQLite locale (données de travail absentes)
- Le dépôt ne constitue pas un environnement de déploiement

## Validation

- 129 fichiers publiés dans le premier commit
- Branche `main` synchronisée avec `origin/main` (hash : `d606777f107c40287ec5b311b102d3968600caf0`)
- `.env`, `.venv/`, `.local/` et SQLite absents du dépôt distant
- Templates, CSS, SVG et documentation présents
- Aucun push forcé
- Aucun secret, mot de passe, token ou clé dans le commit
