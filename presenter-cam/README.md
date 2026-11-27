# Presenter Cam

My own lightweight presenter camera: Mac (Apple silicon). Elgato webcam in, calm animated overlays on top,
out through **OBS Virtual Camera** into Zoom, Teams and Meet. I never open OBS itself.

> Status: **Step 2**: six effects, a web address per effect, and Clear all. Stream Deck setup comes next.

## Step 0: test the camera route

### One-time preparation
1. **Python 3.14** from <https://www.python.org/downloads/macos/> (3.11 to 3.14 work; 3.15 is
   not supported yet by the virtual camera library). This is the only
   thing installed system-wide, and you do it yourself).
2. **OBS Studio 30 or newer** from <https://obsproject.com>.
3. Wake up the OBS virtual camera driver once:
   open OBS → click **Start Virtual Camera** → allow anything your computer asks →
   click **Stop Virtual Camera** → quit OBS. You never need to open OBS again after this.
   - macOS asks you to allow a "system extension". Where to find it:
     macOS 14/15: System Settings → General → Login Items & Extensions;
     macOS 26: System Settings → Privacy & Security → Media Extensions.
4. Run the setup: double-click **`setup_mac.command`**. It creates a private `.venv`
   folder *inside this folder*; nothing else on your computer changes.
   - The first time, macOS may say the file "can't be opened because it is from an
     unidentified developer". Right-click (or Control-click) the file → **Open** → **Open**.
     You only do this once per file.

### The test
1. Double-click **`run_step0_mac.command`**. A Terminal window opens and shows progress.
2. Open Zoom → Settings → Video → Camera → **OBS Virtual Camera**.
   (If it isn't in the list, quit Zoom completely and open it again.)
3. **You should see:** a slowly shifting rainbow, a white ball gliding smoothly left
   and right, and the clock ticking. The window prints the frame rate every 5 seconds;
   it should say about 30 fps.
4. Press Control+C (or close the Terminal window) to stop.

If the ball glides smoothly, Step 0 passed.

## Step 1: the control window

1. Double-click **`setup_mac.command`** again (it adds a few new pieces). Do this whenever
   I tell you the requirements changed.
2. Double-click **`run_mac.command`**. The Presenter Cam window opens.
3. The first time, macOS asks: *"Terminal" would like to access the camera*. Click **Allow**.
   (The app runs inside Terminal, so Terminal is the name macOS shows.) If you missed it:
   System Settings → Privacy & Security → Camera → switch on **Terminal**, then restart the app.
4. Choose your camera in the **Camera** list. The app picks anything called "Elgato" by
   itself and remembers your choice next time. "Test pattern" works without any camera.
5. Press **Start camera output**, then pick **OBS Virtual Camera** in Zoom.
6. Close the window to quit.

The line under the button shows the frame rate (should be about 30 fps) and how long one frame
takes to build (must stay well under 33 ms).

### Changing settings
Open **`config.yaml`** in TextEdit, change a value, save, restart the app. It holds the
output size, the camera resolution and your colours (Marine Blue is the main one).

## Step 2: the effects

| Button | What it does | Web address |
|---|---|---|
| Key word | A word or phrase pops up beside you; each press shows the next one | `http://127.0.0.1:8765/effect/keyword` |
| Confetti | Confetti tumbles down for a few seconds | `http://127.0.0.1:8765/effect/confetti` |
| Countdown | Timer in the top-right corner; press again to stop | `http://127.0.0.1:8765/effect/countdown` |
| Logo | Your logo rests in a corner (on/off) | `http://127.0.0.1:8765/effect/logo` |
| Warm glow | A soft wash of warm light (on/off) | `http://127.0.0.1:8765/effect/glow` |
| Back in a moment | Calm full-screen card over a blurred camera (on/off) | `http://127.0.0.1:8765/effect/brb` |
| Clear all | Removes every effect | `http://127.0.0.1:8765/clear` |

Extras you can add to any address:
* `/on` or `/off` at the end switches an effect on or off for sure, e.g. `.../effect/brb/on`
* Countdown with a different length: `http://127.0.0.1:8765/effect/countdown?minutes=10`
* Key word with your own text: `http://127.0.0.1:8765/effect/keyword?text=Well%20done`
  (`%20` is a space)

**Try it:** with the app open, visit <http://127.0.0.1:8765/> in Safari. You get a page with a
button for each effect. The web addresses only work on your own Mac, and only while the app is open.

### Changing texts, colours and timings
Everything is in **`config.yaml`** under `effects:`: your key words, countdown minutes, the
"Back in a moment" text, glow colour and strength, confetti colours. Save and restart the app.

### Your own logo
Save your logo as a PNG with a transparent background and name it **`logo.png`** in the
**`assets`** folder. Until then a "Your logo" placeholder is shown. Change its size or corner in
`config.yaml` under `logo:`.

### Adding a new effect
1. Copy **`effects/_example.py`** and name the copy, for example, `effects/hello.py` (no underscore).
2. Change the `title` and what it draws. Restart the app.
3. It appears as a button and at `http://127.0.0.1:8765/effect/hello` automatically.
Settings for it go in `config.yaml` under `effects:` → `hello:`.
If an effect has a mistake, the app still starts; the status line tells you which effect failed.

### Fonts
The app uses **Inter** (free, SIL Open Font License; see `fonts/Inter-LICENSE.txt`).
