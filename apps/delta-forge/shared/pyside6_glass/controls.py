from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from .effects import apply_shadow, repolish
from .icons import apply_icon


_BUTTON_VARIANT_ALIASES = {
    "default": "secondary",
    "neutral": "secondary",
    "outline": "ghost",
    "tertiary": "subtle",
}
_SUPPORTED_BUTTON_VARIANTS = {
    "primary",
    "secondary",
    "subtle",
    "ghost",
    "danger",
    "warning",
    "success",
}
_SHADOW_ALPHA_BY_VARIANT = {
    "primary": 28,
    "secondary": 14,
    "success": 22,
    "danger": 16,
}


def _normalize_button_variant(value: str) -> str:
    normalized = str(value or "").strip().lower() or "secondary"
    normalized = _BUTTON_VARIANT_ALIASES.get(normalized, normalized)
    if normalized in _SUPPORTED_BUTTON_VARIANTS:
        return normalized
    return "secondary"


def list_button_variants() -> tuple[str, ...]:
    return tuple(sorted(_SUPPORTED_BUTTON_VARIANTS))


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
    button.setFlat(True)
    variant_name = _normalize_button_variant(variant)
    button.setProperty("variant", variant_name)
    button.setAccessibleName(str(text or "action_button").strip())
    if tooltip:
        button.setToolTip(tooltip)
    if minimum_width is not None:
        button.setMinimumWidth(max(72, int(minimum_width)))
    if default:
        button.setDefault(True)
    button.setEnabled(button.isEnabled())
    button.setAutoDefault(bool(default))
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
    shadow_blur = 16.0 if variant_name == "primary" else 12.0
    shadow_alpha = _SHADOW_ALPHA_BY_VARIANT.get(variant_name, 14)
    apply_shadow(button, blur=shadow_blur, y_offset=4.0, alpha=shadow_alpha)
    repolish(button)
    return button
