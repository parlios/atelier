# Intégration Hermes — Commandes Atelier

- **Version :** 2.0
- **Date :** 18 juillet 2026
- **Commandes :** `status` (lecture), `capture` (écriture contrôlée)

## Principe

Hermes interroge et alimente Atelier en appelant des **commandes Django locales** depuis le terminal. Pas d'API REST, pas de service réseau, pas d'accès direct à SQLite.

```text
Hermes (agent IA)  ──terminal()──→  manage.py atelier <sous-commande>
                                       │
                                       ↓
                                    Django ORM
                                       │
                                       ↓
                                    Réponse JSON (stdout)
```

## Commande `status` — Lecture seule

```bash
python manage.py atelier status --format json
```

Retourne un résumé complet d'Atelier : projets, inbox, décisions, activités, avertissements.

**Contrat :** voir section dédiée ci-dessous.

## Commande `capture` — Écriture contrôlée

```bash
python manage.py atelier capture \
  --title "Titre de l'élément" \
  --idempotency-key "clé-opaque-unique" \
  --notes "Notes facultatives" \
  --suggested-type task \
  --project-slug mon-projet \
  --format=json
```

### Arguments

| Argument | Obligatoire | Description |
|---|---|---|
| `--title` | **oui** | Titre de l'élément (max 300 car., non vide après strip) |
| `--idempotency-key` | **oui** | Clé opaque unique (max 255 car.) — garantit qu'un même appel ne crée pas de doublon |
| `--notes` | non | Notes ou contenu libre (max 10 000 car.) |
| `--suggested-type` | non | Type pressenti : `idea`, `task`, `decision`, `resource`, `other` |
| `--project-slug` | non | Projet suggéré (slug, doit exister et être non archivé) |
| `--format` | non | `json` uniquement (défaut) |

### Comportements

| Cas | statut JSON | Code |
|---|---|---|
| Première utilisation d'une clé | `created` | 0 |
| Même clé, même payload | `reused` | 0 |
| Même clé, payload différent | erreur `idempotency_conflict` | 1 |
| Titre vide ou > 300 car. | erreur `invalid_title` | 1 |
| Notes > 10000 car. | erreur `notes_too_long` | 1 |
| Type invalide | erreur `invalid_suggested_type` | 1 |
| Projet inexistant | erreur `project_not_found` | 1 |
| Erreur argparse | stderr standard | 2 |

### Transaction

Chaque capture réussie crée atomiquement :
1. Un `InboxItem` (statut `unprocessed`)
2. Une `Activity` (acteur `hermes`, type `inbox_capture`)

Si l'une des deux écritures échoue, aucune n'est conservée.

### Règles de sécurité

- **La commande ne crée que des `InboxItem`** — pas de Project, Task, Decision, Resource ou Release
- La qualification reste humaine dans l'interface Atelier
- **Aucun secret ne doit être placé dans l'Inbox** : la commande ne peut pas détecter tous les secrets dans un texte libre
- L'Activity créée contient un message générique (pas de titre, notes ou clé)
- Les clés d'idempotence ne sont pas des secrets et ne sont pas retournées dans le JSON

## Contrats JSON

### status (v1.0)

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
  "projects": [ … ],
  "recent_activity": [ … ],
  "warnings": [ … ]
}
```

### capture — Création / Réutilisation (v1.0)

```json
{
  "schema_version": "1.0",
  "status": "created",
  "inbox_item": {
    "id": "uuid-string",
    "status": "unprocessed",
    "created_at": "2026-07-18T20:00:00Z"
  },
  "activity_created": true,
  "warnings": []
}
```

- `status` = `"created"` ou `"reused"`
- `activity_created` = `true` pour création, `false` pour réutilisation
- Le titre, les notes et la clé d'idempotence ne sont **pas** retournés

### capture — Erreur métier (v1.0)

```json
{
  "schema_version": "1.0",
  "status": "error",
  "error": {
    "code": "invalid_title",
    "message": "Le titre est obligatoire.",
    "fields": {
      "title": ["Le titre est obligatoire."]
    }
  }
}
```

## stdout, stderr et codes de sortie

| Cas | stdout | stderr | Code |
|---|---|---|---|
| `status` succès | JSON | vide | 0 |
| `capture` créé | JSON | vide | 0 |
| `capture` réutilisé | JSON | vide | 0 |
| Erreur métier | JSON | vide | 1 |
| Erreur argparse | vide | message standard | 2 |
| Sous-commande inconnue | vide | message | 1 |

## Sécurité

- **Lecture seule (`status`) :** aucun objet créé, modifié ou supprimé
- **Écriture contrôlée (`capture`) :** seul `InboxItem` + `Activity` créés
- **ORM uniquement :** pas de SQL brut, pas d'accès direct à `db.sqlite3`
- **Aucune dépendance externe :** pas de REST, HTTP, subprocess
- **Aucune donnée sensible :** les JSON ne contiennent pas de mots de passe, tokens, clés ou secrets

## Architecture

```text
apps/integrations/
├── contracts.py                             ← Contrats JSON (status + capture)
├── services/
│   ├── status.py                            ← Requêtes ORM (lecture)
│   └── capture.py                           ← Validation + transaction (écriture)
├── management/commands/atelier.py            ← CLI (status + capture)
└── tests/
    ├── test_atelier_status.py               ← 16 tests
    └── test_atelier_capture.py              ← 17 tests
```

Apps/inbox/models.py : champ `idempotency_key` (unique, nullable, max 255).

## Tests

- `status` : 16 tests
- `capture` : 17 tests
- Suite complète : 109 tests

## Limites actuelles

- `capture` ne crée que des InboxItems — qualification humaine requise
- Pas de sous-commande `project` (détail) ni `propose` (suggestion)
- Pas de cache — chaque exécution lance les requêtes ORM
- Concurrence : deux créations simultanées avec la même clé peuvent produire une IntegrityError (le client doit relire)

## Futures sous-commandes (envisagées, non implémentées)

- `atelier project <slug>` — détail complet d'un projet
- `atelier propose` — proposer une action à qualifier
