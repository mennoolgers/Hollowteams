"""Zoom chat probe (Mac only).

Writes down how the Zoom window is built (its buttons, texts and panels), so the
chat reader can be made to find the chat messages. Nothing is sent anywhere: the
result is a text file in this folder, zoom_chat_probe.txt, which you can read first.

Use it in a TEST meeting: open Zoom's chat panel, type a few messages such as
"yes" and "nee" (from a second device if you can), then run run_zoom_probe.command.
"""
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "zoom_chat_probe.txt"
ATTRS = ("AXRole", "AXSubrole", "AXRoleDescription", "AXTitle", "AXValue", "AXDescription",
         "AXIdentifier", "AXHelp", "AXPlaceholderValue")
MAX_NODES, MAX_DEPTH = 25000, 45


def main() -> int:
    if sys.platform != "darwin":
        print("This probe only works on a Mac.")
        return 1
    try:
        from AppKit import NSWorkspace
        from ApplicationServices import (AXIsProcessTrustedWithOptions, AXUIElementCopyAttributeValue,
                                         AXUIElementCreateApplication, kAXTrustedCheckOptionPrompt)
    except ImportError:
        print("A helper is missing. Close this window, double-click setup_mac.command, then try again.")
        return 1

    if not AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: True}):
        print("\nmacOS needs your OK first:")
        print("  System Settings > Privacy & Security > Accessibility > switch on Terminal.")
        print("Then close this window and run the probe again.")
        return 1

    zoom = [a for a in NSWorkspace.sharedWorkspace().runningApplications()
            if str(a.bundleIdentifier() or "").startswith("us.zoom")]
    if not zoom:
        print("Zoom is not running. Start a test meeting, open the chat panel, then run this again.")
        return 1

    def get(el, name):
        err, value = AXUIElementCopyAttributeValue(el, name, None)
        return value if err == 0 else None

    lines, count = [], 0

    def walk(el, depth):
        nonlocal count
        if count >= MAX_NODES or depth > MAX_DEPTH:
            return
        count += 1
        parts = []
        for name in ATTRS:
            value = get(el, name)
            if value is None or value == "":
                continue
            text = str(value).replace("\n", "\\n")
            if len(text) > 160:
                text = text[:160] + "..."
            parts.append(f"{name[2:]}={text!r}")
        lines.append("  " * depth + " ".join(parts))
        for child in get(el, "AXChildren") or []:
            walk(child, depth + 1)

    for app in zoom:
        root = AXUIElementCreateApplication(app.processIdentifier())
        lines.append(f"### {app.localizedName()} ({app.bundleIdentifier()}) pid={app.processIdentifier()}")
        for window in get(root, "AXWindows") or []:
            lines.append(f"## WINDOW title={get(window, 'AXTitle')!r}")
            walk(window, 1)

    OUT.write_text(
        f"Zoom chat probe, {time.strftime('%Y-%m-%d %H:%M')}, {count} items\n\n" + "\n".join(lines),
        encoding="utf-8")
    print(f"\nDone: {count} items written to\n  {OUT}")
    print("Open it in TextEdit if you like, then send it to your developer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
