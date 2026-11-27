#!/bin/bash
# Double-click to run the Step 0 test pattern on a Mac.
cd "$(dirname "$0")"
./.venv/bin/python step0_test_pattern.py
read -n 1 -s -r -p "Press any key to close."
