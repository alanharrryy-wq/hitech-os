from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .compositions import GlassExampleCatalog


def run() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = GlassExampleCatalog()
    window.setWindowTitle("PySide6 Glass Framework Demos")
    window.resize(1480, 940)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(run())
