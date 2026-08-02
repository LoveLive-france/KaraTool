import sys
import os
from unittest.mock import patch, MagicMock

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.scraper_paroles_uta_net import extraire_paroles_japonaises
from core.scraper_paroles_fandom import ErreurScrapingParoles


def _reponse_html(html: str, statut: int = 200) -> MagicMock:
    reponse = MagicMock()
    reponse.status_code = statut
    reponse.text = html
    return reponse


_HTML_MINIMAL = """
<html><body>
<div id="kashi_area" itemprop="text">ligne un<br />ligne deux<br /><br />ligne trois &amp; quatre</div>
</body></html>
"""


def test_lorsque_page_contient_kashi_area_alors_paroles_japonaises_retournees():
    """Lorsque la page contient le bloc kashi_area, alors les paroles japonaises sont retournées, lignes séparées."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    # When
    with patch("requests.get", return_value=_reponse_html(_HTML_MINIMAL)):
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    assert resultat == "ligne un\nligne deux\nligne trois & quatre"


def test_lorsque_statut_http_non_200_alors_erreur_scraping_paroles_levee():
    """Lorsque le serveur répond avec un statut différent de 200, alors ErreurScrapingParoles est levée."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    # When / Then
    with patch("requests.get", return_value=_reponse_html(_HTML_MINIMAL, statut=404)):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_erreur_reseau_alors_erreur_scraping_paroles_levee():
    """Lorsqu'une erreur réseau survient, alors ErreurScrapingParoles est levée sans crash."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    # When / Then
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_timeout_reseau_alors_erreur_scraping_paroles_levee():
    """Lorsqu'un timeout survient, alors ErreurScrapingParoles est levée sans crash."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    # When / Then
    with patch("requests.get", side_effect=requests.Timeout):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_page_sans_kashi_area_alors_erreur_scraping_paroles_levee():
    """Lorsque la page ne contient pas de bloc kashi_area, alors ErreurScrapingParoles est levée."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    html_sans_paroles = "<html><body><p>Page introuvable</p></body></html>"
    # When / Then
    with patch("requests.get", return_value=_reponse_html(html_sans_paroles)):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_url_ne_correspond_pas_au_format_uta_net_alors_value_error_levee():
    """Lorsque l'URL ne correspond pas au format https://www.uta-net.com/song/<id>/, alors ValueError est levée."""
    # Given
    url_page = "https://www.uta-net.com/artist/12345/"
    # When / Then
    with pytest.raises(ValueError):
        extraire_paroles_japonaises(url_page)
