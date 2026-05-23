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


def _couleur_override_legende(definition: str) -> str | None:
    champs = definition.split(",")
    if len(champs) < 5:
        return None
    primaire = champs[3].strip()
    if primaire.upper().endswith("FFFFFF"):
        secondaire = champs[4].strip()
        couleur_hex = (
            secondaire[4:] if secondaire.upper().startswith("&H") else secondaire
        )
        return f"&H{couleur_hex}&"
    return None


def _entree_legende(style: dict) -> str:
    nom = style["nom"]
    override = _couleur_override_legende(style["definition"])
    if override:
        return f"{{\\r{nom}}}{{\\1c{override}}}{nom}"
    return f"{{\\r{nom}}}{nom}"


def _generer_ligne_legende(styles: list[dict]) -> str:
    style_base = styles[0]["nom"]
    entrees = " {\\2cHFFFFFF}| ".join(_entree_legende(s) for s in styles)
    return (
        f"Dialogue: 0,0:00:00.00,0:00:10.00,{style_base},,0,0,0,legend,"
        f"{{\\an2\\k1000}}{{\\k0}}{entrees}"
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
    styles_effectifs = [
        {"nom": n, "definition": par_nom[n]} for n in noms_effectifs if n in par_nom
    ] or [{"nom": _NOM_STYLE_DEFAUT, "definition": par_nom[_NOM_STYLE_DEFAUT]}]
    style_dialogue = styles_effectifs[0]["nom"]
    contenu_template = contenu_template.replace(
        f",{_NOM_STYLE_DEFAUT},,", f",{style_dialogue},,", 1
    )
    definitions = [s["definition"] for s in styles_effectifs]
    header = _injecter_styles(contenu_template, definitions)
    legende = (
        _generer_ligne_legende(styles_effectifs)
        if styles_a_inclure and len(styles_a_inclure) > 1
        else ""
    )
    dialogues = "\n".join(
        f"Dialogue: 0,0:00:00.00,0:00:00.00,{style_dialogue},,0,0,0,,{ligne}"
        for ligne in lignes
        if ligne.strip()
    )
    contenu_events = "\n".join(filter(None, [legende, dialogues]))
    with open(chemin_destination, "w", encoding="utf-8") as fichier:
        fichier.write(header + contenu_events + ("\n" if contenu_events else ""))
