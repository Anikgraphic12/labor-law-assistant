#!/usr/bin/env python3
"""Point d'entrée principal — Assistant Code du Travail (RAG)."""

import argparse

from src.corpus_loader import CorpusLoader
from src.chunker import Chunker
from src.embedder import Embedder
from src.chatbot import get_chatbot


def index_corpus(force: bool = False):
    """Indexe le corpus dans ChromaDB."""

    print("=" * 60)
    print("INDEXATION DU CORPUS")
    print("=" * 60)

    loader = CorpusLoader()
    articles = loader.load()

    print(f"📄 Articles chargés : {len(articles)}")

    chunker = Chunker()
    chunks = chunker.chunk_all(articles)

    print(f"✂️ Chunks créés : {len(chunks)}")

    embedder = Embedder()
    embedder.index_chunks(chunks, force_reindex=force)

    print("\n✅ Indexation terminée !")

    try:
        stats = embedder.get_stats()
        print(f"📊 Stats : {stats}")
    except Exception:
        pass


def chat_mode():
    """Mode conversation avec l'assistant juridique."""

    print("=" * 60)
    print("🤖 Assistant Juridique — Code du Travail")
    print("Base : Code du travail + RAG")
    print("LLM : Groq")
    print("Tapez 'quit' pour quitter")
    print("Tapez 'index' pour réindexer")
    print("=" * 60)

    bot = get_chatbot()

    while True:

        try:
            question = input("\n❓ Votre question : ").strip()

            if question.lower() in ["quit", "exit", "q"]:
                print("👋 Au revoir !")
                break


            if question.lower() == "index":
                index_corpus(force=True)
                continue


            if not question:
                continue


            print("\n⏳ Recherche en cours...")

            result = bot.ask(question)


            print(
                f"\n🔍 Type de recherche : "
                f"{result.get('type_recherche', 'N/A')}"
            )


            articles = result.get("articles", [])

            print(
                f"📄 Articles trouvés : {len(articles)}"
            )


            for i, article in enumerate(articles, 1):

                numero = article.get("numero") or "N/A"
                titre = article.get("titre") or "Sans titre"
                etat = article.get("etat") or ""

                print(
                    f"   {i}. Article {numero} "
                    f"- {titre} ({etat})"
                )


            print("\n📋 Réponse :")
            print("-" * 50)

            print(
                result.get(
                    "reponse",
                    "Aucune réponse générée."
                )
            )

            print("-" * 50)


        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break


        except Exception as e:
            print(f"❌ Erreur : {e}")


def test_retrieval():

    print("=" * 60)
    print("TEST DU RETRIEVAL")
    print("=" * 60)

    bot = get_chatbot()


    questions = [
        "Quelle est la durée légale du travail ?",
        "Comment fonctionne la rupture conventionnelle ?",
        "Qu'est-ce qu'un CDD ?",
        "Combien de congés payés possède un salarié ?"
    ]


    for question in questions:

        print(f"\n📝 Question : {question}")

        articles, type_recherche = bot.rag.recherche(question)

        print(
            f"Recherche : {type_recherche}"
        )

        if articles:
            print(
                "Articles trouvés :",
                [
                    a.get("numero")
                    for a in articles[:3]
                ]
            )

        else:
            print("❌ Aucun article trouvé")



def main():

    parser = argparse.ArgumentParser(
        description="Assistant Code du Travail RAG"
    )


    parser.add_argument(
        "--index",
        action="store_true",
        help="Indexe le corpus"
    )


    parser.add_argument(
        "--force-index",
        action="store_true",
        help="Force la réindexation"
    )


    parser.add_argument(
        "--test",
        action="store_true",
        help="Teste le retrieval"
    )


    args = parser.parse_args()


    if args.index or args.force_index:

        index_corpus(
            force=args.force_index
        )

    elif args.test:

        test_retrieval()

    else:

        chat_mode()



if __name__ == "__main__":
    main()