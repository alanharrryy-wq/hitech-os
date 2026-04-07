
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from visuals.controls.chips import create_chip
from visuals.effects.shadow import apply_shadow

from ..widgets.empty_state import EmptyStateCard
from ..widgets.log_console import LogConsole


class ResultsPanel(QFrame):
    resultActivated = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "true")
        apply_shadow(self, blur=16.0, y_offset=6.0, alpha=12)
        self._rows: list[dict[str, Any]] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(8)
        layout.addLayout(header)

        title = QLabel("Results Deck", self)
        title.setProperty("role", "section")
        header.addWidget(title)

        header.addStretch(1)
        self.mode_chip = create_chip("Recent", tone="accent", icon="overview", parent=self)
        self.count_chip = create_chip("0 rows", tone="neutral", icon="status", parent=self)
        header.addWidget(self.mode_chip, 0)
        header.addWidget(self.count_chip, 0)

        self.summary_label = QLabel("Recent operational records and search results land here.", self)
        self.summary_label.setProperty("role", "hint")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        self.empty_state = EmptyStateCard(
            self,
            title="Results surface ready",
            subtitle="Run a search or load recent records to populate the deck.",
            icon="search",
            tone="neutral",
            badge_text="Standby",
        )
        self.empty_state.set_state(
            "Results surface ready",
            "Run a search or load recent records to populate the deck.",
            icon="search",
            tone="neutral",
            badge_text="Standby",
            points=(
                "Search uses the indexed engine surface instead of reparsing files live.",
                "Selecting a result hydrates the detail inspector with session context.",
            ),
        )
        layout.addWidget(self.empty_state)

        self.table = QTreeWidget(self)
        self.table.setHeaderLabels(["When", "Type", "Session", "Source"])
        self.table.setRootIsDecorated(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.table.setMinimumHeight(220)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.setVisible(False)
        layout.addWidget(self.table, 1)

        self.preview = LogConsole(self, title="Selected row preview")
        layout.addWidget(self.preview, 1)

    def clear_results(self, *, summary: str = "No results loaded.") -> None:
        self._rows = []
        self.table.clear()
        self.table.setVisible(False)
        self.empty_state.setVisible(True)
        self.summary_label.setText(summary)
        self.count_chip.setText("0 rows")
        self.preview.set_lines(["No row selected."])

    def set_results(self, rows: list[dict[str, Any]], *, summary: str, mode_label: str = "Results") -> None:
        self._rows = list(rows)
        self.table.clear()
        for row in self._rows:
            item = QTreeWidgetItem(
                [
                    str(row.get("timestamp_utc") or row.get("day") or ""),
                    str(row.get("record_type") or row.get("kind") or "record"),
                    str(row.get("session_id") or row.get("label") or ""),
                    str(row.get("source_path") or row.get("source_ref") or row.get("text") or ""),
                ]
            )
            item.setData(0, Qt.ItemDataRole.UserRole, row)
            self.table.addTopLevelItem(item)

        self.empty_state.setVisible(not bool(self._rows))
        self.table.setVisible(bool(self._rows))
        self.summary_label.setText(summary)
        self.mode_chip.setText(mode_label)
        self.count_chip.setText(f"{len(self._rows)} rows")
        if self._rows:
            self.table.setCurrentItem(self.table.topLevelItem(0))
            self.table.resizeColumnToContents(0)
            self.table.resizeColumnToContents(1)
        else:
            self.preview.set_lines(["No row selected."])

    def _on_selection_changed(self) -> None:
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].data(0, Qt.ItemDataRole.UserRole) or {}
        snippet = str(row.get("text") or row.get("summary") or row.get("headline") or "No preview available.")
        source = str(row.get("source_path") or row.get("source_ref") or "")
        lines = [snippet]
        if source:
            lines.append("")
            lines.append(f"Source: {source}")
        self.preview.set_lines(lines)
        self.resultActivated.emit(row)
