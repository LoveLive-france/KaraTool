# KaraTool
Un petit outil pour aider à la création de karaokés

## Création de l'exécutable

### _Prérequis_
Bien avoir le ffmpeg.exe au même endroit que le .py : c'est imporant car il sera embarqué directement dans l'app.

### _Commande de création_
```pyinstaller --clean --onefile --windowed --add-binary "ffmpeg.exe;." youtube_downloader.py```
