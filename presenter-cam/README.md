# Presenter Cam

My own lightweight presenter camera: Mac (Apple silicon). Elgato webcam in, calm animated overlays on top,
out through **OBS Virtual Camera** into Zoom, Teams and Meet. I never open OBS itself.

> Status: **Step 2**: six effects, a web address per effect, and Clear all. Stream Deck setup comes next.

## Updating to a new version

1. Save the new **presenter-cam ZIP** in your **Downloads** folder (do not unzip it).
2. Double-click **`update_mac.command`** in your presenter-cam folder.

It copies in the new version, **keeps your own files** (`config.yaml`, the `slides` folder, your
`assets/logo.png`, remembered choices), removes macOS's "downloaded from the internet" flag so
you are not asked to approve scripts again, and updates the helpers. New example settings land in
`config.example.yaml`, so you can copy anything new into your own `config.yaml`.

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

## Step 3: the Stream Deck

Every button uses the Stream Deck's **built-in "Website" action** with **"GET request in
background"** ticked. It calls the app's web address silently, no browser opens and no plugin
is needed. (BarRaider's API Ninja plugin is Windows-only, so it does not apply to a Mac.)

### Set up one button
1. Open the **Stream Deck** app on your Mac.
2. In the action list on the right, type **Website** in the search box (it sits under **System**).
3. Drag **Website** onto an empty key.
4. In the settings below the keys:
   * **URL:** paste the address from the table below, e.g. `http://127.0.0.1:8765/effect/confetti`
   * Tick **GET request in background**.
   * **Title:** leave it empty (the icon already has a label).
5. Click the **icon square** next to Title → **Set from File** → choose the matching PNG from the
   **`stream-deck-icons`** folder.
6. Repeat for each effect.

| Key | URL | Icon |
|---|---|---|
| Key word | `http://127.0.0.1:8765/effect/keyword` | `keyword.png` |
| Confetti | `http://127.0.0.1:8765/effect/confetti` | `confetti.png` |
| Countdown 5 min | `http://127.0.0.1:8765/effect/countdown` | `countdown.png` |
| Logo | `http://127.0.0.1:8765/effect/logo` | `logo.png` |
| Warm glow | `http://127.0.0.1:8765/effect/glow` | `glow.png` |
| Back in a moment | `http://127.0.0.1:8765/effect/brb` | `brb.png` |
| Clear all | `http://127.0.0.1:8765/clear` | `clear.png` |

Extra ideas: a "10 min" countdown key with `http://127.0.0.1:8765/effect/countdown?minutes=10`,
or a key that always shows one phrase: `http://127.0.0.1:8765/effect/keyword?text=Well%20done`.

Tip: put all keys in their own Stream Deck **profile** or **folder** called "Presenter Cam".

### If a key does nothing
1. Is the Presenter Cam app open? The addresses only work while it runs.
2. Paste the address into Safari. If the effect appears, the app is fine and the key's URL or
   checkbox needs another look.
3. The icons can be re-made in your colours: `.venv/bin/python tools/make_icons.py`

## Step 4: slides beside you

Show your slide deck on the right, with you on the left (the camera moves over a little and the
area behind the slide darkens so the slide stands out).

### Getting your deck in
1. **PowerPoint:** File → Export → File Format **PDF** → Export.
   (Keynote: File → Export To → PDF. Google Slides: File → Download → PDF.)
2. Put the PDF in the **`slides`** folder inside presenter-cam. Several decks are fine.
   A folder of images (Slide1.png, Slide2.png ...) also works.
3. Restart the app. Choose your deck in the **Slides** list in the window.

### In the window
* **Slides** button: show / hide.  **‹ Back** / **Next ›**: previous / next slide.
* **Auto shape / Landscape / Portrait:** Auto follows each slide's own shape. Landscape or
  Portrait force that shape; a slide of the other shape is cropped to fit.
* **Slide in / Fade:** how the slide appears.
* **Blur camera**, **Tint camera** (Marine Blue), **Frame** (thin white border).
The app remembers these choices. Fine-tuning (darkness, how far you move, slide size) is in
`config.yaml` under `slides:`.

### Stream Deck keys (Website action, "GET request in background" ticked)
| Key | URL | Icon |
|---|---|---|
| Slides on/off | `http://127.0.0.1:8765/effect/slides` | `slides.png` |
| Next slide | `http://127.0.0.1:8765/effect/slides/next` | `slide-next.png` |
| Previous slide | `http://127.0.0.1:8765/effect/slides/prev` | `slide-prev.png` |
| Back to slide 1 | `http://127.0.0.1:8765/effect/slides/first` | |
| Jump to slide 5 | `http://127.0.0.1:8765/effect/slides/go?n=5` | |
| Landscape / Portrait / Auto | `http://127.0.0.1:8765/effect/slides/landscape` (or `/portrait`, `/auto`) | |
| Next deck in the folder | `http://127.0.0.1:8765/effect/slides/deck` | |

Note: the slides are pictures of your deck, so animations and videos inside PowerPoint do not play.
After changing the deck, export the PDF again and choose it in the list (or restart the app).

## Step 5: Yes / No poll

A poll card at the bottom of the picture: the question in the middle, **Yes** on the left and
**No** on the right with live counts, the names of the latest voters, and a balance bar.
Each person counts once; if they change their answer, they move to the other side.

### Running a poll
* **Poll** button (or Stream Deck): starts the next question from `config.yaml`; press again to hide.
* People answer in the chat. The first word counts: *yes, ja, y, j, 👍* or *no, nee, n, 👎*
  (change the words under `poll:` in `config.yaml`).

| Key | URL | Icon |
|---|---|---|
| Poll on/off | `http://127.0.0.1:8765/effect/poll` | `poll.png` |
| Next question (votes cleared) | `http://127.0.0.1:8765/effect/poll/next` | `poll-next.png` |
| Clear the votes | `http://127.0.0.1:8765/effect/poll/reset` | |
| Your own question | `http://127.0.0.1:8765/effect/poll?text=Did%20you%20enjoy%20this%3F` | |
| Add a vote by hand | `http://127.0.0.1:8765/effect/poll/vote?name=Ana&answer=yes` | |

(`%20` is a space, `%3F` is a question mark.)

### Reading the Zoom chat
The app reads new messages from Zoom's chat panel on your Mac (the way a screen reader does).
Nothing leaves your Mac. The line **"Zoom chat:"** at the bottom of the window shows how it goes:

| It says | What to do |
|---|---|
| reading the chat | All good. |
| open the Chat panel in Zoom | Open Chat in the meeting (popped-out chat window also works). |
| Zoom is not running | Start or join the meeting. |
| allow Terminal under ... Accessibility | System Settings → Privacy & Security → Accessibility → switch on Terminal, restart the app. |

Good to know:
* Only messages sent **while the poll is showing** count. Older chat is ignored.
* Keep the chat panel open during the poll. While you **share your screen**, Zoom moves the chat to
  a floating window that may not be readable; test this once.
* Your own messages count too (handy for testing).
* Switch the reader off in `config.yaml`: `chat:` → `zoom: false`.
* If Zoom changes its layout in an update, run **`run_zoom_probe.command`** again and send the
  `zoom_chat_probe.txt` file to your developer.
