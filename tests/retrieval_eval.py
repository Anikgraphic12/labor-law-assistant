from sentence_transformers import SentenceTransformer
from src.indexing import get_collection, MODEL_NAME

model = SentenceTransformer(MODEL_NAME)
collection = get_collection()

tests = [
    ("Combien de jours de congés payés par mois de travail ?", "L3141-3"),
]

for question, article_attendu in tests:
    emb = model.encode(question).tolist()
    res = collection.query(query_embeddings=[emb], n_results=3)
    articles_trouves = [m["article"] for m in res["metadatas"][0]]
    ok = article_attendu in articles_trouves
    print(f"{'OK' if ok else 'ECHEC'} - {question} -> top: {articles_trouves}")
