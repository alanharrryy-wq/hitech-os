from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .catalog_shell import GlassCatalogShell
from .catalog_builtin import register_builtin_catalog_entries
from .catalog_foundry_foundation_entries import iter_foundry_foundation_catalog_specs


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    register_builtin_catalog_entries(force=True)
    shell = GlassCatalogShell()
    shell.setWindowTitle("PySide6 Glass • Foundry Foundation")
    shell.resize(1480, 980)
    shell.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
