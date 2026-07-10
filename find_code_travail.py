import os
import xml.etree.ElementTree as ET


DOSSIER_LEGI = r"data\data\legi_extract\20260708-215132\legi\global\code_et_TNC_en_vigueur\code_en_vigueur\LEGI"


for root, dirs, files in os.walk(DOSSIER_LEGI):

    for file in files:

        if file.endswith(".xml"):

            chemin = os.path.join(root, file)

            try:

                tree = ET.parse(chemin)

                texte = tree.getroot()

                contenu = ET.tostring(
                    texte,
                    encoding="unicode"
                )

                if "Code du travail" in contenu:

                    print("TROUVE :")
                    print(chemin)


            except Exception:
                pass