from io import BytesIO

from PIL import Image, ImageFilter, ImageOps

FACTEUR_HAUTEUR_DEFAUT = 0.6
MARGE_GAUCHE_DEFAUT = 0.0625
_OPACITE_FOND = 0.5


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
        flou = ImageOps.fit(image, (largeur, hauteur)).filter(
            ImageFilter.GaussianBlur(radius=20)
        )
        fond_noir = Image.new("RGB", (largeur, hauteur), (0, 0, 0))
        return Image.blend(fond_noir, flou.convert("RGB"), alpha=_OPACITE_FOND)

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
