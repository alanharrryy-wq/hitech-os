"""Reusable PySide6 glass visual template for ForgeOS tools."""

from .backdrop import FrostedGlassBackdrop
from .chrome import WindowChromeBar
from .contracts import GLASS_RADIUS, GlassRadiusContract
from .controls import create_button
from .scene import build_glass_dialog_scene
from .template import (
    GlassPanelTemplate,
    GlassTemplateActions,
    GlassTemplateCards,
    GlassTemplateSlots,
)
from .theme import DEFAULT_THEME_ID, build_stylesheet

__all__ = [
    "DEFAULT_THEME_ID",
    "FrostedGlassBackdrop",
    "GLASS_RADIUS",
    "GlassPanelTemplate",
    "GlassTemplateActions",
    "GlassTemplateCards",
    "GlassRadiusContract",
    "GlassTemplateSlots",
    "WindowChromeBar",
    "build_glass_dialog_scene",
    "build_stylesheet",
    "create_button",
]
