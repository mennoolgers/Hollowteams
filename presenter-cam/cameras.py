"""Finding cameras and reading frames from them.

Each camera is read in its own background thread, so a slow camera can never
make the output stutter: the engine always takes the most recent frame.
"""
import sys
import threading
import time

import cv2
import numpy as np

IS_MAC = sys.platform == "darwin"
TEST_PATTERN = -1  # special "camera" number for the built-in test pattern

# Cameras that are really outputs: picking these as input would show the app inside itself.
_SKIP_WORDS = ("obs virtual camera",)


def _mac_camera_names() -> list:
    """Camera names in the same order OpenCV numbers them on a Mac."""
    try:
        import AVFoundation  # from pyobjc-framework-AVFoundation
    except ImportError:
        return []
    devices = AVFoundation.AVCaptureDevice.devicesWithMediaType_(AVFoundation.AVMediaTypeVideo) or []
    # OpenCV sorts by the device's unique ID, so we do the same to keep numbers in step.
    devices = sorted(devices, key=lambda d: str(d.uniqueID()))
    return [str(d.localizedName()) for d in devices]


_permission_handler = None  # kept alive until macOS answers


def camera_permission() -> str:
    """'granted', 'denied' or 'ask' (not decided yet). Always 'granted' off the Mac."""
    if not IS_MAC:
        return "granted"
    try:
        import AVFoundation
    except ImportError:
        return "granted"  # cannot check; let OpenCV try
    status = AVFoundation.AVCaptureDevice.authorizationStatusForMediaType_(AVFoundation.AVMediaTypeVideo)
    return {0: "ask", 3: "granted"}.get(int(status), "denied")


def request_camera_permission() -> None:
    """Show macOS's 'allow camera access' question. Must be called from the main thread."""
    global _permission_handler
    if not IS_MAC:
        return
    try:
        import AVFoundation
    except ImportError:
        return
    _permission_handler = lambda granted: None  # noqa: E731 - we poll the status instead
    AVFoundation.AVCaptureDevice.requestAccessForMediaType_completionHandler_(
        AVFoundation.AVMediaTypeVideo, _permission_handler)


def list_cameras() -> list:
    """Return [(number, name), ...] for the camera picker, test pattern first."""
    found = [(TEST_PATTERN, "Test pattern (no camera)")]
    names = _mac_camera_names() if IS_MAC else []
    if names:
        for index, name in enumerate(names):
            if not any(word in name.lower() for word in _SKIP_WORDS):
                found.append((index, name))
    else:
        # No names available: offer the first few numbers; the preview shows which is which.
        found += [(i, f"Camera {i}") for i in range(4)]
    return found


class TestPatternSource:
    """A calm moving pattern, handy for testing without a webcam."""

    def __init__(self, width=1280, height=720):
        x = np.linspace(0, 1, width, dtype=np.float32)[None, :]
        y = np.linspace(0, 1, height, dtype=np.float32)[:, None]
        base = np.dstack([0.55 + 0.35 * (1 - x) * (1 - y), 0.3 + 0.3 * y + 0 * x, 0.15 + 0.3 * x + 0 * y])
        self._base = (np.clip(base, 0, 1) * 255).astype(np.uint8)  # stored as BGR
        self._start = time.perf_counter()
        self.error = None
        self.name = "Test pattern"

    def latest(self):
        t = time.perf_counter() - self._start
        frame = self._base.copy()
        h, w = frame.shape[:2]
        cx = int(w / 2 + (w / 2 - 120) * np.sin(t * 0.8))
        cv2.circle(frame, (cx, h // 2), 90, (240, 235, 230), -1, lineType=cv2.LINE_AA)
        return frame

    def stop(self):
        pass


class CameraSource(threading.Thread):
    """Reads a real webcam in the background and keeps only the newest frame."""

    def __init__(self, index: int, name: str, width: int, height: int, fps: int):
        super().__init__(daemon=True)
        self.index, self.name = index, name
        self._want = (width, height, fps)
        self._frame = None
        self._lock = threading.Lock()
        self._running = True
        self.error = None
        self.start()

    def run(self):
        backend = cv2.CAP_AVFOUNDATION if IS_MAC else cv2.CAP_ANY
        cap = cv2.VideoCapture(self.index, backend)
        if not cap.isOpened():
            self.error = ("Could not open this camera. On a Mac: System Settings > Privacy & "
                          "Security > Camera, switch on Terminal, then restart the app.")
            return
        width, height, fps = self._want
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)
        failures = 0
        while self._running:
            ok, frame = cap.read()
            if ok and frame is not None:
                failures = 0
                with self._lock:
                    self._frame = frame
            else:
                failures += 1
                if failures > 100:
                    self.error = "The camera stopped sending pictures. Is it unplugged or used elsewhere?"
                time.sleep(0.01)
        cap.release()

    def latest(self):
        with self._lock:
            return self._frame

    def stop(self):
        self._running = False


def open_source(index: int, name: str, cam_cfg: dict, out_cfg: dict):
    if index == TEST_PATTERN:
        return TestPatternSource(out_cfg["width"], out_cfg["height"])
    return CameraSource(index, name, cam_cfg["width"], cam_cfg["height"], cam_cfg["fps"])
