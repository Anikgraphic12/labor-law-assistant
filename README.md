# labor_law_assistant
Assistant Code du Travail - RAG
Description du projet

Ce projet consiste à développer un assistant juridique basé sur une architecture Retrieval-Augmented Generation (RAG) permettant de répondre à des questions concernant le Code du travail français.

L'objectif est de combiner :

une base documentaire issue du Code du travail ;
un moteur de recherche sémantique basé sur des embeddings ;
un modèle de langage (LLM) capable de générer des réponses contextualisées.

L'assistant recherche d'abord les articles pertinents dans le corpus juridique, puis utilise ces informations pour produire une réponse accompagnée d'un avertissement juridique.

⚠️ Cet assistant ne constitue pas un conseil juridique. Les réponses générées doivent être vérifiées avec les sources officielles ou auprès d'un professionnel du droit.

Architecture du projet

Le pipeline RAG fonctionne selon les étapes suivantes :

Base LEGI (data.gouv.fr)
          |
          v
Extraction des articles du Code du travail
          |
          v
Corpus JSON
          |
          v
Découpage en chunks
          |
          v
Création des embeddings
          |
          v
Base vectorielle ChromaDB
          |
          v
Recherche des articles pertinents
          |
          v
Génération de réponse par le LLM
Source des données

La première approche utilisant l'API Légifrance n'a pas pu être finalisée en raison de problèmes d'autorisation d'accès.

Nous avons donc utilisé la base LEGI disponible sur data.gouv.fr.

Le traitement réalisé :

Téléchargement de l'archive LEGI.
Décompression de la base XML.
Exploration de l'arborescence juridique.
Extraction des articles du Code du travail.
Transformation du contenu en corpus exploitable par le moteur RAG.

Le corpus actuel contient 36 articles du Code du travail.

Une extraction complète du Code du travail (environ 7000 articles) permettrait d'améliorer la couverture documentaire et la qualité du retrieval.

Technologies utilisées
Backend et traitement des données
Python
JSON
XML parsing
Sentence Transformers
ChromaDB
Intelligence artificielle
Modèle d'embeddings :
paraphrase-multilingual-MiniLM-L12-v2
Modèle de génération :
LLM via API
Gestion du projet
Git / GitHub
Environnement virtuel Python
Structure du dépôt
labor-law-assistant/

│
├── app.py                    # Point d'entrée de l'application
├── requirements.txt          # Dépendances Python
├── README.md
│
├── src/
│   ├── config.py             # Configuration du projet
│   ├── corpus_loader.py      # Chargement du corpus juridique
│   ├── chunker.py            # Découpage des documents
│   ├── embedder.py           # Création des embeddings
│   ├── rag_engine.py         # Moteur de recherche RAG
│   ├── llm_client.py         # Client LLM
│   └── chatbot.py            # Gestion du chatbot
│
├── data/
│   ├── corpus.json           # Corpus extrait du Code du travail
│   └── chroma_db/            # Base vectorielle persistée
│
├── tests/
│   └── test_retrieval.py     # Tests du moteur de recherche
│
└── rapport/
    └── compte_rendu.md       # Rapport du projet
Installation
1. Cloner le projet
git clone https://github.com/Anikgraphic12/labor-law-assistant.git

cd labor-law-assistant
2. Créer un environnement virtuel
python -m venv .venv

Activation :

Windows
.venv\Scripts\activate
3. Installer les dépendances
pip install -r requirements.txt
4. Configuration des variables d'environnement

Créer un fichier .env à partir du modèle :

.env.example

Puis renseigner les clés nécessaires :

GROQ_API_KEY=votre_cle_api
Lancement de l'application

Depuis la racine du projet :

python app.py

L'application charge la base vectorielle existante et permet d'interroger le chatbot.

Fonctionnement du Retrieval

Le système utilise deux méthodes complémentaires :

Recherche par numéro d'article

Une détection par expression régulière permet d'identifier directement les demandes contenant un numéro d'article.

Exemple :

Que dit l'article L3121-27 ?

L'article correspondant est récupéré directement.

Recherche sémantique

Pour les questions générales, les embeddings permettent de retrouver les articles juridiquement proches du sujet demandé.

Exemple :

Quelle est la durée légale du travail ?

Le moteur recherche les articles associés au temps de travail.

Choix de conception
1 article = 1 chunk

Chaque article du Code du travail constitue une unité documentaire indépendante.

Ce choix permet :

une meilleure traçabilité juridique ;
la conservation du numéro d'article ;
une réponse plus facilement vérifiable.
Persistance de ChromaDB

La base vectorielle est sauvegardée localement afin d'éviter une réindexation complète à chaque lancement.

Disclaimer juridique automatique

Un avertissement juridique est ajouté automatiquement aux réponses afin de limiter les risques liés à l'interprétation automatique du droit.

Limites actuelles
Corpus limité à 36 articles.
Recherche perfectible avec une base documentaire réduite.
Nécessité d'intégrer l'ensemble du Code du travail pour obtenir une couverture complète.
Les réponses du LLM restent soumises aux limites des modèles génératifs.
Améliorations possibles

Avec davantage de temps, plusieurs évolutions seraient possibles :

Extraction complète du Code du travail.
Recherche hybride avancée (BM25 + embeddings).
Reranking des documents récupérés.
Ajout des conventions collectives.
Interface utilisateur web.
Évaluation automatique de la qualité des réponses.
Équipe projet

Projet réalisé dans le cadre d'un module Data & IA.

Architecture basée sur les principes de :

NLP ;
recherche vectorielle ;
modèles de langage ;
systèmes RAG.