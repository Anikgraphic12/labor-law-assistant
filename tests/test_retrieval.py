"""Tests de retrieval (Jalon 3)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.chatbot import get_chatbot


def test_questions():
    """Vérifie que les articles attendus remontent pour chaque question."""
    
    QUESTIONS_TEST = [
        ("Quelle est la durée légale du travail ?", "L3121"),
        ("Combien de jours de congés payés par an ?", "L3141"),
        ("Comment fonctionne la rupture conventionnelle ?", "L1237-11"),
        ("Qu'est-ce qu'un contrat à durée déterminée ?", "L1242"),
        ("Quel est le montant du SMIC ?", "L3231"),
    ]
    
    bot = get_chatbot()
    scores = []
    
    print("=" * 60)
    print("TEST DE RETRIEVAL — Jalon 3")
    print("=" * 60)
    
    for question, article_attendu in QUESTIONS_TEST:
        chunks, type_rech, score = bot.rag.recherche(question)
        
        numeros = [c["metadata"].get("numero", "") for c in chunks]
        trouve = any(article_attendu in n for n in numeros)
        
        status = "✅ PASS" if trouve else "❌ FAIL"
        scores.append(trouve)
        
        print(f"\n{status} | {question}")
        print(f"      Attendu : {article_attendu}*")
        print(f"      Trouvés : {numeros[:3]}")
        print(f"      Score   : {score:.2f}")
    
    print(f"\n{'='*60}")
    print(f"Résultat : {sum(scores)}/{len(scores)} tests réussis")
    
    return all(scores)


if __name__ == "__main__":
    success = test_questions()
    sys.exit(0 if success else 1)