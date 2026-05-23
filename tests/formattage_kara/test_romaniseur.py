import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.formattage_kara.romaniseur import romaniser_texte


def test_lorsque_hiragana_saisi_alors_romaji_retourne():
    """Lorsque du texte en hiragana est saisi, alors le romaji correspondant est retourné."""
    # Given
    texte_hiragana = "ようこそ"
    # When
    resultat = romaniser_texte(texte_hiragana)
    # Then
    assert resultat == "you koso"


def test_lorsque_kanji_saisi_alors_romaji_retourne():
    """Lorsque du texte en kanji est saisi, alors le romaji correspondant est retourné."""
    # Given
    texte_kanji = "東京"
    # When
    resultat = romaniser_texte(texte_kanji)
    # Then
    assert resultat == "Tokyo"


def test_lorsque_katakana_translitteration_directe_alors_mot_etranger_retourne():
    """Lorsque le katakana est une translittération directe, alors le mot étranger en majuscules est retourné."""
    # Given
    texte_katakana = "サッカー"
    # When
    resultat = romaniser_texte(texte_katakana)
    # Then
    assert resultat == "SOCCER"


def test_lorsque_katakana_abrege_japonais_alors_romanise_phonetiquement():
    """Lorsque le katakana est un abrégé japonais (ratio < 0.7), alors il est romanisé phonétiquement."""
    # Given
    texte_katakana = (
        "アニメ"  # abréviation de "animation" → ratio < 0.7 → reste japonais
    )
    # When
    resultat = romaniser_texte(texte_katakana)
    # Then
    assert resultat == "anime"


def test_lorsque_phrase_avec_particules_alors_espaces_entre_mots():
    """Lorsqu'une phrase avec particules est saisie, alors des espaces sont présents entre les mots."""
    # Given
    phrase = "時がとまればいいのに"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert resultat == "toki ga tomareba ii no ni"


def test_lorsque_texte_multiligne_alors_retours_a_la_ligne_preserves():
    """Lorsque le texte est multiligne, alors les retours à la ligne sont préservés."""
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
    """Lorsque du texte latin commun est présent dans l'input, alors il est retourné en majuscules."""
    # Given
    phrase = "東京へ行く I love you"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert "I" in resultat
    assert "LOVE" in resultat
    assert "YOU" in resultat


def test_lorsque_parenthese_latine_et_toggle_actif_alors_casse_preservee():
    """Lorsqu'une parenthèse contient du latin dans une ligne japonaise et le toggle est actif, alors la casse d'origine est préservée."""
    # Given
    phrase = "気持ちが (Let's do it now!!)"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    lignes = resultat.split("\n")
    assert lignes[0] == "kimochi ga"
    assert lignes[1] == "Let's do it now"


def test_lorsque_parenthese_latine_et_toggle_inactif_alors_mots_en_majuscules():
    """Lorsqu'une parenthèse contient du latin et le toggle est inactif, alors tous les mots sont en majuscules."""
    # Given
    phrase = "気持ちが (Let's do it now!!)"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=False)
    # Then
    lignes = resultat.split("\n")
    assert lignes[0] == "kimochi ga"
    assert lignes[1] == "LET'S DO IT NOW"


def test_lorsque_plusieurs_parentheses_latines_et_toggle_actif_alors_toutes_preservees():
    """Lorsque plusieurs parenthèses latines sont présentes et le toggle est actif, alors toutes conservent leur casse."""
    # Given
    phrase = "気持ちが (Let's do it now!!)\nあがってく！ (Up to you!!)"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    assert "Let's do it now" in resultat
    assert "Up to you" in resultat


def test_lorsque_latin_all_caps_dans_input_alors_all_caps_conserve():
    """Lorsque du latin en majuscules est présent dans l'input, alors les majuscules sont conservées."""
    # Given
    phrase = "I LOVE YOU"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert resultat == "I LOVE YOU"


