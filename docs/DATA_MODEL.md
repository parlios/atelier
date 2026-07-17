# Modèle de données du MVP — Atelier

- **Version :** 1.0
- **Statut :** validé
- **Documents parents :**
  - `docs/PRODUCT_CHARTER.md`
  - `docs/USER_JOURNEY_AND_GLOSSARY.md`
- **Portée :** modèle métier et contraintes du MVP, avant implémentation Django

## 1. Objectif

Définir le plus petit modèle de données capable de prendre en charge le cycle :

```text
Inbox
  → Qualification
    → Projet
      → Prochaine action
        → Résultat
          → Nouvelle prochaine action
```

Le modèle doit aussi conserver les décisions, ressources, actifs et versions significatives sans reproduire Git, GitHub ou un gestionnaire documentaire complet.

## 2. Principes de modélisation

1. Utiliser des identifiants UUID stables pour préparer les exports et une future API.
2. Conserver un modèle relationnel explicite et éviter les données métier opaques dans des champs JSON.
3. Archiver plutôt que supprimer.
4. Empêcher autant que possible les états incohérents par des contraintes de base de données.
5. Compléter les contraintes de base par des validations métier lorsque la règle traverse plusieurs tables.
6. Ne stocker aucun secret.
7. Ne pas créer une table pour chaque notion du vocabulaire si un champ ou un état suffit.
8. Ne pas ajouter de modèle multi-utilisateur au MVP.

## 3. Vue d’ensemble

```text
Project
 ├── Task
 ├── Decision
 ├── Resource
 ├── Asset
 └── Release

InboxItem
 └── destination facultative vers Project, Task, Decision ou Resource

Asset
 └── Release facultative

Activity
 └── événement historique léger lié facultativement à un Project
```

## 4. Champs communs

Les entités métier modifiables partagent les champs suivants :

| Champ | Type logique | Obligatoire | Rôle |
|---|---|---:|---|
| `id` | UUID | oui | Identifiant stable |
| `created_at` | date et heure | oui | Date de création générée par le système |
| `updated_at` | date et heure | oui | Dernière modification générée par le système |
| `archived_at` | date et heure | non | Archivage logique ; `null` signifie actif dans les vues courantes |

`Activity` est immuable et n’a pas besoin de `updated_at` ni de `archived_at`.

## 5. Entités du MVP

### 5.1 Project

**Responsabilité :** représenter une initiative limitée dans le temps et orientée vers un résultat.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `name` | texte court | oui | Nom visible |
| `slug` | texte court | oui | Unique et stable dans les URL |
| `problem_statement` | texte Markdown | selon état | Obligatoire pour un projet actif |
| `expected_outcome` | texte Markdown | selon état | Obligatoire pour un projet actif |
| `description` | texte Markdown | non | Contexte complémentaire |
| `status` | choix | oui | Voir cycle de vie ci-dessous |
| `priority` | choix | oui | `high`, `normal`, `low`; défaut `normal` |
| `workspace_path` | chemin texte | non | Chemin du projet, sans contenu de fichier |
| `repository_url` | URL | non | Dépôt principal |
| `primary_url` | URL | non | Application, documentation ou service principal |
| `review_due_on` | date | non | Prochaine date de revue souhaitée |
| `last_reviewed_at` | date et heure | non | Dernière revue effectuée |
| `completed_at` | date et heure | non | Renseigné quand le projet est terminé |
| `abandoned_reason` | texte | selon état | Obligatoire si le projet est abandonné |
| champs communs | — | oui/non | UUID, dates et archivage |

#### États de Project

- `exploration`
- `planned`
- `active`
- `paused`
- `completed`
- `abandoned`

#### Contraintes

- `slug` est unique globalement, y compris après archivage.
- Un projet `active` doit posséder un problème et un résultat attendu.
- Un projet `active` doit posséder exactement une tâche marquée prochaine action.
- Un projet `completed` ou `abandoned` ne peut pas conserver de tâche `in_progress`.
- `completed_at` est requis pour un projet `completed`.
- `abandoned_reason` est requis pour un projet `abandoned`.
- Archiver un projet ne change pas son état métier.

La règle « exactement une prochaine action » traverse `Project` et `Task` ; elle sera validée dans le service métier et lors des changements d’état du projet.

### 5.2 InboxItem

