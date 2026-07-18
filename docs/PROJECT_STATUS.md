# État du projet — Atelier

- **Date :** 18 juillet 2026
- **Version :** MVP complet, interface refondue, versionné sur GitHub
- **Tests :** 76/76 OK
- **Environnement :** WSL Ubuntu, `/home/maxime/projects/apps/atelier`

## Avancement

| Phase | Contenu | Statut |
|---|---|---|
| 1 — Fondation | Django 5.2.16, config, `.env`, core | ✅ |
| 2 — Modèles | 9 entités, relations, contraintes | ✅ |
| 3 — Noyau UI | Auth, dashboard, projets | ✅ |
| 4 — Tâches + Inbox | Détail, capture, qualification | ✅ |
| 5 — Modules | Décisions, ressources, registre, releases | ✅ |
| 6 — Recherche | Recherche textuelle multi-entités | ✅ |
| 7 — Interface | Design system, shell, 28 templates, CSS, SVG local | ✅ |
| 8 — Git/GitHub | Dépôt local + GitHub privé, SSH, 129 fichiers | ✅ |
| Déploiement | Local uniquement | ⬜ |

## Architecture

```text
atelier/
├── manage.py
├── atelier/settings.py
├── apps/
│   ├── core/              # BaseModel UUID, auth, dashboard, recherche, context processor
│   ├── projects/          # Project (slug unique, 6 états)
│   ├── tasks/             # Task (is_next_action unique par projet)
│   ├── inbox/             # InboxItem (capture → qualification vers 4 destinations)
│   ├── decisions/         # Decision (proposée → acceptée/rejetée/remplacée)
│   ├── resources/         # Resource (6 types, contenu Markdown)
│   ├── registry/          # Asset (6 types, vérification)
│   ├── releases/          # Release (version_label unique par projet)
│   └── activity/          # Activity (journal immuable)
├── templates/             # 28 templates HTML + includes
├── static/atelier/
│   ├── css/app.css        # Design system complet (543 lignes)
│   └── icons/ui.svg       # Sprite SVG local (9 icônes)
├── docs/                  # 8 documents + décisions
└── .local/                # Sauvegardes et données non versionnées
```

## Intégration Hermes (lecture seule)

Atelier expose une interface locale par commande Django produisant du JSON, accessible depuis Hermes via le terminal.

**Commande :**
```bash
.venv/bin/python manage.py atelier status --format json
```

**Contrat de sortie :**
```json
{
  "schema_version": "1.0",
  "generated_at": "...",
  "summary": {
    "active_projects": …,
    "paused_projects": …,
    "projects_to_review": …,
    "inbox_pending": …,
    "decisions_pending": …,
    "blocked_tasks": …
  },
  "projects": [
    {
      "name": "...",
      "slug": "...",
      "status": "...",
      "priority": "...",
      "next_action_title": "...",
      "next_action_status": "...",
      "review_due_on": null
    }
  ],
  "recent_activity": [],
  "warnings": []
}
```

**Architecture :** `apps/integrations/` (10ᵉ app Django)
- `contracts.py` — construction du contrat JSON
- `services/status.py` — requêtes ORM et logique métier
- `services/capture.py` — validation, idempotence, transaction
- `management/commands/atelier.py` — point d'entrée CLI

**Tests :** 33 tests dédiés (109 total)
**Sécurité :** `status` lecture seule ; `capture` écriture limitée à InboxItem + Activity
**Idempotence :** persistante via `InboxItem.idempotency_key` (unique, nullable)
**Migration :** `inbox/0003_add_inbox_idempotency_key`
**Disponibilité :** sur `feat/integration-capture` — non fusionnée dans `main`

```bash
# Capture
.venv/bin/python manage.py atelier capture \
  --title "..." --idempotency-key "<uuid>" \
  --notes "..." --suggested-type task \
  --project-slug mon-projet --format=json
```

## Git et GitHub

### Dépôt local

