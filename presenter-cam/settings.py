"""Loads config.yaml (your settings) and remembers small things like the last camera."""
import json
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CONFIG_FILE = HERE / "config.yaml"
STATE_FILE = HERE / ".state.json"   # remembered choices; safe to delete

DEFAULTS = {
    "output": {"width": 1280, "height": 720, "fps": 30},
    "camera": {"width": 1920, "height": 1080, "fps": 30},
    "colours": {"primary": "#0A3A66", "deep": "#061E36", "accent": "#6FA8DC", "text": "#FFFFFF"},
}


def _merge(base: dict, extra: dict) -> dict:
    out = dict(base)
    for key, value in (extra or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load_config() -> dict:
    try:
        with open(CONFIG_FILE, encoding="utf-8") as fh:
            user = yaml.safe_load(fh) or {}
    except FileNotFoundError:
        user = {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"There is a typing mistake in config.yaml:\n{exc}")
    return _merge(DEFAULTS, user)


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def hex_to_rgb(value: str) -> tuple:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
