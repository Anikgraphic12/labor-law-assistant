"""Logique conversationnelle du chatbot juridique."""
from src.rag_engine import get_engine
from src.llm_client import get_llm


# DISCLAIMER JURIDIQUE — obligatoire, ajouté systématiquement
DISCLAIMER = "\n\n⚠️ **Avertissement** : Cet assistant ne fournit pas de conseil juridique. Consultez un avocat ou l'inspection du travail pour votre situation personnelle."


class Chatbot:
    """Assistant juridique Code du travail."""
    
    def __init__(self):
        self.rag = get_engine()
        self.llm = get_llm()
    
    def ask(self, question: str) -> dict:
        """
        Pose une question et retourne la réponse structurée.
        Le disclaimer est AJOUTÉ SYSTÉMATIQUEMENT dans le code,
        indépendamment de ce que répond le LLM.
        """
        # Recherche RAG
        articles, type_recherche = self.rag.recherche(question)
        
        if not articles:
            return {
                "question": question,
                "reponse": (
                    "Je n'ai trouvé aucun article pertinent dans le Code du travail "
                    "pour répondre à cette question."
                    + DISCLAIMER
                ),
                "articles": [],
                "type_recherche": type_recherche,
                "prompt": None
            }
        
        # Construction du prompt
        prompt = self.rag.construire_prompt(question, articles)
        
        # Génération LLM
        reponse_llm = self.llm.generate(prompt)
        
        # AJOUT DU DISCLAIMER — garanti à 100%, le LLM ne peut pas l'oublier
        reponse_finale = reponse_llm + DISCLAIMER
        
        return {
            "question": question,
            "reponse": reponse_finale,
            "articles": [
                {
                    "numero": a.get("numero"),
                    "titre": a.get("titre"),
                    "etat": a.get("etat")
                }
                for a in articles
            ],
            "type_recherche": type_recherche,
            "prompt": prompt
        }


# Singleton
_chatbot = None

def get_chatbot() -> Chatbot:
    global _chatbot
    if _chatbot is None:
        _chatbot = Chatbot()
    return _chatbot