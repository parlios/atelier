# Écrans fonctionnels du MVP — Atelier

- **Version :** 1.0
- **Statut :** validé
- **Documents parents :**
  - `docs/PRODUCT_CHARTER.md`
  - `docs/USER_JOURNEY_AND_GLOSSARY.md`
  - `docs/DATA_MODEL.md`

## 1. Objectif

Décrire chaque écran du MVP avec précision : ce qu'il affiche, ce que l'utilisateur peut y faire, et les règles métier qui s'y appliquent. Ce document guide l'implémentation sans décider du style ni du framework.

## 2. Navigation générale

```text
Tableau de bord ──┬── Projets (liste)
                  │       └── Projet (fiche)
                  │              ├── Tâche (détail)
                  │              ├── Décision (détail)
                  │              ├── Ressource (détail)
                  │              └── Version (détail)
                  │
                  ├── Inbox
                  │
                  ├── Actifs (registre)
                  │
                  └── Recherche
```

Chaque fiche projet donne accès à ses sous-objets. La zone de capture rapide est accessible depuis tous les écrans.

## 3. Écrans

### 3.1 Tableau de bord

**Objectif :** répondre « quelle est la meilleure chose à faire maintenant ? »

**Données affichées :**

| Section | Contenu |
|---|---|
| Projets actifs | Nom, état, priorité, prochaine action, date de dernière revue |
| Prochaines actions | Tâches marquées `is_next_action`, groupées par projet, avec leur projet |
| Tâches prioritaires | Tâches `high` non terminées, hors prochaines actions |
| Blocages | Tâches `blocked`, avec description du blocage et projet |
| Inbox | Compteur d'éléments `unprocessed` |
| Projets sans prochaine action | Projets `active` sans tâche `is_next_action` |
| Projets à revoir | Projets avec `review_due_on` dépassée |
| Activité récente | 10 derniers événements |

**Actions disponibles :**

- accéder à un projet, une tâche ou l'inbox
- capturer dans l'inbox (barre toujours visible)

**Règles :**

- aucun projet `completed` ni `abandoned` dans la vue active
- une tâche `blocked` sans `blocker_description` est signalée comme incomplète
- les projets `paused` apparaissent dans une section séparée

---

### 3.2 Inbox

**Objectif :** capturer sans classer, puis qualifier.

**Données affichées :**

| État | Affichage |
|---|---|
| `unprocessed` | Liste principale : titre, type suggéré, projet pressenti, date |
| `processed` / `discarded` | Liste secondaire (filtrée par défaut) |

Chaque élément affiche : titre, type suggéré, projet pressenti (si renseigné), source (si lien), date de capture.

**Actions disponibles :**

