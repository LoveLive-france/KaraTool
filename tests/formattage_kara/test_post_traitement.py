import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.formattage_kara.post_traitement import post_traiter


def test_lorsque_ponctuation_presente_alors_ponctuation_retiree():
    """Lorsque de la ponctuation est présente, alors elle est retirée."""
    # Given
    texte = "hello, world! how are you?"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "hello world how are you"


def test_lorsque_apostrophe_presente_alors_apostrophe_conservee():
    """Lorsqu'une apostrophe est présente, alors elle est conservée."""
    # Given
    texte = "don't stop"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "don't stop"


def test_lorsque_contenu_entre_parentheses_alors_mis_sur_nouvelle_ligne():
    """Lorsque du contenu est entre parenthèses, alors il est mis sur une nouvelle ligne."""
    # Given
    texte = "toki ga tomareba (ii no ni)"
    # When
    resultat = post_traiter(texte)
    # Then
    lignes = resultat.split("\n")
    assert lignes[0] == "toki ga tomareba"
    assert lignes[1] == "ii no ni"


def test_lorsque_parentheses_japonaises_alors_contenu_mis_sur_nouvelle_ligne():
    """Lorsque du contenu est entre parenthèses japonaises （）, alors il est mis sur une nouvelle ligne."""
    # Given
    texte = "toki（ii no ni）ga"
    # When
    resultat = post_traiter(texte)
    # Then
    lignes = resultat.split("\n")
    assert lignes[0] == "toki"
    assert lignes[1] == "ii no ni"
    assert lignes[2] == "ga"


def test_lorsque_retours_a_la_ligne_presents_alors_conserves():
    """Lorsque des retours à la ligne sont présents, alors ils sont conservés."""
    # Given
    texte = "tokyo\nanime"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "tokyo\nanime"


def test_lorsque_ponctuation_japonaise_presente_alors_retiree():
    """Lorsque de la ponctuation japonaise est présente, alors elle est retirée."""
    # Given
    texte = "toki、ga。tomareba"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "tokigatomareba"
