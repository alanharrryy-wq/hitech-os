from __future__ import annotations

import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class NexusVisualModuleBase(QWidget):
    """
    Base visual module surface used by Nexus-hosted views.

    Keeps visual surface composition explicit and reusable inside Nexus
    without leaking business logic into the shared platform core.
    """

    def __init__(self, title: str, hint: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        self.title_label = QLabel(title, self)
        self.title_label.setProperty("role", "panel_title")
        self.hint_label = QLabel(hint, self)
        self.hint_label.setProperty("role", "panel_subtitle")
        self.hint_label.setWordWrap(True)

        column = QVBoxLayout()
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(2)
        column.addWidget(self.title_label)
        column.addWidget(self.hint_label)
        header.addLayout(column, 1)
        root.addLayout(header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        root.addLayout(self.content_layout, 1)


class NexusSummarySurface(NexusVisualModuleBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Nexus Runtime Overview",
            "Summary from neutral query contracts and workspace snapshots.",
            parent,
        )
        self.metrics_label = QLabel("No summary loaded.", self)
        self.metrics_label.setProperty("role", "subtitle")
        self.metrics_label.setWordWrap(True)
        self.preview = QTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Summary JSON payload")
        self.content_layout.addWidget(self.metrics_label)
        self.content_layout.addWidget(self.preview, 1)

    def update_summary(self, payload: dict[str, Any]) -> None:
        record_count = int(payload.get("record_count") or 0)
        approval_count = int(payload.get("approval_count") or 0)
        workspace_id = str(payload.get("workspace_id") or "(none)")
        self.metrics_label.setText(
            f"Workspace: {workspace_id} | Records: {record_count} | Approvals: {approval_count}"
        )
        self.preview.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))


class NexusRecordsSurface(NexusVisualModuleBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Records",
            "Operational records managed by Nexus runtime engine.",
            parent,
        )
        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(["Record", "Title", "Stage", "Owner", "Updated"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.detail = QTextEdit(self)
        self.detail.setReadOnly(True)
        self.detail.setPlaceholderText("Record detail will appear here.")
        self.content_layout.addWidget(self.table, 2)
        self.content_layout.addWidget(self.detail, 1)

    def update_records(self, rows: list[dict[str, Any]]) -> None:
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row.get("record_id") or ""),
                str(row.get("title") or ""),
                str(row.get("stage") or ""),
                str(row.get("owner") or ""),
                str(row.get("updated_at") or ""),
            ]
            for col_index, value in enumerate(values):
                self.table.setItem(row_index, col_index, QTableWidgetItem(value))
        if rows:
            self.table.selectRow(0)
            self.show_record_detail(rows[0])
        else:
            self.detail.setPlainText("No records available.")

    def selected_record_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        value = item.text().strip()
        return value or None

    def show_record_detail(self, payload: dict[str, Any]) -> None:
        self.detail.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))


class NexusApprovalsSurface(NexusVisualModuleBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Approvals",
            "Approval queue state for runtime actions.",
            parent,
        )
        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(["Record", "State", "Assignee", "Actor", "Updated"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.content_layout.addWidget(self.table, 1)

    def update_approvals(self, rows: list[dict[str, Any]]) -> None:
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            values = [
                str(row.get("record_id") or ""),
                str(row.get("state") or ""),
                str(row.get("assignee") or ""),
                str(row.get("last_actor") or ""),
                str(row.get("updated_at") or ""),
            ]
            for col_index, value in enumerate(values):
                self.table.setItem(row_index, col_index, QTableWidgetItem(value))
        if rows:
            self.table.selectRow(0)

    def selected_record_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None:
            return None
        value = item.text().strip()
        return value or None


class NexusTimelineSurface(NexusVisualModuleBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Timeline and Events",
            "Combined runtime timeline + integration event poll feedback.",
            parent,
        )
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("No timeline entries yet.")
        self.content_layout.addWidget(self.log, 1)

    def set_timeline_entries(self, entries: list[dict[str, Any]]) -> None:
        if not entries:
            self.log.setPlainText("No timeline entries yet.")
            return
        lines: list[str] = []
        for item in entries:
            lines.append(
                f"[{item.get('sequence', '?')}] {item.get('timestamp_utc', '')} "
                f"{item.get('event', '')} ({item.get('actor', '')})"
            )
            message = str(item.get("message") or "").strip()
            if message:
                lines.append(f"  {message}")
        self.log.setPlainText("\n".join(lines))
        self.log.moveCursor(self.log.textCursor().End)

    def append_integration_events(self, events: list[dict[str, Any]]) -> None:
        if not events:
            return
        cursor = self.log.textCursor()
        cursor.movePosition(cursor.End)
        for item in events:
            cursor.insertText(
                "\n"
                f"[integration:{item.get('sequence', '?')}] "
                f"{item.get('event', '')} topic={item.get('topic', '')}"
            )
        self.log.setTextCursor(cursor)
        self.log.moveCursor(self.log.textCursor().End)


class NexusHealthSurface(NexusVisualModuleBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            "Runtime Health",
            "Operational status projection from Nexus runtime.",
            parent,
        )
        self.preview = QTextEdit(self)
        self.preview.setReadOnly(True)
        self.preview.setPlaceholderText("Health payload will appear here.")
        self.content_layout.addWidget(self.preview, 1)

    def update_health(self, payload: dict[str, Any]) -> None:
        self.preview.setPlainText(json.dumps(payload, indent=2, ensure_ascii=True))

