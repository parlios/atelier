# Décision 0001 — Système d’interface d’Atelier

- **Date :** 2026-07-16
- **Statut :** acceptée
- **Portée :** frontend du MVP local

## Contexte

L’application Django était fonctionnelle mais utilisait des templates HTML bruts, sans CSS, composants partagés, navigation complète ni hiérarchie visuelle. La charte produit exige que le tableau de bord permette d’identifier rapidement la prochaine action utile, sans transformer Atelier en tableau de statistiques décoratives.

## Décision

Atelier utilise un système d’interface local fondé sur :

- les templates Django standards ;
- Django staticfiles ;
- un fichier CSS structuré et autonome ;
- une typographie système, sans police distante ;
- un sprite SVG local pour les icônes ;
- aucun JavaScript, framework CSS, CDN ou télémétrie ;
- une sidebar sur desktop et une navigation native `details/summary` sur mobile ;
- un shell partagé avec navigation active, recherche, session, messages et footer ;
- des composants HTML/CSS réutilisables : boutons, cartes, badges, listes, tableaux, formulaires, messages, états vides et pagination.

Le thème clair est la seule variante livrée dans le MVP. Les couleurs, surfaces et espacements sont définis par des variables CSS afin de permettre un futur thème sombre sans le développer maintenant.

## Navigation

La navigation principale contient : Tableau de bord, Projets, Tâches, Inbox, Décisions, Ressources, Registre, Releases et Recherche.

Comme les listes globales Tâches, Décisions et Releases n’existaient pas, trois vues en lecture seule ont été ajoutées. Elles réutilisent les modèles actuels, acceptent un filtre d’état et ne nécessitent aucune migration.

L’état actif repose sur `request.resolver_match`. Le compteur Inbox est fourni par un context processor léger aux seules pages authentifiées.

## Sémantique des statuts

Chaque statut est toujours affiché avec son libellé. La couleur n’est qu’un renforcement visuel.

- information : actif, en cours, livré ;
- succès : terminé, accepté, validé, traité ;
- avertissement : en pause, en attente, à traiter, dégradé ;
- danger : abandonné, bloqué, échoué ;
- inactif : annulé, remplacé, retiré, inactif, écarté ;
- neutre : exploration, planifié, à faire, proposé, préparé.

## Accessibilité et responsive

- un seul `h1` rendu par page ;
- lien d’évitement ;
- landmarks et fils d’Ariane nommés ;
- labels associés aux champs ;
- focus clavier visible ;
- zones interactives dimensionnées ;
- messages avec rôles `status` ou `alert` ;
- aucune information transmise uniquement par une icône ou une couleur ;
- adaptation desktop, portable, tablette et mobile ;
- respect de `prefers-reduced-motion` ;
- aucune commande de navigation dépendante de JavaScript.

## Conséquences

### Positives

- cohérence visuelle sur tous les écrans ;
- dépendances nulles côté frontend ;
- fonctionnement hors ligne ;
- maintenance centralisée ;
- amélioration progressive possible ;
- aucun impact sur les modèles ou migrations.

### Limites acceptées

- les formulaires métier restent actuellement des formulaires HTML traités directement dans les vues ;
- les erreurs métier sont surtout globales, même si elles sont désormais visibles ;
- la pagination est préparée comme composant mais n’est pas activée tant que le volume local ne la justifie pas ;
- aucun thème sombre n’est livré ;
- aucune interaction dynamique ou modal JavaScript n’est introduite.

## Alternatives rejetées

- Bootstrap ou Tailwind : dépendances et conventions inutiles à ce stade ;
- SPA React/Vue/Svelte : complexité sans bénéfice pour le MVP local ;
- HTMX : différé jusqu’à observation d’une friction réelle ;
- polices et icônes via CDN : incompatibles avec l’objectif d’autonomie locale ;
- faux bouton hamburger : remplacé par un contrôle HTML natif fonctionnel.
