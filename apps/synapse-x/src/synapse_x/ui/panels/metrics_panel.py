from __future__ import annotations

import json

try:
    from PySide6.QtWidgets import QTextEdit, QVBoxLayout, QWidget
except Exception as exc:  # noqa: BLE001
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if _IMPORT_ERROR is None:

    class MetricsPanel(QWidget):
        def __init__(self) -> None:
            super().__init__()
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.body = QTextEdit()
            self.body.setReadOnly(True)
            layout.addWidget(self.body)

        def set_metrics(self, metrics: dict) -> None:
            self.body.setPlainText(json.dumps(metrics, indent=2, ensure_ascii=False))
else:

    class MetricsPanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for MetricsPanel") from _IMPORT_ERROR
