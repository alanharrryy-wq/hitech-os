from __future__ import annotations

try:
    from PySide6.QtCore import Signal
    from PySide6.QtWidgets import (
        QComboBox,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QSpinBox,
        QWidget,
    )
except Exception as exc:  # noqa: BLE001
    Signal = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


if Signal is not None:

    class SearchPanel(QWidget):
        search_requested = Signal(str, str, str, str, int)

        def __init__(self) -> None:
            super().__init__()
            root_layout = QGridLayout(self)
            root_layout.setContentsMargins(0, 0, 0, 0)

            self.query_input = QLineEdit()
            self.query_input.setPlaceholderText("Search text")

            self.type_combo = QComboBox()
            self.type_combo.addItems(["", "error", "event", "tool", "log", "json", "jsonl", "report"])

            self.date_from_input = QLineEdit()
            self.date_from_input.setPlaceholderText("YYYY-MM-DD")
            self.date_to_input = QLineEdit()
            self.date_to_input.setPlaceholderText("YYYY-MM-DD")

            self.limit_spin = QSpinBox()
            self.limit_spin.setRange(1, 500)
            self.limit_spin.setValue(50)

            self.search_button = QPushButton("Search")

            root_layout.addWidget(QLabel("Query"), 0, 0)
            root_layout.addWidget(self.query_input, 0, 1, 1, 5)
            root_layout.addWidget(self.search_button, 0, 6)

            root_layout.addWidget(QLabel("Type"), 1, 0)
            root_layout.addWidget(self.type_combo, 1, 1)
            root_layout.addWidget(QLabel("From"), 1, 2)
            root_layout.addWidget(self.date_from_input, 1, 3)
            root_layout.addWidget(QLabel("To"), 1, 4)
            root_layout.addWidget(self.date_to_input, 1, 5)
            limit_box = QHBoxLayout()
            limit_box.addWidget(QLabel("Limit"))
            limit_box.addWidget(self.limit_spin)
            holder = QWidget()
            holder.setLayout(limit_box)
            root_layout.addWidget(holder, 1, 6)

            self.search_button.clicked.connect(self.emit_search)
            self.query_input.returnPressed.connect(self.emit_search)

        def emit_search(self) -> None:
            self.search_requested.emit(
                self.query_input.text().strip(),
                self.type_combo.currentText().strip(),
                self.date_from_input.text().strip(),
                self.date_to_input.text().strip(),
                int(self.limit_spin.value()),
            )
else:

    class SearchPanel:  # type: ignore[no-redef]
        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            raise RuntimeError("PySide6 is required for SearchPanel") from _IMPORT_ERROR
