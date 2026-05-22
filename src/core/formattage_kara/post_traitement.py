import re


def post_traiter(texte: str) -> str:
    texte = _extraire_parentheses_en_nouvelle_ligne(texte)
    texte = _supprimer_ponctuation(texte)
    return texte


def _extraire_parentheses_en_nouvelle_ligne(texte: str) -> str:
    texte = re.sub(r"\s*[（(]([^）)]*)[）)]\s*", r"\n\1\n", texte)
    return re.sub(r"\n{2,}", "\n", texte).strip("\n")


def _supprimer_ponctuation(texte: str) -> str:
    return re.sub(r"[^\w\s'\n]", "", texte)
