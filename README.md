# KaraTool
Un petit outil pour aider à la création de karaokés

## Prérequis

### _Dépendances Python_
Installer les bibliothèques nécessaires :
```
pip install customtkinter yt-dlp pyinstaller
```

### _FFmpeg_
Télécharger `ffmpeg.exe` et le placer dans le même dossier que le `.py`.

## Création de l'exécutable

### _Prérequis_
Bien avoir le ffmpeg.exe au même endroit que le .py : c'est important car il sera embarqué directement dans l'app.

### _Commande de création_
```pyinstaller --clean --onefile --windowed --add-binary "ffmpeg.exe;." youtube_downloader.py```
