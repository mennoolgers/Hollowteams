"""TEMPLATE for a new effect. Copy this file, give the copy a short name WITHOUT the
underscore (for example  effects/hello.py ), restart the app, and it appears as a
button and at  http://127.0.0.1:8765/effect/hello

Settings for it go in config.yaml under  effects:  ->  hello:  and arrive here as self.cfg.
"""
from PIL import ImageDraw

from fx import Effect, anchor_position, blend, font, soft_card, to_array


class Hello(Effect):
    title = "Hello"      # text on the button
    kind = "toggle"      # "toggle" (on/off) or "trigger" (runs once by itself)
    layer = 45           # lower = further back

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        text = self.cfg.get("text", "Hello!")
        fnt = font(48, "semibold")
        w, h = int(fnt.getlength(text)) + 80, 90
        img, (ox, oy) = soft_card(w, h, (*self.colours["primary"], 240))
        ImageDraw.Draw(img).text((ox + w / 2, oy + h / 2), text, font=fnt,
                                 fill=(*self.colours["text"], 255), anchor="mm")
        self.sprite = to_array(img)       # made ONCE here, reused every frame (fast)
        sh, sw = self.sprite.shape[:2]
        self.pos = anchor_position("bottom-right", self.W, self.H, sw, sh, margin=0)

    def render(self, frame, now):
        level = self.fade.value(now)      # 0 = hidden ... 1 = fully shown, eased
        blend(frame, self.sprite, self.pos[0], self.pos[1], opacity=level)
        return frame
