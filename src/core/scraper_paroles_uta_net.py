import html
import re
from urllib.parse import urlparse

import requests

from core.scraper_paroles_fandom import ErreurScrapingParoles

_TIMEOUT_SECONDES = 10


def extraire_paroles_japonaises(url_page: str) -> str:
    _valider_url(url_page)
    html_page = _recuperer_html(url_page)
    bloc_japonais = _extraire_bloc_japonais(html_page)
    if bloc_japonais is None:
        raise ErreurScrapingParoles(
            "Aucune section de paroles japonaises trouvée sur cette page."
        )
    return _nettoyer_html(bloc_japonais)


def _valider_url(url_page: str) -> None:
    resultat = urlparse(url_page)
    if resultat.netloc != "www.uta-net.com" or not re.match(
        r"^/song/\d+/?$", resultat.path
    ):
        raise ValueError(
            f"URL invalide, format attendu https://www.uta-net.com/song/<id>/ : {url_page}"
        )


def _recuperer_html(url_page: str) -> str:
    try:
        reponse = requests.get(url_page, timeout=_TIMEOUT_SECONDES)
    except requests.RequestException as erreur:
        raise ErreurScrapingParoles(
            f"Impossible de contacter le site ({erreur})."
        ) from erreur

    if reponse.status_code != 200:
        raise ErreurScrapingParoles(
            f"Le site a répondu avec le statut {reponse.status_code}."
        )
    return reponse.text


def _extraire_bloc_japonais(html_page: str) -> str | None:
    correspondance = re.search(
        r'<div id="kashi_area"[^>]*>(.*?)</div>', html_page, re.DOTALL
    )
    return correspondance.group(1) if correspondance else None


def _nettoyer_html(bloc: str) -> str:
    texte = re.sub(r"<br\s*/?>", "\n", bloc, flags=re.IGNORECASE)
    texte = html.unescape(texte)
    lignes = [ligne.strip() for ligne in texte.splitlines()]
    lignes = [ligne for ligne in lignes if ligne]
    return "\n".join(lignes)
