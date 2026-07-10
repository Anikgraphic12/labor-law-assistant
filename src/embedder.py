"""Gestion de la base vectorielle avec ChromaDB.

Contrainte du sujet : la base doit être persistée et rechargée
sans réindexation à chaque lancement.
"""
import os
from pathlib import Path
from typing import List, Dict, Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_DIR, EMBEDDING_MODEL


class Embedder:
    """
    Gère les embeddings et la base vectorielle ChromaDB.
    La base est persistée sur disque dans data/chroma_db/.
    """
    
    COLLECTION_NAME = "code_travail"
    
    def __init__(self):
        self.model = None
        self.client = None
        self.collection = None
        self._init_model()
        self._init_chroma()
    
    def _init_model(self):
        """Charge le modèle d'embedding (une seule fois)."""
        print(f"🔄 Chargement du modèle d'embedding : {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Modèle chargé")
    
    def _init_chroma(self):
        """Initialise ChromaDB avec persistance sur disque."""
        # Crée le dossier s'il n'existe pas
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Récupère ou crée la collection
        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME,
            metadata={"embedding_model": EMBEDDING_MODEL}
        )
        
        count = self.collection.count()
        print(f"✅ Collection '{self.COLLECTION_NAME}' : {count} documents")
    
    def index_chunks(self, chunks: List[Dict], force_reindex: bool = False):
        """
        Indexe les chunks dans ChromaDB.
        Si la base existe déjà et force_reindex=False, ne réindexe pas.
        """
        existing_count = self.collection.count()
        
        if existing_count > 0 and not force_reindex:
            print(f"⏭️  Base déjà indexée ({existing_count} docs). Pas de réindexation.")
            return
        
        if existing_count > 0 and force_reindex:
            print("🗑️  Suppression de l'ancienne collection...")
            self.client.delete_collection(self.COLLECTION_NAME)
            self.collection = self.client.create_collection(
                name=self.COLLECTION_NAME,
                metadata={"embedding_model": EMBEDDING_MODEL}
            )
        
        print(f"🔄 Indexation de {len(chunks)} chunks...")
        
        # Préparation des données
        ids = [c["id"] for c in chunks]
        texts = [c["texte_embedding"] for c in chunks]
        metadatas = [{
            "numero": c["numero"],
            "titre": c["titre"],
            "texte": c["texte"],
            "etat": c["etat"],
            "contexte_hierarchie": c["contexte_hierarchie"],
            "source_file": c["source_file"]
        } for c in chunks]
        
        # Génération des embeddings par batch
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_end = min(i + batch_size, len(chunks))
            batch_texts = texts[i:batch_end]
            batch_ids = ids[i:batch_end]
            batch_metadatas = metadatas[i:batch_end]
            
            embeddings = self.model.encode(batch_texts).tolist()
            
            self.collection.add(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_texts,
                metadatas=batch_metadatas
            )
            
            print(f"   ... {batch_end}/{len(chunks)} chunks indexés")
        
        print(f"✅ Indexation terminée : {self.collection.count()} documents")
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Recherche vectorielle par similarité cosinus.
        Retourne les chunks les plus pertinents avec leurs métadonnées.
        """
        # Embedding de la requête
        query_embedding = self.model.encode([query]).tolist()
        
        # Recherche
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        # Formatage des résultats
        chunks_trouves = []
        for i in range(len(results["ids"][0])):
            chunks_trouves.append({
                "id": results["ids"][0][i],
                "texte_embedding": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            })
        
        return chunks_trouves
    
    def search_by_article_number(self, numero: str) -> List[Dict]:
        """
        Recherche lexicale par numéro d'article (recherche hybride).
        Utilise la métadonnée 'numero' pour une correspondance exacte.
        """
        # ChromaDB ne supporte pas les requêtes WHERE complexes,
        # donc on fait une recherche vectorielle large et on filtre
        results = self.search(f"Article {numero}", n_results=20)
        
        # Filtre par numéro exact
        filtered = [
            r for r in results 
            if numero.upper() in r["metadata"].get("numero", "").upper()
        ]
        
        return filtered[:5]
    
    def get_stats(self) -> Dict:
        """Statistiques de la base."""
        return {
            "collection": self.COLLECTION_NAME,
            "documents": self.collection.count(),
            "embedding_model": EMBEDDING_MODEL,
            "chroma_dir": str(CHROMA_DIR)
        }