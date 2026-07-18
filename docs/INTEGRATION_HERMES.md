# Intégration Hermes — Lecture seule

- **Version :** 1.0
- **Date :** 18 juillet 2026
- **Commande :** `python manage.py atelier status --format json`

## Principe

Hermes interroge Atelier en appelant une **commande Django locale** depuis le terminal. Pas d'API REST, pas de service réseau, pas d'accès direct à SQLite.

```text
Hermes (agent IA)  ──terminal()──→  manage.py atelier status --format json
                                       │
                                       ↓
                                    Django ORM
                                       │
                                       ↓
                                    Réponse JSON (stdout)
```

## Commande disponible

```bash
python manage.py atelier status --format json
```

La sous-commande `status` est l'argument par défaut :

```bash
python manage.py atelier --format json
```

Produit exactement la même sortie.

## Contrat JSON (version 1.0)

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-07-18T20:00:00Z",
  "summary": {
    "active_projects": 2,
    "paused_projects": 1,
    "projects_to_review": 0,
    "inbox_pending": 3,
    "decisions_pending": 1,
    "blocked_tasks": 0
  },
  "projects": [
    {
      "name": "Atelier",
      "slug": "atelier",
      "status": "active",
      "priority": "high",
      "next_action_title": "Créer les vues projets",
      "next_action_status": "todo",
      "review_due_on": null
    }
  ],
  "recent_activity": [
    {
      "occurred_at": "2026-07-18T19:00:00Z",
      "actor": "max",
      "event_type": "status_check",
      "message": "Consultation du statut",
      "project_name": "Atelier"
    }
  ],
  "warnings": [
    "Le projet « Sans action » est actif mais n'a pas de prochaine action."
  ]
}
```

## Définition des compteurs

| Compteur | Définition métier | Requête |
|---|---|---|
| `active_projects` | Projets non archivés, statut `active` | `Project.objects.filter(status='active')` |
| `paused_projects` | Projets non archivés, statut `paused` | `Project.objects.filter(status='paused')` |
| `projects_to_review` | Projets actifs/en pause avec `review_due_on ≤ aujourd'hui` | Calcul Python après requête |
| `inbox_pending` | Éléments Inbox non traités (`unprocessed`) | `InboxItem.objects.filter(status='unprocessed')` |
| `decisions_pending` | Décisions proposées (`proposed`) | `Decision.objects.filter(status='proposed')` |
| `blocked_tasks` | Tâches bloquées non archivées (`blocked`) | `Task.objects.filter(status='blocked')` |

## Ordre des listes

- **Projets :** triés par `status`, puis `-priority`, puis `-updated_at` (ordre Django existant)
- **Activité récente :** les 10 dernières entrées par `-occurred_at`

## stdout, stderr et codes de sortie

| Condition | stdout | stderr | Code |
|---|---|---|---|
| Succès | JSON uniquement | vide | 0 |
| Sous-commande inconnue | vide | message d'erreur | 1 |
| Format invalide | vide | message d'erreur | 1 |

## Sécurité

- **Lecture seule :** la commande ne crée, ne modifie et ne supprime aucun objet
- **ORM uniquement :** pas de SQL brut, pas d'accès direct à `db.sqlite3`
- **Aucune dépendance externe :** pas de REST, pas de HTTP, pas de subprocess
- **Aucune donnée sensible :** le JSON ne contient pas de mots de passe, tokens, clés ou secrets
- **Aucune entrée Activity :** la commande ne journalise pas son propre appel

## Architecture

```text
apps/integrations/
├── __init__.py
├── apps.py                                  # AppConfig
├── contracts.py                             # Construction du contrat JSON
├── services/
│   ├── __init__.py
│   └── status.py                            # Requêtes ORM et logique métier
├── management/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       └── atelier.py                       # Point d'entrée CLI
└── tests/
    ├── __init__.py
    └── test_atelier_status.py               # 16 tests
```

## Tests

16 tests dédiés dans `apps/integrations/tests/test_atelier_status.py` :

- JSON valide, base vide, projets avec/sans prochaine action
- Compteurs des différents statuts
- Inbox, décisions, tâches bloquées
- Activité récente
- Contrat JSON : `schema_version` "1.0", types, ISO 8601
- Lecture seule (vérification sans modification)
- Budget de requêtes (6 requêtes maximum)
- Sous-commande par défaut, `--format=json` avec `=`, `--help`
- Sous-commande inconnue (stderr + exit ≠ 0)
- stderr vide en cas de succès

## Limites actuelles

- **Lecture seule uniquement :** Hermes peut consulter l'état d'Atelier mais pas le modifier
- **Pas de détail projet :** la commande ne donne pas accès au contenu détaillé d'un projet
- **Pas d'écriture :** `capture`, `project` et `propose` ne sont pas encore implémentés
- **Pas de cache :** chaque exécution lance les requêtes ORM complètes
- **Pas de filtrage :** la réponse inclut tous les projets actifs/en pause

## Futures sous-commandes (envisagées, non implémentées)

- `atelier capture` — ajouter un élément dans l'inbox
- `atelier project <slug>` — obtenir le détail complet d'un projet
- `atelier propose` — proposer une action à qualifier
