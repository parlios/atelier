# Parcours utilisateur et vocabulaire métier — Atelier

- **Version :** 1.0
- **Statut :** validé
- **Document parent :** `docs/PRODUCT_CHARTER.md`
- **Portée :** MVP

## 1. Principe directeur

Atelier organise un cycle d’exécution plutôt qu’une accumulation d’informations :

```text
Capturer une information
        ↓
La qualifier
        ↓
Décider si elle mérite un projet ou une action
        ↓
Choisir la prochaine action
        ↓
Exécuter l’action
        ↓
Enregistrer le résultat
        ↓
Choisir la prochaine action
```

**Règle centrale : tout projet actif doit présenter clairement une prochaine action exécutable.**

Un projet actif sans prochaine action nécessite une revue.

## 2. Parcours utilisateur principal

### 2.1 Ouvrir le tableau de bord

À l’ouverture d’Atelier, max voit en priorité :

1. les projets actifs ;
2. la prochaine action de chaque projet ;
3. les actions prioritaires ;
4. les éléments bloqués ou en attente ;
5. les décisions à prendre ;
6. les éléments non traités dans l’inbox ;
7. les projets nécessitant une revue.

Le tableau de bord doit permettre de répondre à la question : **quelle est la meilleure chose à faire maintenant ?**

Il ne doit pas devenir un écran rempli de statistiques décoratives.

### 2.2 Capturer une information

Une zone de capture rapide est disponible depuis toutes les pages.

**Champ obligatoire :**

- titre ou texte libre.

**Champs facultatifs :**

- type pressenti ;
- projet éventuel ;
- commentaire ;
- lien.

La capture doit rester possible en moins de 30 secondes. L’utilisateur ne doit pas être obligé de choisir immédiatement entre une idée, une tâche, un document ou une décision. L’élément entre d’abord dans l’inbox.

### 2.3 Qualifier l’élément d’inbox

Lors du traitement de l’inbox, chaque élément reçoit l’une des destinations suivantes :

| Destination | Usage |
|---|---|
| Créer un projet | L’élément représente une initiative suffisamment importante |
| Créer une tâche | Une action concrète doit être réalisée |
| Créer une décision | Un choix doit être formulé ou conservé |
| Créer une ressource | L’information mérite d’être conservée |
| Associer à un élément existant | L’information complète un objet existant |
| Écarter | L’élément n’apporte pas suffisamment de valeur |
| Conserver dans l’inbox | La qualification est reportée |

L’élément original reste traçable, mais n’apparaît plus dans l’inbox active une fois traité.

### 2.4 Créer ou compléter un projet

Une idée ne devient pas automatiquement un projet.

Pour créer un projet, il faut au minimum pouvoir formuler :

- son nom ;
- le problème qu’il cherche à résoudre ;
- le résultat attendu ;
- son état ;
- sa prochaine action s’il devient actif.

Un projet sans prochaine action peut exister en exploration ou être planifié, mais il ne doit pas être considéré comme actif.

### 2.5 Définir la prochaine action

Une prochaine action doit être :

- concrète ;
- observable ;
- suffisamment petite ;
- réalisable sans nouvelle clarification majeure ;
- rédigée avec un verbe d’action.

Un projet actif peut contenir plusieurs tâches, mais une seule tâche est désignée comme prochaine action principale.

### 2.6 Exécuter l’action

Dans le MVP, l’exécution se déroule généralement en dehors d’Atelier :

- dans le dépôt du projet ;
- dans Hermes ;
- dans Base44 ;
- dans GitHub ;
- dans un service externe ;
- lors d’un échange humain.

Atelier conserve l’action prévue, son état, son résultat, les liens vers les preuves et la prochaine action qui en découle. Il n’exécute pas encore lui-même les agents et automatisations.

### 2.7 Terminer l’action et enregistrer son résultat

Lorsqu’une tâche est terminée, l’utilisateur indique :

- le résultat obtenu ;
- une preuve ou un lien éventuel ;
- les informations importantes apprises ;
- la prochaine action du projet.

