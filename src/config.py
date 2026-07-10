"""Configuration centralisée du projet."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le .env AVANT tout le reste
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Debug (à retirer après)
print(f"[DEBUG] .env chargé depuis: {env_path}")
print(f"[DEBUG] GROQ_API_KEY présente: {'OUI' if os.getenv('GROQ_API_KEY') else 'NON'}")

# Chemins
DATA_DIR = BASE_DIR / "data" / "code_travail"

# Fichiers de données
ARTICLES_FILE = DATA_DIR / "code_travail_articles_vigueur.json"
CHUNKS_FILE = DATA_DIR / "code_travail_chunks_vigueur.json"

# LLM - GROQ (par défaut)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Ollama (optionnel, offline)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# RAG
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", "5"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))