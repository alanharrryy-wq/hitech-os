from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QWidget


def apply_shadow(
    widget: QWidget,
    color: str,
    blur: float = 20.0,
    x_offset: float = 0.0,
    y_offset: float = 4.0,
) -> None:
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        effect = QGraphicsDropShadowEffect(widget)
        widget.setGraphicsEffect(effect)
    effect.setBlurRadius(blur)
    effect.setOffset(x_offset, y_offset)
    effect.setColor(QColor(color))


def fade_in(widget: QWidget, duration_ms: int = 150) -> None:
    effect = widget.graphicsEffect()
    if effect is not None and not isinstance(effect, QGraphicsOpacityEffect):
        return
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, b"opacity", widget)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setDuration(duration_ms)
    animation.setEasingCurve(QEasingCurve.OutCubic)
    animation.start()
    widget._fade_animation = animation  # type: ignore[attr-defined]
