# Assistant Code du travail (RAG)

Assistant en ligne de commande qui répond à des questions de droit du travail
français en citant systématiquement les articles du Code du travail sur
lesquels il s'appuie, sans utiliser LangChain ni LlamaIndex.

## Lancement (version finale)

```bash
python -m src.main
```

## Architecture du pipeline

## Structure du dépôt
src/
config.py          # Configuration centralisée
corpus_loader.py    # Chargement et classement par thème du corpus
embedder.py          # Embeddings + ChromaDB, persistance
rag_engine.py         # Recherche (numéro exact / mots-clés / vectorielle)
llm_client.py         # Client Groq
chatbot.py             # Logique conversationnelle, disclaimer garanti
main.py                # Point d'entrée CLI
data/
code_travail/code_travail_articles_vigueur.json   # Corpus (5 thèmes)
tests/
retrieval_eval.py     # Validation du retrieval

## Installation

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy .env.example .env   # puis renseignez GROQ_API_KEY dans .env
```

## Corpus

Corpus constitué manuellement (Option C) à partir des textes officiels du
Code du travail sur Légifrance, complété par une tentative d'extraction
automatisée du dump LEGI (Option B). Couvre 5 thèmes : congés payés,
rupture conventionnelle, SMIC, licenciement.

## Questions de réflexion

### 1. Granularité du chunking
Chunking par article : un chunk = un article de loi, pour une précision de
citation maximale. Inconvénient : perte du contexte de section pour
certains articles isolés.

### 2. Traçabilité
Le numéro d'article est conservé dans les métadonnées de chaque chunk et
utilisé directement par le code pour construire la liste des sources
citées, plutôt que de faire confiance au texte libre généré par le LLM.

### 3. Fraîcheur
Le corpus indique sa source et sa date de constitution. Une vérification
périodique sur Légifrance des articles suivis serait nécessaire pour un
usage réel.

### 4. Réponses conditionnelles
Le prompt système demande une réponse générale assortie de réserves quand
la question dépend de la taille de l'entreprise ou d'une convention
collective.

### 5. Frontière du conseil juridique
Le système distingue les questions factuelles (réponse directe sourcée)
des questions d'appréciation (ex. "mon licenciement est-il abusif ?"),
pour lesquelles il rappelle les règles applicables sans rendre de verdict,
et renvoie vers un professionnel.

## Limites connues

- Corpus encore limité en volume malgré l'extraction LEGI (bug résolu sur
  les champs numero/titre, mais peu d'articles extraits au total).
- Jalon 6 (amélioration : score de confiance) non implémenté.

## Ce que nous ferions avec plus de temps

- Corriger le filtre d'extraction XML pour couvrir davantage d'articles
  du dump LEGI.
- Ajouter un score de confiance pour détecter les questions hors corpus.
