"""The heart of the app: 30 times a second it takes the newest camera picture,
puts the effects on top, and sends the result to OBS Virtual Camera.

Everything that touches the virtual camera happens in this one background
thread, so the control window can never make the video stutter.
"""
import threading
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from effects_manager import EffectsManager
from settings import hex_to_rgb


def fit_cover(frame_bgr: np.ndarray, width: int, height: int) -> np.ndarray:
    """Crop to the output shape (no black bars, no stretching), resize, convert to RGB."""
    h, w = frame_bgr.shape[:2]
    target = width / height
    if abs(w / h - target) > 0.01:
        if w / h > target:            # too wide: trim the sides
            new_w = int(h * target)
            x0 = (w - new_w) // 2
            frame_bgr = frame_bgr[:, x0:x0 + new_w]
        else:                         # too tall: trim top and bottom
            new_h = int(w / target)
            y0 = (h - new_h) // 2
            frame_bgr = frame_bgr[y0:y0 + new_h]
    if frame_bgr.shape[1] != width:
        shrinking = frame_bgr.shape[1] > width
        frame_bgr = cv2.resize(frame_bgr, (width, height),
                               interpolation=cv2.INTER_AREA if shrinking else cv2.INTER_LINEAR)
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)


def load_font(size: int):
    """A clean system font; falls back to Pillow's built-in font."""
    for path in ("/System/Library/Fonts/SFNS.ttf",
                 "/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def waiting_card(width: int, height: int, colours: dict, message: str) -> np.ndarray:
    """A calm Marine Blue card shown when there is no camera picture yet."""
    top, bottom = np.array(hex_to_rgb(colours["primary"])), np.array(hex_to_rgb(colours["deep"]))
    ramp = np.linspace(0, 1, height)[:, None, None]
    img = (top * (1 - ramp) + bottom * ramp).astype(np.uint8).repeat(width, axis=1)
    pil = Image.fromarray(img)
    draw = ImageDraw.Draw(pil)
    font = load_font(int(height * 0.045))
    box = draw.textbbox((0, 0), message, font=font)
    draw.text(((width - (box[2] - box[0])) / 2, (height - (box[3] - box[1])) / 2), message,
              font=font, fill=hex_to_rgb(colours["text"]))
    return np.asarray(pil)


class Engine:
    def __init__(self, config: dict):
        out = config["output"]
        self.width, self.height, self.fps = out["width"], out["height"], out["fps"]
        self.colours = config["colours"]
        self.source = None
        self.want_output = False      # set by the Start/Stop button
        self.output_on = False        # what is really happening
        self.output_error = None
        self.preview = None           # newest finished frame (RGB) for the window
        self.frame_ms = 0.0           # average time to build one frame
        self.actual_fps = 0.0
        self._cards = {}
        self.effects = EffectsManager(
            {"width": self.width, "height": self.height, "fps": self.fps, "colours": self.colours},
            config.get("effects", {}))
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    # ---- called from the window -------------------------------------------
    def set_source(self, source):
        old, self.source = self.source, source
        if old is not None:
            old.stop()

    def shutdown(self):
        self._running = False
        self._thread.join(timeout=2)
        if self.source is not None:
            self.source.stop()

    # ---- internals -------------------------------------------------------
    def _card(self, message):
        if message not in self._cards:
            self._cards[message] = waiting_card(self.width, self.height, self.colours, message)
        return self._cards[message]

    def _build_frame(self, now: float) -> np.ndarray:
        src = self.source
        raw = src.latest() if src is not None else None
        self.effects.apply_commands(now)
        if raw is None:
            if src is not None and getattr(src, "error", None):
                frame = self._card("Camera problem: see the control window")
            else:
                frame = self._card("Waiting for camera..." if src else "No camera yet")
            if not self.effects.any_active(now):
                return frame
            frame = frame.copy()      # never paint on the stored card itself
        else:
            frame = fit_cover(raw, self.width, self.height)
        return self.effects.render(frame, now)

    def _loop(self):
        cam = None
        period = 1.0 / self.fps
        next_tick = time.perf_counter()
        avg_ms, count, fps_start = 0.0, 0, time.perf_counter()
        while self._running:
            # Open or close the virtual camera when the button asks for it.
            if self.want_output and cam is None:
                try:
                    import pyvirtualcam
                    cam = pyvirtualcam.Camera(self.width, self.height, self.fps, backend="obs")
                    self.output_error = None
                except Exception as exc:  # noqa: BLE001
                    self.output_error = (f"Could not start OBS Virtual Camera ({exc}). "
                                         "Run the Step 0 test for tips.")
                    self.want_output = False
            elif not self.want_output and cam is not None:
                cam.close()
                cam = None
            self.output_on = cam is not None

            t0 = time.perf_counter()
            frame = self._build_frame(t0)
            build_ms = (time.perf_counter() - t0) * 1000
            avg_ms = avg_ms * 0.95 + build_ms * 0.05
            self.frame_ms = avg_ms
            self.preview = frame

            if cam is not None:
                cam.send(frame)
                cam.sleep_until_next_frame()
            else:
                next_tick += period
                delay = next_tick - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_tick = time.perf_counter()

            count += 1
            elapsed = time.perf_counter() - fps_start
            if elapsed >= 1.0:
                self.actual_fps, count, fps_start = count / elapsed, 0, time.perf_counter()
        if cam is not None:
            cam.close()
