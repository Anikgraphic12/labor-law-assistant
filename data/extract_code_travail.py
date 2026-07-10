import xml.etree.ElementTree as ET
import os
import json


# Chemin de base LEGI
BASE_DIR = r"D:\BUREAU\labor_law_assistant\data\data\legi_extract\20260708-215132\legi\global\code_et_TNC_en_vigueur\code_en_vigueur\LEGI\TEXT"

# CID Code du travail
CODE_TRAVAIL_CID = "LEGITEXT000006072050"

CODE_TRAVAIL_PATH = os.path.join(
    BASE_DIR,
    "00",
    "00",
    "06",
    "07",
    "20",
    CODE_TRAVAIL_CID
)

# Sortie
OUTPUT_DIR = r"D:\BUREAU\labor_law_assistant\data\code_travail"
os.makedirs(OUTPUT_DIR, exist_ok=True)



# --------------------------------------------------
# Fonction utilitaire pour lire les tags LEGI
# --------------------------------------------------

def find_tag_text(root, possible_tags):
    """
    Recherche un texte dans l'arbre XML
    en ignorant les namespaces XML.
    """

    for elem in root.iter():

        # Retire le namespace éventuel
        tag = elem.tag.split("}")[-1].upper()

        if tag in possible_tags and elem.text:
            return elem.text.strip()

    return ""



# --------------------------------------------------
# Parsing d'un article XML
# --------------------------------------------------

def parse_article(xml_path):

    try:

        tree = ET.parse(xml_path)
        root = tree.getroot()


        # Métadonnées
        numero = find_tag_text(
            root,
            {"NUM", "NUMERO", "NUM_ART"}
        )

        article_id = find_tag_text(
            root,
            {"ID"}
        )

        titre = find_tag_text(
            root,
            {"TITRE", "TITRE_TXT"}
        )

        etat = find_tag_text(
            root,
            {"ETAT"}
        )


        # Hiérarchie
        hierarchie = {}

        contexte = root.find(".//CONTEXTE")

        if contexte is not None:

            texte_ref = contexte.find(".//TEXTE")

            if texte_ref is not None:

                hierarchie["code"] = (
                    texte_ref.findtext(
                        "TITRE_TXT",
                        default="Code du travail"
                    )
                )


            for niveau in [
                "TITRE",
                "CHAPITRE",
                "SECTION",
                "SOUS_SECTION"
            ]:

                elem = contexte.find(f".//{niveau}")

                if elem is not None:

                    hierarchie[niveau.lower()] = (
                        elem.findtext(
                            "TITRE",
                            default=""
                        )
                    )



        # Texte juridique

        texte = ""

        bloc_textuel = root.find(".//BLOC_TEXTUEL")

        if bloc_textuel is not None:

            contenu = bloc_textuel.find("CONTENU")

            if contenu is not None:

                texte = " ".join(
                    contenu.itertext()
                ).strip()

                texte = " ".join(
                    texte.split()
                )



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

        print(
            f"Erreur {xml_path}: {e}"
        )

        return None




# --------------------------------------------------
# Extraction complète
# --------------------------------------------------

def extract_code_travail():

    articles_dir = os.path.join(
        CODE_TRAVAIL_PATH,
        "article"
    )


    print(
        f"Recherche dans: {articles_dir}"
    )


    if not os.path.exists(articles_dir):

        print(
            "Dossier article introuvable"
        )

        return [], []



    articles = []

    total = 0



    for root_path, dirs, files in os.walk(articles_dir):

        for file in files:


            if file.endswith(".xml") and file.startswith("LEGIARTI"):


                total += 1


                filepath = os.path.join(
                    root_path,
                    file
                )


                article = parse_article(filepath)


                if article and article["texte"]:

                    articles.append(article)



    print(
        f"\n✅ Total fichiers: {total}"
    )

    print(
        f"✅ Articles valides: {len(articles)}"
    )


    articles_vigueur = [

        a for a in articles

        if a["etat"].upper() == "VIGUEUR"

    ]


    print(
        f"✅ Articles en vigueur: {len(articles_vigueur)}"
    )


    return articles, articles_vigueur




# --------------------------------------------------
# Préparation RAG
# --------------------------------------------------

def save_for_rag(articles, suffix=""):


    output_file = os.path.join(
        OUTPUT_DIR,
        f"code_travail_articles{suffix}.json"
    )


    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            articles,
            f,
            ensure_ascii=False,
            indent=2
        )


    print(
        f"💾 JSON : {output_file}"
    )



    chunks = []


    for art in articles:


        chunk = {

            "id": art["id"],

            "numero": art["numero"],

            "titre": art["titre"],

            "code": "Code du travail",

            "etat": art["etat"],

            "hierarchie": art["hierarchie"],

            "content":
                f"Article {art['numero']} - {art['titre']}\n\n{art['texte']}",


            "metadata": {

                "source": "LEGI",

                "cid": CODE_TRAVAIL_CID,

                "date_extraction": "2026-07-09"

            }

        }


        chunks.append(chunk)



    chunks_file = os.path.join(
        OUTPUT_DIR,
        f"code_travail_chunks{suffix}.json"
    )


    with open(
        chunks_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            chunks,
            f,
            ensure_ascii=False,
            indent=2
        )


    print(
        f"💾 Chunks RAG : {chunks_file}"
    )


    return chunks




# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":


    print("="*60)

    print(
        "EXTRACTION DU CODE DU TRAVAIL - BASE LEGI"
    )

    print("="*60)



    all_articles, articles_vigueur = extract_code_travail()



    if all_articles:


        save_for_rag(
            all_articles,
            "_complet"
        )


        if articles_vigueur:


            chunks = save_for_rag(
                articles_vigueur,
                "_vigueur"
            )


            print("\nEXEMPLE")

            exemple = chunks[0]


            print(
                "Article:",
                exemple["numero"]
            )

            print(
                "Titre:",
                exemple["titre"]
            )

            print(
                exemple["content"][:200]
            )
