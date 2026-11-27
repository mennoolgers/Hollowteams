#!/bin/bash
# Double-click during a TEST Zoom meeting with the chat panel open.
cd "$(dirname "$0")"
./.venv/bin/python tools/zoom_chat_probe.py
read -n 1 -s -r -p "Press any key to close."
