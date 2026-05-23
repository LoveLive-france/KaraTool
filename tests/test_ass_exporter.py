import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.ass_exporter import (
    exporter_ass,
    lire_styles_disponibles,
    extraire_styles_depuis_ass,
    fusionner_styles,
    _generer_ligne_legende,
)


def test_lorsque_une_ligne_alors_une_dialogue_creee(tmp_path):
    """Lorsqu'une seule ligne est fournie, alors une seule ligne Dialogue est créée."""
    # Given
    chemin = tmp_path / "sortie.ass"
    lignes = ["kimi no na wa"]
    # When
    exporter_ass(str(chemin), lignes)
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert contenu.count("Dialogue:") == 1
    assert (
        "Dialogue: 0,0:00:00.00,0:00:00.00,Sample KM [Up],,0,0,0,,kimi no na wa"
        in contenu
    )


def test_lorsque_plusieurs_lignes_alors_plusieurs_dialogues_crees(tmp_path):
    """Lorsque plusieurs lignes sont fournies, alors autant de lignes Dialogue sont créées."""
    # Given
    chemin = tmp_path / "sortie.ass"
    lignes = ["kimi no na wa", "nani wo shite iru", "koko de"]
    # When
    exporter_ass(str(chemin), lignes)
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert contenu.count("Dialogue:") == 3


def test_lorsque_ligne_vide_alors_ignoree(tmp_path):
    """Lorsqu'une ligne est vide, alors elle ne génère pas de ligne Dialogue."""
    # Given
    chemin = tmp_path / "sortie.ass"
    lignes = ["kimi no na wa", "", "nani wo shite iru"]
    # When
    exporter_ass(str(chemin), lignes)
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert contenu.count("Dialogue:") == 2


def test_lorsque_export_alors_header_script_info_present(tmp_path):
    """Lorsque le fichier est exporté, alors la section Script Info est présente."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "[Script Info]" in contenu
    assert "ScriptType: v4.00+" in contenu


def test_lorsque_export_alors_styles_presents(tmp_path):
    """Lorsque le fichier est exporté, alors la section V4+ Styles est présente."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "[V4+ Styles]" in contenu
    assert "Style: Sample KM [Up]" in contenu


def test_lorsque_export_alors_commentaire_template_present(tmp_path):
    """Lorsque le fichier est exporté, alors la ligne Comment template est présente."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert (
        "Comment: 0,0:00:00.00,0:00:00.00,Sample KM [Up],,0,0,0,template pre-line all keeptags,"
        in contenu
    )


def test_lorsque_export_alors_encodage_utf8(tmp_path):
    """Lorsque le fichier est exporté, alors l'encodage UTF-8 est respecté."""
    # Given
    chemin = tmp_path / "sortie.ass"
    lignes = ["natsukashii"]
    # When
    exporter_ass(str(chemin), lignes)
    # Then
    contenu = chemin.read_bytes()
    assert "natsukashii".encode("utf-8") in contenu


def test_lorsque_liste_vide_alors_fichier_cree_sans_dialogue(tmp_path):
    """Lorsque la liste est vide, alors le fichier est créé sans ligne Dialogue."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), [])
    # Then
    assert chemin.exists()
    contenu = chemin.read_text(encoding="utf-8")
    assert "Dialogue:" not in contenu


def test_lorsque_titre_fourni_alors_title_mis_a_jour(tmp_path):
    """Lorsqu'un titre est fourni, alors le champ Title du header est mis à jour."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"], titre="Kimi no Na wa")
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "Title: Kimi no Na wa" in contenu


def test_lorsque_pas_de_titre_alors_title_par_defaut(tmp_path):
    """Lorsqu'aucun titre n'est fourni, alors le champ Title reste 'New subtitles'."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "Title: New subtitles" in contenu


def test_lorsque_lire_styles_disponibles_alors_styles_de_base_presents():
    """Lorsqu'on lit les styles disponibles, alors les styles de base sont présents."""
    # Given / When
    styles = lire_styles_disponibles()
    # Then
    noms = [s["nom"] for s in styles]
    assert "Sample KM [Up]" in noms
    assert "Sample KM [Choir]" in noms


