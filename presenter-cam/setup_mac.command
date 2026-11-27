#!/bin/bash
# Double-click this file once to set up Presenter Cam on a Mac.
# It creates a private Python environment INSIDE this folder (.venv).
# Nothing is installed system-wide.
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 was not found. Please install Python 3.11 or newer from python.org first."
  read -n 1 -s -r -p "Press any key to close."; exit 1
fi
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' || {
  echo "Your Python is older than 3.11. Please install a newer one from python.org."
  read -n 1 -s -r -p "Press any key to close."; exit 1; }
python3 -m venv .venv && ./.venv/bin/python -m pip install --upgrade pip && \
  ./.venv/bin/python -m pip install -r requirements.txt && echo && echo "Setup finished." 
read -n 1 -s -r -p "Press any key to close."