- **Initialisé :** oui, dans `/home/maxime/projects/apps/atelier`
- **Branche principale :** `main`
- **Premier commit :** `d606777f107c40287ec5b311b102d3968600caf0`
- **Message :** `chore: initialize Atelier project`
- **Fichiers :** 129
- **Remote :** aucun HTTPS

### Dépôt distant

- **Nom :** `parlios/atelier`
- **Visibilité :** privée
- **Remote :** SSH uniquement
- **Adresse :** `git@github.com:parlios/atelier.git`
- **Branche publiée :** `main` → `origin/main`
- **Upstream :** configuré
- **Push :** sans `--force`
- **Synchronisation :** locale et distante identiques lors de la publication initiale

### Exclusions de sécurité

| Fichier | Exclu |
|---|---|
| `.env` | ✅ |
| `.venv/` | ✅ |
| `.local/` | ✅ |
| `db.sqlite3` | ✅ |
| `*.sqlite3` / `*.sqlite` | ✅ |
| `__pycache__/` | ✅ |
| `staticfiles/` (généré) | ✅ dossier absent |
| `.env.example` | ✅ versionné (valeurs fictives) |
| `static/atelier/` | ✅ versionné |
| `templates/` | ✅ versionné |
| `docs/` | ✅ versionné |
| 9 apps Django | ✅ versionnées |
| 18 migrations | ✅ versionnées |

## Interface

Refonte complète du 16 juillet 2026 :

- **Design system :** CSS structuré, variables, composants réutilisables
- **Shell :** sidebar desktop, navigation mobile native, topbar, messages Django
- **Dashboard :** centre de pilotage avec projets actifs, Inbox, décisions, releases, activité
- **Formulaires :** labels associés, distinction requis/facultatif, erreurs visibles
- **Badges :** statuts et priorités avec libellés textuels
- **États vides :** utiles et orientés action
- **Accessibilité :** lien d'évitement, focus visible, landmarks, `prefers-reduced-motion`
- **Responsive :** 3 breakpoints (74rem, 60rem, 42rem)
- **Dépendances :** aucune (pas de CDN, police, framework, JavaScript)

Décision : `docs/decisions/0001-systeme-interface-atelier.md`

## Superuser

- **Username :** `max`
- Compte superutilisateur local existant
- Le mot de passe est connu de l'utilisateur et ne figure dans aucun fichier versionné.

## Lancer le projet

```bash
cd /home/maxime/projects/apps/atelier
.venv/bin/python manage.py runserver
# → http://localhost:8000
```

## Exécuter les tests

```bash
.venv/bin/python manage.py test apps
# 109 tests, ~2 min
```

## Documents de conception

| Document | Version | Contenu |
|---|---|---|
| `PRODUCT_CHARTER.md` | 1.0 | Charte produit |
| `USER_JOURNEY_AND_GLOSSARY.md` | 1.0 | Parcours et vocabulaire |
| `DATA_MODEL.md` | 1.0 | Modèle de données |
| `FUNCTIONAL_SCREENS.md` | 1.0 | Spécification des écrans |
| `PROJECT_STATUS.md` | 2.0 | État du projet (ce document) |
| `decisions/0001-systeme-interface-atelier.md` | 1.0 | Architecture frontend |
| `decisions/0002-initialisation-git-github.md` | 1.0 | Git et GitHub |

## Prochaines étapes recommandées

1. Finaliser le second commit documentaire Git/GitHub
2. Définir la première intégration entre Atelier et Hermes
3. Examiner les améliorations fonctionnelles du MVP
4. Envisager HTMX uniquement lorsqu'un besoin concret est identifié
5. Préparer un snapshot WSL final après stabilisation

## Contraintes

- `.env` jamais versionné
- Aucun secret dans le code, les templates, la base ou la documentation
- SQLite local, mono-utilisateur
- Application privée
- Projets sous `/home/maxime/projects`
- Aucune dépendance frontend externe
- `git add -f` interdit
- Push forcé interdit sauf décision explicite et documentée