**Responsabilité :** conserver une capture non encore qualifiée, puis la trace de sa destination.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `title` | texte court | oui | Seul champ métier obligatoire à la capture |
| `notes` | texte Markdown | non | Contexte libre |
| `suggested_type` | choix | non | `idea`, `task`, `decision`, `resource`, `other` |
| `suggested_project` | relation vers Project | non | Projet pressenti, sans qualification définitive |
| `source_url` | URL | non | Source externe éventuelle |
| `status` | choix | oui | `unprocessed`, `processed`, `discarded` |
| `discarded_reason` | texte | selon état | Facultatif dans l’interface, recommandé si écarté |
| `processed_at` | date et heure | selon état | Requis si traité ou écarté |
| `destination_project` | relation vers Project | non | Destination possible |
| `destination_task` | relation vers Task | non | Destination possible |
| `destination_decision` | relation vers Decision | non | Destination possible |
| `destination_resource` | relation vers Resource | non | Destination possible |
| champs communs | — | oui/non | UUID, dates et archivage |

#### Contraintes

- Un élément `unprocessed` ne possède aucune destination ni `processed_at`.
- Un élément `processed` possède `processed_at` et exactement une destination.
- Un élément `discarded` possède `processed_at` et aucune destination.
- Une destination existante ne peut pas être supprimée définitivement tant qu’un élément d’inbox la référence.
- `suggested_project` est une aide de capture et ne compte pas comme destination.

Les quatre relations de destination sont explicites afin de conserver l’intégrité référentielle sans relation générique opaque.

### 5.3 Task

**Responsabilité :** représenter une action concrète contribuant à un projet.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `project` | relation vers Project | oui | Une tâche appartient toujours à un projet |
| `title` | texte court | oui | Commence idéalement par un verbe d’action |
| `description` | texte Markdown | non | Détails nécessaires à l’exécution |
| `status` | choix | oui | Voir états ci-dessous |
| `priority` | choix | oui | `high`, `normal`, `low`; défaut `normal` |
| `is_next_action` | booléen | oui | Défaut `false` |
| `due_on` | date | non | Échéance réelle, distincte de la priorité |
| `review_on` | date | non | Date de revue d’un élément en attente ou bloqué |
| `blocker_description` | texte | selon état | Requis si bloquée |
| `unblock_action` | texte | non | Action pressentie pour lever le blocage |
| `result_summary` | texte Markdown | selon état | Requis si terminée |
| `evidence_url` | URL | non | Preuve externe éventuelle |
| `completed_at` | date et heure | selon état | Requis si terminée |
| `canceled_reason` | texte | non | Raison de l’annulation |
| champs communs | — | oui/non | UUID, dates et archivage |

#### États de Task

- `todo`
- `in_progress`
- `waiting`
- `blocked`
- `completed`
- `canceled`

#### Contraintes

- Une tâche `completed` possède `result_summary` et `completed_at`.
- Une tâche `blocked` possède `blocker_description`.
- Une tâche marquée `is_next_action` est obligatoirement `todo` ou `in_progress`.
- Une contrainte unique conditionnelle autorise au maximum une tâche `is_next_action = true` par projet.
- Une tâche archivée ne peut pas être prochaine action.
- Une tâche d’un projet archivé ne peut pas passer à `in_progress`.
- Terminer, annuler, bloquer ou mettre en attente la prochaine action impose de la désigner comme non prochaine et de choisir la suite ou de changer l’état du projet.

### 5.4 Decision

**Responsabilité :** conserver un choix important, son raisonnement et ses conséquences.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `project` | relation vers Project | oui | Projet concerné |
| `title` | texte court | oui | Nom de la décision |
| `context` | texte Markdown | oui | Situation ayant conduit au choix |
| `question` | texte Markdown | oui | Question à résoudre |
| `choice` | texte Markdown | selon état | Requis si acceptée |
| `alternatives` | texte Markdown | non | Options considérées |
| `consequences` | texte Markdown | selon état | Requis si acceptée |
| `status` | choix | oui | Voir états ci-dessous |
| `decided_at` | date et heure | selon état | Requis si acceptée ou rejetée |
| `superseded_by` | relation vers Decision | selon état | Requis si remplacée |
| champs communs | — | oui/non | UUID, dates et archivage |

#### États de Decision

- `proposed`
- `accepted`
- `rejected`
- `superseded`

#### Contraintes

- Une décision `accepted` possède `choice`, `consequences` et `decided_at`.
- Une décision `rejected` possède `decided_at`.
- Une décision `superseded` référence une autre décision du même projet.
- Une décision ne peut pas se remplacer elle-même.
- Une décision acceptée n’est pas réécrite silencieusement ; une nouvelle décision la remplace.

### 5.5 Resource

