
from __future__ import annotations

from pathlib import Path

from synapse_x.config import Settings
from visuals.common.helpers import ensure_app

from .main_window import SynapseXMainWindow
from .runtime import hide_console_window, install_qt_warning_filter, maybe_relaunch_with_pythonw


def create_window(*, settings: Settings | None = None) -> SynapseXMainWindow:
    return SynapseXMainWindow(settings=settings)


def main() -> int:
    if maybe_relaunch_with_pythonw(Path(__file__).resolve().parents[3] / "run_ui.py"):
        return 0
    hide_console_window()
    install_qt_warning_filter()

    app = ensure_app()
    window = create_window()
    window.show()
    return app.exec()
