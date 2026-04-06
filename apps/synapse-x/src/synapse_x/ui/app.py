
from __future__ import annotations

import argparse
import os
from pathlib import Path

from synapse_x.config import Settings
from visuals.common.helpers import ensure_app

from .main_window import SynapseXMainWindow
from .runtime import hide_console_window, install_qt_warning_filter, maybe_relaunch_with_pythonw


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="synapse-x glass UI host")
    parser.add_argument("--root", default=None, help="Project root for data directories and SQLite storage")
    parser.add_argument("--demo", action="store_true", help="Boot directly into demo state")
    parser.add_argument("--show-console", action="store_true", help="Keep the console window visible on Windows")
    return parser


def create_window(*, settings: Settings | None = None, demo: bool = False) -> SynapseXMainWindow:
    return SynapseXMainWindow(settings=settings, boot_demo=demo)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.show_console:
        os.environ["SYNAPSE_X_FORCE_CONSOLE"] = "1"

    if maybe_relaunch_with_pythonw(Path(__file__).resolve().parents[3] / "run_ui.py"):
        return 0
    hide_console_window()
    install_qt_warning_filter()

    settings = Settings(root=Path(args.root).expanduser().resolve()) if args.root else None
    app = ensure_app()
    window = create_window(settings=settings, demo=bool(args.demo))
    window.show()
    return app.exec()
