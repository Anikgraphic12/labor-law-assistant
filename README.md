# Assistant Code du travail (RAG)

Assistant en ligne de commande qui répond à des questions de droit du travail
français en citant systématiquement les articles du Code du travail sur
lesquels il s'appuie, sans utiliser LangChain ni LlamaIndex.

<<<<<<< HEAD
## Architecture du pipeline# labor_law_assistant

Question utilisateur
-> Recherche vectorielle (ChromaDB, embeddings multilingues)
-> Récupération des chunks les plus proches (top-k)
-> Génération de la réponse (Groq, température basse) avec citations obligatoires
-> Ajout de l'avertissement juridique par le code (pas seulement demandé au LLM)

## Structure du dépôt
src/
indexing.py    # Jalon 2 : chunking par article, embeddings, ChromaDB, persistance
generation.py  # Jalon 4 : prompt système, appel Groq, citations, disclaimer
cli.py         # Jalon 5 : boucle interactive
data/
corpus.json    # Corpus source (Option C, saisi manuellement)
chroma_db/     # Base vectorielle persistée (non versionnée, régénérée localement)
tests/
retrieval_eval.py  # Jalon 3 : validation du retrieval sur des questions test
=======
## Architecture du pipeline

```
Question utilisateur
   -> Recherche vectorielle (ChromaDB, embeddings multilingues)
   -> Récupération des chunks les plus proches (top-k)
   -> Génération de la réponse (Groq, température basse) avec citations obligatoires
   -> Ajout de l'avertissement juridique par le code (pas seulement demandé au LLM)
```

## Structure du dépôt

```
src/
  indexing.py    # Jalon 2 : chunking par article, embeddings, ChromaDB, persistance
  generation.py  # Jalon 4 : prompt système, appel Groq, citations, disclaimer
  cli.py         # Jalon 5 : boucle interactive
data/
  corpus.json    # Corpus source (Option C, saisi manuellement)
  chroma_db/     # Base vectorielle persistée (non versionnée, régénérée localement)
tests/
  retrieval_eval.py  # Jalon 3 : validation du retrieval sur des questions test
```
>>>>>>> feature/projet-complet

## Installation

```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # puis renseignez GROQ_API_KEY dans .env
```

## Lancement

```bash
# 1. Indexation (une seule fois, ou après modification du corpus)
python src/indexing.py

# 2. Validation du retrieval (à faire avant d'utiliser le LLM)
python -m tests.retrieval_eval

# 3. Boucle interactive de questions-réponses
python -m src.cli
```

## Corpus

Le corpus (`data/corpus.json`) est constitué manuellement (Option C du sujet),
à partir des textes officiels du Code du travail consultés sur Légifrance.
**État actuel : corpus réduit, à étendre à au moins 5 thèmes** avant la
soutenance (durée du travail, congés payés, contrat de travail, licenciement,
rupture conventionnelle, SMIC, représentation du personnel, harcèlement).

Format attendu (voir `corpus.json`) : une liste d'objets avec `id` (numéro
d'article), `article`, `theme`, `titre`, `texte`, `source`.

## Questions de réflexion

### 1. Granularité du chunking

Nous avons retenu un chunking **par article** : un chunk = un article de loi.
Avantage principal : précision de citation maximale, le numéro d'article
retourné est toujours exact et non ambigu. Inconvénient : un article isolé
peut perdre le contexte de sa section (ex. un article qui suppose qu'on sait
déjà qu'on est dans le cadre d'une rupture conventionnelle). Nous avons
choisi cette approche pour ce projet car la priorité du sujet est la
traçabilité exacte des citations, plus importante ici que la richesse
contextuelle. Une approche hybride (ajouter un résumé par thème en
complément) serait une amélioration possible avec plus de temps.

### 2. Traçabilité

Le numéro d'article est présent à la fois dans le texte embeddé (le titre et
le texte de l'article sont concaténés avant l'embedding) et dans les
métadonnées du chunk (champ `article`). Les métadonnées sont la source de
vérité utilisée par le code pour afficher les articles sources — le prompt
système interdit explicitement au LLM d'inventer un numéro absent du
contexte fourni.

### 3. Fraîcheur

Le corpus a été constitué manuellement à la date indiquée dans le champ
`source` de chaque article. Le système n'implémente pas encore d'indication
automatique de date de mise à jour dans les réponses ; c'est un axe
d'amélioration identifié (afficher la date du corpus dans chaque réponse,
et prévoir une procédure de vérification périodique des articles suivis
sur Légifrance).

### 4. Réponses conditionnelles

Le prompt système demande explicitement une réponse générale assortie de
réserves quand la question dépend de la taille de l'entreprise ou d'une
convention collective, plutôt qu'une question de clarification préalable —
plus adapté à un assistant en ligne de commande sans gestion de session
complexe.

### 5. Frontière du conseil juridique

Le prompt distingue les questions factuelles (réponse directe avec
citation) des questions d'appréciation au cas par cas (ex. "mon
licenciement est-il abusif ?"), pour lesquelles le système rappelle la
règle générale applicable sans jamais rendre de verdict personnel, et
renvoie vers un professionnel (avocat, inspection du travail).

## Choix techniques justifiés

- **ChromaDB avec métrique cosinus explicite** : la métrique par défaut de
  Chroma (distance euclidienne) n'est pas adaptée à des embeddings de
  phrases ; la métrique cosinus est fixée à la création de la collection.
- **Modèle d'embedding multilingue** (`paraphrase-multilingual-mpnet-base-v2`) :
  permet de matcher des questions familières en français avec des articles
  de loi au registre plus formel.
- **Avertissement juridique assemblé par le code**, pas seulement demandé
  dans le prompt : garantit sa présence dans 100% des réponses, répondant
  directement à la contrainte du sujet.
- **Base vectorielle persistée sur disque**, jamais reconstruite au
  lancement du CLI : `src/indexing.py` est un script séparé, lancé
  uniquement quand le corpus change.

## Limites connues / à compléter

- Corpus réduit (Option C, 2 articles actuellement) : à étendre à au moins
  5 thèmes.
 feature/projet-complet
- Un seul cas de test dans `tests/retrieval_eval.py` : à enrichir avec
  5 questions couvrant chaque thème avant la soutenance.
- Pas encore de score de confiance ni de mécanisme de refus explicite hors
  corpus (jalon 6) : amélioration prévue si le temps le permet.
- Pas de mécanisme de mise à jour incrémentale du corpus.

## Ce que nous ferions avec plus de temps

- Étendre le corpus via l'API Légifrance ou le dump LEGI (data.gouv.fr) pour
  couvrir davantage d'articles par thème.
- Ajouter un score de confiance (distance renvoyée par ChromaDB) pour
  détecter et refuser les questions hors corpus sans appeler le LLM.
- Enrichir le jeu de test du retrieval avec une question par thème couvert.
 HEAD

Une fois collé et sauvegardé :
git add README.md
git commit -m "Redaction du README : architecture, installation, questions de reflexion"
git push

 feature/projet-complet
