"""Slides beside you: your slide deck on the right, you on the left.

Put a PDF export of your deck (or a folder of PNG/JPG images) in the  slides  folder.

Web addresses (Stream Deck):
  /effect/slides                 show / hide
  /effect/slides/next            next slide        /effect/slides/prev   previous slide
  /effect/slides/first           back to slide 1   /effect/slides/go?n=5 jump to slide 5
  /effect/slides/landscape       /effect/slides/portrait     /effect/slides/auto
  /effect/slides/deck            switch to the next deck in the folder
"""
import re
import threading
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from fx import HERE, Effect, blend, blend_card, ease_out_cubic, to_array

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
SWAP = 0.35   # seconds for the cross-fade between two slides


def natural_key(path: Path):
    """Sort 'Slide2' before 'Slide10'."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", path.name)]


def list_decks(folder: Path) -> list:
    if not folder.is_dir():
        return []
    decks = []
    for p in sorted(folder.iterdir(), key=natural_key):
        if p.name.startswith("."):
            continue
        if p.suffix.lower() == ".pdf":
            decks.append(p)
        elif p.is_dir() and any(c.suffix.lower() in IMAGE_EXT for c in p.iterdir()):
            decks.append(p)
    if any(c.suffix.lower() in IMAGE_EXT for c in folder.iterdir()):
        decks.append(folder)          # loose images directly in the slides folder
    return decks


def load_pages(path: Path, long_edge: int) -> list:
    if path.is_file():
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(str(path))
        pages = []
        for i in range(len(pdf)):
            page = pdf[i]
            w, h = page.get_size()
            pages.append(page.render(scale=long_edge / max(w, h)).to_pil().convert("RGB"))
            page.close()
        pdf.close()
        return pages
    pages = []
    for f in sorted((c for c in path.iterdir() if c.suffix.lower() in IMAGE_EXT), key=natural_key):
        img = Image.open(f).convert("RGB")
        img.thumbnail((long_edge, long_edge), Image.LANCZOS)
        pages.append(img)
    return pages


def as_bool(value) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class Slides(Effect):
    title = "Slides"
    kind = "toggle"
    layer = 20   # above the warm glow, below logo / key word / timer

    def __init__(self, ctx, cfg):
        super().__init__(ctx, cfg)
        self.fade.seconds_in = self.cfg.get("fade_in", 0.7)
        self.fade.seconds_out = self.cfg.get("fade_out", 0.55)
        self.folder = HERE / self.cfg.get("folder", "slides")
        self.opts = {
            "orientation": self.cfg.get("orientation", "auto"),
            "animation": self.cfg.get("animation", "slide"),
            "frame": bool(self.cfg.get("frame", True)),
            "blur": bool(self.cfg.get("blur_camera", False)),
            "tint": bool(self.cfg.get("tint_camera", False)),
        }
        self.shade = float(self.cfg.get("shade", 0.8))
        self.camera_shift = float(self.cfg.get("camera_shift", 0.7))
        self.size = float(self.cfg.get("size", 0.6))
        self.dark = np.array(self.colours["deep"], np.float32) * 0.35   # near-black with a marine hint

        self.decks = list_decks(self.folder)
        wanted = self.cfg.get("deck") or ""
        self.deck = next((d for d in self.decks if d.name == wanted), self.decks[0] if self.decks else None)
        self.pages, self.sprites, self.index = [], {}, 0
        self.shown = self.previous = None          # (sprite, margin, w, h)
        self.swap_t = -1e9
        self.loading = False
        self.message = ""
        self._gen = 0
        self._lock = threading.Lock()
        self._shade_cache = {}
        self._full_shade = {}
        self._tint = np.empty((self.H, self.W, 3), np.uint8)
        self._tint[:] = self.colours["primary"]
        self._reload(load_deck=True)

    # ---- background work: reading the deck and preparing the cards ---------
    def _reload(self, load_deck=False):
        with self._lock:
            self._gen += 1
            gen = self._gen
            self.sprites = {}
        self.loading = True
        threading.Thread(target=self._work, args=(gen, load_deck), daemon=True).start()

    def _work(self, gen, load_deck):
        try:
            if load_deck:
                self.pages, self.index = [], 0
                if self.deck is None:
                    self.message = f"No slides yet: put a PDF in the '{self.folder.name}' folder."
                    return
                self.message = f"Loading {self.deck.name}..."
                pages = load_pages(self.deck, long_edge=int(self.W * 1.1))
                if gen != self._gen:
                    return
                self.pages = pages
                self.message = ""
            # Current slide first, then its neighbours, so Next is instant.
            order = sorted(range(len(self.pages)), key=lambda i: (abs(i - self.index), i < self.index))
            for i in order:
                if gen != self._gen:
                    return
                sprite = self._build(self.pages[i])
                with self._lock:
                    if gen == self._gen:
                        self.sprites[i] = sprite
        except Exception as exc:  # noqa: BLE001
            self.message = f"Could not read the slides: {exc}"
        finally:
            if gen == self._gen:
                self.loading = False

    def _card_size(self, page):
        pw, ph = page.size
        aspect = pw / ph
        orient = self.opts["orientation"]
        if orient not in ("landscape", "portrait"):
            orient = "portrait" if aspect < 1 else "landscape"
        if orient == "landscape":
            a = aspect if aspect >= 1 else 16 / 9
            w = self.W * self.size
            h = w / a
            if h > self.H * 0.84:
                h = self.H * 0.84
                w = h * a
        else:
            a = aspect if aspect < 1 else 3 / 4
            h = self.H * 0.86
            w = h * a
            if w > self.W * 0.46:
                w = self.W * 0.46
                h = w / a
        return int(w), int(h)

    def _build(self, page):
        """A finished card: slide cropped to shape, rounded corners, white frame, soft shadow."""
        w, h = self._card_size(page)
        frame_px = max(4, int(self.H * 0.008)) if self.opts["frame"] else 0
        radius = int(self.H * 0.028)
        iw, ih = w - 2 * frame_px, h - 2 * frame_px
        pw, ph = page.size
        target = iw / ih
        if pw / ph > target + 0.01:                    # too wide: trim the sides
            nw = int(ph * target)
            page = page.crop(((pw - nw) // 2, 0, (pw - nw) // 2 + nw, ph))
        elif pw / ph < target - 0.01:                  # too tall: trim top and bottom
            nh = int(pw / target)
            page = page.crop((0, (ph - nh) // 2, pw, (ph - nh) // 2 + nh))
        page = page.resize((iw, ih), Image.LANCZOS)

        m = int(self.H * 0.06)
        img = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
        shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((m, m + m // 4, m + w, m + h + m // 4), radius,
                                                 fill=(0, 0, 0, 130))
        img = Image.alpha_composite(img, shadow.filter(ImageFilter.GaussianBlur(m // 2)))
        if frame_px:
            ImageDraw.Draw(img).rounded_rectangle((m, m, m + w, m + h), radius, fill=(255, 255, 255, 255))
        mask = Image.new("L", (iw, ih), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, iw - 1, ih - 1), max(1, radius - frame_px), fill=255)
        img.paste(page, (m + frame_px, m + frame_px), mask)
        solid = (m + radius, m + radius, m + w - radius, m + h - radius)
        return to_array(img), m, w, h, solid

    # ---- controls -----------------------------------------------------------
    def _go(self, index, now):
        if not self.pages:
            return
        index = max(0, min(len(self.pages) - 1, index))
        if index != self.index:
            self.index = index
            self.previous, self.swap_t = self.shown, now
            if index not in self.sprites:      # make sure this one is prepared next
                self._reload()

    def handle(self, action, now, options):
        if action == "next":
            self._go(self.index + 1, now)
        elif action in ("prev", "previous", "back"):
            self._go(self.index - 1, now)
        elif action == "first":
            self._go(0, now)
        elif action == "last":
            self._go(len(self.pages) - 1, now)
        elif action == "go":
            self._go(int(options.get("n", 1)) - 1, now)
        elif action in ("landscape", "portrait", "auto"):
            self.opts["orientation"] = action
            self._reload()
        elif action == "deck":
            self.decks = list_decks(self.folder)
            name = options.get("name")
            if name:
                self.deck = next((d for d in self.decks if d.name == name), self.deck)
            elif self.decks:
                pos = self.decks.index(self.deck) if self.deck in self.decks else -1
                self.deck = self.decks[(pos + 1) % len(self.decks)]
            self.shown = self.previous = None
            self._reload(load_deck=True)
        elif action == "configure":           # from the control window
            rebuild = False
            for key in ("frame", "blur", "tint"):
                if key in options:
                    rebuild |= key == "frame" and as_bool(options[key]) != self.opts["frame"]
                    self.opts[key] = as_bool(options[key])
            if options.get("animation") in ("slide", "fade"):
                self.opts["animation"] = options["animation"]
            if options.get("orientation") in ("landscape", "portrait", "auto") \
                    and options["orientation"] != self.opts["orientation"]:
                self.opts["orientation"], rebuild = options["orientation"], True
            if rebuild:
                self._reload()
        elif action in ("frame", "blur", "tint"):      # flip one option
            self.handle("configure", now, {action: str(not self.opts[action])})

    def info(self) -> str:
        if self.message:
            return self.message
        if not self.pages:
            return "Loading slides..." if self.loading else "No slides"
        return f"Slide {self.index + 1} / {len(self.pages)}   ({self.deck.name})"

    # ---- each frame -----------------------------------------------------------
    def _apply_shade(self, frame, card_left, level):
        """Darken towards the slide. When fully shown, a ready-made version is reused (fast)."""
        if level >= 0.998:
            key = ("full", card_left)
            if key not in self._full_shade:
                if len(self._full_shade) >= 4:
                    self._full_shade.clear()
                first, keep, add = self._shade(card_left, 1.0)
                h = self.H
                keep8 = np.ascontiguousarray(np.broadcast_to(
                    np.clip(keep.astype(np.int32) * 255 // 256, 0, 255).astype(np.uint8)[None, :, None],
                    (h, keep.shape[0], 3)))
                add8 = np.ascontiguousarray(np.broadcast_to(add.astype(np.uint8)[None], (h, add.shape[0], 3)))
                self._full_shade[key] = (first, keep8, add8)
            first, keep8, add8 = self._full_shade[key]
            region = np.ascontiguousarray(frame[:, first:])
            frame[:, first:] = cv2.add(cv2.multiply(region, keep8, scale=1 / 255), add8)
            return
        first, keep, add = self._shade(card_left, level)
        region = frame[:, first:]
        region[:] = ((region.astype(np.uint16) * keep[None, :, None] >> 8) + add[None]).astype(np.uint8)

    def _shade(self, card_left, level):
        """Darkening that grows from the middle of the picture towards the slide."""
        key = (card_left // 4, round(level * 40))
        if key not in self._shade_cache:
            if len(self._shade_cache) > 120:
                self._shade_cache.clear()
            x = np.arange(self.W, dtype=np.float32)
            start, end = card_left - self.W * 0.32, card_left + self.W * 0.05
            t = np.clip((x - start) / max(end - start, 1), 0, 1)
            a = (t * t * (3 - 2 * t)) * self.shade * (key[1] / 40)
            keep = np.round(256 * (1 - a)).astype(np.uint16)
            add = (a[:, None] * self.dark[None, :]).astype(np.uint16)
            first = int(np.argmax(a > 0.003)) if (a > 0.003).any() else self.W
            self._shade_cache[key] = (first, keep[first:], add[first:])
        return self._shade_cache[key]

    def render(self, frame, now):
        level = self.fade.value(now)
        with self._lock:
            current = self.sprites.get(self.index)
        if current is not None and current is not self.shown:
            if self.shown is not None and self.previous is None:
                self.previous, self.swap_t = self.shown, now
            self.shown = current
        card = self.shown or self.previous
        card_w = card[2] if card else int(self.W * self.size)
        right_margin = int(self.W * 0.035)
        card_left = self.W - right_margin - card_w

        # 1. Move the camera picture left, to make room.
        free_centre = card_left / 2
        shift = int(max(0.0, self.W / 2 - free_centre) * self.camera_shift * level)
        if shift > 0:
            moved = np.empty_like(frame)
            moved[:, :self.W - shift] = frame[:, shift:]
            moved[:, self.W - shift:] = frame[:, self.W - 1:self.W]
            frame = moved
        # 2. Optional soft blur and Marine Blue tint of the camera.
        if self.opts["blur"]:
            small = cv2.resize(frame, (self.W // 10, self.H // 10), interpolation=cv2.INTER_AREA)
            blurred = cv2.resize(cv2.GaussianBlur(small, (0, 0), 1.6), (self.W, self.H))
            frame = cv2.addWeighted(frame, 1 - level, blurred, level, 0)
        if self.opts["tint"]:
            frame = cv2.addWeighted(frame, 1 - 0.35 * level, self._tint, 0.35 * level, 0)
        # 3. Darken towards the slide, so it stands out.
        if self.shade > 0:
            self._apply_shade(frame, card_left, level)
        # 4. The slide itself (with a cross-fade when it changes).
        slide_in = self.opts["animation"] == "slide"
        p_in = ease_out_cubic(level) if slide_in else level
        offset = (1 - p_in) * (card_w * 0.45 + 80) if slide_in else 0
        opacity = min(1.0, level * 1.5) if slide_in else level
        swap = (now - self.swap_t) / SWAP
        if self.previous is not None and swap < 1 and self.shown is not None:
            self._draw(frame, self.previous, offset, opacity)
            self._draw(frame, self.shown, offset, opacity * ease_out_cubic(swap))
        else:
            self.previous = None
            if card is not None:
                self._draw(frame, card, offset, opacity)
        return frame

    def _draw(self, frame, card, offset, opacity):
        sprite, m, w, h, solid = card
        x = self.W - int(self.W * 0.035) - w - m + offset
        y = (self.H - h) // 2 - m
        if opacity >= 0.998:
            blend_card(frame, sprite, x, y, solid)
        else:
            blend(frame, sprite, x, y, opacity)
