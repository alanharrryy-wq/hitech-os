from __future__ import annotations

try:
    from PySide6.QtCore import Qt, Signal
    from PySide6.QtWidgets import (
        QHeaderView,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    Signal = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if Signal is not None:

    class ResultsPanel(QWidget):
        session_selected = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.table = QTableWidget(0, 6)
            self.table.setHorizontalHeaderLabels(["Session", "Timestamp", "Type", "Score", "Snippet", "Source"])
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.Stretch)
            header.setSectionResizeMode(5, QHeaderView.Stretch)
            self.table.setSelectionBehavior(QTableWidget.SelectRows)
            self.table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table.itemSelectionChanged.connect(self._emit_selection)

            layout.addWidget(self.table)
            self._rows: list[dict] = []

        def set_rows(self, rows: list[dict]) -> None:
            self._rows = list(rows)
            self.table.setRowCount(len(self._rows))
            for index, row in enumerate(self._rows):
                cells = [
                    str(row.get("session_id") or ""),
                    str(row.get("timestamp_utc") or ""),
                    str(row.get("record_type") or ""),
                    str(row.get("score") or ""),
                    str(row.get("snippet") or row.get("text") or ""),
                    str(row.get("source_path") or ""),
                ]
                for column, value in enumerate(cells):
                    item = QTableWidgetItem(value)
                    item.setData(Qt.UserRole, row)
                    self.table.setItem(index, column, item)
            if self._rows:
                self.table.selectRow(0)

        def _emit_selection(self) -> None:
            row_index = self.table.currentRow()
            if row_index < 0 or row_index >= len(self._rows):
                return
            session_id = str(self._rows[row_index].get("session_id") or "")
            if session_id:
                self.session_selected.emit(session_id)
else:

    class ResultsPanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for ResultsPanel") from _IMPORT_ERROR
