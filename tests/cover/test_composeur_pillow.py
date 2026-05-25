import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from PIL import Image, ImageStat
from core.adaptateurs.composeur_pillow import ComposeurPillow


def _image_unie(couleur: tuple, taille: tuple = (100, 100)) -> Image.Image:
    return Image.new("RGB", taille, couleur)


def test_lorsque_couvrir_et_flouter_alors_fond_plus_sombre_que_image_source():
    """Lorsque couvrir_et_flouter est appelé, alors le fond est plus sombre que l'image source."""
    # Given
    image_rouge = _image_unie((255, 0, 0))
    composeur = ComposeurPillow()
    # When
    fond = composeur.couvrir_et_flouter(image_rouge, 100, 100)
    # Then
    r_moyen = ImageStat.Stat(fond).mean[0]
    assert r_moyen < 255


def test_lorsque_couvrir_et_flouter_alors_fond_non_noir():
    """Lorsque couvrir_et_flouter est appelé, alors le fond n'est pas entièrement noir (blend partiel)."""
    # Given
    image_rouge = _image_unie((255, 0, 0))
    composeur = ComposeurPillow()
    # When
    fond = composeur.couvrir_et_flouter(image_rouge, 100, 100)
    # Then
    r_moyen = ImageStat.Stat(fond).mean[0]
    assert r_moyen > 0


def test_lorsque_couvrir_et_flouter_alors_dimensions_respectees():
    """Lorsque couvrir_et_flouter est appelé avec des dimensions cibles, alors l'image retournée a ces dimensions."""
    # Given
    image = _image_unie((100, 200, 50), taille=(300, 200))
    composeur = ComposeurPillow()
    # When
    fond = composeur.couvrir_et_flouter(image, 1920, 1080)
    # Then
    assert fond.size == (1920, 1080)
