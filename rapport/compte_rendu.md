Compte rendu — Assistant Code du Travail basé sur une architecture RAG
1. Présentation du projet

Dans le cadre de ce projet, nous avons développé un assistant juridique basé sur une architecture Retrieval-Augmented Generation (RAG) permettant d'interroger le Code du travail français en langage naturel.

L'objectif est de mettre en place un système capable de :

rechercher automatiquement les articles juridiques pertinents ;
fournir un contexte fiable à un modèle de langage ;
générer une réponse synthétique tout en conservant la traçabilité des sources utilisées.

Le projet combine plusieurs briques technologiques :

extraction et préparation d'un corpus juridique ;
traitement de documents XML ;
création d'embeddings ;
recherche vectorielle ;
génération de réponses par un LLM.
2. Architecture générale du système

Le fonctionnement global du système suit le pipeline suivant :

Base LEGI (data.gouv.fr)
          |
          v
Extraction des fichiers XML
          |
          v
Sélection des articles du Code du travail
          |
          v
Corpus JSON
          |
          v
Découpage documentaire (chunking)
          |
          v
Création des embeddings
          |
          v
Indexation dans ChromaDB
          |
          v
Recherche des documents pertinents
          |
          v
Génération de réponse par le LLM
3. Constitution du corpus juridique
Première approche : API Légifrance

La première solution envisagée était d'utiliser l'API Légifrance afin d'obtenir directement les articles du Code du travail.

Cependant, malgré plusieurs demandes d'accès, les permissions nécessaires n'ont pas été obtenues dans les délais du projet.

Cette contrainte nous a conduits à changer d'approche.

Solution retenue : base LEGI sur data.gouv.fr

Nous avons utilisé la base juridique LEGI disponible sur data.gouv.fr.

L'archive téléchargée présente plusieurs difficultés :

environ 500 Mo compressée ;
environ 2 Go après extraction ;
une structure XML fortement imbriquée ;
une organisation par identifiants juridiques et arborescences complexes.

L'extraction a nécessité plusieurs étapes :

téléchargement de l'archive LEGI ;
décompression des fichiers ;
exploration de l'arborescence XML ;
identification des documents correspondant au Code du travail ;
extraction du contenu des articles ;
transformation en format JSON exploitable.

À cause de la complexité de la structure XML et du temps disponible, nous avons finalement extrait un corpus de 36 articles du Code du travail.

4. Préparation et indexation des documents
Choix du chunking

Nous avons choisi une granularité :

1 article de loi = 1 chunk

Ce choix est volontaire.

Les articles juridiques constituent déjà des unités sémantiques cohérentes. Regrouper plusieurs articles dans un même chunk aurait diminué :

la précision de recherche ;
la traçabilité juridique ;
la capacité à citer correctement les références.

Cette approche permet également de conserver facilement le numéro de l'article associé au contenu récupéré.

Création des embeddings

Les textes extraits sont transformés en représentations vectorielles grâce au modèle :

paraphrase-multilingual-MiniLM-L12-v2

Ce modèle permet de représenter la similarité sémantique entre :

la question de l'utilisateur ;
les articles du corpus.

La première utilisation nécessite le téléchargement du modèle (environ 200 Mo), ce qui a ralenti les phases de test.

Stockage vectoriel avec ChromaDB

Les embeddings sont stockés dans une base vectorielle ChromaDB.

La base est persistée localement :

data/chroma_db/

Au démarrage de l'application, cette base est rechargée afin d'éviter une réindexation complète.

Cette décision permet :

un lancement plus rapide ;
une meilleure expérience utilisateur ;
une architecture conforme aux attentes d'un système RAG.
5. Stratégie de recherche (Retrieval)

Afin d'améliorer la pertinence des résultats, nous avons mis en place une approche hybride.

Recherche directe par numéro d'article

Une détection par expression régulière permet d'identifier les questions contenant une référence juridique.

