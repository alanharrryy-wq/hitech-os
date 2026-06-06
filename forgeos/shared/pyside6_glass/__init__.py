"""Reusable PySide6 glass framework for ForgeOS tools.

This package stays import-light so Code Atlas can import direct submodules
without pulling every demo/catalog dependency at startup.
"""

from __future__ import annotations

__all__ = [
    "FrostedGlassBackdrop",
    "build_glass_dialog_scene",
    "build_stylesheet",
    "create_button",
]


def __getattr__(name: str):
    if name == "create_button":
        from .controls import create_button
        return create_button
    if name == "build_stylesheet":
        from .theme import build_stylesheet
        return build_stylesheet
    if name == "build_glass_dialog_scene":
        from .scene import build_glass_dialog_scene
        return build_glass_dialog_scene
    if name == "FrostedGlassBackdrop":
        from .backdrop import FrostedGlassBackdrop
        return FrostedGlassBackdrop
    raise AttributeError(name)
