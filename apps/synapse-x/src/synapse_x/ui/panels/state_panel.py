from __future__ import annotations

try:
    from PySide6.QtWidgets import (
        QGridLayout,
        QLabel,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class StatePanel(QWidget):
        def __init__(self) -> None:
            super().__init__()
            layout = QGridLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)

            self.message = QLabel("Ready")
            self.db_path = QLabel("-")
            self.last_run = QLabel("-")
            self.counts = QLabel("-")

            layout.addWidget(QLabel("State"), 0, 0)
            layout.addWidget(self.message, 0, 1)
            layout.addWidget(QLabel("DB"), 1, 0)
            layout.addWidget(self.db_path, 1, 1)
            layout.addWidget(QLabel("Last Ingest"), 2, 0)
            layout.addWidget(self.last_run, 2, 1)
            layout.addWidget(QLabel("Counts"), 3, 0)
            layout.addWidget(self.counts, 3, 1)

        def set_message(self, value: str) -> None:
            self.message.setText(value)

        def set_status(self, payload: dict) -> None:
            self.db_path.setText(str(payload.get("db_path") or "-"))
            run = payload.get("last_ingest_run") or {}
            self.last_run.setText(
                f"#{run.get('run_id', '-')} {run.get('status', '-')} seen={run.get('files_seen', 0)} processed={run.get('files_processed', 0)}"
                if run
                else "-"
            )
            counts = payload.get("counts") or {}
            self.counts.setText(
                f"sessions={counts.get('sessions', 0)} records={counts.get('records', 0)} files={counts.get('files', 0)}"
            )
else:

    class StatePanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for StatePanel") from _IMPORT_ERROR
