#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.gui_qt.main_window import RepoAnalyzerMainWindow


def main() -> None:
    app = QApplication(sys.argv)
    QApplication.setApplicationName('RepoAnalyzerQt')
    QApplication.setOrganizationName('Hitech')
    window = RepoAnalyzerMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