**Responsabilité :** conserver une information utile à la compréhension ou à l’exécution du travail.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `project` | relation vers Project | non | `null` autorisé pour une ressource transversale |
| `title` | texte court | oui | Nom visible |
| `resource_type` | choix | oui | Voir types ci-dessous |
| `content` | texte Markdown | non | Contenu non sensible |
| `source_url` | URL | non | Source externe |
| `source_path` | chemin texte | non | Chemin local, jamais contenu du fichier |
| champs communs | — | oui/non | UUID, dates et archivage |

#### Types de Resource

- `note`
- `idea`
- `document`
- `prompt`
- `procedure`
- `reference`

#### Contraintes

- Une ressource possède au moins `content`, `source_url` ou `source_path`.
- Une ressource sans projet est considérée comme transversale.
- Un prompt reste du texte ; aucune exécution ni mesure de performance n’est associée au MVP.
- `source_path` peut identifier un fichier sensible, mais le contenu sensible ne doit jamais être copié dans `content`.

### 5.6 Asset

**Responsabilité :** répertorier un élément technique ou opérationnel durable.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `owner_project` | relation vers Project | non | Projet propriétaire ; `null` si actif partagé |
| `name` | texte court | oui | Nom visible |
| `asset_type` | choix | oui | Voir types ci-dessous |
| `status` | choix | oui | Voir états ci-dessous |
| `environment` | choix ou texte court | non | Par exemple `local`, `development`, `staging`, `production` |
| `url` | URL | non | Accès principal |
| `path` | chemin texte | non | Emplacement local éventuel |
| `description` | texte Markdown | non | Fonction et limites |
| `last_verified_at` | date et heure | non | Dernière vérification réelle |
| champs communs | — | oui/non | UUID, dates et archivage |

#### Types de Asset

- `application`
- `ai_agent`
- `automation`
- `repository`
- `external_service`
- `infrastructure`

#### États de Asset

- `planned`
- `active`
- `degraded`
- `inactive`
- `retired`

#### Contraintes

- Un actif possède au moins `url`, `path` ou `description`.
- Un actif `retired` ne doit pas être présenté comme disponible dans les vues opérationnelles.
- Aucun secret, token ou identifiant d’authentification n’est stocké dans ses champs.
- Un actif partagé peut ne pas avoir de projet propriétaire dans le MVP.

### 5.7 Release

**Responsabilité :** représenter une version ou livraison significative.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `project` | relation vers Project | oui | Projet ayant produit la livraison |
| `asset` | relation vers Asset | non | Actif concerné si identifié |
| `version_label` | texte court | oui | Par exemple `0.1.0`, `MVP` ou `Prototype 1` |
| `status` | choix | oui | Voir états ci-dessous |
| `summary` | texte Markdown | oui | Changements ou résultat livré |
| `reference_url` | URL | non | Tag Git, commit, déploiement ou preuve |
| `released_at` | date et heure | selon état | Requis si livrée, validée, échouée ou retirée |
| `validation_result` | texte Markdown | selon état | Requis si validée ou échouée |
| `validated_at` | date et heure | selon état | Requis si validée ou échouée |
| champs communs | — | oui/non | UUID, dates et archivage |

#### États de Release

- `prepared`
- `released`
- `validated`
- `failed`
- `withdrawn`

#### Contraintes

- `version_label` est unique à l’intérieur d’un projet.
- Une version `validated` ou `failed` possède un résultat et une date de validation.
- Une version autre que `prepared` possède une date de livraison.
- Si `asset` est renseigné, son projet propriétaire doit correspondre au projet de la version ou être nul pour un actif partagé.

### 5.8 Activity

**Responsabilité :** fournir un historique léger des événements significatifs et alimenter l’activité récente du tableau de bord.

| Champ | Type logique | Obligatoire | Règle |
|---|---|---:|---|
| `id` | UUID | oui | Clé primaire |
| `project` | relation vers Project | non | Projet concerné si applicable |
| `event_type` | texte court contrôlé | oui | Par exemple `project.created`, `task.completed` |
| `object_type` | texte court contrôlé | oui | Type d’objet source |
| `object_id` | UUID | oui | Identifiant de l’objet source |
| `actor` | choix | oui | `max`, `hermes`, `system` |
| `message` | texte court | oui | Résumé humain non sensible |
| `occurred_at` | date et heure | oui | Générée par le système |

#### Contraintes

- Une activité est ajoutée, jamais modifiée comme donnée métier.
- Elle ne remplace pas un audit de sécurité complet.
- Elle ne contient ni secret, ni contenu documentaire complet.
- La référence générique `object_type` + `object_id` est acceptée ici uniquement parce qu’Activity est un journal dérivé et non la source d’intégrité métier.

## 6. Relations et politiques de suppression

