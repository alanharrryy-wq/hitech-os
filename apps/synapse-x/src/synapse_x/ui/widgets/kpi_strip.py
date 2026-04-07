
from __future__ import annotations

from collections.abc import Iterable, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from visuals.effects.shadow import apply_shadow


class _KPIBlock(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setProperty("card", "muted")
        apply_shadow(self, blur=14.0, y_offset=5.0, alpha=10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        self.eyebrow = QLabel("METRIC", self)
        self.eyebrow.setProperty("role", "field")
        layout.addWidget(self.eyebrow, 0, Qt.AlignmentFlag.AlignLeft)

        self.value_label = QLabel("0", self)
        self.value_label.setProperty("role", "section")
        layout.addWidget(self.value_label, 0, Qt.AlignmentFlag.AlignLeft)

        self.detail_label = QLabel("", self)
        self.detail_label.setProperty("role", "hint")
        self.detail_label.setWordWrap(True)
        layout.addWidget(self.detail_label)

    def set_content(self, label: str, value: str, detail: str = "") -> None:
        self.eyebrow.setText(str(label or "METRIC").upper())
        self.value_label.setText(str(value or "0"))
        self.detail_label.setText(str(detail or ""))


class KPIStrip(QFrame):
    def __init__(self, parent: QWidget | None = None, *, columns: int = 4) -> None:
        super().__init__(parent)
        self._columns = max(1, int(columns))
        self.setProperty("card", "false")

        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setHorizontalSpacing(10)
        self._layout.setVerticalSpacing(10)
        self._blocks: list[_KPIBlock] = []

    def _ensure_blocks(self, count: int) -> None:
        while len(self._blocks) < count:
            block = _KPIBlock(self)
            self._blocks.append(block)
            index = len(self._blocks) - 1
            row = index // self._columns
            col = index % self._columns
            self._layout.addWidget(block, row, col)

    def set_metrics(self, items: Iterable[Mapping[str, object]]) -> None:
        normalized = [dict(item) for item in items]
        self._ensure_blocks(len(normalized))
        for idx, item in enumerate(normalized):
            self._blocks[idx].setVisible(True)
            self._blocks[idx].set_content(
                str(item.get("label") or "Metric"),
                str(item.get("value") or "0"),
                str(item.get("detail") or ""),
            )
        for idx in range(len(normalized), len(self._blocks)):
            self._blocks[idx].setVisible(False)
