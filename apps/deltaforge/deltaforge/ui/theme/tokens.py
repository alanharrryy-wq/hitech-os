from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ThemeTokens:
    theme_id: str
    colors: dict[str, str] = field(default_factory=dict)
    spacing: dict[str, int] = field(default_factory=dict)
    radius: dict[str, int] = field(default_factory=dict)
    typography: dict[str, int] = field(default_factory=dict)
    semantic: dict[str, str] = field(default_factory=dict)


def build_default_theme() -> ThemeTokens:
    return ThemeTokens(
        theme_id="deltaforge_steel",
        colors={
            "canvas": "#0b1118",
            "shell": "#111a24",
            "panel": "#151f2b",
            "panel_alt": "#1a2634",
            "surface": "#202f40",
            "hairline": "#2b3d52",
            "focus": "#4da6ff",
            "focus_soft": "#294f72",
            "text": "#e5edf6",
            "text_soft": "#9fb2c8",
            "text_muted": "#7d91a8",
            "positive": "#36c57a",
            "warning": "#f4b45a",
            "danger": "#ff6f75",
            "chip_bg": "#1b2a3a",
            "mono_bg": "#0f1822",
        },
        spacing={"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 20, "xxl": 24},
        radius={"sm": 8, "md": 12, "lg": 16, "xl": 20},
        typography={"title": 18, "subtitle": 12, "body": 12, "small": 11, "mono": 11},
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
