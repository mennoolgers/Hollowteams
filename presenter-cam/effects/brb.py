"""'Back in a moment': a calm full-screen card over a soft blur of the camera (toggle)."""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw

from fx import Effect, blend, font, mix, text_shadow_layer, to_array


class BackSoon(Effect):
    title = "Back in a moment"
    kind = "toggle"
    layer = 90  # on top of everything

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.fade.seconds_in = self.cfg.get("fade_in", 0.9)
        self.fade.seconds_out = self.cfg.get("fade_out", 0.8)
        c = self.colours
        self.tint = np.empty((self.H, self.W, 3), np.uint8)
        self.tint[:] = c["deep"]
        self.tint_amount = float(self.cfg.get("tint", 0.55))

        title = self.cfg.get("title", "Back in a moment")
        subtitle = self.cfg.get("subtitle", "We'll continue shortly")
        t_font, s_font = font(int(self.H * 0.085), "semibold"), font(int(self.H * 0.034), "regular")
        size = (self.W, int(self.H * 0.42))
        cx, ty, sy = size[0] / 2, size[1] * 0.36, size[1] * 0.62

        def draw_text(d, fill_title=255, fill_sub=255):
            d.text((cx, ty), title, font=t_font, fill=fill_title, anchor="mm")
            d.text((cx, sy), subtitle, font=s_font, fill=fill_sub, anchor="mm")

        img = text_shadow_layer(size, draw_text, blur=14, opacity=0.5)
        d = ImageDraw.Draw(img)
        d.text((cx, ty), title, font=t_font, fill=(*c["text"], 255), anchor="mm")
        d.text((cx, sy), subtitle, font=s_font, fill=(*mix(c["text"], c["accent"], 0.45), 235),
               anchor="mm")
        line_w = int(self.W * 0.06)
        d.rounded_rectangle((cx - line_w / 2, size[1] * 0.49 - 2, cx + line_w / 2, size[1] * 0.49 + 2),
                            2, fill=(*c["accent"], 255))
        self.card = to_array(img)
        self.card_y = int(self.H * 0.5 - size[1] * 0.5)
        self.dots_y = int(self.card_y + size[1] * 0.82)
        # Warm up the blur tools once now, so the first real use has no hiccup.
        warm = np.zeros((self.H, self.W, 3), np.uint8)
        self.fade.set(True, -100.0)
        self.render(warm, 0.0)
        self.fade = type(self.fade)(self.fade.seconds_in, self.fade.seconds_out)

    def render(self, frame, now):
        level = self.fade.value(now)
        if level <= 0.002:
            return frame
        # Soft blur: shrink, blur, grow back (much faster than blurring full size).
        small = cv2.resize(frame, (self.W // 12, self.H // 12), interpolation=cv2.INTER_AREA)
        small = cv2.GaussianBlur(small, (0, 0), 2.2)
        scene = cv2.resize(small, (self.W, self.H), interpolation=cv2.INTER_LINEAR)
        scene = cv2.addWeighted(scene, 1 - self.tint_amount, self.tint, self.tint_amount, 0)
        blend(scene, self.card, 0, self.card_y)
        # Three softly breathing dots.
        accent, gap, r = self.colours["accent"], int(self.H * 0.03), max(3, int(self.H * 0.0065))
        for i in range(3):
            glow = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(now * 2.4 - i * 0.9))
            colour = mix(self.colours["deep"], accent, glow)
            cv2.circle(scene, (self.W // 2 + (i - 1) * gap, self.dots_y), r, colour, -1, cv2.LINE_AA)
        if level >= 0.998:
            return scene
        return cv2.addWeighted(frame, 1 - level, scene, level, 0)
