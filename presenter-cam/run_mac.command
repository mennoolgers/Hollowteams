#!/bin/bash
# Double-click to start Presenter Cam.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "First run setup_mac.command (double-click it), then try again."
  read -n 1 -s -r -p "Press any key to close."; exit 1
fi
./.venv/bin/python app.py
