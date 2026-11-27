"""Finds every effect in the effects/ folder and runs the commands sent to them.

Commands can come from the control window, the local web address (Stream Deck)
or keyboard shortcuts. They are queued and carried out by the video thread at
the start of the next frame, so nothing ever collides.
"""
import importlib
import inspect
import pkgutil
import queue
import time
import traceback

import effects as effects_package
from fx import Effect


class EffectsManager:
    def __init__(self, ctx: dict, effect_settings: dict):
        self.effects = {}           # name -> effect object, e.g. "confetti" -> Confetti(...)
        self.load_errors = []
        self._commands = queue.Queue()
        for info in pkgutil.iter_modules(effects_package.__path__):
            if info.name.startswith("_"):
                continue            # files starting with _ are templates / helpers
            try:
                module = importlib.import_module(f"effects.{info.name}")
                classes = [c for _n, c in inspect.getmembers(module, inspect.isclass)
                           if issubclass(c, Effect) and c is not Effect and c.__module__ == module.__name__]
                if classes:
                    self.effects[info.name] = classes[0](ctx, (effect_settings or {}).get(info.name, {}))
            except Exception:  # noqa: BLE001 - one broken effect must not stop the app
                self.load_errors.append(f"Effect '{info.name}' could not load:\n{traceback.format_exc()}")
        self.order = sorted(self.effects, key=lambda n: (self.effects[n].layer, n))

    # ---- called from any thread -----------------------------------------
    def command(self, name: str, action: str = "press", options: dict = None) -> bool:
        """action: 'press', 'on' or 'off'. name 'clear' clears everything."""
        if name != "clear" and name not in self.effects:
            return False
        self._commands.put((name, action, options or {}))
        return True

    def status(self) -> list:
        return [{"name": n, "title": self.effects[n].title, "kind": self.effects[n].kind,
                 "on": bool(self.effects[n].is_on())} for n in self.button_order()]

    def button_order(self) -> list:
        preferred = ["slides", "keyword", "confetti", "countdown", "logo", "glow", "brb"]
        return [n for n in preferred if n in self.effects] + \
               sorted(n for n in self.effects if n not in preferred)

    # ---- called by the video thread ------------------------------------
    def apply_commands(self, now: float):
        while True:
            try:
                name, action, options = self._commands.get_nowait()
            except queue.Empty:
                return
            targets = self.effects.values() if name == "clear" else [self.effects[name]]
            for effect in targets:
                try:
                    if name == "clear" or action == "off":
                        effect.clear(now)
                    elif action == "on":
                        effect.set(True, now, options)
                    elif action == "press":
                        effect.press(now, options)
                    elif hasattr(effect, "handle"):      # extra actions, e.g. slides/next
                        effect.handle(action, now, options)
                except Exception:  # noqa: BLE001
                    traceback.print_exc()

    def any_active(self, now: float) -> bool:
        return any(e.active(now) for e in self.effects.values())

    def render(self, frame, now: float):
        for name in self.order:
            effect = self.effects[name]
            if effect.active(now):
                try:
                    frame = effect.render(frame, now)
                except Exception:  # noqa: BLE001 - a buggy effect switches itself off
                    traceback.print_exc()
                    effect.clear(now)
        return frame


def clock() -> float:
    return time.perf_counter()
