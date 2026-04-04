from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ..appearance import AppearanceSnapshot
from ..visual_contracts import set_visual_properties
from .overlays import install_surface_overlay, sync_surface_overlay


def apply_surface_role(
    widget: QWidget,
    *,
    role: str,
    variant: str = 'glass',
    emphasis: str = 'normal',
    fx_level: str = 'normal',
) -> QWidget:
    if widget is None:
        return widget
    set_visual_properties(
        widget,
        role=role or 'panel_workspace',
        variant=variant or 'glass',
        emphasis=emphasis or 'normal',
        fx_level=fx_level or 'normal',
    )
    return widget


def install_surface_renderer(widget: QWidget) -> QWidget:
    install_surface_overlay(widget)
    return widget


def sync_surface_renderer(widget: QWidget, snapshot: AppearanceSnapshot) -> QWidget:
    sync_surface_overlay(widget, snapshot)
    return widget


def sync_surface_tree(root: QWidget, snapshot: AppearanceSnapshot) -> QWidget:
    if root.property('visualRole'):
        sync_surface_overlay(root, snapshot)
    for widget in root.findChildren(QWidget):
        if widget.property('visualRole'):
            sync_surface_overlay(widget, snapshot)
    return root
