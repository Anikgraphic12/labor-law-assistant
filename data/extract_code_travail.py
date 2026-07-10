import xml.etree.ElementTree as ET
import os
import json

# Chemin de base (depuis votre find_code_travail.py)
BASE_DIR = r"D:\BUREAU\labor_law_assistant\data\data\legi_extract\20260708-215132\legi\global\code_et_TNC_en_vigueur\code_en_vigueur\LEGI\TEXT"

# Le CID du Code du travail et son chemin réel dans l'arborescence
CODE_TRAVAIL_CID = "LEGITEXT000006072050"
CODE_TRAVAIL_PATH = os.path.join(BASE_DIR, "00", "00", "06", "07", "20", CODE_TRAVAIL_CID)

# Dossier de sortie
OUTPUT_DIR = r"D:\BUREAU\labor_law_assistant\data\code_travail"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_article(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        meta_commun = root.find(".//META_COMMUN")
        meta_article = root.find(".//META_ARTICLE")
        
        numero = meta_commun.findtext("NUM", default="") if meta_commun is not None else ""
        article_id = meta_commun.findtext("ID", default="") if meta_commun is not None else ""
        titre = meta_article.findtext("TITRE", default="") if meta_article is not None else ""
        etat = meta_article.findtext("ETAT", default="") if meta_article is not None else ""
        
        # Hiérarchie
        contexte = root.find(".//CONTEXTE")
        hierarchie = {}
        if contexte is not None:
            texte_ref = contexte.find(".//TEXTE")
            if texte_ref is not None:
                hierarchie["code"] = texte_ref.findtext("TITRE_TXT", default="Code du travail")
            for niveau in ["TITRE", "CHAPITRE", "SECTION", "SOUS_SECTION"]:
                elem = contexte.find(f".//{niveau}")
                if elem is not None:
                    hierarchie[niveau.lower()] = elem.findtext("TITRE", default="")
        
        # Texte
        bloc_textuel = root.find(".//BLOC_TEXTUEL")
        texte = ""
        if bloc_textuel is not None:
            contenu = bloc_textuel.find("CONTENU")
            if contenu is not None:
                texte = " ".join(contenu.itertext()).strip()
                texte = " ".join(texte.split())
        
        return {
            "id": article_id,
            "numero": numero,
            "titre": titre,
            "etat": etat,
            "hierarchie": hierarchie,
            "texte": texte,
            "source_file": str(xml_path)
        }
        
    except Exception as e:
        print(f"  Erreur {xml_path}: {e}")
        return None


def extract_code_travail():
    articles_dir = os.path.join(CODE_TRAVAIL_PATH, "article")
    
    print(f"Recherche dans: {articles_dir}")
    
    if not os.path.exists(articles_dir):
        print(f"❌ Dossier non trouvé: {articles_dir}")
        # Essayons de trouver le bon chemin automatiquement
        print("\n🔍 Recherche automatique du dossier article...")
        for root_path, dirs, files in os.walk(BASE_DIR):
            if CODE_TRAVAIL_CID in root_path and "article" in dirs:
                articles_dir = os.path.join(root_path, "article")
                print(f"✅ Trouvé: {articles_dir}")
                break
        else:
            print("❌ Impossible de trouver le dossier article")
            return [], []
    
    articles = []
    total = 0
    
    for root_path, dirs, files in os.walk(articles_dir):
        for file in files:
            if file.endswith(".xml") and file.startswith("LEGIARTI"):
                total += 1
                filepath = os.path.join(root_path, file)
                article = parse_article(filepath)
                if article and article["texte"]:
                    articles.append(article)
                
                if total % 500 == 0:
                    print(f"   ... {total} fichiers, {len(articles)} articles valides")
    
    print(f"\n✅ Total fichiers: {total}")
    print(f"✅ Articles valides: {len(articles)}")
    
    articles_vigueur = [a for a in articles if a["etat"] == "VIGUEUR"]
    print(f"✅ Articles en vigueur: {len(articles_vigueur)}")
    
    return articles, articles_vigueur


def save_for_rag(articles, suffix=""):
    # JSON brut
    output_file = os.path.join(OUTPUT_DIR, f"code_travail_articles{suffix}.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n💾 JSON: {output_file} ({len(articles)} articles)")
    
    # Format chunks pour RAG
    chunks = []
    for art in articles:
        chunk = {
            "id": art["id"],
            "numero": art["numero"],
            "titre": art["titre"],
            "code": "Code du travail",
            "etat": art["etat"],
            "hierarchie": art["hierarchie"],
            "content": f"Article {art['numero']} - {art['titre']}\n\n{art['texte']}",
            "metadata": {
                "source": "LEGI",
                "cid": CODE_TRAVAIL_CID,
                "date_extraction": "2026-07-09"
            }
        }
        chunks.append(chunk)
    
    chunks_file = os.path.join(OUTPUT_DIR, f"code_travail_chunks{suffix}.json")
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    print(f"💾 Chunks RAG: {chunks_file}")
    
    return chunks


if __name__ == "__main__":
    print("=" * 60)
    print("EXTRACTION DU CODE DU TRAVAIL - BASE LEGI")
    print("=" * 60)
    
    all_articles, articles_vigueur = extract_code_travail()
    
    if all_articles:
        print("\n" + "=" * 60)
        print("SAUVEGARDE")
        print("=" * 60)
        
        save_for_rag(all_articles, "_complet")
        
        if articles_vigueur:
            chunks = save_for_rag(articles_vigueur, "_vigueur")
            
            print("\n" + "=" * 60)
            print("EXEMPLE")
            print("=" * 60)
            ex = chunks[0]
            print(f"Article: {ex['numero']}")
            print(f"Titre: {ex['titre']}")
            print(f"Texte (200 car): {ex['content'][:200]}...")
    else:
        print("\n❌ Aucun article extrait")