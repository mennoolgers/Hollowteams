"""Presenter Cam: the small control window.

Shows a live preview, lets you choose your camera, and has one big
Start / Stop button for sending the picture to OBS Virtual Camera.
"""
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

import cameras
from engine import Engine
from settings import load_config, load_state, save_state

PREVIEW_W, PREVIEW_H = 512, 288
PREVIEW_EVERY_MS = 66   # the preview refreshes ~15 times a second; the output stays at 30


class FlatButton(tk.Label):
    """A coloured button. (Normal Mac buttons ignore custom colours.)"""

    def __init__(self, master, text, command, bg, fg, **kw):
        super().__init__(master, text=text, bg=bg, fg=fg, cursor="hand2",
                         padx=18, pady=10, font=("Helvetica", 15, "bold"), **kw)
        self.bind("<Button-1>", lambda _e: command())

    def restyle(self, text, bg):
        self.configure(text=text, bg=bg)


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

        tk.Label(self.root, text="Effects: coming in the next step", bg=c["deep"], fg=c["accent"],
                 anchor="w", font=("Helvetica", 12, "italic")).pack(fill="x", padx=12, pady=(0, 12))

        self.engine = Engine(self.config)
        self.camera_list = []
        self.refresh_cameras(select=self.state.get("camera_name"))
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.root.after(PREVIEW_EVERY_MS, self.tick)

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
        self.engine.set_source(cameras.open_source(index, name, self.config["camera"],
                                                   self.config["output"]))
        self.state["camera_name"] = name
        save_state(self.state)

    # ---- output -----------------------------------------------------------
    def toggle_output(self):
        self.engine.want_output = not self.engine.want_output

    # ---- regular refresh --------------------------------------------------
    def tick(self):
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
        problems = [p for p in (e.output_error, getattr(e.source, "error", None)) if p]
        if problems:
            line += "\n" + "\n".join(problems)
        self.status.configure(text=line)
        self.root.after(PREVIEW_EVERY_MS, self.tick)

    def quit(self):
        self.engine.shutdown()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    App().run()
