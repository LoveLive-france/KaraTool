import re
import cutlet
from core.formattage_kara.post_traitement import post_traiter
from core.formattage_kara.detecteur_emprunts import remplacer_emprunts_katakana

_katsu = cutlet.Cutlet(use_foreign_spelling=False)
_LATIN = re.compile(r"[A-Za-z']+")
_JAPONAIS = re.compile(r"[ぁ-ん゛゜ァ-ヾ一-龯]")
_PARENS = re.compile(r"[（(]([^）)]*)[）)]")
_SENTINEL_PARENS = "__{}__"
_SENTINEL_LATIN_ORIGINAL = "\x01{}\x01"


def romaniser_texte(texte_japonais: str, conserver_casse_latine: bool = False) -> str:
    if not texte_japonais:
        return ""
    lignes = texte_japonais.split("\n")
    romaji = "\n".join(
        _romaniser_ligne(ligne, conserver_casse_latine) for ligne in lignes
    )
    romaji = _corriger_particules(romaji)
    return post_traiter(romaji)


def _est_ligne_entierement_latine(ligne: str) -> bool:
    return not _JAPONAIS.search(ligne)


def _romaniser_ligne(ligne: str, conserver_casse_latine: bool = False) -> str:
    if not ligne:
        return ""
    if conserver_casse_latine and _est_ligne_entierement_latine(ligne):
        return ligne

    segments_proteges = {}

    if conserver_casse_latine:

        def _proteger_parens_latines(m):
            contenu = m.group(1)
            if not _JAPONAIS.search(contenu):
                cle = _SENTINEL_PARENS.format(len(segments_proteges))
                segments_proteges[cle] = m.group(0)
                return cle
            return m.group(0)

        ligne = _PARENS.sub(_proteger_parens_latines, ligne)
    else:

        def _minuscules_parens_latines(m):
            contenu = m.group(1)
            if not _JAPONAIS.search(contenu):
                open_p, close_p = m.group(0)[0], m.group(0)[-1]
                return f"{open_p}{contenu.lower()}{close_p}"
            return m.group(0)

        ligne = _PARENS.sub(_minuscules_parens_latines, ligne)

    def _proteger_latin_original(m):
        cle = _SENTINEL_LATIN_ORIGINAL.format(len(segments_proteges))
        segments_proteges[cle] = m.group(0).upper()
        return cle

    ligne = _LATIN.sub(_proteger_latin_original, ligne)
    ligne = remplacer_emprunts_katakana(ligne)

    def _proteger_latin_emprunt(m):
        cle = f"__L{len(segments_proteges)}__"
        segments_proteges[cle] = _casse_segment_latin(m.group(0))
        return cle

    ligne = _LATIN.sub(_proteger_latin_emprunt, ligne)
    romaji = _katsu.romaji(ligne, capitalize=False)

    for cle, valeur in segments_proteges.items():
        romaji = romaji.replace(cle, valeur)

    return romaji


def _casse_segment_latin(segment: str) -> str:
    # @devnote cutlet capitalise les noms propres (ex: "Nike") même avec capitalize=False — on préserve ce title case
    if segment[0].isupper() and not segment.isupper():
        return segment
    return segment.upper()


def _corriger_particules(texte: str) -> str:
    # @devnote cutlet romanise la particule へ en "e" (hepburn standard), prononciation attendue "he"
    return re.sub(r"\be\b", "he", texte)
