import sys
import os
from unittest.mock import patch, MagicMock

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.scraper_paroles_fandom import (
    extraire_paroles_japonaises,
    ErreurScrapingParoles,
)


def _reponse_wikitexte(wikitexte: str) -> MagicMock:
    reponse = MagicMock()
    reponse.json.return_value = {"parse": {"wikitext": {"*": wikitexte}}}
    return reponse


_WIKITEXTE_UNISON = """
==Lyrics==
{{Liella Tab|
<center>
<tabber>
Rōmaji=
<poem>
Saa shinkokyuu shite
</poem>
|-|
Kanji=
<poem>
さあ深呼吸して　熱い想い解き放とう
いつもと違う自分　出会えるように
</poem>
|-|
English=
<poem>
Take a deep breath
</poem>
</tabber>
</center>
}}
"""


def test_lorsque_wikitexte_contient_bloc_kanji_alors_paroles_japonaises_retournees():
    """Lorsque le wikitexte contient un bloc Kanji, alors les paroles japonaises sont retournées."""
    # Given
    url_page = "https://love-live.fandom.com/wiki/Unison"
    # When
    with patch("requests.get", return_value=_reponse_wikitexte(_WIKITEXTE_UNISON)):
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    assert (
        resultat
        == "さあ深呼吸して　熱い想い解き放とう\nいつもと違う自分　出会えるように"
    )


def test_lorsque_bloc_japanese_utilise_au_lieu_de_kanji_alors_paroles_retournees():
    """Lorsque le label 'Japanese' est utilisé à la place de 'Kanji', alors les paroles sont quand même extraites."""
    # Given
    wikitexte = """
    <tabber>
    Japanese=
    <poem>
    こんにちは世界
    </poem>
    |-|
    English=
    <poem>
    Hello world
    </poem>
    </tabber>
    """
    url_page = "https://love-live.fandom.com/wiki/Test"
    # When
    with patch("requests.get", return_value=_reponse_wikitexte(wikitexte)):
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    assert resultat == "こんにちは世界"


def test_lorsque_markup_wiki_present_dans_le_bloc_alors_texte_nettoye_retourne():
    """Lorsque le bloc kanji contient du markup wiki (gras, liens, commentaires), alors ils sont retirés."""
    # Given
    wikitexte = """
    <tabber>
    Kanji=
    <poem>
    '''強い'''想いを[[込めて|込めて]]<!-- commentaire -->
    ラララ<br>
    </poem>
    </tabber>
    """
    url_page = "https://love-live.fandom.com/wiki/Test"
    # When
    with patch("requests.get", return_value=_reponse_wikitexte(wikitexte)):
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    assert "'''" not in resultat
    assert "[[" not in resultat
    assert "<!--" not in resultat
    assert "<br>" not in resultat
    assert "強い" in resultat
    assert "込めて" in resultat


def test_lorsque_api_retourne_une_erreur_alors_erreur_scraping_paroles_levee():
    """Lorsque l'API MediaWiki retourne une erreur (page inexistante), alors ErreurScrapingParoles est levée."""
    # Given
    reponse = MagicMock()
    reponse.json.return_value = {
        "error": {"code": "missingtitle", "info": "La page n'existe pas."}
    }
    url_page = "https://love-live.fandom.com/wiki/PageInexistante"
    # When / Then
    with patch("requests.get", return_value=reponse):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_erreur_reseau_alors_erreur_scraping_paroles_levee():
    """Lorsqu'une erreur réseau survient, alors ErreurScrapingParoles est levée sans crash."""
    # Given
    url_page = "https://love-live.fandom.com/wiki/Unison"
    # When / Then
    with patch("requests.get", side_effect=requests.ConnectionError):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_timeout_reseau_alors_erreur_scraping_paroles_levee():
    """Lorsqu'un timeout survient, alors ErreurScrapingParoles est levée sans crash."""
    # Given
    url_page = "https://love-live.fandom.com/wiki/Unison"
    # When / Then
    with patch("requests.get", side_effect=requests.Timeout):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_wikitexte_sans_section_japonaise_alors_erreur_scraping_paroles_levee():
    """Lorsque le wikitexte ne contient aucune section de paroles japonaises, alors ErreurScrapingParoles est levée."""
    # Given
    wikitexte = "{{CD Infobox}}\nCeci est une page sans paroles."
    url_page = "https://love-live.fandom.com/wiki/PageSansParoles"
    # When / Then
    with patch("requests.get", return_value=_reponse_wikitexte(wikitexte)):
        with pytest.raises(ErreurScrapingParoles):
            extraire_paroles_japonaises(url_page)


def test_lorsque_url_ne_correspond_pas_au_format_wiki_alors_value_error_levee():
    """Lorsque l'URL ne correspond pas au format https://.../wiki/Titre, alors ValueError est levée."""
    # Given
    url_page = "https://love-live.fandom.com/pas-une-page-wiki"
    # When / Then
    with pytest.raises(ValueError):
        extraire_paroles_japonaises(url_page)


def test_lorsque_titre_avec_underscores_alors_titre_transmis_tel_quel_a_l_api():
    """Lorsque le titre de la page contient des underscores, alors il est transmis tel quel en paramètre 'page' de l'appel API."""
    # Given
    url_page = "https://love-live.fandom.com/wiki/Aozora_Jumping_Heart"
    # When
    with patch(
        "requests.get", return_value=_reponse_wikitexte(_WIKITEXTE_UNISON)
    ) as mock_get:
        extraire_paroles_japonaises(url_page)
    # Then
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["page"] == "Aozora_Jumping_Heart"
    assert "love-live.fandom.com/api.php" in mock_get.call_args[0][0]
