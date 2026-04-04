from __future__ import annotations

from PySide6.QtWidgets import QLayout, QWidget

from .contracts import (
    PANEL_ROLES,
    SUPPORTED_PANEL_STATES,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_ICON_MODES,
    SUPPORTED_TAB_PLACEMENT,
    SUPPORTED_TAB_STATES,
    SUPPORTED_TAB_VARIANTS,
)

def _normalize_tab_state(state: str) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in SUPPORTED_TAB_STATES:
        return normalized
    return "visible"


def _normalize_panel_role(role: str) -> str:
    normalized = str(role or "").strip().lower()
    if normalized in PANEL_ROLES:
        return normalized
    return "workspace"


def _normalize_panel_state(state: str) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in SUPPORTED_PANEL_STATES:
        return normalized
    return "visible"


def _choice(value: str, allowed: tuple[str, ...], fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


def _polish_widget(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _layout_parent_widget(layout: QLayout | None) -> QWidget | None:
    if layout is None:
        return None
    parent = layout.parent()
    return parent if isinstance(parent, QWidget) else None

__all__ = [
    "_choice",
    "_layout_parent_widget",
    "_normalize_panel_role",
    "_normalize_panel_state",
    "_normalize_tab_state",
    "_polish_widget",
]
