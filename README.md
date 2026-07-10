Assistant Code du Travail — RAG
Description du projet

Ce projet consiste à développer un assistant juridique basé sur une architecture RAG (Retrieval Augmented Generation) permettant de répondre aux questions relatives au Code du travail français.

L'objectif est de combiner :

une base documentaire juridique issue de la base LEGI disponible sur data.gouv.fr ;
une recherche vectorielle permettant de retrouver les articles pertinents ;
un modèle de langage capable de générer une réponse contextualisée.
Architecture du projet

Le pipeline fonctionne selon les étapes suivantes :

Extraction du corpus juridique
Téléchargement de la base LEGI depuis data.gouv.fr.
Extraction des articles du Code du travail au format XML avec des fichiers python
Transformation en corpus exploitable.
Préparation des documents
Chaque article de loi correspond à une unité documentaire.
Conservation du numéro d'article afin de garantir la traçabilité juridique.
Indexation vectorielle
Génération des embeddings avec un modèle sentence-transformers.
Stockage dans une base vectorielle ChromaDB persistante.
Retrieval + génération
Recherche des articles pertinents selon la question utilisateur.
Injection du contexte retrouvé dans le prompt du LLM.
Génération d'une réponse accompagnée d'un avertissement juridique.
Structure des données

Le corpus utilisé par le système est :

data/
├── code_travail/
│   └── code_travail_articles_vigueur.json
│
└── chroma_db/
    └── Base vectorielle ChromaDB persistée

Le fichier code_travail_articles_vigueur.json contient les articles du Code du travail extraits depuis la base LEGI.

La base chroma_db contient les embeddings déjà générés afin d'éviter une réindexation complète au premier lancement.

Installation

Créer un environnement virtuel :

python -m venv .venv

Activer l'environnement :

Windows :

.venv\Scripts\activate

Installer les dépendances :

pip install -r requirements.txt
Configuration

Créer un fichier .env à partir de :

.env.example

Puis renseigner les variables nécessaires :

GROQ_API_KEY=votre_cle_api
Lancement du projet

Lancer l'application :

python app.py
Tests

Tester le moteur de recherche :

python test_search.py
Limites actuelles

Le corpus extrait contient actuellement un nombre limité d'articles du Code du travail.

Une extraction complète des articles permettrait :

d'améliorer la couverture documentaire ;
d'augmenter la pertinence des résultats ;
de réduire les risques d'absence de contexte.
Avertissement

Cet assistant fournit une aide à la recherche juridique et ne constitue pas un avis juridique professionnel.
Les réponses doivent être vérifiées avec les textes officiels en vigueur.