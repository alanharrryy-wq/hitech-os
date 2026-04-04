from __future__ import annotations

"""Visual material facade.

`pyside6_glass.theme` remains as a stable import target, but the actual visual
material authority now lives in `pyside6_glass.skin.*`.
"""

from .contracts import DEFAULT_THEME_ID
from .skin.materializer import build_stylesheet
from .skin.palette_registry import (
    GlassPalette,
    GlassThemeManifest,
    get_palette,
    get_theme_manifest,
    list_theme_ids,
    register_theme,
    register_theme_overrides,
)
from .skin.surface_spec import _scale_rgba_alpha


def build_stylesheet_exact_atlas(
    theme_id: str = DEFAULT_THEME_ID,
    *,
    density: str = "comfortable",
    typography_scale: str = "lg",
    tab_density: str | None = None,
    tab_variant: str = "glass",
    border_strength_scale: float = 1.0,
    surface_opacity_scale: float = 1.0,
) -> str:
    """Compatibility shim.

    Atlas is no longer part of the productive materialization path. The shim
    survives for legacy callers, but resolves to the same governed stylesheet.
    """

    return build_stylesheet(
        theme_id=theme_id,
        density=density,
        typography_scale=typography_scale,
        tab_density=tab_density,
        tab_variant=tab_variant,
        border_strength_scale=border_strength_scale,
        surface_opacity_scale=surface_opacity_scale,
    )


__all__ = [
    "DEFAULT_THEME_ID",
    "GlassPalette",
    "GlassThemeManifest",
    "_scale_rgba_alpha",
    "build_stylesheet",
    "get_palette",
    "get_theme_manifest",
    "list_theme_ids",
    "register_theme",
    "register_theme_overrides",
]
