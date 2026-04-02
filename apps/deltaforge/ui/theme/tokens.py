from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ThemeTokens:
    theme_id: str
    colors: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int] = field(default_factory=dict)
    radius: dict[str, int] = field(default_factory=dict)
    typography: dict[str, int | str] = field(default_factory=dict)
    semantic: dict[str, str] = field(default_factory=dict)



def build_default_theme() -> ThemeTokens:
    colors = {
        # foundational surfaces
        "canvas": "#0b1118",
        "shell": "#111a24",
        "panel": "#151f2b",
        "panel_alt": "#1a2634",
        "panel_elevated": "#1c2a3a",
        "panel_overlay": "#223244",
        "surface": "#202f40",
        "surface_subtle": "#162230",
        "surface_strong": "#223447",
        "mono_bg": "#0f1822",
        "chip_bg": "#1b2a3a",
        # strokes and focus
        "hairline": "#2b3d52",
        "stroke_soft": "#30465d",
        "selection_fill": "#1f4564",
        "focus": "#4da6ff",
        "focus_soft": "#294f72",
        "focus_ring": "#79c7ff",
        # text system
        "text": "#e5edf6",
        "text_soft": "#9fb2c8",
        "text_muted": "#7d91a8",
        "text_primary": "#e5edf6",
        "text_secondary": "#9fb2c8",
        "text_inverse": "#081119",
        # accents and feedback
        "accent": "#57a6ff",
        "accent_hover": "#79c7ff",
        "accent_pressed": "#3a8be8",
        "positive": "#36c57a",
        "success": "#36c57a",
        "warning": "#f4b45a",
        "danger": "#ff6f75",
        "info": "#57a6ff",
        # overlays
        "scrim": "rgba(4, 11, 18, 185)",
    }

    return ThemeTokens(
        theme_id="deltaforge_steel",
        colors=colors,
        spacing={"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "xxl": 24},
        radius={"sm": 8, "md": 12, "lg": 16, "xl": 20, "pill": 999},
        typography={
            "family": "Segoe UI",
            "title": 18,
            "subtitle": 12,
            "body": 12,
            "small": 11,
            "mono": 11,
            "weight_medium": 500,
            "weight_semibold": 600,
            "weight_bold": 700,
        },
        semantic={
            "empty": "#8ea5bf",
            "scope_loaded": "#57a6ff",
            "ops_loaded": "#6fd1b8",
            "validated": "#39c67a",
            "plan_generated": "#5ca8ff",
            "applied": "#48d68f",
            "rollback_available": "#f2c060",
            "dirty_or_stale": "#f5a264",
            "error": "#ff7c84",
        },
    )
