from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from .icons import apply_icon

def create_button(
    text: str,
    variant: str = "secondary",
    on_click: Optional[Callable[[], None]] = None,
    *,
    parent: Optional[QWidget] = None,
    tooltip: Optional[str] = None,
    default: bool = False,
    minimum_width: Optional[int] = None,
    icon_name: str | None = None,
    icon_namespace: str | None = None,
    icon_pack: str | None = None,
    icon_size: int | str = "body",
    icon_accessible_name: str | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setCursor(Qt.PointingHandCursor)
    button.setProperty("variant", variant)
    button.setAccessibleName(str(text or "action_button").strip())
    if tooltip:
        button.setToolTip(tooltip)
    if minimum_width is not None:
        button.setMinimumWidth(max(72, int(minimum_width)))
    if default:
        button.setDefault(True)
    if on_click is not None:
        button.clicked.connect(on_click)
    if icon_name:
        apply_icon(
            button,
            icon_name,
            namespace=icon_namespace,
            pack=icon_pack,
            size=icon_size,
            accessible_name=icon_accessible_name,
            tooltip=tooltip,
        )
    return button
