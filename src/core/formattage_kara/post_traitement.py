import re


def post_traiter(texte: str) -> str:
    texte = _rattacher_n_isole(texte)
    texte = _corriger_ra_en_la(texte)
    texte = _extraire_parentheses_en_nouvelle_ligne(texte)
    texte = _supprimer_ponctuation(texte)
    return texte


def _corriger_ra_en_la(texte: str) -> str:
    texte = _remplacer_ra_repetes_en_la(texte)
    texte = _remplacer_ra_isole_en_la(texte)
    texte = _corriger_ra_titre_en_la(texte)
    texte = _fusionner_la_adjacents(texte)
    return texte


def _remplacer_ra_repetes_en_la(texte: str) -> str:
    return re.sub(r"\b(ra)+\b", lambda m: "la" * (len(m.group()) // 2), texte)


def _remplacer_ra_isole_en_la(texte: str) -> str:
    return re.sub(r"\bra\b", "la", texte)


def _corriger_ra_titre_en_la(texte: str) -> str:
    return re.sub(r"\bRa(ra)*\b", lambda m: "la" * (len(m.group()) // 2), texte)


def _fusionner_la_adjacents(texte: str) -> str:
    return re.sub(
        r"((?:la)+)(?: (?:la)+)+", lambda m: m.group(0).replace(" ", ""), texte
    )


def _rattacher_n_isole(texte: str) -> str:
    return re.sub(r"(?<=\w) n (?=\w)", "n", texte)


def _extraire_parentheses_en_nouvelle_ligne(texte: str) -> str:
    texte = re.sub(r"\s*[（(]([^）)]*)[）)]\s*", r"\n\1\n", texte)
    return re.sub(r"\n{2,}", "\n", texte).strip("\n")


def _supprimer_ponctuation(texte: str) -> str:
    return re.sub(r"[^\w\s'\n]", "", texte)
