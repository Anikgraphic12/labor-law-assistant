import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client_groq = Groq(api_key=os.environ["GROQ_API_KEY"])

AVERTISSEMENT = ("Cet assistant ne fournit pas de conseil juridique. "
                  "Consultez un avocat ou l'inspection du travail pour votre situation personnelle.")

SYSTEM_PROMPT = """Tu es un assistant qui repond a des questions sur le Code du travail francais.
Regles strictes :
- Reponds UNIQUEMENT a partir des articles fournis dans le contexte ci-dessous.
- Cite systematiquement le numero de chaque article sur lequel tu t'appuies.
- Si l'information n'est pas dans le contexte, reponds explicitement :
  "Je ne trouve pas cette information dans ma base."
- Si la question depend de la taille de l'entreprise ou de la convention collective,
  donne la reponse generale avec cette reserve clairement indiquee.
- Ne rends jamais de verdict sur le caractere abusif d'une situation individuelle :
  rappelle les regles applicables et renvoie vers un professionnel.
"""


def generate_answer(question, chunks):
    contexte = "\n\n".join(
        f"[Article {c['metadata']['article']} - {c['metadata']['theme']}]\n{c['document']}"
        for c in chunks
    )
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Contexte :\n{contexte}\n\nQuestion : {question}"}
    ]
    resp = client_groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.1,
    )
    reponse = resp.choices[0].message.content
    return f"{reponse}\n\n---\n{AVERTISSEMENT}"
