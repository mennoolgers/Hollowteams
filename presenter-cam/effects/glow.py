"""Warm glow: a soft wash of warm light, as if from a window beside you (toggle)."""
import cv2
import numpy as np

from fx import Effect, rgb


class Glow(Effect):
    title = "Warm glow"
    kind = "toggle"
    layer = 10  # furthest back: it colours the picture itself

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.fade.seconds_in = self.cfg.get("fade_in", 1.4)
        self.fade.seconds_out = self.cfg.get("fade_out", 1.2)
        colour = np.array(rgb(self.cfg.get("colour", "#FFB870")), dtype=np.float32)
        strength = float(self.cfg.get("strength", 0.32))
        # Light falls in from the top-left corner and spreads softly over the picture.
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        lx, ly = self.W * 0.12, -self.H * 0.15
        dist = np.sqrt((xx - lx) ** 2 + (yy - ly) ** 2) / np.hypot(self.W, self.H)
        light = np.clip(1.0 - dist / 0.95, 0, 1) ** 1.7
        mask = 0.22 + 0.78 * light               # a little warmth everywhere, most near the light
        self._full = (mask[..., None] * colour * strength).astype(np.float32)
        self._level, self._inverse = None, None

    def render(self, frame, now):
        level = self.fade.value(now)
        if level <= 0.002:
            return frame
        if self._level is None or abs(level - self._level) > 0.004:
            add = cv2.convertScaleAbs(self._full, alpha=level)
            self._inverse, self._level = cv2.bitwise_not(add), level
        # "Screen" blend: brightens gently, never clips skin tones harshly.
        return cv2.bitwise_not(cv2.multiply(cv2.bitwise_not(frame), self._inverse, scale=1 / 255))
