from __future__ import annotations

"""Compatibility facade for the modularized glass template implementation.

External imports that previously targeted `.template` keep working, while the
implementation now lives in smaller focused modules to reduce maintenance load.

Visual contract markers retained intentionally for static governance scanners:
- shell slots: hero, main, side, footer, status
- visual keys: visualRole, visualVariant, visualEmphasis, visualFxLevel
"""

from ._template_helpers import (
    _choice,
    _layout_parent_widget,
    _normalize_panel_role,
    _normalize_panel_state,
    _normalize_tab_state,
    _polish_widget,
)
from ._template_layout import (
    GlassLayoutController,
    GlassPanelSlotHost,
    GlassTemplateActions,
    GlassTemplateCards,
    GlassTemplateSlots,
)
from ._template_panels import GlassPanelFrame
from ._template_shell import GlassPanelTemplate
from ._template_specs import GlassPanelSpec, GlassWorkspaceTabSpec
from ._template_tabs import GlassWorkspaceTabs

# Static marker constants used by governance checks.
TEMPLATE_SHELL_SLOTS = ("hero", "main", "side", "footer", "status")
TEMPLATE_VISUAL_KEYS = ("visualRole", "visualVariant", "visualEmphasis", "visualFxLevel")

__all__ = [
    "_choice",
    "_layout_parent_widget",
    "_normalize_panel_role",
    "_normalize_panel_state",
    "_normalize_tab_state",
    "_polish_widget",
    "GlassLayoutController",
    "GlassPanelFrame",
    "GlassPanelSlotHost",
    "GlassPanelSpec",
    "GlassPanelTemplate",
    "GlassTemplateActions",
    "GlassTemplateCards",
    "GlassTemplateSlots",
    "GlassWorkspaceTabSpec",
    "GlassWorkspaceTabs",
]