def test_lorsque_katakana_emprunt_dans_phrase_alors_majuscules():
    """Lorsqu'un emprunt katakana est présent dans une phrase, alors il est retourné en majuscules."""
    # Given
    phrase = "サッカーが好き"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert "SOCCER" in resultat


def test_lorsque_katakana_nom_propre_etranger_alors_title_case():
    """Lorsqu'un emprunt katakana est un nom propre reconnu par cutlet, alors il est retourné en title case."""
    # Given
    phrase = "ナイキが好き"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert "Nike" in resultat


def test_lorsque_particule_he_alors_romanisee_he():
    """Lorsque la particule へ est présente, alors elle est romanisée "he"."""
    # Given
    phrase = "東京へ行く"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " he " in resultat


def test_lorsque_particule_wa_alors_romanisee_wa():
    """Lorsque la particule は est présente, alors elle est romanisée "wa"."""
    # Given
    phrase = "私は行く"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " wa " in resultat


def test_lorsque_particule_wo_alors_romanisee_wo():
    """Lorsque la particule を est présente, alors elle est romanisée "wo"."""
    # Given
    phrase = "りんごを食べる"
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert " wo " in resultat


def test_lorsque_he_dans_mot_alors_non_modifie():
    """Lorsque へ est dans un mot et non une particule, alors il n'est pas modifié."""
    # Given
    phrase = "へや"  # heya, へ non-particule
    # When
    resultat = romaniser_texte(phrase)
    # Then
    assert resultat == "heya"


def test_lorsque_texte_vide_alors_chaine_vide_retournee():
    """Lorsque le texte est vide, alors une chaîne vide est retournée."""
    # Given
    texte_vide = ""
    # When
    resultat = romaniser_texte(texte_vide)
    # Then
    assert resultat == ""


def test_lorsque_texte_avec_macrons_alors_macrons_supprimes():
    """Lorsque le texte contient des voyelles longues, alors aucun macron (ō, ū) n'est retourné."""
    # Given
    texte_avec_macron = "東京"
    # When
    resultat = romaniser_texte(texte_avec_macron)
    # Then
    assert "ō" not in resultat
    assert "ū" not in resultat


def test_lorsque_ligne_latine_et_toggle_actif_alors_casse_preservee():
    """Lorsqu'une ligne est entièrement latine et le toggle actif, alors la casse d'origine est conservée."""
    # Given
    phrase = "I love you"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    assert resultat == "I love you"


def test_lorsque_ligne_latine_et_toggle_inactif_alors_full_caps():
    """Lorsqu'une ligne est entièrement latine et le toggle inactif, alors elle est en majuscules."""
    # Given
    phrase = "I love you"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=False)
    # Then
    assert resultat == "I LOVE YOU"


def test_lorsque_ligne_mixte_et_toggle_actif_alors_non_affectee():
    """Lorsqu'une ligne contient du japonais et le toggle est actif, alors elle est romanisée normalement."""
    # Given
    phrase = "東京 is beautiful"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    assert "Tokyo" in resultat
    assert "IS BEAUTIFUL" in resultat


def test_lorsque_texte_multiligne_et_toggle_actif_alors_seules_lignes_latines_preservees():
    """Lorsque le texte est multiligne et le toggle actif, alors seules les lignes sans japonais conservent leur casse."""
    # Given
    phrase = "I love you\n東京へ行く"
    # When
    resultat = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    lignes = resultat.split("\n")
    assert lignes[0] == "I love you"
    assert "Tokyo" in lignes[1]


def test_lorsque_mot_title_case_dans_ligne_japonaise_alors_toujours_en_majuscules():
    """Lorsqu'un mot latin en title case est dans une ligne mixte japonais-latin, alors il est toujours mis en majuscules."""
    # Given
    phrase = "決して消えない Fever 何度も"
    # When
    resultat_toggle_inactif = romaniser_texte(phrase, conserver_casse_latine=False)
    resultat_toggle_actif = romaniser_texte(phrase, conserver_casse_latine=True)
    # Then
    assert "FEVER" in resultat_toggle_inactif
    assert "FEVER" in resultat_toggle_actif