Exemple :

Que dit l'article L3121-27 ?

Dans ce cas, le système récupère directement l'article correspondant.

Recherche sémantique

Pour les questions générales, une recherche vectorielle basée sur la similarité est utilisée.

Exemple :

Quelle est la durée légale du travail ?

Le système recherche les articles dont le contenu est proche du sens de la question.

6. Génération des réponses

Après récupération des documents pertinents, le contexte juridique est transmis au modèle de langage.

Le prompt a été renforcé afin de :

limiter les hallucinations ;
obliger le modèle à utiliser uniquement le contexte fourni ;
conserver les références aux articles.
7. Difficultés rencontrées
Extraction du corpus

La principale difficulté concernait l'exploitation de la base LEGI.

La structure XML complexe a rendu difficile l'identification automatique des articles du Code du travail.

Le corpus obtenu reste donc limité par rapport à l'objectif initial.

Compatibilité des outils d'indexation

L'intégration de ChromaDB et de Sentence Transformers a nécessité plusieurs ajustements liés aux versions des bibliothèques Python.

Qualité du retrieval

Avec seulement 36 articles disponibles :

la diversité documentaire est faible ;
les scores de similarité restent parfois insuffisants ;
certaines questions peuvent retourner des documents peu pertinents.

Le modèle de génération pouvait également :

inventer des références d'articles ;
produire des citations incorrectes.

Pour limiter ces problèmes, nous avons renforcé le prompt et ajouté un nettoyage des réponses générées.

Gestion du projet avec Git

La collaboration via GitHub a également présenté plusieurs difficultés :

conflits de merge ;
suppression accidentelle de branches ;
mauvaise gestion temporaire des modifications.

Nous avons finalement adopté une organisation basée sur :

main
 |
dev
 |
feature/*

Chaque fonctionnalité est développée sur une branche dédiée puis intégrée via Pull Request.

8. Décisions de conception principales
Conservation de la traçabilité juridique

Le choix "1 article = 1 chunk" permet de toujours associer une réponse à une référence juridique identifiable.

Disclaimer juridique automatique

Plutôt que de demander au LLM de générer systématiquement un avertissement, celui-ci est ajouté directement dans le code.

Cela garantit que chaque réponse rappelle :

que l'assistant est un outil d'aide ;
qu'il ne remplace pas un professionnel du droit.
Persistance de l'index

La sauvegarde de ChromaDB évite de reconstruire les embeddings à chaque lancement.

9. Limites actuelles

Le principal facteur limitant reste la taille du corpus.

Le système actuel fonctionne avec :

36 articles

alors que le Code du travail complet contient plusieurs milliers d'articles.

Cette limitation impacte :

la précision du retrieval ;
la diversité des réponses ;
la confiance des résultats.
10. Améliorations possibles

Avec davantage de temps, plusieurs améliorations pourraient être intégrées :

Corpus complet

Extraire l'ensemble du Code du travail français (~7000 articles).

Cela améliorerait fortement :

la couverture documentaire ;
la pertinence des recherches ;
la qualité des réponses.
Recherche avancée

Ajouter :

BM25 pour une recherche lexicale ;
combinaison BM25 + embeddings ;
reranking des documents récupérés.
Évaluation automatique

Mettre en place une évaluation avec :

jeux de questions/réponses juridiques ;
mesure de précision du retrieval ;
évaluation des réponses générées.
Conclusion

Ce projet nous a permis de mettre en œuvre une architecture RAG complète appliquée au domaine juridique.

Malgré les difficultés liées à l'accès aux données et à la complexité du corpus juridique, nous avons réussi à construire un assistant fonctionnel intégrant :

extraction documentaire ;
embeddings ;
recherche vectorielle ;
génération augmentée par contexte.

Les prochaines évolutions consisteraient principalement à enrichir le corpus et améliorer les méthodes de recherche afin d'obtenir un assistant juridique plus complet et plus fiable.