Une tâche ne doit pas être marquée comme terminée simplement parce qu’elle a été commencée ou qu’un fichier a été produit. Le résultat doit correspondre à son objectif.

### 2.8 Enregistrer une version significative

Une version est créée seulement lorsqu’un résultat constitue une livraison significative :

- première version utilisable ;
- MVP ;
- version bêta ;
- mise en production ;
- correction importante ;
- évolution majeure.

Les modifications techniques détaillées restent dans Git. Toutes les tâches terminées ne produisent donc pas une version.

### 2.9 Revenir au tableau de bord

Après l’enregistrement du résultat :

- la tâche terminée disparaît des actions en cours ;
- la nouvelle prochaine action est mise en avant ;
- le projet reste actif ;
- son historique est conservé ;
- un éventuel blocage apparaît clairement.

Le cycle peut alors recommencer.

## 3. Boucles d’utilisation

### 3.1 Capture continue

```text
Nouvelle information
    → Inbox
```

Objectif : ne pas perdre l’information sans interrompre le travail pour la classer.

### 3.2 Pilotage quotidien

```text
Tableau de bord
    → Choisir une prochaine action
    → Exécuter
    → Enregistrer le résultat
    → Définir la suite
```

C’est la boucle principale du produit.

### 3.3 Revue périodique

```text
Traiter l’inbox
    → Revoir les projets actifs
    → Identifier les projets sans prochaine action
    → Examiner les blocages
    → Mettre en pause ou clôturer les projets
    → Réorganiser les priorités
```

La revue empêche Atelier de devenir une base obsolète.

## 4. Vocabulaire métier

### 4.1 Inbox

**Définition :** espace temporaire de capture contenant des informations qui n’ont pas encore été qualifiées.

Elle peut recevoir une idée, une observation, une tâche pressentie, une question, un lien, un prompt, une décision potentielle ou une information à classer.

Elle n’est ni une liste permanente de tâches, ni un espace documentaire, ni un projet, ni une archive.

| État | Signification |
|---|---|
| À traiter | L’élément attend une qualification |
| Traité | Il a été transformé ou associé |
| Écarté | Il a été rejeté |

**Règle :** l’inbox doit pouvoir être vidée régulièrement.

### 4.2 Idée

**Définition :** possibilité, hypothèse ou opportunité qui n’a pas encore été qualifiée comme projet.

Une idée n’est pas une entité indépendante dans le MVP. Elle est d’abord un élément d’inbox. Si elle mérite d’être conservée sans devenir un projet, elle devient une ressource de type `Idée`.

### 4.3 Projet

**Définition :** initiative limitée dans le temps, orientée vers un résultat identifiable et nécessitant plusieurs actions coordonnées.

Un projet possède un problème, un résultat attendu, un état, une priorité, une prochaine action lorsqu’il est actif, des tâches, des décisions, des ressources, des actifs et éventuellement des versions.

Une tâche isolée, une simple note, un actif durable ou un domaine permanent ne sont pas des projets.

| État | Signification |
|---|---|
| Exploration | Le problème ou la solution est encore étudié |
| Planifié | Le projet est accepté, mais son exécution n’a pas commencé |
| Actif | Le projet est en cours d’exécution |
| En pause | Le travail est volontairement suspendu |
| Terminé | Le résultat attendu a été atteint |
| Abandonné | Le projet est arrêté sans atteindre le résultat prévu |

L’archivage est une action de rangement, pas un résultat métier. Un projet terminé ou abandonné peut ensuite être archivé.

### 4.4 Tâche

**Définition :** unité de travail concrète contribuant à l’avancement d’un projet.

Une tâche doit de préférence commencer par un verbe, produire un résultat vérifiable et être associée à un projet.

| État | Signification |
|---|---|
| À faire | La tâche peut être exécutée |
| En cours | Le travail a effectivement commencé |
| En attente | La tâche dépend d’une date ou d’un événement externe |
| Bloquée | Un obstacle identifié empêche son exécution |
| Terminée | Le résultat attendu a été obtenu |
| Annulée | La tâche ne doit plus être exécutée |

