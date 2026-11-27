"""Shared toolkit for effects: easing curves, fonts, soft cards and fast blending.

You only need this file when you write a new effect. See effects/_example.py.
"""
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONT_DIR = HERE / "fonts"


# ---------------------------------------------------------------------------
# Easing: these make movement start and stop softly instead of mechanically.
# Each takes a value from 0 to 1 and returns a value from 0 to 1.
# ---------------------------------------------------------------------------
def clamp01(t: float) -> float:
    return 0.0 if t < 0 else 1.0 if t > 1 else t


def ease_out_cubic(t):
    t = clamp01(t)
    return 1 - (1 - t) ** 3


def ease_in_cubic(t):
    t = clamp01(t)
    return t ** 3


def ease_in_out_cubic(t):
    t = clamp01(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out_back(t, overshoot=1.3):
    """Goes a touch past the end and settles back: a gentle 'pop'."""
    t = clamp01(t)
    c3 = overshoot + 1
    return 1 + c3 * (t - 1) ** 3 + overshoot * (t - 1) ** 2


def ease_in_out_sine(t):
    t = clamp01(t)
    return -(math.cos(math.pi * t) - 1) / 2


class Fade:
    """A smooth 0-to-1 level for things that switch on and off."""

    def __init__(self, seconds_in=0.6, seconds_out=0.5):
        self.seconds_in, self.seconds_out = seconds_in, seconds_out
        self.target, self.start_value, self.t0 = 0.0, 0.0, -1e9

    def set(self, on: bool, now: float):
        self.start_value = self.value(now)
        self.target = 1.0 if on else 0.0
        self.t0 = now

    @property
    def on(self) -> bool:
        return self.target == 1.0

    def value(self, now: float) -> float:
        duration = self.seconds_in if self.target else self.seconds_out
        p = ease_in_out_cubic((now - self.t0) / max(duration, 1e-6))
        return self.start_value + (self.target - self.start_value) * p

    def visible(self, now: float) -> bool:
        return self.on or self.value(now) > 0.002


# ---------------------------------------------------------------------------
# Colours and fonts
# ---------------------------------------------------------------------------
def rgb(hex_value: str) -> tuple:
    hex_value = hex_value.lstrip("#")
    return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: tuple, b: tuple, t: float) -> tuple:
    return tuple(int(round(x + (y - x) * t)) for x, y in zip(a, b))


_fonts = {}


def font(size: int, weight: str = "semibold"):
    """Inter in 'regular', 'medium', 'semibold' or 'bold'. Falls back to a system font."""
    key = (int(size), weight)
    if key not in _fonts:
        names = {"regular": "Inter-Regular.ttf", "medium": "Inter-Medium.ttf",
                 "semibold": "Inter-SemiBold.ttf", "bold": "Inter-Bold.ttf"}
        candidates = [FONT_DIR / names.get(weight, "Inter-SemiBold.ttf"),
                      Path("/System/Library/Fonts/Helvetica.ttc")]
        for path in candidates:
            try:
                _fonts[key] = ImageFont.truetype(str(path), int(size))
                break
            except OSError:
                continue
        else:
            _fonts[key] = ImageFont.load_default(int(size))
    return _fonts[key]


def wrap_text(text: str, fnt, max_width: int) -> list:
    """Split text into lines that fit max_width pixels."""
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if fnt.getlength(trial) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines or [""]


# ---------------------------------------------------------------------------
# Soft cards with shadows (made once, then reused every frame)
# ---------------------------------------------------------------------------
def soft_card(width, height, fill, radius=None, shadow_blur=18, shadow_offset=8, shadow_opacity=0.35):
    """A rounded card with a soft drop shadow.

    Returns (PIL RGBA image, (x, y) of the card's top-left inside that image).
    Draw your text on the returned image at that offset.
    """
    radius = height // 2 if radius is None else radius
    margin = shadow_blur * 2 + shadow_offset
    img = Image.new("RGBA", (width + 2 * margin, height + 2 * margin), (0, 0, 0, 0))
    if shadow_opacity > 0:
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle(
            (margin, margin + shadow_offset, margin + width, margin + height + shadow_offset),
            radius, fill=(0, 0, 0, int(255 * shadow_opacity)))
        img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(shadow_blur)))
    card = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((margin, margin, margin + width, margin + height),
                                           radius, fill=fill)
    return Image.alpha_composite(img, card), (margin, margin)


