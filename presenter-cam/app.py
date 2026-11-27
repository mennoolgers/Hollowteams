"""Presenter Cam: the small control window.

Shows a live preview, lets you choose your camera, has one big Start / Stop
button for sending the picture to OBS Virtual Camera, and a button per effect.
"""
import os
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

# The app asks macOS for camera permission itself (OpenCV cannot from a background thread).
os.environ.setdefault("OPENCV_AVFOUNDATION_SKIP_AUTH", "1")

import cameras  # noqa: E402
from engine import Engine  # noqa: E402
from settings import load_config, load_state, save_state  # noqa: E402
from web import start_server  # noqa: E402
from chat_reader import ZoomChatReader  # noqa: E402

PREVIEW_W, PREVIEW_H = 512, 288
PREVIEW_EVERY_MS = 66   # the preview refreshes ~15 times a second; the output stays at 30


class FlatButton(tk.Label):
    """A coloured button. (Normal Mac buttons ignore custom colours.)"""

    def __init__(self, master, text, command, bg, fg, size=15, **kw):
        super().__init__(master, text=text, bg=bg, fg=fg, cursor="hand2",
                         padx=18, pady=10, font=("Helvetica", size, "bold"), **kw)
        self.bind("<Button-1>", lambda _e: command())

    def restyle(self, text, bg, fg=None):
        if (self.cget("text"), self.cget("bg"), fg or self.cget("fg")) != (text, bg, fg or self.cget("fg")):
            self.configure(text=text, bg=bg, fg=fg or self.cget("fg"))


