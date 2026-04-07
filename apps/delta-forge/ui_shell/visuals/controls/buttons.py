from __future__ import annotations

from typing import Any, Callable, Optional

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QPushButton, QWidget

from ..effects.polish import repolish
from ..effects.shadow import apply_shadow, set_shadow_lift
from .icons import icon_text


class _ButtonLiftFilter(QObject):
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if isinstance(watched, QPushButton):
            if event.type() in {QEvent.Enter, QEvent.HoverEnter}:
                set_shadow_lift(watched, True, intensity=0.22)
            elif event.type() in {QEvent.Leave, QEvent.HoverLeave}:
                set_shadow_lift(watched, False)
        return False


_BUTTON_LIFT_FILTER: _ButtonLiftFilter | None = None


def create_button(
    text: str,
    variant: str,
    callback: Optional[Callable[..., Any]] = None,
    *,
    icon: str | None = None,
    tooltip: str = "",
    default: bool = False,
    auto_default: Optional[bool] = None,
    minimum_width: int = 0,
    enabled: bool = True,
    parent: Optional[QWidget] = None,
) -> QPushButton:
    global _BUTTON_LIFT_FILTER
    button = QPushButton(icon_text(text, icon), parent)
    button.setProperty("variant", (variant or "secondary").strip().lower())
    button.setProperty("with_icon", bool(icon))
    button.setFocusPolicy(Qt.NoFocus)
    button.setEnabled(enabled)
    button.setDefault(bool(default))
    button.setAutoDefault(bool(default) if auto_default is None else bool(auto_default))

    if tooltip:
        button.setToolTip(tooltip)
    if minimum_width > 0:
        button.setMinimumWidth(int(minimum_width))
    if callable(callback):
        button.clicked.connect(callback)

    shadow_alpha = {
        "primary": 28,
        "secondary": 14,
        "success": 22,
        "danger": 16,
    }.get((variant or "secondary").strip().lower(), 14)
    shadow_blur = 16.0 if (variant or "").strip().lower() == "primary" else 12.0
    apply_shadow(button, blur=shadow_blur, y_offset=4.0, alpha=shadow_alpha)

    if _BUTTON_LIFT_FILTER is None:
        _BUTTON_LIFT_FILTER = _ButtonLiftFilter()
    button.setAttribute(Qt.WA_Hover, True)
    button.setMouseTracking(True)
    button.installEventFilter(_BUTTON_LIFT_FILTER)

    repolish(button)
    return button
