# Presenter Cam

My own lightweight presenter camera: Mac (Apple silicon). Elgato webcam in, calm animated overlays on top,
out through **OBS Virtual Camera** into Zoom, Teams and Meet. I never open OBS itself.

> Status: **Step 0** (checking that the camera route works). The full app comes next.

## Step 0: test the camera route

### One-time preparation
1. **Python 3.11 or newer** from <https://www.python.org/downloads/> (this is the only
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
