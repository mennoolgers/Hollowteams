#!/bin/bash
# Double-click during a TEST Zoom meeting with the chat panel open.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo "First run setup_mac.command (double-click it), then try again."
  read -n 1 -s -r -p "Press any key to close."; exit 1
fi
echo "Checking helpers (a few seconds)..."
./.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt || \
  echo "Could not install the helpers. Is the internet connected?"
./.venv/bin/python tools/zoom_chat_probe.py
read -n 1 -s -r -p "Press any key to close."
