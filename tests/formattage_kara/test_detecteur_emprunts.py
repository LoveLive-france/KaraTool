import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.formattage_kara.detecteur_emprunts import remplacer_emprunts_katakana


def test_lorsque_katakana_translitteration_directe_alors_mot_etranger_retourne():
    """Lorsque le katakana est une translittération directe (ratio ≥ 0.7), alors le mot étranger est retourné."""
    # Given
    texte = "サッカー"  # "sakkaa" / "soccer" → ratio 1.0 ≥ 0.7
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert resultat == "soccer"


def test_lorsque_katakana_abrege_japonais_alors_katakana_conserve():
    """Lorsque le katakana est un abrégé japonais (ratio < 0.7), alors le katakana est conservé."""
    # Given
    texte = "テレビ"  # "terebi" / "television" → ratio 0.6 < 0.7
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert resultat == "テレビ"


def test_lorsque_katakana_abrege_anime_alors_katakana_conserve():
    """Lorsque le katakana est un abrégé culturel (ratio < 0.7), alors le katakana est conservé."""
    # Given
    texte = "アニメ"  # "anime" / "animation" → ratio 0.56 < 0.7
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert resultat == "アニメ"


def test_lorsque_katakana_identique_phonetique_et_etranger_alors_katakana_conserve():
    """Lorsque les formes phonétique et étrangère du katakana sont identiques, alors le katakana est conservé."""
    # Given
    texte = "カラオケ"  # karaoke = phonétique == étranger
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert resultat == "カラオケ"


def test_lorsque_texte_mixte_alors_seuls_emprunts_directs_remplaces():
    """Lorsque le texte est mixte, alors seuls les emprunts directs sont remplacés."""
    # Given
    texte = "サッカーとテレビ"
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert "soccer" in resultat
    assert "テレビ" in resultat


def test_lorsque_texte_sans_katakana_alors_inchange():
    """Lorsque le texte ne contient pas de katakana, alors il est retourné inchangé."""
    # Given
    texte = "toki ga tomareba"
    # When
    resultat = remplacer_emprunts_katakana(texte)
    # Then
    assert resultat == "toki ga tomareba"
