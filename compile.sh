#!/bin/bash
NAME=${1:-KaraTool}
VERSION=${2:-dev}
echo "__version__ = \"$VERSION\"" > src/version.py

# Trouver le dossier Python
PYTHON_DIR=$(python -c "import sys; print(sys.base_prefix)")

pyinstaller --noconsole --onefile --name "$NAME" \
  --add-data "tools/ffmpeg.exe;." \
  --add-data "src/template.ass;." \
  --add-data "src/styles_disponibles.json;." \
  --add-binary "$PYTHON_DIR/python312.dll;." \
  --add-binary "$PYTHON_DIR/python312d.dll;." \
  --collect-all unidic_lite \
  --collect-all fugashi \
  --collect-all cutlet \
  --collect-all customtkinter \
  --collect-all yt_dlp \
  src/main.py
