"""Yes / No poll: people answer in the chat, the results appear live on screen.

Web addresses (Stream Deck):
  /effect/poll                     start a poll (next question from config) / stop it
  /effect/poll?text=Your%20question  start with your own question
  /effect/poll/next                next question, votes cleared
  /effect/poll/reset               clear the votes
  /effect/poll/vote?name=Ana&answer=yes    add a vote by hand (also handy for testing)

Chat messages arrive through the 'chat' action (see chat_reader.py): the first word of a
message decides, e.g. "yes", "ja", "y", or "no", "nee", "n".
"""
import math
import re

import cv2
from PIL import Image, ImageDraw

from fx import (Effect, blend, ease_in_cubic, ease_out_cubic, font, mix, rgb,
                scale_sprite, soft_card, to_array)

ROWS = 4          # names shown per side


def initials(name: str) -> str:
    parts = [p for p in re.split(r"[\s._-]+", name) if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def tracked_text(draw, xy, text, fnt, fill, spacing, anchor="l"):
    """Text with extra space between letters (small caps labels)."""
    x, y = xy
    total = sum(fnt.getlength(ch) for ch in text) + spacing * (len(text) - 1)
    if anchor == "r":
        x -= total
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill, anchor="lm")
        x += fnt.getlength(ch) + spacing


