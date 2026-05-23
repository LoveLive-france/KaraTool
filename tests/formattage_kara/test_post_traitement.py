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


def test_lorsque_n_isole_entre_deux_mots_alors_rattache():
    """Lorsqu'un n isolé est entre deux mots, alors il est rattaché sans espaces."""
    # Given
    texte = "omoeta n da"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "omoetanda"


def test_lorsque_plusieurs_n_isoles_alors_tous_rattaches():
    """Lorsque plusieurs n isolés sont présents, alors ils sont tous rattachés."""
    # Given
    texte = "hontou na n da"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "hontou nanda"


def test_lorsque_n_en_fin_de_mot_alors_non_modifie():
    """Lorsque le n est en fin de mot, alors il n'est pas modifié."""
    # Given
    texte = "wakaran"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "wakaran"


def test_lorsque_n_en_debut_de_mot_alors_non_modifie():
    """Lorsque le n est en début de mot, alors il n'est pas modifié."""
    # Given
    texte = "nan darou"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "nan darou"


def test_lorsque_ra_isoles_separes_par_ponctuation_alors_la_isoles():
    """Lorsque des ra isolés sont séparés par de la ponctuation, alors ils restent séparés après conversion."""
    # Given
    texte = "ra! ra! ra!"  # ponctuation préservée au moment de la correction
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "la la la"


def test_lorsque_ra_repetes_attaches_alors_remplaces_par_la():
    """Lorsqu'un mot composé uniquement de ra répétés est présent, alors il est remplacé par la."""
    # Given
    texte = "rarara"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "lalala"


def test_lorsque_ra_dans_vrai_mot_alors_non_modifie():
    """Lorsque ra fait partie d'un vrai mot, alors il n'est pas modifié."""
    # Given
    texte = "sakura"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "sakura"


def test_lorsque_ra_majuscule_alors_non_modifie():
    """Lorsque RA est en majuscules, alors il n'est pas modifié."""
    # Given
    texte = "RARARA"
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "RARARA"


def test_lorsque_ra_titre_isole_alors_remplace_par_la():
    """Lorsque Ra en titre (artefact cutlet) est isolé, alors il est remplacé par la."""
    # Given
    texte = "Ra!"  # cutlet capitalise le premier token après ponctuation
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "la"


def test_lorsque_groupes_ra_separes_par_espace_seul_alors_fusionnes():
    """Lorsque des groupes ra sont séparés par un espace seul (artefact cutlet), alors ils sont fusionnés."""
    # Given
    texte = "rarara Rara"  # cutlet tokenise ラ×5 en rarara + Rara
    # When
    resultat = post_traiter(texte)
    # Then
    assert resultat == "lalalalala"
