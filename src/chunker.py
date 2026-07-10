"""Stratégie de chunking pour les articles juridiques.

Q1 Réponse (à documenter dans le README) :
Nous retenons l'approche « 1 article = 1 chunk » car :
- Les articles de loi sont déjà des unités sémantiques cohérentes
- La tracabilité (numéro d'article) est maximale
- Le risque de couper un raisonnement juridique est nul
- La taille moyenne (~200-500 tokens) est compatible avec les modèles d'embedding

Inconvénient : les articles très longs (listes à puces) pourraient être
mieux décomposés, mais c'est rare dans le Code du travail.
"""
from typing import List, Dict


class Chunker:
    """Découpe le corpus en chunks pour l'embedding."""
    
    def __init__(self):
        pass
    
    def chunk_article(self, article: Dict) -> Dict:
        """
        Transforme un article en chunk unique.
        Le texte embeddé inclut le numéro et le titre pour la pertinence.
        """
        numero = article.get("numero", "")
        titre = article.get("titre", "")
        texte = article.get("texte", "")
        hierarchie = article.get("hierarchie", {})
        
        # Texte à embedder : numéro + titre + texte pour maximiser la pertinence
        # Le numéro aide pour les recherches par référence exacte
        texte_embedding = f"Article {numero} - {titre}\n\n{texte}"
        
        # Hiérarchie formatée pour le contexte
        contexte_hierarchie = " > ".join([
            v for k, v in hierarchie.items() 
            if v and k != "code"
        ])
        
        return {
            "id": article.get("id", ""),
            "numero": numero,
            "titre": titre,
            "texte": texte,
            "texte_embedding": texte_embedding,  # Ce qui est embeddé
            "hierarchie": hierarchie,
            "contexte_hierarchie": contexte_hierarchie,
            "etat": article.get("etat", ""),
            "source_file": article.get("source_file", "")
        }
    
    def chunk_all(self, articles: List[Dict]) -> List[Dict]:
        """Chunk tous les articles."""
        chunks = []
        for art in articles:
            chunk = self.chunk_article(art)
            if chunk["texte_embedding"].strip():
                chunks.append(chunk)
        print(f"✅ {len(chunks)} chunks créés (1 article = 1 chunk)")
        return chunks