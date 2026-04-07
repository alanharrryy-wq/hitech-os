from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtWidgets import QWidget

from .shadow import set_shadow_lift


def _widget_alive(widget: QWidget | None) -> bool:
    if widget is None:
        return False
    try:
        widget.style()
        return True
    except RuntimeError:
        return False


def _apply_repolish(widget: QWidget, recursive: bool = False) -> None:
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


def repolish(widget: QWidget, recursive: bool = False, *, immediate: bool = False) -> None:
    if not _widget_alive(widget):
        return

    pending_key = "_repolish_pending_recursive" if recursive else "_repolish_pending"

    if immediate or not widget.isVisible():
        widget.setProperty(pending_key, False)
        _apply_repolish(widget, recursive)
        return

    if bool(widget.property(pending_key)):
        return

    widget.setProperty(pending_key, True)

    def _run() -> None:
        if not _widget_alive(widget):
            return
        widget.setProperty(pending_key, False)
        _apply_repolish(widget, recursive)

    QTimer.singleShot(0, _run)


class _HoverCardFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        # perf-safe-margin-patch: hover guard prevents redundant repolish churn.
        if isinstance(watched, QWidget):
            event_type = event.type()
            if event_type in {QEvent.Enter, QEvent.HoverEnter}:
                if not bool(watched.property("hover")):
                    watched.setProperty("hover", True)
                    set_shadow_lift(watched, True, intensity=0.16)
                    repolish(watched)
            elif event_type in {QEvent.Leave, QEvent.HoverLeave}:
                if bool(watched.property("hover")):
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

