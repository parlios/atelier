# Charte produit — Atelier

- **Version :** 1.0
- **Statut :** validée
- **Propriétaire :** max
- **Assistant opérationnel :** Hermes
- **Type :** application web privée de pilotage

## 1. Vision

Atelier est le système central permettant à max et Hermes de transformer les idées en projets exécutables, de conserver les décisions importantes et de toujours identifier la prochaine action utile.

À terme, Atelier doit fournir une vision cohérente de l’ensemble des produits, applications, agents IA, automatisations et expérimentations.

## 2. Problème à résoudre

Les informations nécessaires à la conduite des projets risquent d’être dispersées entre les conversations IA, les dépôts GitHub, les documents, les outils no-code et les listes de tâches.

Cette fragmentation rend difficiles :

- la compréhension de l’état réel d’un projet ;
- la conservation du raisonnement derrière les décisions ;
- la priorisation des idées ;
- l’identification de la prochaine action ;
- le suivi des versions et livraisons ;
- la coordination entre max, Hermes et les futures automatisations.

Atelier doit fournir une **source de vérité opérationnelle**, sans dupliquer inutilement les systèmes spécialisés.

## 3. Utilisateurs initiaux

### max

Utilisateur humain principal, propriétaire du produit et responsable des décisions.

### Hermes

Assistant opérationnel disposant progressivement de droits contrôlés pour :

- consulter le contexte des projets ;
- enregistrer des éléments dans l’inbox ;
- proposer des tâches ou décisions ;
- mettre à jour une prochaine action après validation ;
- produire des rapports ;
- relier les résultats d’une automatisation au projet concerné.

Le MVP doit rester utilisable sans intégration automatisée avec Hermes.

## 4. Promesse principale

À l’ouverture d’Atelier, max doit pouvoir déterminer rapidement :

1. quels projets sont actifs ;
2. pourquoi ils existent ;
3. dans quel état ils se trouvent ;
4. ce qui les bloque ;
5. quelle est la prochaine action de chacun ;
6. quelles décisions récentes ont été prises ;
7. où se trouvent leurs ressources principales.

La priorité du produit est de **piloter la prochaine action de chaque projet**, et non de stocker un maximum d’informations.

## 5. Cycle de travail principal

```text
Capturer
   ↓
Qualifier
   ↓
Décider
   ↓
Planifier la prochaine action
   ↓
Exécuter
   ↓
Enregistrer le résultat ou la version
   ↓
Définir la prochaine action
```

Toute fonction du MVP doit contribuer directement à ce cycle.

## 6. Périmètre du MVP

Le MVP comprend :

- une application privée et mono-utilisateur ;
- un compte administrateur ;
- une inbox de capture rapide ;
- la gestion des projets ;
- les tâches et prochaines actions ;
- les décisions ;
- les notes, prompts et références ;
- le registre des applications, agents, automatisations et dépôts ;
- les versions ou livraisons significatives ;
- un tableau de bord ;
- une recherche simple et des filtres ;
- des exports ;
- une procédure de sauvegarde et de restauration.

Les notes, petits documents et prompts sont stockés en Markdown. Les documents volumineux sont référencés par lien ou chemin. Aucun secret ne doit être enregistré dans ces contenus.

## 7. Éléments exclus du MVP

Le MVP ne comprend pas :

- la collaboration multi-utilisateur ;
- une application mobile native ;
- une messagerie interne ;
- un CRM, la facturation ou la gestion budgétaire ;
- un diagramme de Gantt ;
- des dépendances complexes entre tâches ;
- la synchronisation automatique avec GitHub ;
- l’exécution d’agents ;
- un moteur d’automatisation ;
- des appels LLM ;
- la recherche vectorielle ou le résumé automatique ;
- les notifications multicanales ;
- le stockage de secrets ou de documents volumineux ;
- une exposition publique.

Ces fonctions ne pourront être réévaluées qu’après une période d’utilisation réelle.

## 8. Sources de vérité

| Information | Source officielle |
|---|---|
| Code source | Dépôt Git |
| Commits, branches et tags | Git |
| Pull requests et workflows | GitHub |
| Documentation technique proche du code | Dépôt du projet |
| Secrets | Gestionnaire ou fichier local protégé prévu à cet effet |
| Contexte produit | Atelier |
| État général du projet | Atelier |
| Décisions produit | Atelier |
| Prochaine action | Atelier |
| Répertoire des actifs | Atelier |
| Versions produit significatives | Atelier, avec lien vers Git ou le déploiement |

Atelier suit uniquement les versions produit significatives. Git conserve le détail technique des changements.

## 9. Contraintes non négociables

- le projet reste sous `/home/maxime/projects` ;
- le dépôt GitHub est privé ;
- aucun secret n’est stocké dans le code ou les contenus ;
- les données sont sauvegardables et exportables ;
- les modifications importantes sont testées ;
- l’architecture reste simple ;
- aucune dépendance n’est ajoutée sans besoin concret ;
- aucune intégration externe n’est indispensable au fonctionnement du MVP ;
- les opérations destructives nécessitent une confirmation ;
- le système doit fonctionner localement avant tout déploiement.

## 10. Choix de réalisation

Atelier est développé directement dans l’environnement local sous `/home/maxime/projects/apps/atelier`.

Base44 n’est pas utilisé pour le cœur d’Atelier. Le plan Base44 Pro reste disponible pour prototyper de futurs produits lorsque sa rapidité apporte un avantage réel.

## 11. Critères de réussite du MVP

Après deux semaines d’utilisation réelle, le MVP est considéré comme utile si :

- chaque projet actif possède une prochaine action explicite ;
- un nouvel élément peut être capturé en moins de 30 secondes ;
- le contexte essentiel d’un projet peut être retrouvé en moins de deux minutes ;
- les décisions importantes ne dépendent plus uniquement des conversations ;
- les dépôts, documents et actifs principaux sont accessibles depuis la fiche du projet ;
- Atelier est consulté naturellement pour décider quoi faire ensuite ;
- la charge de saisie est jugée inférieure au temps économisé ;
- une sauvegarde peut être restaurée avec succès.

Les durées sont des objectifs de conception, pas des engagements contractuels.

## 12. Condition de passage après le MVP

Une phase importante d’intégration, d’IA ou d’automatisation ne sera engagée que si :

1. Atelier est réellement utilisé ;
2. le modèle de données s’est montré suffisamment stable ;
3. le besoin a été observé dans le travail réel ;
4. l’intégration réduit une friction mesurable ;
5. les permissions et le retour arrière sont définis.
