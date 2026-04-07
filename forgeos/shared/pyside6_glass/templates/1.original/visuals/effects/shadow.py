from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


def _same_color(left: QColor, right: QColor) -> bool:
    return (
        left.red() == right.red()
        and left.green() == right.green()
        and left.blue() == right.blue()
        and left.alpha() == right.alpha()
    )


def _close_enough(left: float, right: float, *, tolerance: float = 0.05) -> bool:
    return abs(float(left) - float(right)) <= tolerance


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

    base_blur = max(0.0, float(blur))
    base_x = float(x_offset)
    base_y = float(y_offset)
    base_alpha = max(0, min(255, int(alpha)))
    target_color = color or QColor(0, 0, 0, base_alpha)

    widget.setProperty("_shadow_base_blur", base_blur)
    widget.setProperty("_shadow_base_x", base_x)
    widget.setProperty("_shadow_base_y", base_y)
    widget.setProperty("_shadow_base_alpha", base_alpha)

    if (
        _close_enough(effect.blurRadius(), base_blur)
        and _close_enough(effect.xOffset(), base_x)
        and _close_enough(effect.yOffset(), base_y)
        and _same_color(effect.color(), target_color)
    ):
        return

    effect.setBlurRadius(base_blur)
    effect.setOffset(base_x, base_y)
    effect.setColor(target_color)


def set_shadow_lift(widget: QWidget, lifted: bool, *, intensity: float = 0.20) -> None:
    if widget is None:
        return
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        return

    shadow_state = widget.property("_shadow_lifted")
    if shadow_state is not None and bool(shadow_state) == bool(lifted):
        return
    widget.setProperty("_shadow_lifted", bool(lifted))

    base_blur = float(widget.property("_shadow_base_blur") or effect.blurRadius())
    base_x = float(widget.property("_shadow_base_x") or effect.xOffset())
    base_y = float(widget.property("_shadow_base_y") or effect.yOffset())
    base_alpha = int(widget.property("_shadow_base_alpha") or effect.color().alpha())

    if lifted:
        factor = 1.0 + max(0.05, float(intensity))
        effect.setBlurRadius(base_blur * factor)
        effect.setOffset(base_x, max(0.0, base_y - (1.6 * intensity * 5.0)))
        lift_color = QColor(effect.color())
        lift_color.setAlpha(max(0, min(255, int(base_alpha * (1.0 + (0.6 * intensity))))))
        effect.setColor(lift_color)
    else:
        effect.setBlurRadius(base_blur)
        effect.setOffset(base_x, base_y)
        base_color = QColor(effect.color())
        base_color.setAlpha(base_alpha)
        effect.setColor(base_color)
