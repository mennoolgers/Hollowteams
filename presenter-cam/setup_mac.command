#!/bin/bash
# Double-click this file to set up (or update) Presenter Cam on a Mac.
# It creates a private Python environment INSIDE this folder (.venv).
# Nothing is installed system-wide.
cd "$(dirname "$0")"

# pyvirtualcam (the link to OBS Virtual Camera) supports Python 3.11 to 3.14.
# Use the newest of those that is installed, even if a newer Python is also present.
PY=""
for v in 3.14 3.13 3.12 3.11; do
  for cand in "/Library/Frameworks/Python.framework/Versions/$v/bin/python$v" "$(command -v python$v)"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then PY="$cand"; break 2; fi
  done
done

if [ -z "$PY" ]; then
  echo
  echo "I need Python 3.14 (or 3.11 to 3.13). Newer versions such as 3.15 are not supported yet"
  echo "by the virtual camera library."
  echo
  echo "Please install Python 3.14 from:  https://www.python.org/downloads/macos/"
  echo "(pick the latest 3.14.x 'macOS 64-bit universal2 installer'). It lives next to any"
  echo "other Python you have. Then double-click this setup file again."
  echo
  read -n 1 -s -r -p "Press any key to close."; exit 1
fi

WANT="$("$PY" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
echo "Using Python $WANT ($PY)"

# If an older setup used a different Python, start the private environment afresh.
if [ -x .venv/bin/python ]; then
  HAVE="$(.venv/bin/python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null)"
  if [ "$HAVE" != "$WANT" ]; then
    echo "Rebuilding the private environment (was Python $HAVE)..."
    rm -rf ./.venv
  fi
fi

[ -x .venv/bin/python ] || "$PY" -m venv .venv || { read -n 1 -s -r -p "Press any key to close."; exit 1; }
if ./.venv/bin/python -m pip install --upgrade pip && ./.venv/bin/python -m pip install -r requirements.txt; then
  echo; echo "Setup finished."
else
  echo; echo "Setup did NOT finish. Please send the messages above to your developer."
fi
read -n 1 -s -r -p "Press any key to close."
