from typing import Protocol

LARGEUR_COVER_DEFAUT = 1920
HAUTEUR_COVER_DEFAUT = 1080


class ComposeurImage(Protocol):
    def couvrir_et_flouter(self, image, largeur: int, hauteur: int): ...
    def placer_avant_plan(self, fond, image_originale): ...
    def vers_bytes_jpeg(self, image) -> bytes: ...


class EcriveurMetadonnees(Protocol):
    def embedder_cover(self, chemin_audio: str, donnees_jpeg: bytes) -> None: ...


def generer_cover(
    image,
    composeur: ComposeurImage,
    largeur: int = LARGEUR_COVER_DEFAUT,
    hauteur: int = HAUTEUR_COVER_DEFAUT,
):
    fond = composeur.couvrir_et_flouter(image, largeur, hauteur)
    return composeur.placer_avant_plan(fond, image)


def appliquer_cover(
    chemin_audio: str,
    image,
    composeur: ComposeurImage,
    ecriveur: EcriveurMetadonnees,
    largeur: int = LARGEUR_COVER_DEFAUT,
    hauteur: int = HAUTEUR_COVER_DEFAUT,
) -> None:
    image_composee = generer_cover(image, composeur, largeur, hauteur)
    donnees_jpeg = composeur.vers_bytes_jpeg(image_composee)
    ecriveur.embedder_cover(chemin_audio, donnees_jpeg)
