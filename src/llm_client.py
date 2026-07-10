"""Client LLM : support Groq et Ollama (local)."""
import os
from typing import Optional

from groq import Groq

from src.config import (
    LLM_PROVIDER, GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_URL, OLLAMA_MODEL, TEMPERATURE, MAX_TOKENS
)


class LLMClient:
    """Client unifié pour différents fournisseurs LLM."""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self.client = None
        self._init_client()
    
    def _init_client(self):
        if self.provider == "groq":
            if not GROQ_API_KEY:
                raise ValueError(
                    "GROQ_API_KEY manquante.\n"
                    "1. Créez un compte sur https://console.groq.com\n"
                    "2. Générez une API key\n"
                    "3. Ajoutez-la dans le fichier .env"
                )
            self.client = Groq(api_key=GROQ_API_KEY)
            self.model = GROQ_MODEL
        
        elif self.provider == "ollama":
            # Ollama utilise l'API compatible OpenAI
            from openai import OpenAI
            self.client = OpenAI(
                base_url=f"{OLLAMA_URL}/v1",
                api_key="ollama"
            )
            self.model = OLLAMA_MODEL
        
        else:
            raise ValueError(f"Provider inconnu: {self.provider}")
    
    def generate(self, prompt: str) -> str:
        """Génère une réponse à partir du prompt."""
        try:
            if self.provider == "groq":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant juridique spécialisé en droit du travail français. Réponds de manière précise et factuelle."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                return response.choices[0].message.content
            
            elif self.provider == "ollama":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Tu es un assistant juridique spécialisé en droit du travail français."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                return response.choices[0].message.content
                
        except Exception as e:
            return f"❌ Erreur LLM ({self.provider}): {str(e)}"


# Singleton
_llm_client = None

def get_llm() -> LLMClient:
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client