- **Capture rapide :** champ titre + bouton créer (depuis n'importe quel écran)
- **Sur un élément `unprocessed` :**
  - Qualifier vers un projet, une tâche, une décision ou une ressource
  - Associer à un élément existant
  - Écarter (avec raison facultative)
  - Conserver dans l'inbox
  - Modifier le titre ou les notes
- **Filtres :** par état et par type suggéré

**Règles :**

- capture possible en < 30 secondes (titre seul suffit)
- un élément traité garde la trace de sa destination
- un élément écarté ne crée aucun objet
- l'inbox peut être vidée régulièrement (lors de la revue)

---

### 3.3 Liste des projets

**Objectif :** voir tous les projets et leur état.

**Données affichées :**

- nom, état, priorité, prochaine action (titre), date de dernière revue
- compteur de tâches `todo` et `in_progress`

**Actions disponibles :**

- créer un projet
- filtrer par état et priorité
- accéder à la fiche d'un projet
- archiver un projet (depuis un menu d'action)

**Règles :**

- projets archivés masqués par défaut (filtre activable)
- tri par défaut : actifs d'abord, puis priorité, puis date de dernière revue

---

### 3.4 Fiche projet

**Objectif :** tout voir et tout faire sur un projet.

**Données affichées :**

- nom, slug, état, priorité
- problème à résoudre (`problem_statement`)
- résultat attendu (`expected_outcome`)
- description
- workspace, dépôt, URL principale
- dates de revue

**Sous-sections avec listes :**

| Sous-section | Contenu |
|---|---|
| Prochaine action | Titre de la tâche `is_next_action` (lien cliquable) |
| Tâches | Liste avec état, priorité, échéance ; possibilité de créer |
| Décisions | Liste avec état ; possibilité de créer |
| Ressources | Liste avec type ; possibilité de créer |
| Actifs | Liste avec type et état ; possibilité d'associer un actif existant |
| Versions | Liste avec label, état, date ; possibilité de créer |
| Activité récente | Derniers événements du projet |

**Actions disponibles :**

- modifier les champs du projet
- changer l'état (avec validation des contraintes)
- mettre en pause, terminer, abandonner
- archiver
- créer une tâche, une décision, une ressource ou une version

**Règles :**

- passer à `active` exige `problem_statement`, `expected_outcome` et une prochaine action
- passer à `completed` exige `completed_at` et vérifie qu'aucune tâche n'est `in_progress`
- passer à `abandoned` exige `abandoned_reason`
- `completed` et `abandoned` masquent les boutons de création de tâche

---

### 3.5 Détail d'une tâche

**Objectif :** voir, modifier et faire progresser une tâche.

**Données affichées :** tous les champs de `Task`.

**Actions disponibles :**

- modifier titre, description, priorité, échéance
- désigner comme prochaine action (`is_next_action`)
- changer d'état :
  - `todo` → `in_progress`
  - `in_progress` → `completed` (avec `result_summary` et `evidence_url`)
  - `in_progress` → `blocked` (avec `blocker_description`)
  - `in_progress` → `waiting` (avec `review_on`)
  - `blocked` → `todo` (blocage levé)
  - `waiting` → `todo` (disponible à nouveau)
- annuler (avec `canceled_reason` facultatif)
- archiver

**Règles :**

- `completed` exige `result_summary` et `completed_at`
- `blocked` exige `blocker_description`
- une tâche `blocked`, `waiting`, `completed` ou `canceled` ne peut pas être `is_next_action`
- terminer la prochaine action déclenche la sélection d'une nouvelle prochaine action

---

### 3.6 Détail d'une décision

**Objectif :** documenter un choix et son raisonnement.

**Données affichées :** tous les champs de `Decision`.

**Actions disponibles :**

- créer une décision depuis la fiche projet
- modifier les champs d'une décision `proposed`
- accepter (avec `choice`, `consequences`, `decided_at`)
- rejeter (avec `decided_at`)
- remplacer par une nouvelle décision (l'ancienne passe à `superseded`)

**Règles :**

- `accepted` exige `choice`, `consequences` et `decided_at`
- `superseded` exige `superseded_by` pointant vers une décision du même projet
- une décision ne peut pas se remplacer elle-même
- une décision acceptée n'est pas modifiée silencieusement

---

### 3.7 Détail d'une ressource

**Objectif :** conserver une information utile.

**Données affichées :** titre, type, contenu Markdown, URL source, chemin source (sans contenu de fichier), projet (optionnel).

**Actions disponibles :**

- créer, modifier, archiver
- le contenu Markdown est édité avec aperçu

**Règles :**

- une ressource possède au moins `content`, `source_url` ou `source_path`
- `source_path` peut pointer vers un fichier sensible sans en copier le contenu
- un prompt (`resource_type = prompt`) est un texte structuré, pas un objet exécutable

---

### 3.8 Registre des actifs

**Objectif :** répertorier tout élément technique durable.

**Données affichées :**

- liste : nom, type, état, environnement, projet propriétaire, dernière vérification
- filtres par type, état et environnement

**Fiche d'un actif :** nom, type, état, environnement, URL, chemin, description, projet propriétaire, dernière vérification.

**Actions disponibles :**

- créer un actif
- modifier, archiver
- marquer comme vérifié (`last_verified_at` mis à jour)
- associer à un projet

**Règles :**

- un actif possède au moins `url`, `path` ou `description`
- aucun secret dans les champs
- un actif `retired` n'apparaît pas dans les vues actives

---

### 3.9 Détail d'une version

**Objectif :** documenter une livraison significative.

**Données affichées :** label, statut, résumé, URL de référence, dates, résultat de validation, projet, actif associé.

**Actions disponibles :**

- créer une version depuis la fiche projet
- modifier une version `prepared`
- marquer comme `released`, `validated`, `failed` ou `withdrawn`

**Règles :**

- `version_label` unique dans le projet
- `validated` ou `failed` exige `validation_result` et `validated_at`
- les états autres que `prepared` exigent `released_at`
- si `asset` est renseigné, son projet propriétaire doit correspondre

---

### 3.10 Recherche

**Objectif :** retrouver rapidement n'importe quel élément.

**Données :** résultats groupés par type (projets, tâches, décisions, ressources, actifs, versions). Chaque résultat affiche le titre, le type, le projet associé, et l'état.

**Actions :** saisie textuelle, accès direct à l'élément.

---

### 3.11 Authentification

**Objectif :** protéger l'accès (MVP mono-utilisateur).

**Écrans :** connexion (login + mot de passe), déconnexion.

**Règles :**

- une seule session admin
- pas d'inscription publique
- protection CSRF
- mot de passe jamais loggé ni affiché

---

## 4. Ordre de construction recommandé

| Ordre | Écran | Justification |
|---|---|---|
| 1 | Authentification | Prérequis à tout le reste |
| 2 | Tableau de bord | Page d'accueil, vide au début mais structure en place |
| 3 | Projets (liste + fiche) | Premier objet métier, permet de créer le premier projet |
| 4 | Tâches (détail) | Permet le cycle projet → prochaine action |
| 5 | Inbox | Capture rapide, rend l'outil utilisable au quotidien |
| 6 | Décisions | Conservation des choix importants |
| 7 | Ressources | Notes, prompts et références |
| 8 | Actifs | Registre technique |
| 9 | Versions | Livraisons significatives |
| 10 | Recherche | Utile dès que le volume de données augmente |

Le tableau de bord, les projets et les tâches forment le **noyau** à construire en premier.

---

## 5. Ce que ce document ne contient pas

- maquettes graphiques, couleurs et typographie
- code HTML, CSS ou templates Django
- design system ou composants réutilisables
- gestion des erreurs détaillée
- pagination précise
- responsive design (l'application est locale et desktop dans le MVP)
- mode sombre, thèmes ou préférences utilisateur
