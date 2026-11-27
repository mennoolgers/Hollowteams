"""Key word pop: a word or short phrase appears beside you (each press shows the next word)."""
from PIL import ImageDraw

from fx import (Effect, blend, ease_in_cubic, ease_out_back, ease_out_cubic, font, scale_sprite,
                soft_card, to_array, wrap_text)

IN, OUT = 0.6, 0.5   # seconds to appear / disappear


class KeyWord(Effect):
    title = "Key word"
    kind = "trigger"
    layer = 40

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.words = [str(w) for w in self.cfg.get("words", ["Key word"])] or ["Key word"]
        self.hold = float(self.cfg.get("seconds", 5))
        self.side = self.cfg.get("position", "right")
        self.index = -1
        self.sprite = None
        self.t0 = self.out_t = None
        self._cache = {}

    def _make(self, word):
        if word in self._cache:
            return self._cache[word]
        c = self.colours
        size = int(self.H * 0.075)
        fnt = font(size, "bold")
        lines = wrap_text(word, fnt, int(self.W * 0.34))
        line_h = int(size * 1.18)
        text_w = max(int(fnt.getlength(line)) for line in lines)
        pad_x, pad_y, bar = int(size * 0.75), int(size * 0.5), max(6, size // 9)
        w, h = text_w + 2 * pad_x + bar, line_h * len(lines) + 2 * pad_y
        img, (ox, oy) = soft_card(w, h, (*c["primary"], 240), radius=int(size * 0.4),
                                  shadow_blur=22, shadow_offset=10, shadow_opacity=0.38)
        d = ImageDraw.Draw(img)
        # A slim accent stripe on the left, for a calm, editorial look.
        d.rounded_rectangle((ox + pad_x // 2, oy + pad_y, ox + pad_x // 2 + bar, oy + h - pad_y),
                            bar // 2, fill=(*c["accent"], 255))
        for i, line in enumerate(lines):
            d.text((ox + pad_x + bar, oy + pad_y + i * line_h + line_h // 2), line, font=fnt,
                   fill=(*c["text"], 255), anchor="lm")
        self._cache[word] = to_array(img)
        return self._cache[word]

    def press(self, now, options):
        self.index = (self.index + 1) % len(self.words)
        word = options.get("text") or self.words[self.index]
        self.sprite = self._make(word)
        self.t0, self.out_t = now, None

    def clear(self, now):
        if self.sprite is not None and self.out_t is None:
            self.out_t = now

    def is_on(self):
        return self.sprite is not None and self.out_t is None

    def active(self, now):
        return self.sprite is not None

    def render(self, frame, now):
        t = now - self.t0
        if self.out_t is None and t > IN + self.hold:
            self.out_t = self.t0 + IN + self.hold
        if self.out_t is not None:
            p = (now - self.out_t) / OUT
            if p >= 1:
                self.sprite = None
                return frame
            opacity, scale, dy = 1 - ease_in_cubic(p), 1 - 0.04 * ease_in_cubic(p), -14 * ease_in_cubic(p)
        else:
            p = t / IN
            opacity, scale, dy = ease_out_cubic(p), 0.9 + 0.1 * ease_out_back(p), 18 * (1 - ease_out_cubic(p))
        spr = scale_sprite(self.sprite, scale)
        h, w = spr.shape[:2]
        cx = self.W * (0.74 if self.side == "right" else 0.26)
        cy = self.H * 0.42
        blend(frame, spr, cx - w / 2, cy - h / 2 + dy, opacity)
        return frame
