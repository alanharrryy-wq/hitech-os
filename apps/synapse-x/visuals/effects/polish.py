from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QWidget

from .shadow import set_shadow_lift


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
                set_shadow_lift(watched, True, intensity=0.16)
                repolish(watched)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                watched.setProperty("hover", False)
                set_shadow_lift(watched, False)
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
