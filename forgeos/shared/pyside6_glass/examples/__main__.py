from __future__ import annotations

import argparse
import os


def _run_catalog() -> int:
    from .demo_app import run

    return run()


def _run_integration() -> int:
    from .integration_demo import run_demo

    return run_demo()


def _run_catalog_smoke() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from .compositions import GlassExampleCatalog

    app = QApplication.instance() or QApplication([])
    widget = GlassExampleCatalog()
    widget.deleteLater()
    app.quit()
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pyside6_glass examples.")
    parser.add_argument(
        "--mode",
        choices=("catalog", "integration", "smoke"),
        default="catalog",
        help="Example mode: catalog UI, integration CLI demo, or offscreen smoke.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.mode == "integration":
        return _run_integration()
    if args.mode == "smoke":
        return _run_catalog_smoke()
    return _run_catalog()


if __name__ == "__main__":
    raise SystemExit(main())
