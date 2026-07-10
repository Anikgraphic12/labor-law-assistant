"""Charge le corpus JSON extrait de LEGI."""
import json
from pathlib import Path
from typing import List, Dict

from src.config import CORPUS_FILE


class CorpusLoader:
    """Charge et valide les articles du Code du travail."""
    
    def __init__(self, filepath: Path = None):
        self.filepath = filepath or CORPUS_FILE
    
    def load(self) -> List[Dict]:
        """Charge les articles depuis le JSON."""
        with open(self.filepath, "r", encoding="utf-8") as f:
            articles = json.load(f)
        
        # Validation minimale : au moins un champ utile
        valid = []
        for art in articles:
            if art.get("numero") or art.get("texte") or art.get("titre") or art.get("id"):
                valid.append(art)
        
        print(f"✅ {len(valid)}/{len(articles)} articles valides chargés")
        return valid
    
    def get_themes(self) -> Dict[str, List[Dict]]:
        """Regroupe les articles par thème (approximatif via numéro)."""
        articles = self.load()
        themes = {
            "contrat_travail": [],
            "duree_travail": [],
            "conges_payes": [],
            "licenciement": [],
            "rupture_conventionnelle": [],
            "salaire": [],
            "representation_personnel": [],
            "harcelement": [],
            "autre": []
        }
        
        for art in articles:
            num = art.get("numero", "")
            if num.startswith("L122") or num.startswith("L124"):
                themes["contrat_travail"].append(art)
            elif num.startswith("L312"):
                themes["duree_travail"].append(art)
            elif num.startswith("L314"):
                themes["conges_payes"].append(art)
            elif num.startswith("L123"):
                themes["licenciement"].append(art)
            elif num.startswith("L1237-11") or num.startswith("L1237-12") or num.startswith("L1237-13") or num.startswith("L1237-14") or num.startswith("L1237-15") or num.startswith("L1237-16") or num.startswith("L1237-17") or num.startswith("L1237-18") or num.startswith("L1237-19"):
                themes["rupture_conventionnelle"].append(art)
            elif num.startswith("L323"):
                themes["salaire"].append(art)
            elif num.startswith("L231"):
                themes["representation_personnel"].append(art)
            elif num.startswith("L115"):
                themes["harcelement"].append(art)
            else:
                themes["autre"].append(art)
        
        # Affiche les stats
        for theme, arts in themes.items():
            if arts:
                print(f"   📂 {theme}: {len(arts)} articles")
        
        return themes