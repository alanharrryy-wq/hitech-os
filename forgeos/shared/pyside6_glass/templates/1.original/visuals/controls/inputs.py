from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QLineEdit, QListView, QWidget

from ..effects.polish import repolish
from ..effects.shadow import apply_shadow


class _InputFocusFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        # perf-safe-margin-patch: focus guard skips redundant repolish and shadow resets.
        if isinstance(watched, (QLineEdit, QComboBox)):
            event_type = event.type()
            focus_state = bool(watched.property("focus"))
            if event_type == QEvent.FocusIn:
                if not focus_state:
                    watched.setProperty("focus", True)
                    repolish(watched)
                    apply_shadow(
                        watched,
                        blur=12.0,
                        y_offset=0.0,
                        alpha=74,
                        color=QColor(140, 239, 255, 74),
                    )
            elif event_type == QEvent.FocusOut:
                if focus_state:
                    watched.setProperty("focus", False)
                    repolish(watched)
                    apply_shadow(
                        watched,
                        blur=8.0,
                        y_offset=1.0,
                        alpha=22,
                        color=QColor(0, 0, 0, 22),
                    )
        return False


_INPUT_FOCUS_FILTER: _InputFocusFilter | None = None


def _attach_focus_glow(widget: QWidget) -> None:
    global _INPUT_FOCUS_FILTER
    if _INPUT_FOCUS_FILTER is None:
        _INPUT_FOCUS_FILTER = _InputFocusFilter()
    widget.installEventFilter(_INPUT_FOCUS_FILTER)
    widget.setProperty("focus", False)
    apply_shadow(widget, blur=8.0, y_offset=1.0, alpha=22, color=QColor(0, 0, 0, 22))


def create_line_edit(
    placeholder: str,
    *,
    clear_button: bool = True,
    parent: QWidget | None = None,
) -> QLineEdit:
    entry = QLineEdit(parent)
    entry.setPlaceholderText(placeholder)
    entry.setClearButtonEnabled(clear_button)
    _attach_focus_glow(entry)
    return entry


def create_combo(
    items: Iterable[str],
    *,
    parent: QWidget | None = None,
) -> QComboBox:
    combo = QComboBox(parent)
    combo.setProperty("glass_combo", True)
    combo.setProperty("glass_dropdown_ready", True)
    combo.setMaxVisibleItems(8)
    combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
    combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

    popup = QListView(combo)
    popup.setObjectName("GlassComboPopup")
    popup.setProperty("glass_popup", True)
    popup.setProperty("glass_popup_ready", True)
    popup.setSpacing(4)
    popup.setUniformItemSizes(False)
    popup.setFrameShape(QListView.NoFrame)
    popup.setAttribute(Qt.WA_TranslucentBackground, True)
    popup.setAutoFillBackground(False)
    popup.viewport().setAutoFillBackground(False)
    popup.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
    popup.viewport().setAttribute(Qt.WA_Hover, True)
    popup.setVerticalScrollMode(QListView.ScrollPerPixel)
    popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    popup.setMouseTracking(True)
    combo.setView(popup)

    combo.addItems([str(item) for item in items])
    _attach_focus_glow(combo)
    return combo

