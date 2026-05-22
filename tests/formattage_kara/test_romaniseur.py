import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.formattage_kara.romaniseur import romaniser_texte


def test_lorsque_hiragana_saisi_alors_romaji_retourne():
    # Given
    texte_hiragana = "ようこそ"
    # When
    resultat = romaniser_texte(texte_hiragana)
    # Then
    assert resultat == "you koso"


def test_lorsque_kanji_saisi_alors_romaji_retourne():
    # Given
    texte_kanji = "東京"
    # When
    resultat = romaniser_texte(texte_kanji)
    # Then
    assert resultat == "Tokyo"


def test_lorsque_katakana_translitteration_directe_alors_mot_etranger_retourne():
    # Given
    texte_katakana = "サッカー"
    # When
    resultat = romaniser_texte(texte_katakana)
    # Then
    assert resultat == "SOCCER"


def test_lorsque_katakana_abrege_japonais_alors_romanise_phonetiquement():
    # Given
    texte_katakana = "アニメ"  # abréviation de "animation" → ratio < 0.7 → reste japonais
    # When
    resultat = romaniser_texte(texte_katakana)
    # Then
    assert resultat == "anime"


def test_lorsque_phrase_avec_particules_alors_espaces_entre_mots():
    # Given
    phrase = "時がとまればいいのに"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert resultat == "toki ga tomareba ii no ni"


def test_lorsque_texte_multiligne_alors_retours_a_la_ligne_preserves():
    # Given
    texte_multiligne = "東京\nアニメ"
    # When
    resultat = romaniser_texte(texte_multiligne)
    # Then
    lignes = resultat.split("\n")
    assert len(lignes) == 2
    assert lignes[0] == "Tokyo"
    assert lignes[1] == "anime"


def test_lorsque_texte_latin_dans_input_alors_majuscules():
    # Given
    phrase = "東京へ行く I love you"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert "I" in resultat
    assert "LOVE" in resultat
    assert "YOU" in resultat


def test_lorsque_katakana_emprunt_dans_phrase_alors_majuscules():
    # Given
    phrase = "サッカーが好き"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert "SOCCER" in resultat


def test_lorsque_particule_he_alors_romanisee_he():
    # Given
    phrase = "東京へ行く"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " he " in resultat


def test_lorsque_particule_wa_alors_romanisee_wa():
    # Given
    phrase = "私は行く"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " wa " in resultat


def test_lorsque_particule_wo_alors_romanisee_wo():
    # Given
    phrase = "りんごを食べる"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " wo " in resultat


def test_lorsque_he_dans_mot_alors_non_modifie():
    # Given
    phrase = "へや"  # heya, へ non-particule
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert resultat == "heya"


def test_lorsque_texte_vide_alors_chaine_vide_retournee():
    # Given
    texte_vide = ""
    # When
    resultat = romaniser_texte(texte_vide)
    # Then
    assert resultat == ""


def test_lorsque_texte_avec_macrons_alors_macrons_supprimes():
    # Given
    texte_avec_macron = "東京"
    # When
    resultat = romaniser_texte(texte_avec_macron)
    # Then
    assert "ō" not in resultat
    assert "ū" not in resultat
