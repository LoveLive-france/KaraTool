import re
from urllib.parse import urlparse

import requests

_TIMEOUT_SECONDES = 10
_LABELS_JAPONAIS = ("Kanji", "Japanese", "Japonais")


class ErreurScrapingParoles(Exception):
    pass


def extraire_paroles_japonaises(url_page: str) -> str:
    domaine, titre_page = _analyser_url(url_page)
    wikitexte = _recuperer_wikitexte(domaine, titre_page)
    bloc_japonais = _extraire_bloc_japonais(wikitexte)
    if bloc_japonais is None:
        raise ErreurScrapingParoles(
            "Aucune section de paroles japonaises trouvée sur cette page."
        )
    return _nettoyer_wikitexte(bloc_japonais)


def _analyser_url(url_page: str) -> tuple[str, str]:
    resultat = urlparse(url_page)
    correspondance = re.match(r"^/wiki/(.+)$", resultat.path)
    if not resultat.netloc or not correspondance:
        raise ValueError(
            f"URL invalide, format attendu https://<domaine>/wiki/<Titre> : {url_page}"
        )
    return resultat.netloc, correspondance.group(1)


def _recuperer_wikitexte(domaine: str, titre_page: str) -> str:
    try:
        reponse = requests.get(
            f"https://{domaine}/api.php",
            params={
                "action": "parse",
                "page": titre_page,
                "format": "json",
                "prop": "wikitext",
            },
            timeout=_TIMEOUT_SECONDES,
        )
        reponse.raise_for_status()
        contenu = reponse.json()
    except requests.RequestException as erreur:
        raise ErreurScrapingParoles(
            f"Impossible de contacter le wiki ({erreur})."
        ) from erreur

    if "error" in contenu:
        raise ErreurScrapingParoles(
            f"Erreur de l'API du wiki : {contenu['error'].get('info', contenu['error'])}"
        )
    return contenu["parse"]["wikitext"]["*"]


def _extraire_bloc_japonais(wikitexte: str) -> str | None:
    for label in _LABELS_JAPONAIS:
        correspondance = re.search(
            rf"{label}\s*=\s*<poem>(.*?)</poem>", wikitexte, re.DOTALL | re.IGNORECASE
        )
        if correspondance:
            return correspondance.group(1)
    return None


def _nettoyer_wikitexte(bloc: str) -> str:
    texte = re.sub(r"<!--.*?-->", "", bloc, flags=re.DOTALL)
    texte = re.sub(r"<br\s*/?>", "", texte, flags=re.IGNORECASE)
    texte = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", texte)
    texte = re.sub(r"\[\[([^\]]+)\]\]", r"\1", texte)
    texte = re.sub(r"'''(.*?)'''", r"\1", texte)
    texte = re.sub(r"''(.*?)''", r"\1", texte)

    lignes = [ligne.strip() for ligne in texte.splitlines()]
    lignes = [ligne for ligne in lignes if ligne]
    return "\n".join(lignes)
