"""
STEP 0 - Check that the virtual camera route works.

What it does:
  Sends a moving, colourful test pattern to "OBS Virtual Camera" for as long
  as it runs. Open Zoom / Teams / Meet, choose "OBS Virtual Camera" as your
  camera, and you should see the pattern moving smoothly.

How to stop it: press Ctrl+C in the window (or just close the window).

You do NOT need to open OBS Studio for this. OBS only has to be installed
(and, on a Mac, its virtual camera has to have been started once).
"""
import argparse
import sys
import time

import numpy as np
import cv2

WIDTH, HEIGHT, FPS = 1280, 720, 30


def make_frame(t: float, frame_no: int) -> np.ndarray:
    """Build one RGB frame of the test pattern for time t (seconds)."""
    # Soft diagonal colour gradient that slowly shifts over time.
    x = np.linspace(0, 1, WIDTH, dtype=np.float32)[None, :]
    y = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None]
    phase = t * 0.4
    r = 0.5 + 0.5 * np.sin(2 * np.pi * (x + phase))
    g = 0.5 + 0.5 * np.sin(2 * np.pi * (y + phase + 0.33))
    b = 0.5 + 0.5 * np.sin(2 * np.pi * (x + y + phase + 0.66))
    frame = (np.dstack([r + 0 * y, g + 0 * x, b]) * 200 + 30).astype(np.uint8)

    # A white ball bouncing left-right: if it moves smoothly, the route is smooth.
    cx = int(WIDTH / 2 + (WIDTH / 2 - 80) * np.sin(t * 1.5))
    cy = int(HEIGHT / 2 + 120 * np.sin(t * 3.0))
    cv2.circle(frame, (cx, cy), 60, (255, 255, 255), -1, lineType=cv2.LINE_AA)

    # Text so you can also check mirroring (should read normally to others).
    cv2.putText(frame, "PRESENTER CAM - STEP 0 TEST", (60, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 1.6, (255, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(frame, f"frame {frame_no}   {time.strftime('%H:%M:%S')}", (60, HEIGHT - 60),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    return frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Only draw frames and measure speed; do not open the virtual camera.")
    parser.add_argument("--seconds", type=float, default=0,
                        help="Stop after this many seconds (0 = run until Ctrl+C).")
    args = parser.parse_args()

    if args.dry_run:
        t0 = time.perf_counter()
        n = 60
        for i in range(n):
            make_frame(i / FPS, i)
        ms = (time.perf_counter() - t0) / n * 1000
        print(f"Dry run OK: {ms:.1f} ms per frame (budget is 33 ms).")
        return 0

    try:
        import pyvirtualcam
    except ImportError:
        print("pyvirtualcam is not installed. Run the setup script first.")
        return 1

    try:
        cam = pyvirtualcam.Camera(width=WIDTH, height=HEIGHT, fps=FPS, backend="obs")
    except Exception as exc:  # noqa: BLE001 - we want to show any problem plainly
        print("\nCould not open OBS Virtual Camera.")
        print(f"Reason: {exc}\n")
        print("Things to try:")
        print(" - Is OBS Studio 30 or newer installed?")
        print(" - Mac: open OBS once, click 'Start Virtual Camera', allow the system")
        print("   extension in System Settings > General > Login Items & Extensions")
        print("   (on macOS 26: Privacy & Security > Media Extensions), then")
        print("   click 'Stop Virtual Camera' and quit OBS. Then run this test again.")
        print(" - Windows: open OBS once, click 'Start Virtual Camera', then 'Stop', then quit OBS.")
        return 1

    with cam:
        print(f"Sending test pattern to: {cam.device}  ({WIDTH}x{HEIGHT} @ {FPS} fps)")
        print("Now pick 'OBS Virtual Camera' in Zoom / Teams / Meet. Press Ctrl+C to stop.\n")
        start = time.perf_counter()
        frame_no = 0
        worst_ms = 0.0
        last_report = start
        try:
            while True:
                t = time.perf_counter() - start
                f0 = time.perf_counter()
                frame = make_frame(t, frame_no)
                cam.send(frame)
                worst_ms = max(worst_ms, (time.perf_counter() - f0) * 1000)
                cam.sleep_until_next_frame()
                frame_no += 1
                now = time.perf_counter()
                if now - last_report >= 5:
                    print(f"  running: {cam.current_fps:4.1f} fps, slowest frame {worst_ms:.1f} ms")
                    worst_ms, last_report = 0.0, now
                if args.seconds and t >= args.seconds:
                    break
        except KeyboardInterrupt:
            pass
    print("Stopped. If you saw the moving pattern in Zoom, Step 0 passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
