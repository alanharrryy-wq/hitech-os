from __future__ import annotations

from copy import deepcopy

from ui.theme.tokens import ThemeTokens, build_default_theme

PRESET_DEFAULT = "deltaforge_steel"


def workstation_premium_dark() -> ThemeTokens:
    return build_default_theme()


def workstation_premium_ink() -> ThemeTokens:
    theme = build_default_theme()
    colors = deepcopy(theme.colors)
    colors.update(
        {
            "canvas": "#090e14",
            "shell": "#0d141d",
            "panel": "#111d29",
            "panel_alt": "#152435",
            "surface": "#182535",
            "focus": "#79c7ff",
            "focus_soft": "#3b6f96",
        }
    )
    return ThemeTokens(
        theme_id="deltaforge_ink",
        colors=colors,
        spacing=deepcopy(theme.spacing),
        radius=deepcopy(theme.radius),
        typography=deepcopy(theme.typography),
        semantic=deepcopy(theme.semantic),
    )


_PRESETS = {
    PRESET_DEFAULT: workstation_premium_dark,
    "deltaforge_ink": workstation_premium_ink,
}


def list_presets() -> tuple[str, ...]:
    return tuple(_PRESETS.keys())


def get_theme_tokens(preset_name: str = PRESET_DEFAULT) -> ThemeTokens:
    factory = _PRESETS.get(preset_name, _PRESETS[PRESET_DEFAULT])
    return factory()
