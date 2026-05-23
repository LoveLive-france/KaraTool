import re


def post_traiter(texte: str) -> str:
    texte = _rattacher_n_isole(texte)
    texte = _extraire_parentheses_en_nouvelle_ligne(texte)
    texte = _supprimer_ponctuation(texte)
    return texte


def _rattacher_n_isole(texte: str) -> str:
    return re.sub(r"(?<=\w) n (?=\w)", "n", texte)


def _extraire_parentheses_en_nouvelle_ligne(texte: str) -> str:
    texte = re.sub(r"\s*[（(]([^）)]*)[）)]\s*", r"\n\1\n", texte)
    return re.sub(r"\n{2,}", "\n", texte).strip("\n")


def _supprimer_ponctuation(texte: str) -> str:
    return re.sub(r"[^\w\s'\n]", "", texte)
