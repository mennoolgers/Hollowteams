"""Reads new messages from Zoom's chat panel on a Mac, the way a screen reader does.

Needs: Terminal allowed under System Settings > Privacy & Security > Accessibility,
and the chat panel open in Zoom (inside the meeting window or popped out).

Only messages that arrive while the app runs are passed on; older ones are skipped.
Nothing leaves your Mac.
"""
import re
import sys
import threading
import time
from collections import Counter

MESSAGE_CELL = "ZMTextMessageCellView"
_NAME_SUFFIX = re.compile(r"\s+(to everyone|to you|\(privately\)|\(direct message\))$", re.I)


def clean_name(name: str) -> str:
    return _NAME_SUFFIX.sub("", " ".join(str(name).split())).strip() or "Guest"


def parse_rows(rows: list) -> list:
    """Turn row snapshots into (sender, group time, text).

    A row snapshot is {"time": "21:02" or None, "values": [texts in order]}.
    The first message of a group has a time and [sender, ..., message];
    follow-up messages only have [message] and belong to the sender above.
    """
    messages, sender, group_time = [], None, None
    for row in rows:
        if not row or not row["values"]:
            continue
        if row["time"] is not None and len(row["values"]) >= 2:
            sender, group_time = clean_name(row["values"][0]), row["time"]
        if sender is None:
            continue                     # the group's header scrolled out of view
        messages.append((sender, group_time, row["values"][-1]))
    return messages


class ZoomChatReader(threading.Thread):
    def __init__(self, on_message, interval: float = 0.6):
        super().__init__(daemon=True)
        self.on_message = on_message
        self.interval = interval
        self.status = "starting"
        self._running = True
        self._seen = set()
        self._primed = False
        self._table = None
        self._last_search = 0.0

    def stop(self):
        self._running = False

    # ---- macOS accessibility helpers ---------------------------------------
    def _setup(self):
        from AppKit import NSWorkspace
        from HIServices import (AXIsProcessTrusted, AXUIElementCopyAttributeValue,
                                AXUIElementCreateApplication)
        self._ws, self._trusted = NSWorkspace, AXIsProcessTrusted
        self._copy, self._app_el = AXUIElementCopyAttributeValue, AXUIElementCreateApplication

    def _get(self, el, name):
        err, value = self._copy(el, name, None)
        return value if err == 0 else None

    def _find_table(self):
        apps = [a for a in self._ws.sharedWorkspace().runningApplications()
                if str(a.bundleIdentifier() or "") == "us.zoom.xos"]
        if not apps:
            return None, "Zoom is not running"
        root = self._app_el(apps[0].processIdentifier())
        stack = [(w, 0) for w in self._get(root, "AXWindows") or []]
        while stack:
            el, depth = stack.pop()
            if self._get(el, "AXRole") == "AXTable":
                desc = str(self._get(el, "AXDescription") or "")
                if desc.lower().startswith("chat list") or self._has_messages(el):
                    return el, None
                continue
            if depth < 40:
                stack.extend((c, depth + 1) for c in self._get(el, "AXChildren") or [])
        return None, "open the Chat panel in Zoom"

    def _has_messages(self, table):
        for row in (self._get(table, "AXChildren") or [])[:6]:
            for cell in self._get(row, "AXChildren") or []:
                if self._get(cell, "AXIdentifier") == MESSAGE_CELL:
                    return True
        return False

    def _snapshot(self, table):
        rows = []
        children = self._get(table, "AXChildren")
        if children is None:
            return None                      # the table is gone (panel closed)
        for row in children:
            if self._get(row, "AXRole") != "AXRow":
                continue
            snap = None
            for cell in self._get(row, "AXChildren") or []:
                if self._get(cell, "AXIdentifier") != MESSAGE_CELL:
                    continue
                snap = {"time": None, "values": []}
                for part in self._get(cell, "AXChildren") or []:
                    role = self._get(part, "AXRole")
                    if role == "AXStaticText":
                        snap["time"] = str(self._get(part, "AXValue") or "")
                    elif role == "AXUnknown":
                        value = self._get(part, "AXValue")
                        if value not in (None, ""):
                            snap["values"].append(str(value))
                break
            rows.append(snap)
        return rows

    # ---- main loop ----------------------------------------------------------
    def _new_messages(self, messages):
        counts, keys = Counter(), []
        for m in messages:
            counts[m] += 1
            keys.append((m, counts[m]))
        fresh = [k[0] for k in keys if k not in self._seen]
        self._seen.update(keys)
        if not self._primed:                # first look: everything already there is old
            self._primed = True
            return []
        return fresh

    def run(self):
        if sys.platform != "darwin":
            self.status = "only available on a Mac"
            return
        try:
            self._setup()
        except ImportError:
            self.status = "helper missing: run setup_mac.command"
            return
        while self._running:
            try:
                if not self._trusted():
                    self.status = "allow Terminal under Privacy & Security > Accessibility"
                    time.sleep(2)
                    continue
                if self._table is None:
                    if time.time() - self._last_search < 2:
                        time.sleep(self.interval)
                        continue
                    self._last_search = time.time()
                    self._table, problem = self._find_table()
                    if self._table is None:
                        self.status = problem
                        continue
                rows = self._snapshot(self._table)
                if rows is None:
                    self._table = None
                    continue
                self.status = "reading the chat"
                for sender, _t, text in self._new_messages(parse_rows(rows)):
                    self.on_message(sender, text)
            except Exception as exc:  # noqa: BLE001 - keep reading, report the problem
                self.status = f"problem: {exc}"
                self._table = None
            time.sleep(self.interval)
