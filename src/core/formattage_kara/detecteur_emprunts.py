import re
import cutlet

_KATAKANA = re.compile(r"[ァ-ヾー]+")
_SEUIL_RATIO_LONGUEUR = 0.7

_katsu_phonetique = cutlet.Cutlet(use_foreign_spelling=False)
_katsu_etranger = cutlet.Cutlet(use_foreign_spelling=True)


def remplacer_emprunts_katakana(texte: str) -> str:
    return _KATAKANA.sub(_resoudre_sequence, texte)


def _resoudre_sequence(match: re.Match) -> str:
    sequence = match.group(0)
    forme_phonetique = _katsu_phonetique.romaji(sequence, capitalize=False).strip()
    forme_etrangere = _katsu_etranger.romaji(sequence, capitalize=False).strip()

    if _est_sans_equivalent_etranger(forme_phonetique, forme_etrangere):
        return sequence

    if _est_translitteration_directe(forme_phonetique, forme_etrangere):
        return forme_etrangere

    return sequence


def _est_sans_equivalent_etranger(forme_phonetique: str, forme_etrangere: str) -> bool:
    return forme_etrangere.lower() == forme_phonetique.lower()


def _est_translitteration_directe(forme_phonetique: str, forme_etrangere: str) -> bool:
    longueur_etrangere = len(forme_etrangere.replace(" ", ""))
    return len(forme_phonetique) / longueur_etrangere >= _SEUIL_RATIO_LONGUEUR
