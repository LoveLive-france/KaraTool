import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from core.cover_manager import (
    HAUTEUR_COVER_DEFAUT,
    LARGEUR_COVER_DEFAUT,
    appliquer_cover,
    generer_cover,
)


class ComposeurFactice:
    def __init__(self):
        self.appels = []

    def couvrir_et_flouter(self, image, largeur: int, hauteur: int):
        self.appels.append(("couvrir_et_flouter", largeur, hauteur))
        return f"fond_{largeur}x{hauteur}"

    def placer_avant_plan(self, fond, image_originale):
        self.appels.append(("placer_avant_plan", fond))
        return f"{fond}+avant_plan"

    def vers_bytes_jpeg(self, image) -> bytes:
        self.appels.append(("vers_bytes_jpeg", image))
        return b"jpeg_factice"


class EcriveurFactice:
    def __init__(self):
        self.appels = []

    def embedder_cover(self, chemin_audio: str, donnees_jpeg: bytes) -> None:
        self.appels.append((chemin_audio, donnees_jpeg))


def test_lorsque_generer_cover_alors_fond_floute_en_dimensions_defaut():
    """Lorsque generer_cover est appelé sans dimensions, alors le fond est généré en 1920x1080."""
    # Given
    composeur = ComposeurFactice()
    # When
    generer_cover("image_source", composeur=composeur)
    # Then
    assert composeur.appels[0] == (
        "couvrir_et_flouter",
        LARGEUR_COVER_DEFAUT,
        HAUTEUR_COVER_DEFAUT,
    )


def test_lorsque_generer_cover_avec_dimensions_custom_alors_fond_floute_en_ces_dimensions():
    """Lorsque generer_cover est appelé avec des dimensions custom, alors le fond utilise ces dimensions."""
    # Given
    composeur = ComposeurFactice()
    # When
    generer_cover("image_source", composeur=composeur, largeur=1280, hauteur=720)
    # Then
    assert composeur.appels[0] == ("couvrir_et_flouter", 1280, 720)


def test_lorsque_generer_cover_alors_avant_plan_compose_sur_fond():
    """Lorsque generer_cover est appelé, alors l'avant-plan est composé sur le fond."""
    # Given
    composeur = ComposeurFactice()
    # When
    generer_cover("image_source", composeur=composeur)
    # Then
    assert composeur.appels[1] == (
        "placer_avant_plan",
        f"fond_{LARGEUR_COVER_DEFAUT}x{HAUTEUR_COVER_DEFAUT}",
    )


def test_lorsque_generer_cover_alors_image_composee_retournee():
    """Lorsque generer_cover est appelé, alors l'image composée est retournée."""
    # Given
    composeur = ComposeurFactice()
    # When
    resultat = generer_cover("image_source", composeur=composeur)
    # Then
    assert resultat == f"fond_{LARGEUR_COVER_DEFAUT}x{HAUTEUR_COVER_DEFAUT}+avant_plan"


def test_lorsque_appliquer_cover_alors_ecriveur_recoit_chemin_et_bytes_jpeg():
    """Lorsque appliquer_cover est appelé, alors l'ecriveur reçoit le bon chemin et les bytes JPEG."""
    # Given
    composeur = ComposeurFactice()
    ecriveur = EcriveurFactice()
    # When
    appliquer_cover("chanson.mp3", "image_source", composeur, ecriveur)
    # Then
    assert len(ecriveur.appels) == 1
    chemin, donnees = ecriveur.appels[0]
    assert chemin == "chanson.mp3"
    assert donnees == b"jpeg_factice"


def test_lorsque_appliquer_cover_alors_vers_bytes_jpeg_appele_sur_image_composee():
    """Lorsque appliquer_cover est appelé, alors vers_bytes_jpeg reçoit l'image composée."""
    # Given
    composeur = ComposeurFactice()
    ecriveur = EcriveurFactice()
    # When
    appliquer_cover("chanson.mp3", "image_source", composeur, ecriveur)
    # Then
    appel_jpeg = next(a for a in composeur.appels if a[0] == "vers_bytes_jpeg")
    assert (
        appel_jpeg[1]
        == f"fond_{LARGEUR_COVER_DEFAUT}x{HAUTEUR_COVER_DEFAUT}+avant_plan"
    )
