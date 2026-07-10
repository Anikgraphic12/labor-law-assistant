import json
import os
import xml.etree.ElementTree as ET

# Chemin vers les XML du Code du travail
XML_DIR = r"D:\BUREAU\labor_law_assistant\data\data\legi_extract\20260708-215132\legi\global\code_et_TNC_en_vigueur\code_en_vigueur\LEGI\TEXT\00\00\06\07\20\LEGITEXT000006072050\article"

articles = []

for root, dirs, files in os.walk(XML_DIR):
    for file in files:
        if not file.endswith('.xml') or not file.startswith('LEGIARTI'):
            continue
        
        filepath = os.path.join(root, file)
        try:
            tree = ET.parse(filepath)
            root_elem = tree.getroot()
            
            # Attributs du tag ARTICLE (plus fiables)
            article_id = root_elem.get('id', '')
            numero = root_elem.get('numero', '')
            
            # Fallback sur META_COMMUN
            meta = root_elem.find('.//META_COMMUN')
            if meta is not None and not numero:
                numero = meta.findtext('NUM', default='')
                article_id = meta.findtext('ID', default=article_id)
            
            # Titre et état
            titre = ''
            etat = ''
            meta_art = root_elem.find('.//META_ARTICLE')
            if meta_art is not None:
                titre = meta_art.findtext('TITRE', default='')
                etat = meta_art.findtext('ETAT', default='')
            
            # Texte
            texte = ''
            bloc = root_elem.find('.//BLOC_TEXTUEL')
            if bloc is not None:
                contenu = bloc.find('CONTENU')
                if contenu is not None:
                    texte = ' '.join(contenu.itertext()).strip()
                    texte = ' '.join(texte.split())
            
            # Hiérarchie
            hierarchie = {"code": "Code du travail"}
            ctx = root_elem.find('.//CONTEXTE')
            if ctx is not None:
                txt = ctx.find('TEXTE')
                if txt is not None:
                    hierarchie["code"] = txt.findtext('TITRE_TXT', default='Code du travail')
            
            if texte:  # Garde seulement si texte présent
                articles.append({
                    "id": article_id,
                    "numero": numero,
                    "titre": titre or f"Article {numero}",
                    "etat": etat,
                    "hierarchie": hierarchie,
                    "texte": texte,
                    "source_file": file
                })
                
        except Exception as e:
            continue

# Sauvegarde
output = r"D:\BUREAU\labor_law_assistant\data\code_travail\code_travail_articles_complet.json"
with open(output, 'w', encoding='utf-8') as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

print(f"✅ {len(articles)} articles extraits et sauvegardés")
if articles:
    print(f"Exemple: {articles[0]['numero']} - {articles[0]['titre'][:50]}")