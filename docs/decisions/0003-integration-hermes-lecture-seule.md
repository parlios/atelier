# Décision 0003 — Intégration Hermes en lecture seule par commande Django

- **Date :** 18 juillet 2026
- **Statut :** acceptée
- **Portée :** première intégration entre Hermes et Atelier

## Contexte

Hermes doit pouvoir consulter l'état d'Atelier pour contextualiser ses actions et répondre aux questions de l'utilisateur. Atelier est une application locale, mono-utilisateur, sans API REST. L'architecture doit rester simple, sécurisée et sans dépendance réseau.

## Décisions

- **App générique :** `apps/integrations/` — ni `hermes` ni `atelier` pour éviter tout couplage
- **Frontière CLI locale :** commande Django standard, accessible via le terminal Hermes
- **Sortie JSON versionnée :** `schema_version` "1.0" dans chaque réponse
- **Aucune API REST :** pas de serveur, pas de port, pas de framework additionnel
- **Aucune lecture directe de SQLite :** ORM Django uniquement
- **Aucune écriture pour `status` :** commande en lecture seule vérifiée par test
- **Séparation des responsabilités :** commande ≠ service ≠ contrat
- **Aucune nouvelle dépendance :** Python stdlib + Django uniquement
- **Aucune nouvelle table :** pas de modèle, pas de migration

## Conséquences positives

- Hermes peut immédiatement interroger l'état d'Atelier sans infrastructure
- Réponse JSON prévisible et versionnée
- Architecture extensible vers `capture`, `project` ou `propose` sans refonte
- Tests dédiés (16) couvrant la commande, le contrat et les performances
- 6 requêtes ORM maximum, indépendamment du nombre de projets

## Limites et risques

- La sortie JSON peut contenir des titres saisis par l'utilisateur (risque faible : application privée)
- L'absence de cache peut devenir un problème avec des centaines de projets (hors périmètre MVP)
- La commande est fusionnée dans `main` via fast-forward (commit `35c52c8`)

## Extension future

Les sous-commandes `capture`, `project` et `propose` sont envisagées mais non implémentées. Chacune nécessitera une décision séparée et une validation de sécurité, notamment pour l'écriture.
