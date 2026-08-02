from urllib.parse import urlparse

from core.scraper_paroles_fandom import extraire_paroles_japonaises as _extraire_fandom
from core.scraper_paroles_uta_net import (
    extraire_paroles_japonaises as _extraire_uta_net,
)


def extraire_paroles_japonaises(url_page: str) -> str:
    domaine = urlparse(url_page).netloc
    if domaine.endswith(".fandom.com"):
        return _extraire_fandom(url_page)
    if domaine == "www.uta-net.com":
        return _extraire_uta_net(url_page)
    raise ValueError(f"Source non supportée : {domaine}")
