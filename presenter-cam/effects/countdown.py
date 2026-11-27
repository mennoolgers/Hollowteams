"""Countdown timer in a corner, with a gentle 'time's up' at the end.

Press once to start (default minutes from config.yaml), press again to stop.
URL extra: /effect/countdown?minutes=3
"""
import math

from PIL import ImageDraw

from fx import (Effect, anchor_position, blend, ease_in_cubic, ease_out_cubic, font, mix,
                scale_sprite, soft_card, to_array)


class Countdown(Effect):
    title = "Countdown"
    kind = "toggle"
    layer = 50

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.minutes = float(self.cfg.get("minutes", 5))
        self.end_seconds = float(self.cfg.get("end_seconds", 8))
        self.end_text = self.cfg.get("end_text", "Time's up")
        self.corner = self.cfg.get("corner", "top-right")
        self.end_time = self.started = self.out_t = None
        self._cache = {}
        size = int(self.H * 0.07)
        self.fnt = font(size, "semibold")
        self.digit_w = max(self.fnt.getlength(str(d)) for d in range(10))
        self.card_w, self.card_h = int(self.digit_w * 4 + size * 1.8), int(size * 1.75)

    # ---- drawing ----------------------------------------------------------
    def _make(self, text, progress, warm):
        key = (text, round(progress * 300), warm)
        if key in self._cache:
            return self._cache[key]
        if len(self._cache) > 400:
            self._cache.clear()
        c = self.colours
        w, h = self.card_w, self.card_h
        is_clock = ":" in text
        if not is_clock:
            w = max(w, int(self.fnt.getlength(text) + h * 1.1))
        img, (ox, oy) = soft_card(w, h, (*c["primary"], 238), radius=h // 2,
                                  shadow_blur=16, shadow_offset=7, shadow_opacity=0.35)
        d = ImageDraw.Draw(img)
        colour = mix(c["text"], (255, 214, 150), warm)
        cy = oy + h * (0.46 if is_clock else 0.5)
        if is_clock:
            # Fixed-width digits, so the numbers don't wobble as they change.
            total = sum(self.digit_w if ch.isdigit() else self.fnt.getlength(ch) for ch in text)
            x = ox + (w - total) / 2
            for ch in text:
                adv = self.digit_w if ch.isdigit() else self.fnt.getlength(ch)
                d.text((x + adv / 2, cy), ch, font=self.fnt, fill=(*colour, 255), anchor="mm")
                x += adv
        else:
            d.text((ox + w / 2, cy), text, font=self.fnt, fill=(*colour, 255), anchor="mm")
            self._cache[key] = to_array(img)
            return self._cache[key]
        # Thin progress line along the bottom of the pill.
        bar_y, inset = oy + h - h * 0.17, h * 0.55
        d.rounded_rectangle((ox + inset, bar_y - 2, ox + w - inset, bar_y + 2), 2,
                            fill=(*c["deep"], 200))
        if progress > 0:
            d.rounded_rectangle((ox + inset, bar_y - 2, ox + inset + (w - 2 * inset) * progress,
                                 bar_y + 2), 2, fill=(*c["accent"], 255))
        self._cache[key] = to_array(img)
        return self._cache[key]

    # ---- controls ---------------------------------------------------------
    def press(self, now, options):
        self.set(not self.is_on(), now, options)

    def set(self, on, now, options=None):
        if on:
            minutes = float((options or {}).get("minutes", self.minutes))
            self.started, self.end_time, self.out_t = now, now + minutes * 60, None
        elif self.end_time is not None and self.out_t is None:
            self.out_t = now

    def is_on(self):
        return self.end_time is not None and self.out_t is None

    def active(self, now):
        return self.end_time is not None

    # ---- each frame -------------------------------------------------------
    def render(self, frame, now):
        remaining = self.end_time - now
        if remaining <= -self.end_seconds and self.out_t is None:
            self.out_t = now
        if remaining > 0:
            secs = math.ceil(remaining)
            text = f"{secs // 60}:{secs % 60:02d}"
            total = self.end_time - self.started
            sprite = self._make(text, remaining / total, 1.0 if secs <= 10 else 0.0)
            scale = 1.0
        else:
            sprite = self._make(self.end_text, 0, 1.0)
            # Three soft "breaths" when time is up.
            since = -remaining
            scale = 1 + 0.05 * math.sin(math.pi * min(since, 3) / 1.0) ** 2 if since < 3 else 1.0
        opacity = ease_out_cubic((now - self.started) / 0.7)
        slide = 30 * (1 - ease_out_cubic((now - self.started) / 0.7))
        if self.out_t is not None:
            p = (now - self.out_t) / 0.6
            if p >= 1:
                self.end_time = self.out_t = None
                return frame
            opacity *= 1 - ease_in_cubic(p)
            slide = 30 * ease_in_cubic(p)
        spr = scale_sprite(sprite, scale)
        base_w, base_h = sprite.shape[1], sprite.shape[0]
        x, y = anchor_position(self.corner, self.W, self.H, base_w, base_h, margin=0)
        x += (base_w - spr.shape[1]) / 2 + (slide if "right" in self.corner else -slide)
        y += (base_h - spr.shape[0]) / 2
        blend(frame, spr, x, y, opacity)
        return frame
