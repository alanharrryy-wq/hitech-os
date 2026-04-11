from __future__ import annotations

from PySide6.QtWidgets import QApplication

from ..foundry_studio_suite import build_foundry_studio_suite_window, register_builtin_foundry_studio_suite


def main() -> int:
    app = QApplication.instance() or QApplication([])
    register_builtin_foundry_studio_suite()
    window = build_foundry_studio_suite_window()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
