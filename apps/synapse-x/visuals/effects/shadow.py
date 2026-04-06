from __future__ import annotations

from typing import Optional

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

    base_blur = max(0.0, float(blur))
    base_x = float(x_offset)
    base_y = float(y_offset)
    base_alpha = max(0, min(255, int(alpha)))
    widget.setProperty("_shadow_base_blur", base_blur)
    widget.setProperty("_shadow_base_x", base_x)
    widget.setProperty("_shadow_base_y", base_y)
    widget.setProperty("_shadow_base_alpha", base_alpha)

    effect.setBlurRadius(max(0.0, float(blur)))
    effect.setOffset(float(x_offset), float(y_offset))
    effect.setColor(color or QColor(0, 0, 0, max(0, min(255, int(alpha)))))


def set_shadow_lift(widget: QWidget, lifted: bool, *, intensity: float = 0.20) -> None:
    if widget is None:
        return
    effect = widget.graphicsEffect()
    if not isinstance(effect, QGraphicsDropShadowEffect):
        return

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
