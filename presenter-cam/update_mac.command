#!/bin/bash
# Double-click after saving a new presenter-cam ZIP in your Downloads folder.
# It updates this folder, keeps your own files, and tells macOS to trust them
# (so you are not asked to approve every script again).
cd "$(dirname "$0")"
HERE="$(pwd)"
pause() { read -n 1 -s -r -p "Press any key to close."; echo; }

ZIP="$(ls -t "$HOME"/Downloads/presenter-cam*.zip 2>/dev/null | head -1)"
if [ -z "$ZIP" ]; then
  echo "No presenter-cam ZIP found in your Downloads folder."
  echo "Save the new ZIP there (do not unzip it), then double-click this file again."
  pause; exit 1
fi
echo "Updating from: $ZIP"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if ! unzip -q "$ZIP" -d "$TMP" || [ ! -f "$TMP/presenter-cam/app.py" ]; then
  echo "This ZIP does not look like a Presenter Cam update."
  pause; exit 1
fi
SRC="$TMP/presenter-cam"

# Keep your own things: take them out of the new copy before copying it over.
cp "$SRC/config.yaml" "$SRC/config.example.yaml"
rm -rf "$SRC/.venv" "$SRC/config.yaml" "$SRC/slides" "$SRC/assets/logo.png" \
       "$SRC/.state.json" "$SRC/zoom_chat_probe.txt"
cp -R "$SRC"/. "$HERE"/ || { echo "Copying failed."; pause; exit 1; }
mkdir -p "$HERE/slides"

# Tell macOS these are your own files (removes the "downloaded from the internet" flag).
xattr -dr com.apple.quarantine "$HERE" 2>/dev/null
chmod +x "$HERE"/*.command

# Bring the helpers up to date (quick when nothing changed).
if [ -x .venv/bin/python ]; then
  echo "Checking helpers..."
  ./.venv/bin/python -m pip install -q --disable-pip-version-check -r requirements.txt \
    || echo "Could not update the helpers. Is the internet connected? Run setup_mac.command later."
else
  echo "Run setup_mac.command once to finish."
fi

echo
echo "Update finished. Your config.yaml, slides and logo were kept."
echo "New example settings, if any, are in config.example.yaml."
echo "You can now delete the ZIP from Downloads."
pause