class Poll(Effect):
    title = "Poll"
    kind = "toggle"
    layer = 70

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.fade.seconds_in = self.cfg.get("fade_in", 0.6)
        self.fade.seconds_out = self.cfg.get("fade_out", 0.5)
        self.questions = [str(q) for q in self.cfg.get("questions", ["Is this your first time here?"])]
        self.q_index = -1
        self.question = self.questions[0] if self.questions else ""
        self.prompt = str(self.cfg.get("prompt", "Type yes or no in the chat")).upper()
        self.yes_label = str(self.cfg.get("yes_label", "Yes")).upper()
        self.no_label = str(self.cfg.get("no_label", "No")).upper()
        self.yes_words = {w.lower() for w in self.cfg.get("yes_words", ["yes", "ja", "y", "j", "yep", "👍"])}
        self.no_words = {w.lower() for w in self.cfg.get("no_words", ["no", "nee", "n", "nope", "👎"])}
        self.yes_colour = rgb(self.cfg.get("yes_colour", "#3E9E64"))
        self.no_colour = rgb(self.cfg.get("no_colour", "#D64C45"))
        self.votes = {}            # name -> (answer, time)
        self.ratio = 0.5           # shown yes-share, eased towards the real one
        self.pop = {"yes": -1e9, "no": -1e9}
        self.last = None
        self._cache = {}
        H = self.H
        self.margin = int(H * 0.05)
        self.box_w, self.box_h = int(self.W * 0.195), int(H * 0.15)
        self.row_h, self.row_gap = int(H * 0.048), int(H * 0.0085)
        for side in ("yes", "no"):
            self._box(side, 0)
            self._row(side, "Warm up")
        self._centre(0)

    # ---- controls ---------------------------------------------------------
    def press(self, now, options):
        if self.fade.on:
            self.fade.set(False, now)
        else:
            self._start(now, options.get("text"))

    def set(self, on, now, options=None):
        if on and not self.fade.on:
            self._start(now, (options or {}).get("text"))
        elif not on:
            self.fade.set(False, now)

    def _start(self, now, text=None):
        if text:
            self.question = text
        elif self.questions:
            self.q_index = (self.q_index + 1) % len(self.questions)
            self.question = self.questions[self.q_index]
        self.votes.clear()
        self.ratio = 0.5
        self.fade.set(True, now)

    def handle(self, action, now, options):
        if action == "next":
            self._start(now, options.get("text"))
        elif action == "reset":
            self.votes.clear()
        elif action == "vote":
            self._vote(options.get("name", "Guest"), str(options.get("answer", "")).lower(), now)
        elif action == "chat":
            answer = self.parse(options.get("text", ""))
            if answer:
                self._vote(options.get("name", "Guest"), answer, now)

    def parse(self, text: str):
        words = re.findall(r"[\w']+|[^\w\s]", text.strip().lower())
        if not words:
            return None
        if words[0] in self.yes_words:
            return "yes"
        if words[0] in self.no_words:
            return "no"
        return None

    def _vote(self, name, answer, now):
        if not self.fade.on or answer not in ("yes", "no"):
            return
        name = " ".join(str(name).split())[:40] or "Guest"
        previous = self.votes.get(name)
        if previous and previous[0] == answer:
            return                      # same answer again: nothing changes
        self.votes[name] = (answer, now)
        self.pop[answer] = now

    # ---- drawing helpers (cached) -----------------------------------------
    def _blank(self, kind, colour, w, h, radius, blur, offset, sheen):
        """A shadowed card without text, made once (the soft shadow is the slow part)."""
        key = ("blank", kind, colour)
        if key not in self._cache:
            img, (ox, oy) = soft_card(w, h, (*colour, 245), radius=radius, shadow_blur=blur,
                                      shadow_offset=offset, shadow_opacity=0.35)
            if sheen:
                # Soft light from the top, fading out towards the middle.
                light = Image.new("L", img.size, 0)
                grad = Image.linear_gradient("L").resize((1, h)).point(lambda v: int((255 - v) * 0.12))
                light.paste(grad.resize((w, h)), (ox, oy))
                mask = Image.new("L", img.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle((ox, oy, ox + w, oy + h), radius, fill=255)
                from PIL import ImageChops
                white = Image.new("RGBA", img.size, (255, 255, 255, 0))
                white.putalpha(ImageChops.multiply(light, mask))
                img = Image.alpha_composite(img, white)
            self._cache[key] = (img, ox, oy)
        img, ox, oy = self._cache[key]
        return img.copy(), ox, oy

    def _cached(self, key, make):
        if key not in self._cache:
            if len(self._cache) > 300:
                self._cache = {k: v for k, v in self._cache.items() if k[0] == "blank"}
            self._cache[key] = make()
        return self._cache[key]

    def _box(self, side, count):
        def make():
            colour = self.yes_colour if side == "yes" else self.no_colour
            w, h = self.box_w, self.box_h
            img, ox, oy = self._blank(("box", side), colour, w, h, int(h * 0.16), 14, 6, sheen=True)
            d = ImageDraw.Draw(img)
            pad = int(h * 0.18)
            label_f, count_f = font(int(h * 0.24), "bold"), font(int(h * 0.48), "bold")
            label = self.yes_label if side == "yes" else self.no_label
            if side == "yes":
                d.text((ox + pad, oy + pad * 0.75), label, font=label_f, fill=(255, 255, 255), anchor="lt")
                d.text((ox + pad, oy + h - pad * 0.55), str(count), font=count_f, fill=(255, 255, 255), anchor="ls")
            else:
                d.text((ox + w - pad, oy + pad * 0.75), label, font=label_f, fill=(255, 255, 255), anchor="rt")
                d.text((ox + w - pad, oy + h - pad * 0.55), str(count), font=count_f, fill=(255, 255, 255), anchor="rs")
            return to_array(img)
        return self._cached(("box", side, count), make)

    def _row(self, side, name):
        def make():
            colour = self.yes_colour if side == "yes" else self.no_colour
            w, h = self.box_w, self.row_h
            img, ox, oy = self._blank(("row", side), colour, w, h, int(h * 0.22), 8, 3, sheen=False)
            d = ImageDraw.Draw(img)
            r = h * 0.34
            fnt, small = font(int(h * 0.5), "semibold"), font(int(h * 0.27), "bold")
            badge = mix(colour, (0, 0, 0), 0.22)
            cx = ox + h * 0.5 if side == "yes" else ox + w - h * 0.5
            d.ellipse((cx - r, oy + h / 2 - r, cx + r, oy + h / 2 + r), fill=badge)
            d.text((cx, oy + h / 2), initials(name), font=small, fill=(255, 255, 255), anchor="mm")
            room = w - h * 1.3
            text = name
            while fnt.getlength(text) > room and len(text) > 2:
                text = text[:-2] + "…"
            if side == "yes":
                d.text((ox + h * 0.98, oy + h / 2), text, font=fnt, fill=(255, 255, 255), anchor="lm")
            else:
                d.text((ox + w - h * 0.98, oy + h / 2), text, font=fnt, fill=(255, 255, 255), anchor="rm")
            return to_array(img)
        return self._cached(("row", side, name), make)

    def _centre(self, total):
        def make():
            w = self.W - 2 * (self.margin + self.box_w + int(self.H * 0.022))
            h = self.box_h
            img, ox, oy = self._blank("centre", mix(self.colours["deep"], (0, 0, 0), 0.45), w, h,
                                      int(h * 0.16), 14, 6, sheen=False)
            d = ImageDraw.Draw(img)
            pad = int(h * 0.2)
            small = font(int(h * 0.12), "semibold")
            grey = (190, 196, 206)
            tracked_text(d, (ox + pad, oy + pad * 0.95), self.prompt, small, grey, h * 0.025)
            answers = f"{total} ANSWER" + ("" if total == 1 else "S")
            tracked_text(d, (ox + w - pad, oy + pad * 0.95), answers, small, grey, h * 0.025, anchor="r")
            q = font(int(h * 0.28), "bold")
            text = self.question
            while q.getlength(text) > w - 2 * pad and len(text) > 3:
                text = text[:-2] + "…"
            d.text((ox + w / 2, oy + h * 0.52), text, font=q, fill=(255, 255, 255), anchor="mm")
            return to_array(img), ox, oy, w, h
        return self._cached(("centre", self.question, total), make)

    # ---- each frame -------------------------------------------------------
    def render(self, frame, now):
        level = self.fade.value(now)
        dt = 0 if self.last is None else min(max(now - self.last, 0), 0.1)
        self.last = now
        yes = [(n, t) for n, (a, t) in self.votes.items() if a == "yes"]
        no = [(n, t) for n, (a, t) in self.votes.items() if a == "no"]
        total = len(yes) + len(no)
        target = 0.5 if total == 0 else len(yes) / total
        self.ratio += (target - self.ratio) * (1 - math.exp(-dt * 6))

        rise = (1 - ease_out_cubic(level)) * self.H * 0.06 if self.fade.on else \
            ease_in_cubic(1 - level) * self.H * 0.04
        base_y = self.H - self.margin - self.box_h + rise

        # Count boxes with a small "pop" when the number changes.
        for side, items, x in (("yes", yes, self.margin), ("no", no, self.W - self.margin - self.box_w)):
            sprite = self._box(side, len(items))
            p = (now - self.pop[side]) / 0.35
            scale = 1 + 0.07 * math.sin(math.pi * p) if 0 <= p < 1 else 1.0
            spr = scale_sprite(sprite, scale)
            m = (sprite.shape[0] - self.box_h) // 2   # shadow margin around the card
            blend(frame, spr, x - m - (spr.shape[1] - sprite.shape[1]) / 2,
                  base_y - m - (spr.shape[0] - sprite.shape[0]) / 2, level)
            # Latest voters above the box, newest closest to it; they slide in from the edge.
            recent = sorted(items, key=lambda it: it[1])[-ROWS:]
            for i, (name, t) in enumerate(reversed(recent)):
                row = self._row(side, name)
                mr = (row.shape[0] - self.row_h) // 2
                y = base_y - (i + 1) * (self.row_h + self.row_gap) - self.row_gap
                age = ease_out_cubic((now - t) / 0.45)
                dx = (1 - age) * self.box_w * 0.25 * (-1 if side == "yes" else 1)
                blend(frame, row, x - mr + dx, y - mr, level * age)

        # Question card with the balance bar.
        sprite, ox, oy, w, h = self._centre(total)
        cx0 = (self.W - w) / 2
        blend(frame, sprite, cx0 - ox, base_y - oy, level)
        if level > 0.01:
            pad = int(h * 0.2)
            y = int(base_y + h * 0.83)
            x0, x1 = int(cx0 + pad), int(cx0 + w - pad)
            split = int(x0 + (x1 - x0) * self.ratio)
            thick = max(3, int(h * 0.05))
            green = self.yes_colour if total else (90, 96, 106)
            red = self.no_colour if total else (90, 96, 106)
            overlay = frame.copy() if level < 0.99 else frame
            cv2.line(overlay, (x0, y), (split, y), green, thick, cv2.LINE_AA)
            cv2.line(overlay, (split, y), (x1, y), red, thick, cv2.LINE_AA)
            cv2.circle(overlay, (split, y), int(thick * 1.6), (255, 255, 255), -1, cv2.LINE_AA)
            if overlay is not frame:
                cv2.addWeighted(overlay, level, frame, 1 - level, 0, dst=frame)
        return frame
