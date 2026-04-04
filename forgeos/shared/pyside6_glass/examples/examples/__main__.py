from __future__ import annotations

import argparse
import os


def _run_showcase() -> int:
    from .demo_app import run_showcase

    return run_showcase()


def _run_catalog() -> int:
    from .demo_app import run_catalog

    return run_catalog()


def _run_integration() -> int:
    from .integration_demo import run_demo

    return run_demo()


def _run_catalog_smoke() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from .demo_app import create_showcase_window

    app = QApplication.instance() or QApplication([])
    widget = create_showcase_window()
    widget.deleteLater()
    app.quit()
    return 0


def _run_proof() -> int:
    from ..ux_flight_recorder.runner import run_ux_release_proof

    summary = run_ux_release_proof(
        refresh_baseline=False,
        screenshots_enabled=False,
        headless=True,
    )
    print(summary.get("run_dir", ""))
    return 0 if bool(summary.get("passed", False)) else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pyside6_glass examples.")
    parser.add_argument(
        "--mode",
        choices=("showcase", "catalog", "integration", "smoke", "proof"),
        default="showcase",
        help="Example mode: new command-center showcase, legacy catalog, integration CLI demo, offscreen smoke, or headless UX proof.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.mode == "catalog":
        return _run_catalog()
    if args.mode == "integration":
        return _run_integration()
    if args.mode == "smoke":
        return _run_catalog_smoke()
    if args.mode == "proof":
        return _run_proof()
    return _run_showcase()


if __name__ == "__main__":
    raise SystemExit(main())
