import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from core.scraper_paroles import extraire_paroles_japonaises


def test_lorsque_url_fandom_alors_extracteur_fandom_appele():
    """Lorsque l'URL provient d'un domaine fandom.com, alors l'extracteur fandom est utilisé."""
    # Given
    url_page = "https://love-live.fandom.com/wiki/Unison"
    # When
    with patch(
        "core.scraper_paroles._extraire_fandom", return_value="paroles fandom"
    ) as mock_fandom:
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    mock_fandom.assert_called_once_with(url_page)
    assert resultat == "paroles fandom"


def test_lorsque_url_uta_net_alors_extracteur_uta_net_appele():
    """Lorsque l'URL provient de www.uta-net.com, alors l'extracteur uta-net est utilisé."""
    # Given
    url_page = "https://www.uta-net.com/song/365378/"
    # When
    with patch(
        "core.scraper_paroles._extraire_uta_net", return_value="paroles uta-net"
    ) as mock_uta_net:
        resultat = extraire_paroles_japonaises(url_page)
    # Then
    mock_uta_net.assert_called_once_with(url_page)
    assert resultat == "paroles uta-net"


def test_lorsque_domaine_non_supporte_alors_value_error_levee():
    """Lorsque le domaine de l'URL n'est ni fandom.com ni uta-net.com, alors ValueError est levée."""
    # Given
    url_page = "https://www.exemple-inconnu.com/paroles/1"
    # When / Then
    with pytest.raises(ValueError):
        extraire_paroles_japonaises(url_page)
