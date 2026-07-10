from sentence_transformers import SentenceTransformer
from src.indexing import get_collection, MODEL_NAME
from src.generation import generate_answer


def main():
    model = SentenceTransformer(MODEL_NAME)
    collection = get_collection()

    print("Assistant Code du travail - tapez 'exit' pour quitter.\n")
    while True:
        question = input("Votre question : ").strip()
        if question.lower() in ("exit", "quit"):
            break
        emb = model.encode(question).tolist()
        res = collection.query(query_embeddings=[emb], n_results=4)
        chunks = [
            {"document": doc, "metadata": meta}
            for doc, meta in zip(res["documents"][0], res["metadatas"][0])
        ]
        reponse = generate_answer(question, chunks)
        print("\n" + reponse + "\n")


if __name__ == "__main__":
    main()