| Relation | Cardinalité | Suppression définitive de la cible |
|---|---|---|
| Project → Task | 1:N | protégée si des tâches existent |
| Project → Decision | 1:N | protégée si des décisions existent |
| Project → Resource | 1:N facultatif | protégée si des ressources existent |
| Project → Asset | 1:N facultatif | le projet ne peut pas être supprimé tant qu’il est propriétaire |
| Project → Release | 1:N | protégée si des versions existent |
| Asset → Release | 1:N facultatif | l’actif ne peut pas être supprimé s’il est référencé |
| Decision → superseded_by | N:1 facultatif | protégée si elle remplace une décision |
| InboxItem → destination | N:1 facultatif | protégée tant que l’inbox garde cette destination |
| Activity → Project | N:1 facultatif | l’activité est conservée avec le projet archivé |

### Politique générale

- L’action normale est l’archivage via `archived_at`.
- La suppression définitive est réservée aux erreurs de saisie ou obligations particulières.
- Une suppression définitive exige une confirmation explicite.
- Les relations protégées doivent être résolues ou archivées, jamais contournées silencieusement.

## 7. Transactions métier nécessaires

Certaines opérations doivent être atomiques :

### Activer un projet

1. vérifier le problème et le résultat attendu ;
2. vérifier qu’exactement une tâche exécutable est prochaine action ;
3. passer le projet à `active` ;
4. enregistrer une activité.

### Terminer la prochaine action

1. enregistrer son résultat et sa date ;
2. retirer `is_next_action` ;
3. désigner la nouvelle prochaine action ou changer l’état du projet ;
4. enregistrer une activité.

### Qualifier un élément d’inbox

1. créer ou sélectionner la destination ;
2. renseigner exactement une relation de destination ;
3. passer l’élément à `processed` ;
4. renseigner `processed_at` ;
5. enregistrer une activité.

### Remplacer une décision

1. créer et accepter la nouvelle décision ;
2. passer l’ancienne décision à `superseded` ;
3. renseigner `superseded_by` ;
4. enregistrer une activité.

## 8. Données sensibles interdites

Aucun champ ne doit recevoir :

- mot de passe ;
- clé API ;
- token ;
- clé privée ;
- secret OAuth ;
- cookie de session ;
- contenu complet de `.env` ;
- contenu complet d’un fichier d’authentification ;
- archive contenant une configuration authentifiée.

Atelier peut conserver un chemin ou une référence vers un emplacement protégé si cette information est nécessaire, sans lire ni recopier son contenu.

Un contrôle d’interface pourra afficher un avertissement lorsqu’un contenu ressemble à un secret, mais ce contrôle ne remplacera jamais une gestion correcte des secrets.

## 9. Éléments explicitement reportés

Le MVP ne contient pas de table dédiée pour :

- Idea : représentée par InboxItem puis éventuellement Resource ;
- Prompt : type de Resource ;
- Result : champs de clôture de Task ;
- Blocker : état et champs de Task ;
- Link générique : champs URL ou chemin explicites sur les entités concernées ;
- Tag : reporté jusqu’à observation d’un besoin réel de classification transverse ;
- Comment ;
- Attachment ;
- Team, Organization ou Membership ;
- dépendance entre tâches ;
- objectif stratégique ou OKR ;
- exécution d’agent ou d’automatisation ;
- notification ;
- secret ;
- index vectoriel ;
- audit de sécurité complet.

## 10. Index fonctionnels prévus

Sans détailler encore l’implémentation SQL, les recherches suivantes doivent être efficaces :

- projets par état, priorité et archivage ;
- tâches par projet, état, priorité, échéance et `is_next_action` ;
- inbox par état et date de création ;
- décisions par projet et état ;
- ressources par projet et type ;
- actifs par propriétaire, type, état et environnement ;
- versions par projet, actif et date ;
- activités récentes par projet et date.

## 11. Questions de validation

La version 0.1 propose les décisions suivantes :

1. utiliser des UUID dès le MVP ;
2. rendre `Project.slug` unique et stable ;
3. rendre `Task.project` obligatoire ;
4. modéliser la prochaine action par `Task.is_next_action` avec une unicité conditionnelle par projet ;
5. autoriser les ressources transversales sans projet ;
6. autoriser les actifs partagés sans projet propriétaire ;
7. conserver une table Activity légère et immuable ;
8. ne pas créer de tags ni de liens génériques dans le MVP ;
9. protéger les relations et privilégier l’archivage ;
10. imposer les transitions critiques par des opérations métier atomiques.

Ces décisions doivent être validées avant la conception détaillée des écrans ou l’écriture des modèles Django.
