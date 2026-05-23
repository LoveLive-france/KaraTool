import re
import cutlet
from core.formattage_kara.post_traitement import post_traiter
from core.formattage_kara.detecteur_emprunts import remplacer_emprunts_katakana

_katsu = cutlet.Cutlet(use_foreign_spelling=False)
_LATIN = re.compile(r"[A-Za-z']+")


def romaniser_texte(texte_japonais: str) -> str:
    if not texte_japonais:
        return ""
    lignes = texte_japonais.split("\n")
    romaji = "\n".join(_romaniser_ligne(ligne) for ligne in lignes)
    romaji = _corriger_particules(romaji)
    return post_traiter(romaji)


def _romaniser_ligne(ligne: str) -> str:
    if not ligne:
        return ""
    ligne = remplacer_emprunts_katakana(ligne)

    segments_latins_proteges = {}

    def _mettre_en_placeholder_latin_majuscule(m):
        idx = len(segments_latins_proteges)
        cle_placeholder = f"__L{idx}__"
        segments_latins_proteges[cle_placeholder] = m.group(0).upper()
        return cle_placeholder

    ligne = _LATIN.sub(_mettre_en_placeholder_latin_majuscule, ligne)
    romaji = _katsu.romaji(ligne, capitalize=False)

    for cle_placeholder, valeur in segments_latins_proteges.items():
        romaji = romaji.replace(cle_placeholder, valeur)

    return romaji


def _corriger_particules(texte: str) -> str:
    # @devnote cutlet romanise la particule へ en "e" (hepburn standard), prononciation attendue "he"
    return re.sub(r"\be\b", "he", texte)
