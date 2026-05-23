#!/bin/bash
NAME=${1:-KaraTool}
pyinstaller --noconsole --onefile --name "$NAME" \
  --add-data "tools/ffmpeg.exe;." \
  --add-data "src/template.ass;." \
  --collect-all unidic_lite \
  --collect-all fugashi \
  src/main.py
