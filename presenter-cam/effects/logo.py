"""Logo corner: your logo rests quietly in a corner (toggle)."""
from PIL import Image

from fx import HERE, Effect, anchor_position, blend, text_shadow_layer, to_array


class Logo(Effect):
    title = "Logo"
    kind = "toggle"
    layer = 30

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.fade.seconds_in = self.cfg.get("fade_in", 0.9)
        self.fade.seconds_out = self.cfg.get("fade_out", 0.7)
        self.opacity = float(self.cfg.get("opacity", 0.92))
        path = HERE / self.cfg.get("file", "assets/logo.png")
        if not path.exists():
            path = HERE / "assets" / "logo-placeholder.png"
        img = Image.open(path).convert("RGBA")
        height = int(self.cfg.get("height", 72))
        img = img.resize((max(1, round(img.width * height / img.height)), height), Image.LANCZOS)
        # Soft shadow under the logo so it reads on light and dark backgrounds.
        pad = 24
        canvas = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
        alpha = img.getchannel("A")
        shadow = text_shadow_layer(canvas.size, lambda d: d.bitmap((pad, pad + 3), alpha, fill=255),
                                   blur=8, opacity=0.35)
        canvas = Image.alpha_composite(canvas, shadow)
        canvas.alpha_composite(img, (pad, pad))
        self.sprite = to_array(canvas)
        h, w = self.sprite.shape[:2]
        self.pos = anchor_position(self.cfg.get("corner", "top-left"), self.W, self.H, w, h,
                                   margin=int(self.cfg.get("margin", 36)) - pad)

    def render(self, frame, now):
        level = self.fade.value(now)
        x, y = self.pos
        blend(frame, self.sprite, x, y + (1 - level) * 10, opacity=level * self.opacity)
        return frame
