from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def apply_shadow(
    widget: QWidget,
    *,
    blur: float = 22.0,
    x_offset: float = 0.0,
    y_offset: float = 6.0,
    alpha: int = 68,
    color: Optional[QColor] = None,
    enabled: bool = True,
) -> None:
    if widget is None:
        return

    if not enabled:
        widget.setGraphicsEffect(None)
        return

    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)

    effect.setBlurRadius(max(0.0, float(blur)))
    effect.setOffset(float(x_offset), float(y_offset))
    effect.setColor(color or QColor(0, 0, 0, max(0, min(255, int(alpha)))))


def repolish(widget: QWidget, recursive: bool = False) -> None:
    if widget is None:
        return

    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

    if recursive:
        for child in widget.findChildren(QWidget):
            child_style = child.style()
            child_style.unpolish(child)
            child_style.polish(child)
            child.update()


class _HoverCardFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if isinstance(watched, QWidget):
            if event.type() in {QEvent.Enter, QEvent.HoverEnter}:
                watched.setProperty("hover", True)
                repolish(watched)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                watched.setProperty("hover", False)
                repolish(watched)
        return False


_CARD_HOVER_FILTER: _HoverCardFilter | None = None


def enable_card_hover(widget: QWidget) -> None:
    global _CARD_HOVER_FILTER
    if widget is None:
        return
    if _CARD_HOVER_FILTER is None:
        _CARD_HOVER_FILTER = _HoverCardFilter()
    widget.setAttribute(Qt.WA_Hover, True)
    widget.setMouseTracking(True)
    widget.setProperty("hoverable", True)
    widget.setProperty("hover", False)
    widget.installEventFilter(_CARD_HOVER_FILTER)


__all__ = [
    "apply_shadow",
    "repolish",
    "enable_card_hover",
]
