#!/bin/bash
# GTA Clipper for macOS — double-click to open the app (http://localhost:8765).
# First run: creates .venv next to this file, installs packages, fonts and the speech model (a few minutes).
cd "$(dirname "$0")" || exit 1
# A double-clicked .command does not load ~/.zprofile, so add Homebrew to PATH (Apple Silicon and Intel).
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

PY=".venv/bin/python"
if [ ! -x "$PY" ]; then
  BASE=""
  for c in python3.12 python3.13 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
      BASE="$c"; break
    fi
  done
  if [ -z "$BASE" ]; then
    echo "Potrzebny Python 3.10 lub nowszy. Zainstaluj:  brew install python@3.12"
    read -r -p "Enter zamyka okno…" _; exit 1
  fi
  echo "Tworzę środowisko .venv ($("$BASE" --version))…"
  "$BASE" -m venv .venv || { read -r -p "Nie udało się. Enter zamyka okno…" _; exit 1; }
fi

if [ ! -f .venv/.setup_done ]; then
  for tool in ffmpeg deno; do
    command -v "$tool" >/dev/null 2>&1 || echo "Brak $tool — zainstaluj:  brew install $tool"
  done
  "$PY" -m pip install -q -U pip
  "$PY" -m pip install -r requirements.txt && "$PY" clipper.py setup && touch .venv/.setup_done
fi

exec "$PY" clipper.py app