`En attente` signifie qu’aucune action immédiate n’est nécessaire avant un événement connu. `Bloquée` signifie qu’un obstacle doit être résolu.

### 4.5 Prochaine action

**Définition :** tâche exécutable désignée comme le prochain mouvement principal d’un projet actif.

La prochaine action n’est pas une entité différente de la tâche. C’est un rôle attribué à une tâche.

Règles :

- un projet actif doit posséder une prochaine action ;
- une seule tâche peut être la prochaine action principale ;
- elle doit être dans l’état `À faire` ou `En cours` ;
- une tâche terminée, annulée, bloquée ou en attente ne peut pas rester prochaine action ;
- terminer la prochaine action oblige à en choisir une nouvelle ou à changer l’état du projet.

### 4.6 Décision

**Définition :** choix explicite effectué entre plusieurs options et suffisamment important pour que son raisonnement mérite d’être conservé.

Une décision contient le contexte, la question, le choix, les alternatives considérées, les conséquences, la date et le projet concerné.

| État | Signification |
|---|---|
| Proposée | La décision est encore à prendre |
| Acceptée | Le choix est applicable |
| Rejetée | La proposition n’a pas été retenue |
| Remplacée | Une décision ultérieure l’a rendue obsolète |

Une préférence mineure, une tâche, une note ou un changement accidentel ne constituent pas une décision métier.

### 4.7 Ressource

**Définition :** information utile conservée pour comprendre ou exécuter un projet.

| Type | Usage |
|---|---|
| Note | Information libre ou observation |
| Idée | Idée conservée sans devenir immédiatement un projet |
| Document | Contenu structuré en Markdown |
| Prompt | Instruction réutilisable destinée à une IA |
| Procédure | Suite d’étapes reproductibles |
| Référence | Lien, fichier ou source externe |

Une ressource informe le travail, mais ne représente pas une action à exécuter.

### 4.8 Prompt

**Définition :** ressource textuelle contenant des instructions réutilisables destinées à un modèle ou à un agent IA.

Dans le MVP, un prompt est un type de ressource, pas un objet exécuté automatiquement. Il peut indiquer son objectif, son texte, son contexte d’utilisation, ses variables attendues, le modèle ou l’outil conseillé et des notes d’utilisation.

Les tests comparatifs, l’exécution automatisée et les mesures de performance sont reportés après le MVP.

### 4.9 Actif

**Définition :** élément technique ou opérationnel durable utilisé, produit ou maintenu dans le cadre d’un projet.

Types initiaux :

- application ;
- agent IA ;
- automatisation ;
- dépôt ;
- service externe ;
- infrastructure.

Un actif peut contenir son nom, son type, son projet propriétaire, son état, son URL ou chemin, son environnement, sa dernière validation et des notes non sensibles.

**Différence :** un projet est un travail temporaire visant un résultat ; un actif est un élément durable issu ou utilisé par ce travail.

### 4.10 Version ou livraison

**Définition :** état identifiable d’un actif ou d’un produit remis, publié ou validé à un moment donné.

Une version contient un libellé ou numéro, un résumé, une date, un état, une preuve, un lien vers Git ou le déploiement et le résultat de validation.

| État | Signification |
|---|---|
| Préparée | La version est identifiée mais pas encore livrée |
| Livrée | La version est rendue disponible |
| Validée | Les critères de validation sont satisfaits |
| Échouée | La livraison ou la validation a échoué |
| Retirée | La version a été volontairement retirée |

### 4.11 Résultat

**Définition :** conséquence vérifiable de l’exécution d’une tâche.

Dans le MVP, le résultat n’est pas une entité autonome. Il est enregistré lors de la clôture de la tâche avec une note, une preuve éventuelle et la date d’achèvement.

### 4.12 Blocage

**Définition :** obstacle identifié empêchant une tâche ou un projet d’avancer.

Dans le MVP, le blocage n’est pas une entité indépendante. Une tâche bloquée contient la description de l’obstacle, l’action nécessaire pour le lever et éventuellement une date de revue.

