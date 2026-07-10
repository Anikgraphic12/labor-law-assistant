import tarfile


archive = "LEGI_20260708-215132.tar.gz"


with tarfile.open(
    archive,
    "r:gz"
) as tar:

    tar.extractall(
        "data/legi_extract"
    )


print("Extraction terminée")