from src.retrieval.search import search_articles


question = "Quelle est la durée légale du travail ?"


results = search_articles(question)


for result in results:
    print("----------------")
    print("Article :", result["article"])
    print("Thème :", result["theme"])
    print("Texte :", result["text"])
    print("Score :", result["score"])