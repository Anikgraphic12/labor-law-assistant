"""Moteur de recherche RAG sur le Code du travail."""
import json
import re
from typing import List, Dict, Optional, Tuple

from src.config import ARTICLES_FILE, MAX_ARTICLES


class RAGEngine:
    """Moteur de recherche sur les articles du Code du travail."""
    
    def __init__(self, articles_file=None):
        self.articles_file = articles_file or ARTICLES_FILE
        self.articles = []
        self._load()
    
    def _load(self):
        """Charge les articles en mémoire."""
        with open(self.articles_file, "r", encoding="utf-8") as f:
            self.articles = json.load(f)
        print(f"✅ {len(self.articles)} articles chargés")
    
    def recherche_numero(self, numero: str) -> List[Dict]:
        """Recherche par numéro exact (ex: L1231-1)."""
        numero = numero.upper().strip()
        return [a for a in self.articles if numero in a.get("numero", "").upper()]
    
    def recherche_mots_cles(self, mots_cles: str, max_results: int = None) -> List[Dict]:
        """Recherche par mots-clés avec scoring simple."""
        max_results = max_results or MAX_ARTICLES * 2
        mots = [m.lower() for m in mots_cles.split() if len(m) > 2]
        if not mots:
            return []
        
        results = []
        for art in self.articles:
            texte = f"{art.get('titre','')} {art.get('texte','')}".lower()
            score = sum(1 for m in mots if m in texte)
            if score > 0:
                results.append((score, art))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [art for _, art in results[:max_results]]
    
    def recherche(self, question: str, max_results: int = None) -> Tuple[List[Dict], str]:
        """
        Recherche intelligente : détecte numéro d'article ou mots-clés.
        Retourne (articles, type_recherche).
        """
        max_results = max_results or MAX_ARTICLES
        
        # Détection numéro d'article (pattern: L1234-1, D1234-5, etc.)
        match = re.search(r'[LDRT]\d{4}(?:-\d+)?', question.upper())
        if match:
            articles = self.recherche_numero(match.group())
            return articles[:max_results], f"numéro ({match.group()})"
        
        # Recherche par mots-clés
        articles = self.recherche_mots_cles(question, max_results)
        return articles[:max_results], "mots-clés"
    
    def formater_contexte(self, articles: List[Dict]) -> str:
        """Formate les articles pour le prompt LLM."""
        blocs = []
        for art in articles:
            bloc = f"""--- Article {art.get('numero', 'N/A')} ---
Titre: {art.get('titre', 'N/A')}
État: {art.get('etat', 'N/A')}

{art.get('texte', 'N/A')}
"""
            blocs.append(bloc)
        return "\n\n".join(blocs)
    
    def construire_prompt(self, question: str, articles: List[Dict]) -> str:
        """Construit le prompt complet pour le LLM."""
        contexte = self.formater_contexte(articles)
        
        return f"""Tu es un expert en droit du travail français. Réponds à la question UNIQUEMENT sur la base des articles du Code du travail fournis ci-dessous.

CONTEXTE (Articles du Code du travail):
{contexte}

QUESTION: {question}

INSTRUCTIONS:
- Réponds de manière claire et structurée
- Cite précisément les articles utilisés (ex: "Selon l'article L1231-1...")
- Si le contexte ne permet pas de répondre, dis-le honnêtement
- N'invente aucune information

RÉPONSE:"""


# Singleton pour réutilisation
_rag_engine = None

def get_engine() -> RAGEngine:
    """Retourne l'instance unique du moteur RAG."""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    return _rag_engine