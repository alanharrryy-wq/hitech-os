from __future__ import annotations

from PySide6.QtWidgets import QLabel, QStatusBar

from deltaforge.domain.models import SessionWorkspace


class WorkstationStatusBar(QStatusBar):
    def __init__(self) -> None:
        super().__init__()
        self.root_label = QLabel("root: -")
        self.targets_label = QLabel("targets: 0")
        self.state_label = QLabel("state: empty")
        self.mode_label = QLabel("mode: mock")
        self.stale_label = QLabel("fresh")

        self.addPermanentWidget(self.root_label)
        self.addPermanentWidget(self.targets_label)
        self.addPermanentWidget(self.state_label)
        self.addPermanentWidget(self.mode_label)
        self.addPermanentWidget(self.stale_label)

    def update_from_session(self, session: SessionWorkspace | None) -> None:
        if session is None:
            self.root_label.setText("root: -")
            self.targets_label.setText("targets: 0")
            self.state_label.setText("state: empty")
            self.mode_label.setText("mode: mock")
            self.stale_label.setText("fresh")
            return

        root = session.scope.root_dir or "-"
        self.root_label.setText(f"root: {root}")
        self.targets_label.setText(f"targets: {session.scope.count}")
        self.state_label.setText(f"state: {session.state.value}")
        self.mode_label.setText(f"mode: {session.mode}")
        self.stale_label.setText("stale" if session.stale else "fresh")
