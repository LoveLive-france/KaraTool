def exporter_texte(chemin_destination: str, contenu: str) -> None:
    with open(chemin_destination, "w", encoding="utf-8") as fichier:
        fichier.write(contenu)
