import json
import chromadb
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
CORPUS_PATH = "data/corpus.json"
DB_PATH = "data/chroma_db"
COLLECTION_NAME = "code_du_travail"


def load_corpus(path=CORPUS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_index():
    docs = load_corpus()
    model = SentenceTransformer(MODEL_NAME)
    client = chromadb.PersistentClient(path=DB_PATH)

    # Recree la collection pour eviter les doublons si on relance
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": MODEL_NAME},
    )

    ids, embeddings, texts, metadatas = [], [], [], []
    for doc in docs:
        texte_a_embedder = f"{doc['titre']}. {doc['texte']}"
        emb = model.encode(texte_a_embedder).tolist()

        ids.append(doc["id"])
        embeddings.append(emb)
        texts.append(texte_a_embedder)
        metadatas.append({
            "article": doc["article"],
            "theme": doc["theme"],
            "source": doc["source"],
        })

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Index construit : {collection.count()} chunks indexes dans {DB_PATH}")


def get_collection():
    """Utilise par retrieval.py / cli.py pour se connecter sans reindexer."""
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_collection(COLLECTION_NAME)


if __name__ == "__main__":
    build_index()