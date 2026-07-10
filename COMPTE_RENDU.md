# Compte rendu (1 page)

## Difficultés rencontrées

- **Changement d'équipe en cours de projet** : un troisième membre a quitté
  le groupe, nous obligeant à redistribuer les 6 jalons entre 2 personnes
  et à recommencer sur un nouveau dépôt GitHub, avec un temps réduit.

- **Environnement virtuel et fichiers de configuration** : plusieurs
  aller-retours ont été nécessaires pour bien isoler le venv de chaque
  nouveau clone, et le fichier `.env.example` n'avait pas encore été créé
  sur le nouveau dépôt, bloquant temporairement la configuration de la
  clé API Groq.

- **Fichier `requirements.txt` corrompu** : une première tentative de
  génération du fichier via `pip freeze` a produit une liste de 46
  dépendances transitives (torch, pandas, scipy...) au lieu des paquets
  réellement utilisés, avec en plus un problème d'encodage (le fichier
  était traité comme binaire par Git). Corrigé en le réécrivant
  manuellement avec les 5 dépendances directes du projet (chromadb,
  sentence-transformers, groq, python-dotenv, pytest).

- **Confusion sur l'organisation des branches Git** : plusieurs commits ont
  d'abord été faits sur de mauvaises branches (`feature/indexing` au lieu
  de `feature/corpus`, ou l'inverse), nécessitant des corrections
  (`git reset`, déplacement de commits) pour garder un historique cohérent
  avec la répartition du travail entre les deux membres restants.

- **Caractères accentués mal affichés dans le terminal Windows** : le
  contenu réel du corpus JSON (UTF-8) s'affichait avec des caractères
  corrompus dans `cmd.exe`, ce qui a nécessité une vérification directe en
  Python pour confirmer que le fichier lui-même était correct.

## Décisions de conception

- **Option C pour le corpus** (saisie manuelle depuis Légifrance) plutôt
  que l'API Légifrance ou le dump LEGI, faute de temps disponible après la
  réorganisation de l'équipe.
- **Chunking par article** : un chunk = un article, pour garantir une
  citation toujours exacte (voir README, question 1).
- **Avertissement juridique assemblé par le code**, jamais laissé au seul
  prompt, pour garantir sa présence dans 100% des réponses.
- **Métrique cosinus explicite sur ChromaDB** plutôt que la métrique par
  défaut, plus adaptée aux embeddings de phrases.

## Ce que nous ferions avec plus de temps

- Étendre le corpus à au moins 5 thèmes (actuellement très réduit) via
  l'API Légifrance ou le dump LEGI, pour réduire le plafonnement du
  critère "constitution du corpus".
- Enrichir `tests/retrieval_eval.py` avec une question de test par thème
  plutôt qu'une seule.
- Implémenter une amélioration du jalon 6 (score de confiance basé sur les
  distances ChromaDB, pour détecter et refuser les questions hors corpus
  sans appeler le LLM).
- Ajouter une indication de fraîcheur du corpus dans chaque réponse.
