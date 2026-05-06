from __future__ import annotations

import json

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QHBoxLayout,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    Signal = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if Signal is not None:

    class DetailPanel(QWidget):
        export_requested = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            button_row = QHBoxLayout()
            self.export_button = QPushButton("Export Session")
            self.export_button.setEnabled(False)
            button_row.addStretch(1)
            button_row.addWidget(self.export_button)

            self.body = QTextEdit()
            self.body.setReadOnly(True)
            self._session_id: str | None = None

            layout.addLayout(button_row)
            layout.addWidget(self.body)

            self.export_button.clicked.connect(self._emit_export)

        def set_detail(self, payload: dict) -> None:
            session = payload.get("session") or {}
            self._session_id = session.get("session_id")
            self.export_button.setEnabled(bool(self._session_id))
            formatted = json.dumps(payload, indent=2, ensure_ascii=False)
            self.body.setPlainText(formatted)

        def clear(self) -> None:
            self._session_id = None
            self.export_button.setEnabled(False)
            self.body.setPlainText("")

        def current_session_id(self) -> str | None:
            return self._session_id

        def _emit_export(self) -> None:
            if self._session_id:
                self.export_requested.emit(self._session_id)
else:

    class DetailPanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for DetailPanel") from _IMPORT_ERROR
