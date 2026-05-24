#!/bin/bash
NAME=${1:-KaraTool}
VERSION=${2:-dev}
echo "__version__ = \"$VERSION\"" > src/version.py
pyinstaller --noconsole --onefile --name "$NAME" \
  --add-data "tools/ffmpeg.exe;." \
  --add-data "src/template.ass;." \
  --add-data "src/styles_disponibles.json;." \
  --collect-all unidic_lite \
  --collect-all fugashi \
  --collect-all cutlet \
  --collect-all customtkinter \
  --collect-all yt_dlp \
  src/main.py
