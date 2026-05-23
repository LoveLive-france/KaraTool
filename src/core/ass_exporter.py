import json
import os
import shutil
import sys
from pathlib import Path

_CHEMIN_TEMPLATE = Path(__file__).parent.parent / "template.ass"

_CHEMIN_STYLES_BUNDLE = (
    Path(sys._MEIPASS) / "styles_disponibles.json"
    if getattr(sys, "frozen", False)
    else Path(__file__).parent.parent / "styles_disponibles.json"
)
_CHEMIN_STYLES_UTILISATEUR = (
    Path(os.getenv("APPDATA", Path.home())) / "KaraTool" / "styles_disponibles.json"
)

_PREFIXE_DIALOGUE = "Dialogue: 0,0:00:00.00,0:00:00.00,Sample KM [Up],,0,0,0,,"
_NOM_STYLE_DEFAUT = "Sample KM [Up]"


def _initialiser_styles_utilisateur() -> None:
    if not _CHEMIN_STYLES_UTILISATEUR.exists():
        _CHEMIN_STYLES_UTILISATEUR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(_CHEMIN_STYLES_BUNDLE, _CHEMIN_STYLES_UTILISATEUR)


def lire_styles_disponibles() -> list[dict]:
    _initialiser_styles_utilisateur()
    return json.loads(_CHEMIN_STYLES_UTILISATEUR.read_text(encoding="utf-8"))


def extraire_styles_depuis_ass(chemin: str) -> list[dict]:
    styles = []
    for ligne in Path(chemin).read_text(encoding="utf-8").splitlines():
        if ligne.startswith("Style: "):
            nom = ligne.removeprefix("Style: ").split(",")[0]
            styles.append({"nom": nom, "definition": ligne})
    return styles


def fusionner_styles(existants: list[dict], nouveaux: list[dict]) -> list[dict]:
    noms_existants = {s["nom"] for s in existants}
    return existants + [s for s in nouveaux if s["nom"] not in noms_existants]


def reinitialiser_styles() -> None:
    _CHEMIN_STYLES_UTILISATEUR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(_CHEMIN_STYLES_BUNDLE, _CHEMIN_STYLES_UTILISATEUR)


def sauvegarder_styles(styles: list[dict]) -> None:
    _CHEMIN_STYLES_UTILISATEUR.parent.mkdir(parents=True, exist_ok=True)
    _CHEMIN_STYLES_UTILISATEUR.write_text(
        json.dumps(styles, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _injecter_styles(contenu: str, definitions: list[str]) -> str:
    lignes = contenu.splitlines(keepends=True)
    resultat = []
    en_section_styles = False
    for ligne in lignes:
        resultat.append(ligne)
        if ligne.strip() == "[V4+ Styles]":
            en_section_styles = True
        if en_section_styles and ligne.startswith("Format:"):
            for definition in definitions:
                resultat.append(definition + "\n")
            en_section_styles = False
    return "".join(resultat)


def exporter_ass(
    chemin_destination: str,
    lignes: list[str],
    titre: str = "New subtitles",
    styles_a_inclure: list[str] | None = None,
) -> None:
    contenu_template = _CHEMIN_TEMPLATE.read_text(encoding="utf-8").replace(
        "Title: New subtitles", f"Title: {titre}", 1
    )
    par_nom = {s["nom"]: s["definition"] for s in lire_styles_disponibles()}
    noms_effectifs = styles_a_inclure if styles_a_inclure else [_NOM_STYLE_DEFAUT]
    definitions = [par_nom[nom] for nom in noms_effectifs if nom in par_nom] or [
        par_nom[_NOM_STYLE_DEFAUT]
    ]
    header = _injecter_styles(contenu_template, definitions)
    dialogues = "\n".join(
        f"{_PREFIXE_DIALOGUE}{ligne}" for ligne in lignes if ligne.strip()
    )
    with open(chemin_destination, "w", encoding="utf-8") as fichier:
        fichier.write(header + dialogues + ("\n" if dialogues else ""))