Si lever le blocage nécessite une action concrète, cette action devient une nouvelle tâche.

### 4.13 Activité

**Définition :** événement historique généré par le système, par exemple la création d’un projet, la fin d’une tâche, l’acceptation d’une décision ou la validation d’une version.

L’activité aide à comprendre ce qui s’est passé. Elle ne remplace ni une note ni une décision.

### 4.14 Priorité

**Définition :** indication de l’ordre relatif dans lequel un élément mérite de recevoir de l’attention.

Niveaux initiaux :

- haute ;
- normale ;
- basse.

La priorité ne remplace ni l’échéance, ni l’état, ni le blocage, ni la prochaine action.

### 4.15 Archivage

**Définition :** action consistant à retirer un élément des vues courantes sans le supprimer.

L’archivage ne change pas le résultat métier. La suppression définitive reste exceptionnelle.

## 5. Règles de cohérence métier

### Projets

1. Un projet actif doit avoir un problème et un résultat attendu.
2. Un projet actif doit avoir exactement une prochaine action principale.
3. Un projet terminé ou abandonné ne peut pas avoir de tâche en cours.
4. Mettre un projet en pause retire sa prochaine action des vues quotidiennes.
5. Archiver ne supprime pas le projet.

### Tâches

6. Une tâche terminée doit contenir un résultat minimal.
7. Une tâche bloquée doit expliquer son blocage.
8. Une tâche annulée peut conserver une raison.
9. Une tâche terminée ou annulée ne peut pas être prochaine action.
10. Une tâche appartenant à un projet archivé ne peut pas être démarrée.

### Inbox

11. Un élément traité garde la trace de sa destination.
12. Un élément écarté ne crée aucun nouvel objet.
13. Un élément d’inbox peut être qualifié sans description détaillée.

### Décisions

14. Une décision acceptée doit contenir le choix et ses conséquences.
15. Une décision remplacée doit référencer la décision qui la remplace.
16. Une décision acceptée n’est pas modifiée silencieusement ; une nouvelle décision la remplace.

### Sécurité

17. Aucun champ métier n’est conçu pour recevoir des secrets.
18. Les liens peuvent identifier l’emplacement d’un fichier sensible, mais jamais exposer son contenu.
19. Les suppressions définitives nécessitent une confirmation explicite.

## 6. Scénario de référence

```text
1. max capture :
   « Créer un agent qui analyse les avis clients »

2. L’élément arrive dans l’inbox.

3. Pendant la revue, max constate que le besoin mérite une exploration.

4. Il crée le projet :
   « Agent d’analyse des avis clients »

5. Il renseigne :
   - problème ;
   - résultat attendu ;
   - état : Exploration ;
   - priorité : Normale.

6. Il crée la tâche :
   « Interroger trois commerçants sur leur traitement des avis »

7. Cette tâche devient la prochaine action principale.

8. Après les entretiens, max termine la tâche et enregistre le résultat.

9. Une décision est créée :
   « Construire ou abandonner un prototype ? »

10. La décision est acceptée :
    « Construire un prototype limité à l’analyse thématique. »

11. Le projet passe à l’état Actif.

12. La prochaine action devient :
    « Préparer un jeu de 100 avis clients anonymisés. »

13. Une première version est ultérieurement enregistrée :
    « Prototype 0.1 — classification thématique locale. »
```

Ce scénario constitue le parcours de référence pour la conception et la validation du MVP.

## 7. Décisions de modélisation validées

1. L’inbox est un espace temporaire, pas une bibliothèque permanente.
2. Une idée n’est pas un projet tant que son problème et son résultat attendu ne sont pas suffisamment formulés.
3. La prochaine action est une tâche désignée, pas une entité indépendante.
4. Un projet actif possède exactement une prochaine action principale.
5. Dans le MVP :
   - un prompt est un type de ressource ;
   - un résultat est une information de clôture d’une tâche ;
   - un blocage est un état et un ensemble d’informations portés par une tâche.
