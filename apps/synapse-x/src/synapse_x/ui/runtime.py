
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


_QT_PREV_HANDLER = None


def _should_suppress_console() -> bool:
    return os.environ.get("SYNAPSE_X_FORCE_CONSOLE", "").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }


def maybe_relaunch_with_pythonw(target_script: str | Path) -> bool:
    if os.name != "nt":
        return False
    if not _should_suppress_console():
        return False
    if os.environ.get("_SYNAPSE_X_UI_BOOT") == "1":
        return False
    if os.environ.get("QT_QPA_PLATFORM", "").strip().lower() == "offscreen":
        return False

    executable = Path(sys.executable)
    if executable.name.lower() == "pythonw.exe":
        return False
    pythonw = executable.with_name("pythonw.exe")
    if not pythonw.exists():
        return False

    env = os.environ.copy()
    env["_SYNAPSE_X_UI_BOOT"] = "1"
    args = [str(pythonw), str(Path(target_script).resolve()), *sys.argv[1:]]
    subprocess.Popen(args, cwd=str(Path(target_script).resolve().parent), env=env)
    return True


def hide_console_window() -> None:
    if os.name != "nt" or not _should_suppress_console():
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def install_qt_warning_filter() -> None:
    global _QT_PREV_HANDLER
    if _QT_PREV_HANDLER is not None:
        return

    from PySide6.QtCore import qInstallMessageHandler

    def _handler(msg_type, context, message):
        text = str(message or "")
        if "QFont::setPointSize" in text and "must be greater than 0" in text:
            return
        if callable(_QT_PREV_HANDLER):
            _QT_PREV_HANDLER(msg_type, context, message)

    _QT_PREV_HANDLER = qInstallMessageHandler(_handler)
