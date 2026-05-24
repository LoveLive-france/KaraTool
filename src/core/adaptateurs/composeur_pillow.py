from io import BytesIO

from PIL import Image, ImageFilter, ImageOps

FACTEUR_HAUTEUR_DEFAUT = 0.75
MARGE_GAUCHE_DEFAUT = 0.05


class ComposeurPillow:
    def __init__(
        self,
        facteur_hauteur: float = FACTEUR_HAUTEUR_DEFAUT,
        marge_gauche: float = MARGE_GAUCHE_DEFAUT,
    ):
        self.facteur_hauteur = facteur_hauteur
        self.marge_gauche = marge_gauche

    def couvrir_et_flouter(
        self, image: Image.Image, largeur: int, hauteur: int
    ) -> Image.Image:
        fond = ImageOps.fit(image, (largeur, hauteur))
        return fond.filter(ImageFilter.GaussianBlur(radius=30))

    def placer_avant_plan(
        self, fond: Image.Image, image_originale: Image.Image
    ) -> Image.Image:
        hauteur_max = int(fond.height * self.facteur_hauteur)
        ratio = min(
            hauteur_max / image_originale.height, fond.width / image_originale.width
        )
        largeur_av = int(image_originale.width * ratio)
        hauteur_av = int(image_originale.height * ratio)
        avant_plan = image_originale.resize((largeur_av, hauteur_av), Image.LANCZOS)
        x = int(fond.width * self.marge_gauche)
        y = (fond.height - hauteur_av) // 2
        resultat = fond.copy()
        resultat.paste(avant_plan, (x, y))
        return resultat

    def vers_bytes_jpeg(self, image: Image.Image) -> bytes:
        tampon = BytesIO()
        image.convert("RGB").save(tampon, format="JPEG", quality=95)
        return tampon.getvalue()
