from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QLabel, QVBoxLayout

from visuals.common.helpers import ensure_app
from visuals.common.types import ActionSpec, ChipSpec, TemplateConsoleConfig
from visuals.screens.template_console import TemplateConsoleWindow
from visuals.widgets.primitives import make_placeholder


_QT_PREV_HANDLER = None


def _should_suppress_console() -> bool:
    return os.environ.get("PYSIDE6_GLASS_FORCE_CONSOLE", "").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }


def _maybe_relaunch_with_pythonw() -> bool:
    if os.name != "nt":
        return False
    if not _should_suppress_console():
        return False
    if os.environ.get("_PYSIDE6_GLASS_GUI_BOOT") == "1":
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
    env["_PYSIDE6_GLASS_GUI_BOOT"] = "1"
    target_script = str(Path(__file__).resolve())
    args = [str(pythonw), target_script, *sys.argv[1:]]
    subprocess.Popen(args, cwd=str(Path(__file__).resolve().parent), env=env)
    return True


def _hide_console_window() -> None:
    if os.name != "nt" or not _should_suppress_console():
        return
    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def _install_qt_warning_filter() -> None:
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


def _build_custom_main_slot() -> QFrame:
    frame = QFrame()
    frame.setProperty("card", "muted")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)

    title = QLabel("Live Output Slot")
    title.setProperty("role", "section")
    layout.addWidget(title, 0, Qt.AlignLeft)

    body = QLabel(
        "This is an injected widget. Replace it with charts, logs, terminal output, "
        "data grids, inspectors, or any project-specific panel."
    )
    body.setProperty("role", "hint")
    body.setWordWrap(True)
    layout.addWidget(body)
    layout.addWidget(
        make_placeholder(
            "Nested Placeholder",
            "Slot composition is fully modular. You can swap this block without touching the shell.",
            icon="output",
        )
    )
    return frame


def main() -> int:
    if _maybe_relaunch_with_pythonw():
        return 0
    _hide_console_window()
    _install_qt_warning_filter()

    app: QApplication = ensure_app()

    config = TemplateConsoleConfig(
        window_title="Template Console",
        theme_id="silver_frost_cyan",
        ui_scale="100",
        hero_eyebrow="Workspace",
        hero_title="Template Console",
        hero_subtitle=(
            "Reusable frameless glass console with configurable actions, "
            "panel order, optional icons, and content slots."
        ),
        hero_icon="workspace",
        hero_chips=[
            ChipSpec("Template", tone="accent", icon="spark"),
            ChipSpec("Neutral Demo", tone="neutral", icon="overview"),
        ],
        toolbar_actions=[
            ActionSpec("refresh", "Refresh", icon="refresh", variant="secondary"),
            ActionSpec("open_selector", "Workspace", icon="workspace", variant="secondary"),
            ActionSpec("open_progress", "Progress", icon="play", variant="primary"),
            ActionSpec("toggle_sidebar", "Sidebar", icon="panel", variant="secondary"),
        ],
        panel_order=("sidebar", "main", "aux"),
        show_sidebar=True,
        show_aux=True,
        footer_hint=(
            "Starter ready: reorder toolbar actions, toggle panels, replace slots, and switch themes."
        ),
    )

    window = TemplateConsoleWindow(config=config)
    window.set_slot_widget("main", _build_custom_main_slot())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
