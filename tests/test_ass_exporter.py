import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.ass_exporter import exporter_ass


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
