from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QEvent, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QComboBox, QLineEdit, QWidget

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