def text_shadow_layer(size, draw_fn, blur=10, opacity=0.55):
    """Make a soft shadow for anything drawn by draw_fn(draw) in white."""
    mask = Image.new("L", size, 0)
    draw_fn(ImageDraw.Draw(mask))
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    layer.putalpha(mask.point(lambda v: int(v * opacity)))
    return layer


def to_array(img: Image.Image) -> np.ndarray:
    return np.ascontiguousarray(np.asarray(img.convert("RGBA")))


# ---------------------------------------------------------------------------
# Fast blending onto the camera picture
# ---------------------------------------------------------------------------
def blend(frame: np.ndarray, sprite: np.ndarray, x: int, y: int, opacity: float = 1.0) -> None:
    """Paint an RGBA sprite onto the RGB frame at (x, y). Only touches that area, so it is fast."""
    if opacity <= 0.002:
        return
    fh, fw = frame.shape[:2]
    sh, sw = sprite.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + sw, fw), min(y + sh, fh)
    if x0 >= x1 or y0 >= y1:
        return
    part = sprite[y0 - y:y1 - y, x0 - x:x1 - x]
    alpha = part[..., 3:4].astype(np.uint16)
    if opacity < 0.998:
        alpha = (alpha * int(opacity * 256)) >> 8
    roi = frame[y0:y1, x0:x1]
    roi[:] = ((part[..., :3].astype(np.uint16) * alpha
               + roi.astype(np.uint16) * (255 - alpha) + 127) // 255).astype(np.uint8)


def scale_sprite(sprite: np.ndarray, factor: float) -> np.ndarray:
    if abs(factor - 1) < 0.003:
        return sprite
    h, w = sprite.shape[:2]
    size = (max(1, int(w * factor)), max(1, int(h * factor)))
    return cv2.resize(sprite, size, interpolation=cv2.INTER_AREA if factor < 1 else cv2.INTER_LINEAR)


def anchor_position(corner: str, frame_w, frame_h, sprite_w, sprite_h, margin=36):
    """Top-left (x, y) for a sprite placed in a named corner/side."""
    corner = corner.lower()
    x = margin if "left" in corner else frame_w - sprite_w - margin if "right" in corner \
        else (frame_w - sprite_w) // 2
    y = margin if "top" in corner else frame_h - sprite_h - margin if "bottom" in corner \
        else (frame_h - sprite_h) // 2
    return x, y


# ---------------------------------------------------------------------------
# The base class every effect builds on
# ---------------------------------------------------------------------------
class Effect:
    """Base for all effects.

    kind = "toggle":  press once to switch on, press again to switch off.
    kind = "trigger": each press starts it (again); it ends by itself.
    layer: lower numbers are drawn first (further back).
    """
    title = "Effect"
    kind = "toggle"
    layer = 50

    def __init__(self, ctx: dict, cfg: dict):
        self.ctx, self.cfg = ctx, cfg or {}
        self.W, self.H = ctx["width"], ctx["height"]
        self.colours = {k: rgb(v) for k, v in ctx["colours"].items()}
        self.fade = Fade(self.cfg.get("fade_in", 0.6), self.cfg.get("fade_out", 0.5))

    # Called when the button / URL is pressed. `options` holds URL extras such as ?minutes=3
    def press(self, now: float, options: dict):
        self.set(not self.fade.on, now, options)

    def set(self, on: bool, now: float, options: dict = None):
        self.fade.set(on, now)

    def clear(self, now: float):
        self.set(False, now)

    def is_on(self) -> bool:
        return self.fade.on

    def active(self, now: float) -> bool:
        """True while there is anything to draw."""
        return self.fade.visible(now)

    def render(self, frame: np.ndarray, now: float) -> np.ndarray:
        return frame
