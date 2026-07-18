# Décision 0004 — Intégration Hermes : capture contrôlée et idempotente dans l'Inbox

- **Date :** 18 juillet 2026
- **Statut :** acceptée
- **Portée :** sous-commande `atelier capture`

## Contexte

Après la mise en place de `atelier status` (lecture seule, décision 0003), Hermes doit pouvoir enregistrer des idées, tâches pressenties et signalements dans l'Inbox d'Atelier. L'interface Web existante (`inbox_capture`) crée déjà des InboxItems sans validation approfondie ni traçabilité Hermes.

## Décisions

- **Sous-commande `capture`** ajoutée au CLI `atelier`
- **Arguments obligatoires :** `--title`, `--idempotency-key`
- **Arguments facultatifs :** `--notes`, `--suggested-type`, `--project-slug`
- **Idempotence persistante** par champ `InboxItem.idempotency_key` (unique, nullable, max 255)
- **Transaction atomique** `InboxItem` + `Activity` via `transaction.atomic()`
- **Activity générique** avec acteur `HERMES`, message fixe ne contenant ni titre ni notes
- **Écriture strictement limitée à InboxItem** — pas de création directe de Project, Task, Decision, Resource, Asset ou Release
- **Service dédié** `apps/integrations/services/capture.py` (séparation CLI/métier)
- **Contrat JSON v1.0** pour succès (`created`/`reused`) et erreurs

## Idempotence

| Scénario | Comportement |
|---|---|
| Première capture avec une clé | `InboxItem` + `Activity` créés, statut `created` |
| Même clé, même payload | Objet existant retourné, statut `reused` |
| Même clé, payload différent | Erreur `idempotency_conflict`, aucune écriture |

## Modification du modèle

- Champ `idempotency_key` ajouté à `InboxItem` (migration `0003_add_inbox_idempotency_key`)
- Unique, nullable — compatible avec les captures Web existantes
- Aucune autre modification du schéma

## Conséquences positives

- Hermes peut capturer sans risque de doublon
- Transaction garantit qu'aucune Activity orpheline n'est créée
- Separation service/CLI facilite les tests et extensions futures
- Le modèle reste compatible avec les captures Web (clé nullable)

## Limites

- Concurrence : deux créations simultanées avec la même clé peuvent produire une IntegrityError (le client doit relire avec la même clé pour récupérer l'objet existant)
- La détection de secrets dans le texte libre est impossible — la règle est documentaire
- La qualification reste humaine — `capture` ne crée que des InboxItems
