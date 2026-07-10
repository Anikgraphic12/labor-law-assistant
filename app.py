#!/usr/bin/env python3
"""Point d'entrée principal — Assistant Code du Travail (RAG)."""
import sys
import argparse

from src.corpus_loader import CorpusLoader
from src.chunker import Chunker
from src.embedder import Embedder
from src.chatbot import get_chatbot


def index_corpus(force: bool = False):
    """Indexe le corpus dans ChromaDB (Jalon 2)."""
    print("=" * 60)
    print("INDEXATION DU CORPUS")
    print("=" * 60)
    
    loader = CorpusLoader()
    articles = loader.load()
    
    chunker = Chunker()
    chunks = chunker.chunk_all(articles)
    
    embedder = Embedder()
    embedder.index_chunks(chunks, force_reindex=force)
    
    print("\n✅ Indexation terminée !")
    stats = embedder.get_stats()
    print(f"   Stats : {stats}")


def chat_mode():
    """Mode conversationnel interactif (Jalon 5)."""
    print("=" * 60)
    print("🤖 Assistant Juridique — Code du Travail")
    print("Base vectorielle : ChromaDB + sentence-transformers")
    print("LLM : Groq (llama-3.3-70b-versatile)")
    print("Tapez 'quit', 'exit' ou 'q' pour sortir")
    print("Tapez 'index' pour réindexer le corpus")
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
            
            print(f"\n🔍 Type de recherche : {result['type_recherche']}")
            print(f"📊 Score de confiance : {result['score_confiance']:.2f}")
            print(f"📄 Documents trouvés : {len(result['chunks'])}")
            
            for i, chunk in enumerate(result['chunks'], 1):
                dist = chunk.get('distance', 'N/A')
                num = chunk.get('numero') or 'N/A'
                titre = chunk.get('titre') or 'Sans titre'
                if isinstance(dist, float):
                    print(f"   {i}. {num} — {titre[:50]}... (distance: {dist:.3f})")
                else:
                    print(f"   {i}. {num} — {titre[:50]}...")
            
            print(f"\n📋 Réponse :\n{'-'*50}")
            print(result['reponse'])
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"❌ Erreur : {e}")


def test_retrieval():
    """Test du retrieval (Jalon 3)."""
    print("=" * 60)
    print("TEST DU RETRIEVAL")
    print("=" * 60)
    
    bot = get_chatbot()
    
    questions_test = [
        ("Quelle est la durée légale du travail ?", "L3121"),
        ("Combien de jours de congés payés ?", "L3141"),
        ("Comment fonctionne la rupture conventionnelle ?", "L1237-11"),
        ("Qu'est-ce qu'un CDD ?", "L1242"),
        ("Quel est le SMIC ?", "L3231"),
    ]
    
    for question, article_attendu in questions_test:
        print(f"\n📝 Question : {question}")
        chunks, type_rech, score = bot.rag.recherche(question)
        
        numeros = [c["metadata"].get("numero", "") for c in chunks]
        trouve = any(article_attendu in n for n in numeros)
        
        status = "✅ PASS" if trouve else "❌ FAIL"
        print(f"   {status} Article attendu : {article_attendu}*")
        print(f"   Articles trouvés : {numeros[:3]}")
        print(f"   Score : {score:.2f}")


def main():
    parser = argparse.ArgumentParser(description="Assistant Code du Travail (RAG)")
    parser.add_argument(
        "--index", action="store_true", 
        help="Indexe le corpus (premier lancement ou mise à jour)"
    )
    parser.add_argument(
        "--force-index", action="store_true",
        help="Force la réindexation (supprime l'ancienne base)"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Lance les tests de retrieval (Jalon 3)"
    )
    
    args = parser.parse_args()
    
    if args.index or args.force_index:
        index_corpus(force=args.force_index)
    elif args.test:
        test_retrieval()
    else:
        chat_mode()


if __name__ == "__main__":
    main()