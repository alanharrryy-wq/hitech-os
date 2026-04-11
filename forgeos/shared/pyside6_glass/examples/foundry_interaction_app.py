
from __future__ import annotations

from PySide6.QtWidgets import QApplication

from ..foundry_interaction import build_interaction_demo_app


def main() -> int:
    app = QApplication.instance() or QApplication([])
    widget = build_interaction_demo_app()
    widget.resize(1380, 900)
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