def test_lorsque_styles_selectionnes_alors_seuls_ces_styles_injectes(tmp_path):
    """Lorsque des styles sont sélectionnés, alors seuls ces styles apparaissent dans [V4+ Styles]."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"], styles_a_inclure=["Sample KM [Up]"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "Style: Sample KM [Up]" in contenu
    assert "Style: Sample KM [Choir]" not in contenu


def test_lorsque_ass_avec_styles_alors_styles_extraits(tmp_path):
    """Lorsqu'un fichier .ass contient des styles, alors ils sont extraits avec nom et définition."""
    # Given
    ass = tmp_path / "test.ass"
    ass.write_text(
        "[V4+ Styles]\nFormat: Name, Fontname\nStyle: MonStyle,Arial,24\n",
        encoding="utf-8",
    )
    # When
    styles = extraire_styles_depuis_ass(str(ass))
    # Then
    assert len(styles) == 1
    assert styles[0]["nom"] == "MonStyle"
    assert styles[0]["definition"] == "Style: MonStyle,Arial,24"


def test_lorsque_style_deja_present_alors_non_duplique():
    """Lorsqu'un style existe déjà dans le catalogue, alors il n'est pas ajouté en double."""
    # Given
    existants = [{"nom": "A", "definition": "Style: A,Arial"}]
    nouveaux = [
        {"nom": "A", "definition": "Style: A,Arial"},
        {"nom": "B", "definition": "Style: B,Arial"},
    ]
    # When
    resultat = fusionner_styles(existants, nouveaux)
    # Then
    assert len(resultat) == 2
    assert sum(1 for s in resultat if s["nom"] == "A") == 1


def test_lorsque_aucun_nouveau_style_alors_catalogue_inchange():
    """Lorsque tous les nouveaux styles sont déjà présents, alors le catalogue ne change pas."""
    # Given
    existants = [{"nom": "A", "definition": "Style: A,Arial"}]
    # When
    resultat = fusionner_styles(
        existants, [{"nom": "A", "definition": "Style: A,Arial"}]
    )
    # Then
    assert resultat == existants


def test_lorsque_styles_selectionnes_alors_ligne_legende_generee(tmp_path):
    """Lorsque des styles sont sélectionnés, alors une ligne légende est présente dans le .ass."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(
        str(chemin), ["test"], styles_a_inclure=["Sample KM [Up]", "Sample KM [Choir]"]
    )
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert ",legend," in contenu
    assert "{\\rSample KM [Up]}Sample KM [Up]" in contenu
    assert "{\\rSample KM [Choir]}Sample KM [Choir]" in contenu


def test_lorsque_aucun_style_selectionne_alors_pas_de_legende(tmp_path):
    """Lorsqu'aucun style n'est sélectionné, alors aucune ligne légende n'est générée."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"], styles_a_inclure=[])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert ",legend," not in contenu


def test_lorsque_un_seul_style_selectionne_alors_pas_de_legende(tmp_path):
    """Lorsqu'un seul style est sélectionné, alors aucune ligne légende n'est générée."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"], styles_a_inclure=["Sample KM [Up]"])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert ",legend," not in contenu


def test_lorsque_couleur_primaire_blanche_alors_couleur_secondaire_dans_legende():
    """Lorsque la couleur primaire d'un style est blanche, alors la couleur secondaire est injectée dans la légende."""
    # Given
    styles = [
        {
            "nom": "Style Blanc",
            "definition": "Style: Style Blanc,Arial,24,&H00FFFFFF,&H005050E2,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1",
        }
    ]
    # When
    resultat = _generer_ligne_legende(styles)
    # Then
    assert "\\1c&H5050E2&" in resultat
    assert "Style Blanc" in resultat


def test_lorsque_aucune_selection_alors_sample_km_up_par_defaut(tmp_path):
    """Lorsqu'aucun style n'est sélectionné, alors Sample KM [Up] est utilisé par défaut."""
    # Given
    chemin = tmp_path / "sortie.ass"
    # When
    exporter_ass(str(chemin), ["test"], styles_a_inclure=[])
    # Then
    contenu = chemin.read_text(encoding="utf-8")
    assert "Style: Sample KM [Up]" in contenu
    assert "Style: Sample KM [Choir]" not in contenu
    assert "Style: Sample KM [Down]" not in contenu
