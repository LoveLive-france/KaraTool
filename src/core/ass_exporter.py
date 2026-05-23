from pathlib import Path

_CHEMIN_TEMPLATE = Path(__file__).parent.parent / "template.ass"
_PREFIXE_DIALOGUE = "Dialogue: 0,0:00:00.00,0:00:00.00,Sample KM [Up],,0,0,0,,"


def exporter_ass(
    chemin_destination: str, lignes: list[str], titre: str = "New subtitles"
) -> None:
    header = _CHEMIN_TEMPLATE.read_text(encoding="utf-8").replace(
        "Title: New subtitles", f"Title: {titre}", 1
    )
    dialogues = "\n".join(
        f"{_PREFIXE_DIALOGUE}{ligne}" for ligne in lignes if ligne.strip()
    )
    with open(chemin_destination, "w", encoding="utf-8") as fichier:
        fichier.write(header + dialogues + ("\n" if dialogues else ""))
