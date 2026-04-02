from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget


def create_button(
    text: str,
    variant: str = "secondary",
    on_click: Optional[Callable[[], None]] = None,
    *,
    parent: Optional[QWidget] = None,
    tooltip: Optional[str] = None,
    default: bool = False,
    minimum_width: Optional[int] = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setCursor(Qt.PointingHandCursor)
    button.setProperty("variant", variant)
    if tooltip:
        button.setToolTip(tooltip)
    if minimum_width is not None:
        button.setMinimumWidth(max(72, int(minimum_width)))
    if default:
        button.setDefault(True)
    if on_click is not None:
        button.clicked.connect(on_click)
    return button

