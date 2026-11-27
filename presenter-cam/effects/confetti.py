"""Confetti: colourful paper confetti tumbles down over the picture for a few seconds."""
import cv2
import numpy as np

from fx import Effect, rgb

DEFAULT_COLOURS = ["#0A3A66", "#6FA8DC", "#FFFFFF", "#E9C46A", "#E07A5F", "#A8DADC"]


class Confetti(Effect):
    title = "Confetti"
    kind = "trigger"
    layer = 60

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.amount = int(self.cfg.get("amount", 160))
        self.palette = np.array([rgb(c) for c in self.cfg.get("colours", DEFAULT_COLOURS)])
        self.rng = np.random.default_rng()
        self.p = None          # all pieces, as columns of numbers
        self.last = None

    def press(self, now, options):
        n, r, s = self.amount, self.rng, self.H / 720
        new = {
            "x": r.uniform(-0.05, 1.05, n) * self.W,
            "y": r.uniform(-0.35, -0.02, n) * self.H,
            "vx": r.normal(0, 35, n) * s,
            "vy": r.uniform(60, 160, n) * s,
            "vmax": r.uniform(170, 300, n) * s,            # paper flutters, it doesn't drop
            "rot": r.uniform(0, np.pi, n),
            "spin": r.uniform(-4, 4, n),
            "flip": r.uniform(0, 2 * np.pi, n),
            "flip_speed": r.uniform(4, 10, n),
            "sway": r.uniform(0, 2 * np.pi, n),
            "w": r.uniform(9, 16, n) * s,
            "h": r.uniform(5, 8, n) * s,
            "delay": now + r.uniform(0, 0.7, n),
            "colour": r.integers(0, len(self.palette), n),
        }
        if self.p is None:
            self.p = new
        else:
            self.p = {k: np.concatenate([self.p[k], new[k]]) for k in new}
        self.last = now

    def clear(self, now):
        self.p = None

    def is_on(self):
        return self.p is not None

    def active(self, now):
        return self.p is not None

    def render(self, frame, now):
        p = self.p
        dt = min(max(now - self.last, 0), 0.05)
        self.last = now
        live = now >= p["delay"]
        # Movement: gentle gravity, capped speed, side-to-side sway.
        p["vy"] = np.where(live, np.minimum(p["vy"] + 320 * dt, p["vmax"]), p["vy"])
        p["y"] += np.where(live, p["vy"] * dt, 0)
        p["x"] += np.where(live, (p["vx"] + 45 * np.sin(now * 2.2 + p["sway"])) * dt, 0)
        p["rot"] += p["spin"] * dt
        p["flip"] += p["flip_speed"] * dt
        keep = p["y"] < self.H + 30
        if not keep.any():
            self.p = None
            return frame
        if not keep.all():
            self.p = p = {k: v[keep] for k, v in p.items()}
            live = live[keep]

        # Each piece is a small rectangle that turns and "flips" (gets narrower and darker).
        flip = np.cos(p["flip"])
        half_w = p["w"] / 2 * np.maximum(np.abs(flip), 0.18)
        half_h = p["h"] / 2
        cos_r, sin_r = np.cos(p["rot"]), np.sin(p["rot"])
        corners = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            dx, dy = sx * half_w, sy * half_h
            corners.append((p["x"] + dx * cos_r - dy * sin_r, p["y"] + dx * sin_r + dy * cos_r))
        pts = np.stack([np.stack(c, axis=-1) for c in corners], axis=1)   # (n, 4, 2)
        pts = np.round(pts * 16).astype(np.int32)                         # sub-pixel precision
        shade = 0.72 + 0.28 * np.abs(flip)
        colours = (self.palette[p["colour"]] * shade[:, None]).astype(int)
        for i in np.flatnonzero(live):
            cv2.fillConvexPoly(frame, pts[i], tuple(int(v) for v in colours[i]),
                               lineType=cv2.LINE_AA, shift=4)
        return frame
