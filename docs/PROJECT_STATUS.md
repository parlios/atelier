# État du projet — Atelier

- **Date :** 17 juillet 2026
- **Version :** MVP complet, interface refondue
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
| Git/GitHub | Non initialisé | ⬜ |
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
├── docs/                  # 7 documents
└── .local/                # Sauvegardes et données non versionnées
```

## Interface

La refonte du 16 juillet 2026 a transformé l'interface :

- **Design system :** CSS structuré, variables, composants réutilisables
- **Shell :** sidebar desktop, navigation mobile native, topbar, messages Django
- **Dashboard :** centre de pilotage avec projets actifs, Inbox, décisions, releases, activité
- **Formulaires :** labels associés, distinction requis/facultatif, erreurs visibles
- **Badges :** statuts et priorités avec libellés textuels
- **États vides :** utiles et orientés action
- **Accessibilité :** lien d'évitement, focus visible, landmarks, `prefers-reduced-motion`
- **Responsive :** 3 breakpoints (74rem, 60rem, 42rem)
- **Dépendances :** aucune (pas de CDN, police, framework, JavaScript)

Décision documentée : `docs/decisions/0001-systeme-interface-atelier.md`

## Superuser

- **Username :** `max`
- **Compte :** superutilisateur local existant
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
# 76 tests, ~150s
```

## Documents de conception

| Document | Version | Contenu |
|---|---|---|
| `PRODUCT_CHARTER.md` | 1.0 | Charte produit |
| `USER_JOURNEY_AND_GLOSSARY.md` | 1.0 | Parcours et vocabulaire |
| `DATA_MODEL.md` | 1.0 | Modèle de données |
| `FUNCTIONAL_SCREENS.md` | 1.0 | Spécification des écrans |
| `decisions/0001-systeme-interface-atelier.md` | 1.0 | Décision d'architecture frontend |

## Prochaines étapes recommandées

1. **Initialiser Git et GitHub** — dépôt privé, premier commit après validation visuelle
2. **Commencer à utiliser** — créer les premiers projets réels dans Atelier
3. **Améliorations progressives** — HTMX, formulaires Django, listes paginées
4. **Intégration Hermes** — API REST pour qu'Hermes consulte et écrive

## Contraintes

- `.env` jamais versionné
- Aucun secret dans le code, les templates, la base ou la documentation
- SQLite local, mono-utilisateur
- Application privée
- Projets sous `/home/maxime/projects`
- Aucune dépendance frontend externe