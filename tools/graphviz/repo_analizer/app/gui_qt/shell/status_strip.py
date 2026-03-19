from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QProgressBar, QStatusBar

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class StatusStripBuilder:
    """Build the shell status strip and expose stable status widgets."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window

    def build(self) -> None:
        status = QStatusBar(self.main)
        status.setObjectName('statusStripSurface')
        status.setProperty('visualRole', 'status-surface')
        status.setProperty('visualTier', 'themed')
        status.setSizeGripEnabled(False)

        self.main.progress_bar = QProgressBar(self.main)
        self.main.progress_bar.setObjectName('statusProgressSurface')
        self.main.progress_bar.setProperty('visualRole', 'status-surface')
        self.main.progress_bar.setProperty('visualTier', 'themed')
        self.main.progress_bar.setFixedWidth(196)
        self.main.progress_bar.setTextVisible(False)
        self.main.progress_bar.hide()
        status.addPermanentWidget(self.main.progress_bar)

        self.main.status_scope_label = QLabel("scope: repo completo", self.main)
        self.main.status_scope_label.setObjectName('statusScopeSurface')
        self.main.status_scope_label.setProperty('visualRole', 'status-surface')
        self.main.status_scope_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_scope_label)

        self.main.status_summary = QLabel("0 archivos", self.main)
        self.main.status_summary.setObjectName('statusSummarySurface')
        self.main.status_summary.setProperty('visualRole', 'status-surface')
        self.main.status_summary.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_summary)

        status.showMessage("Ready. Workstation initialized.", 2200)
        self.main.setStatusBar(status)
