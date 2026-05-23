import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.text_exporter import exporter_texte


def test_lorsque_contenu_simple_alors_fichier_cree(tmp_path):
    """Lorsqu'un contenu simple est exporté, alors le fichier est créé."""
    # Given
    chemin_fichier = tmp_path / "sortie.txt"
    contenu = "bonjour"
    # When
    exporter_texte(str(chemin_fichier), contenu)
    # Then
    assert chemin_fichier.exists()


def test_lorsque_texte_japonais_alors_encodage_utf8_preserve(tmp_path):
    """Lorsque du texte japonais est exporté, alors l'encodage UTF-8 est préservé."""
    # Given
    chemin_fichier = tmp_path / "japonais.txt"
    contenu_japonais = "こんにちは世界"
    # When
    exporter_texte(str(chemin_fichier), contenu_japonais)
    # Then
    assert chemin_fichier.read_text(encoding="utf-8") == contenu_japonais


def test_lorsque_fichier_existant_alors_contenu_remplace(tmp_path):
    """Lorsqu'un fichier existant est ciblé, alors son contenu est remplacé."""
    # Given
    chemin_fichier = tmp_path / "existant.txt"
    chemin_fichier.write_text("ancien contenu", encoding="utf-8")
    nouveau_contenu = "nouveau contenu"
    # When
    exporter_texte(str(chemin_fichier), nouveau_contenu)
    # Then
    assert chemin_fichier.read_text(encoding="utf-8") == nouveau_contenu


def test_lorsque_contenu_vide_alors_fichier_cree_vide(tmp_path):
    """Lorsque le contenu est vide, alors le fichier est créé vide."""
    # Given
    chemin_fichier = tmp_path / "vide.txt"
    # When
    exporter_texte(str(chemin_fichier), "")
    # Then
    assert chemin_fichier.exists()
    assert chemin_fichier.stat().st_size == 0
