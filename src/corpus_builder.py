import json, random

def load_corpus(path="data/corpus.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def check_corpus(path="data/corpus.json", n=10):
    docs = load_corpus(path)
    themes = set(d["theme"] for d in docs)
    print(f"{len(docs)} articles, {len(themes)} thèmes : {themes}")
    for d in random.sample(docs, min(n, len(docs))):
        print(f"\n{d['article']} — {d['titre']}\n{d['texte'][:150]}...")

if __name__ == "__main__":
    check_corpus()