class App:
    def __init__(self):
        self.config = load_config()
        self.state = load_state()
        c = self.config["colours"]
        self.c = c

        self.root = tk.Tk()
        self.root.title("Presenter Cam")
        self.root.configure(bg=c["deep"])
        self.root.resizable(False, False)

        header = tk.Label(self.root, text="Presenter Cam", bg=c["primary"], fg=c["text"],
                          font=("Helvetica", 17, "bold"), anchor="w", padx=14, pady=8)
        header.pack(fill="x")

        self._photo = ImageTk.PhotoImage(Image.new("RGB", (PREVIEW_W, PREVIEW_H)))
        self.preview = tk.Label(self.root, image=self._photo, bg="black", borderwidth=0)
        self.preview.pack(padx=12, pady=(12, 8))

        row = tk.Frame(self.root, bg=c["deep"])
        row.pack(fill="x", padx=12)
        tk.Label(row, text="Camera", bg=c["deep"], fg=c["text"],
                 font=("Helvetica", 13)).pack(side="left")
        self.camera_box = ttk.Combobox(row, state="readonly", width=34)
        self.camera_box.pack(side="left", padx=8)
        self.camera_box.bind("<<ComboboxSelected>>", lambda _e: self.choose_camera())
        tk.Button(row, text="Refresh", command=self.refresh_cameras).pack(side="left")

        self.start_button = FlatButton(self.root, "Start camera output", self.toggle_output,
                                       bg=c["accent"], fg=c["deep"])
        self.start_button.pack(fill="x", padx=12, pady=10)

        self.status = tk.Label(self.root, text="", bg=c["deep"], fg=c["text"], anchor="w",
                               justify="left", wraplength=PREVIEW_W, font=("Helvetica", 12))
        self.status.pack(fill="x", padx=12, pady=(0, 6))

        self.engine = Engine(self.config)
        for err in self.engine.effects.load_errors:
            print(err)
        manager = self.engine.effects

        tk.Label(self.root, text="Effects", bg=c["deep"], fg=c["accent"], anchor="w",
                 font=("Helvetica", 13, "bold")).pack(fill="x", padx=12, pady=(4, 4))
        grid = tk.Frame(self.root, bg=c["deep"])
        grid.pack(fill="x", padx=12)
        self.effect_buttons = {}
        names = manager.button_order()
        for i, name in enumerate(names + ["clear"]):
            if name == "clear":
                button = FlatButton(grid, "Clear all", lambda: manager.command("clear"),
                                    bg="#E07A5F", fg=c["text"], size=13)
            else:
                button = FlatButton(grid, manager.effects[name].title,
                                    lambda n=name: manager.command(n), bg=c["primary"], fg=c["text"], size=13)
                self.effect_buttons[name] = button
            button.grid(row=i // 3, column=i % 3, sticky="ew", padx=3, pady=3)
        for col in range(3):
            grid.columnconfigure(col, weight=1, uniform="fx")

        self.slides = manager.effects.get("slides")
        if self.slides is not None:
            self._build_slide_controls(manager)

        port = self.config["server"]["port"]
        self.server, self.server_error = start_server(manager, port, self.config["colours"])
        tk.Label(self.root, text=f"Stream Deck / browser:  http://127.0.0.1:{port}/",
                 bg=c["deep"], fg=c["accent"], anchor="w",
                 font=("Helvetica", 12)).pack(fill="x", padx=12, pady=(8, 2))

        # Zoom chat -> poll answers.
        self.chat = None
        if self.config["chat"].get("zoom", True) and "poll" in manager.effects:
            self.chat = ZoomChatReader(
                lambda name, text: manager.command("poll", "chat", {"name": name, "text": text}))
            self.chat.start()
        self.chat_label = tk.Label(self.root, text="", bg=c["deep"], fg=c["accent"], anchor="w",
                                   font=("Helvetica", 12))
        self.chat_label.pack(fill="x", padx=12, pady=(0, 12))
        self.camera_list = []
        self.waiting_for_permission = False
        self.permission = cameras.camera_permission()
        if self.permission == "ask":
            cameras.request_camera_permission()
        self.refresh_cameras(select=self.state.get("camera_name"))
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.after(PREVIEW_EVERY_MS, self.tick)

    # ---- slides -----------------------------------------------------------
    def _build_slide_controls(self, manager):
        c, sl = self.c, self.slides
        saved = self.state.get("slides", {})
        box = tk.Frame(self.root, bg=c["deep"])
        box.pack(fill="x", padx=12, pady=(10, 0))
        tk.Label(box, text="Slides", bg=c["deep"], fg=c["accent"],
                 font=("Helvetica", 13, "bold")).grid(row=0, column=0, sticky="w")
        self.deck_box = ttk.Combobox(box, state="readonly", width=26,
                                     values=[d.name for d in sl.decks] or ["(no decks in slides folder)"])
        self.deck_box.grid(row=0, column=1, columnspan=2, sticky="w", padx=6)
        if sl.deck is not None:
            self.deck_box.set(saved.get("deck") if saved.get("deck") in [d.name for d in sl.decks] else sl.deck.name)
            if self.deck_box.get() != sl.deck.name:
                manager.command("slides", "deck", {"name": self.deck_box.get()})
        else:
            self.deck_box.current(0)
        self.deck_box.bind("<<ComboboxSelected>>", lambda _e: self._slide_option(
            "deck", self.deck_box.get(), action="deck", options={"name": self.deck_box.get()}))
        nav = tk.Frame(box, bg=c["deep"])
        nav.grid(row=0, column=3, sticky="e")
        FlatButton(nav, "\u2039 Back", lambda: manager.command("slides", "prev"), bg=c["primary"],
                   fg=c["text"], size=13).pack(side="left")
        self.slide_label = tk.Label(nav, text="", width=11, bg=c["deep"], fg=c["text"],
                                    font=("Helvetica", 12))
        self.slide_label.pack(side="left", padx=4)
        FlatButton(nav, "Next \u203A", lambda: manager.command("slides", "next"), bg=c["primary"],
                   fg=c["text"], size=13).pack(side="left")
        box.columnconfigure(3, weight=1)

        opts = tk.Frame(self.root, bg=c["deep"])
        opts.pack(fill="x", padx=12, pady=(6, 0))
        shapes = {"Auto shape": "auto", "Landscape": "landscape", "Portrait": "portrait"}
        anims = {"Slide in": "slide", "Fade": "fade"}
        self.shape_box = ttk.Combobox(opts, state="readonly", width=11, values=list(shapes))
        self.anim_box = ttk.Combobox(opts, state="readonly", width=8, values=list(anims))
        shape = saved.get("orientation", sl.opts["orientation"])
        anim = saved.get("animation", sl.opts["animation"])
        self.shape_box.set(next((k for k, v in shapes.items() if v == shape), "Auto shape"))
        self.anim_box.set(next((k for k, v in anims.items() if v == anim), "Slide in"))
        self.shape_box.bind("<<ComboboxSelected>>", lambda _e: self._slide_option(
            "orientation", shapes[self.shape_box.get()]))
        self.anim_box.bind("<<ComboboxSelected>>", lambda _e: self._slide_option(
            "animation", anims[self.anim_box.get()]))
        self.shape_box.pack(side="left")
        self.anim_box.pack(side="left", padx=6)
        self.slide_flags = {}
        for key, text in (("blur", "Blur camera"), ("tint", "Tint camera"), ("frame", "Frame")):
            var = tk.BooleanVar(value=saved.get(key, sl.opts[key]))
            tk.Checkbutton(opts, text=text, variable=var, bg=c["deep"], fg=c["text"],
                           activebackground=c["deep"], activeforeground=c["text"],
                           selectcolor=c["primary"], highlightthickness=0,
                           command=lambda k=key, v=var: self._slide_option(k, str(v.get()))
                           ).pack(side="left", padx=4)
            self.slide_flags[key] = var
        # Apply remembered choices.
        manager.command("slides", "configure", {
            "orientation": shape, "animation": anim,
            **{k: str(v.get()) for k, v in self.slide_flags.items()}})

    def _slide_option(self, key, value, action="configure", options=None):
        self.state.setdefault("slides", {})[key] = value
        save_state(self.state)
        self.engine.effects.command("slides", action, options or {key: value})

    # ---- camera choice ----------------------------------------------------
    def refresh_cameras(self, select=None):
        self.camera_list = cameras.list_cameras()
        self.camera_box["values"] = [name for _i, name in self.camera_list]
        names = [name for _i, name in self.camera_list]
        if select is None:
            # Prefer anything called Elgato, otherwise keep the current choice.
            select = next((n for n in names if "elgato" in n.lower()), self.camera_box.get() or None)
        if select in names:
            self.camera_box.current(names.index(select))
            self.choose_camera()

    def choose_camera(self):
        pos = self.camera_box.current()
        if pos < 0:
            return
        index, name = self.camera_list[pos]
        self.state["camera_name"] = name
        save_state(self.state)
        if index != cameras.TEST_PATTERN:
            self.permission = cameras.camera_permission()
            if self.permission != "granted":
                # Opening now would fail; tick() opens it as soon as you click Allow.
                self.waiting_for_permission = True
                self.engine.set_source(None)
                return
        self.waiting_for_permission = False
        self.engine.set_source(cameras.open_source(index, name, self.config["camera"],
                                                   self.config["output"]))

    # ---- output -----------------------------------------------------------
    def toggle_output(self):
        self.engine.want_output = not self.engine.want_output

    # ---- regular refresh --------------------------------------------------
    def tick(self):
        if self.waiting_for_permission:
            self.permission = cameras.camera_permission()
            if self.permission == "granted":
                self.choose_camera()
        frame = self.engine.preview
        if frame is not None:
            small = cv2.resize(frame, (PREVIEW_W, PREVIEW_H), interpolation=cv2.INTER_AREA)
            self._photo = ImageTk.PhotoImage(Image.fromarray(small))
            self.preview.configure(image=self._photo)

        e = self.engine
        if e.output_on:
            self.start_button.restyle("Stop camera output", "#E07A5F")
            line = "LIVE: sending to OBS Virtual Camera."
        else:
            self.start_button.restyle("Start camera output", self.c["accent"])
            line = "Not sending. Press Start, then pick OBS Virtual Camera in Zoom."
        line += f"   {e.actual_fps:4.1f} fps, {e.frame_ms:4.1f} ms per frame"
        problems = [p for p in (e.output_error, getattr(e.source, "error", None), self.server_error) if p]
        problems += [err.splitlines()[0] + " (details in the Terminal window)"
                     for err in e.effects.load_errors]
        if self.waiting_for_permission and self.permission == "ask":
            problems.append("Waiting for camera permission: click Allow in the macOS question.")
        elif self.waiting_for_permission:
            problems.append("Camera access is off. System Settings > Privacy & Security > Camera: "
                            "switch on Terminal, then close and restart this app.")
        if self.slides is not None and not self.slides.info().startswith("Slide"):
            problems.append(self.slides.info())
        if problems:
            line += "\n" + "\n".join(problems)
        self.status.configure(text=line)
        if self.chat is not None:
            self.chat_label.configure(text=f"Zoom chat:  {self.chat.status}")
        if self.slides is not None:
            info = self.slides.info()
            self.slide_label.configure(text=info.split("   ")[0][6:] if info.startswith("Slide") else "")
        for item in e.effects.status():
            button = self.effect_buttons.get(item["name"])
            if button is not None:
                on = item["on"]
                button.restyle(item["title"], self.c["accent"] if on else self.c["primary"],
                               self.c["deep"] if on else self.c["text"])
        self.root.after(PREVIEW_EVERY_MS, self.tick)

    def quit(self):
        if self.chat is not None:
            self.chat.stop()
        if self.server is not None:
            self.server.shutdown()
        self.engine.shutdown()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
