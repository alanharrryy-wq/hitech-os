from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from ..effects.polish import repolish
from .icons import icon_text


def create_chip(
    text: str,
    *,
    tone: str = "neutral",
    icon: str | None = None,
    parent: QWidget | None = None,
) -> QLabel:
    chip = QLabel(icon_text(text, icon), parent)
    chip.setProperty("chip", True)
    chip.setProperty("tone", tone)
    chip.setAlignment(Qt.AlignCenter)
    repolish(chip)
    return chip

