# Compte rendu (1 page)

## Difficultés rencontrées

- **Changement d'équipe en cours de projet** : un troisième membre a quitté
  le groupe, nous obligeant à redistribuer les 6 jalons entre 2 personnes,
  puis finalement à reprendre l'ensemble du projet en solo sur un nouveau
  dépôt GitHub, avec un temps réduit.

- **Fusion d'historiques Git non liés** : lors de la reconstitution du
  projet sur le nouveau dépôt, un commit a été créé sur un historique local
  totalement indépendant (aucun ancêtre commun avec la branche `dev`
  distante). Corrigé avec `git merge --allow-unrelated-histories`, suivi
  d'une résolution manuelle des conflits fichier par fichier (`.gitignore`,
  `requirements.txt`, `README.md`, `data/corpus.json`, `src/indexing.py`,
  `.env.example`), en conservant systématiquement la version la plus
  complète et la plus récente.

- **Fichier `requirements.txt` corrompu** : une première tentative de
  génération du fichier via `pip freeze` a produit une liste de 46
  dépendances transitives (torch, pandas, scipy...) au lieu des paquets
  réellement utilisés, avec en plus un problème d'encodage (le fichier
  était traité comme binaire par Git). Corrigé en le réécrivant
  manuellement avec les 5 dépendances directes du projet (chromadb,
  sentence-transformers, groq, python-dotenv, pytest).

- **Caractères accentués mal affichés dans le terminal Windows** : le
  contenu réel du corpus JSON (UTF-8) s'affichait avec des caractères
  corrompus dans `cmd.exe`, ce qui a nécessité une vérification directe en
  Python pour confirmer que le fichier lui-même était correct.

## Décisions de conception

- **Option C pour le corpus** (saisie manuelle depuis Légifrance) plutôt
  que l'API Légifrance ou le dump LEGI, faute de temps disponible après la
  réorganisation de l'équipe. Corpus final : 7 articles couvrant 4 thèmes
  (congés payés, rupture conventionnelle, SMIC, licenciement).
- **Chunking par article** : un chunk = un article, pour garantir une
  citation toujours exacte (voir README, question 1).
- **Avertissement juridique assemblé par le code**, jamais laissé au seul
  prompt, pour garantir sa présence dans 100% des réponses.
- **Métrique cosinus explicite sur ChromaDB** plutôt que la métrique par
  défaut, plus adaptée aux embeddings de phrases.

## Tests réalisés et résultats

Sept questions testées sur le pipeline complet (`python -m src.cli`),
couvrant chaque thème du corpus plus deux cas limites :

| Question | Résultat |
|---|---|
| Congés payés (jours/mois) | OK — cite L3141-3, valeur exacte (2,5 jours) |
| Droit au congé (principe général) | OK — cite L3141-1 |
| Délai de rétractation rupture conventionnelle | OK — cite L1237-13, 15 jours calendaires |
| Finalité du SMIC | OK — cite L3231-2 |
| Notification du licenciement | OK — cite L1232-6, détails corrects |
| Question hors corpus (règles de circulation) | OK — refus explicite, aucune invention |
| Question composée (rupture conventionnelle + congés) | OK — les deux volets traités séparément, articles corrects pour chacun |

**Le cas hors corpus confirme le comportement attendu par le sujet** : à la
question *"Quelles sont les règles de circulation routière ?"*, le système
répond explicitement qu'il ne trouve pas l'information dans sa base, sans
tenter d'inventer une réponse. Ce refus repose uniquement sur la consigne
donnée dans le prompt système (pas de seuil de confiance calculé sur les
distances vectorielles) — une limite assumée, voir ci-dessous.

**Le cas de question composée est le test le plus révélateur** : malgré un
corpus réduit à 7 articles, le système a correctement dissocié les deux
sous-questions (droits en cas de rupture conventionnelle / nombre de jours
de congés), cité les bons articles pour chacune (L1237-13 puis L3141-3 et
L3141-1), et conclu par une réserve appropriée sur la convention
collective — comportement conforme à la règle du prompt sur les réponses
conditionnelles (voir README, question 4).

**Point d'attention observé** : sur la question "tout salarié a-t-il droit
à des congés payés ?", la réponse reproduit le texte de l'article L3141-1
entre guillemets, mot pour mot. Cela ne pose pas de problème juridique (le
Code du travail est un texte public), mais montre que le prompt actuel
n'interdit pas explicitement les citations littérales longues — piste
d'amélioration mineure si le temps le permet.

## Ce que nous ferions avec plus de temps

- Étendre le corpus à au moins 5 thèmes distincts (actuellement 4) via
  l'API Légifrance ou le dump LEGI, pour réduire le plafonnement du
  critère "constitution du corpus" et enrichir les réponses aux questions
  composées.
- Implémenter un score de confiance basé sur les distances retournées par
  ChromaDB (jalon 6), pour détecter et refuser les questions hors corpus
  sans dépendre uniquement de la consigne du prompt.
- Enrichir `tests/retrieval_eval.py` avec une question de test par thème
  plutôt qu'une seule.
- Ajouter une consigne de paraphrase dans le prompt système pour éviter les
  citations littérales longues du texte de loi.
- Ajouter une indication de fraîcheur du corpus dans chaque réponse.
