
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget

from visuals.controls.buttons import create_button
from visuals.controls.chips import create_chip
from visuals.controls.inputs import create_combo, create_line_edit
from visuals.effects.shadow import apply_shadow
from visuals.effects.polish import repolish
from visuals.widgets.primitives import make_separator


class ControlsPanel(QFrame):
    searchRequested = Signal(str)
    refreshRequested = Signal()
    repairRequested = Signal()
    loadDemoRequested = Signal()
    loadRecentRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        apply_shadow(self, blur=16.0, y_offset=6.0, alpha=12)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        heading = QLabel("Operator Controls", self)
        heading.setProperty("role", "section")
        layout.addWidget(heading)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        self.state_chip = create_chip("Ready", tone="good", icon="status", parent=self)
        self.scope_chip = create_chip("Live DB", tone="neutral", icon="workspace", parent=self)
        chip_row.addWidget(self.state_chip, 0)
        chip_row.addWidget(self.scope_chip, 0)
        chip_row.addStretch(1)
        layout.addLayout(chip_row)

        self.query_label = QLabel("Search", self)
        self.query_label.setProperty("role", "field")
        layout.addWidget(self.query_label)

        self.query_entry = create_line_edit("Search sessions, errors, tools, or summaries", parent=self)
        self.query_entry.returnPressed.connect(self._emit_search)
        layout.addWidget(self.query_entry)

        filters = QHBoxLayout()
        filters.setSpacing(8)
        layout.addLayout(filters)

        self.record_type_combo = create_combo(["Any", "json", "jsonl", "log", "md", "report", "txt"], parent=self)
        filters.addWidget(self.record_type_combo, 1)

        self.days_spin = QSpinBox(self)
        self.days_spin.setRange(3, 90)
        self.days_spin.setValue(14)
        self.days_spin.setSuffix(" days")
        filters.addWidget(self.days_spin, 0)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        layout.addLayout(action_row)
        action_row.addWidget(create_button("Search", "primary", self._emit_search, icon="search", parent=self), 1)
        action_row.addWidget(create_button("Refresh", "secondary", self.refreshRequested.emit, icon="refresh", parent=self), 1)

        action_row_two = QHBoxLayout()
        action_row_two.setSpacing(8)
        layout.addLayout(action_row_two)
        action_row_two.addWidget(create_button("Recent", "secondary", self.loadRecentRequested.emit, icon="overview", parent=self), 1)
        action_row_two.addWidget(create_button("Demo", "secondary", self.loadDemoRequested.emit, icon="spark", parent=self), 1)
        action_row_two.addWidget(create_button("Repair", "secondary", self.repairRequested.emit, icon="settings", parent=self), 1)

        layout.addWidget(make_separator())

        self.root_label = QLabel("Root: not resolved", self)
        self.root_label.setProperty("role", "hint")
        self.root_label.setWordWrap(True)
        layout.addWidget(self.root_label)

        self.db_label = QLabel("DB: not resolved", self)
        self.db_label.setProperty("role", "hint")
        self.db_label.setWordWrap(True)
        layout.addWidget(self.db_label)

        self.help_label = QLabel(
            "Ctrl+R refreshes metrics, Ctrl+L focuses search, Ctrl+Shift+C toggles charts, Ctrl+E runs repair, and Ctrl+D loads demo data.",
            self,
        )
        self.help_label.setProperty("role", "hint")
        self.help_label.setWordWrap(True)
        layout.addWidget(self.help_label)
        layout.addStretch(1)

    def _emit_search(self) -> None:
        self.searchRequested.emit(self.query_text())

    def query_text(self) -> str:
        return self.query_entry.text().strip()

    def record_type(self) -> str | None:
        value = self.record_type_combo.currentText().strip().lower()
        return None if value in {"", "any"} else value

    def days_window(self) -> int:
        return int(self.days_spin.value())

    def focus_query(self) -> None:
        self.query_entry.setFocus(Qt.FocusReason.ShortcutFocusReason)
        self.query_entry.selectAll()

    def set_runtime_info(self, *, root_path: str, db_path: str) -> None:
        self.root_label.setText(f"Root: {root_path}")
        self.db_label.setText(f"DB: {db_path}")

    def set_state(self, text: str, *, tone: str = "neutral") -> None:
        self.state_chip.setText(text)
        self.state_chip.setProperty("tone", tone)
        repolish(self.state_chip)
