from __future__ import annotations

from dataclasses import dataclass

from ..common.constants import DEFAULT_THEME_ID
from ..common.helpers import clean_text


@dataclass(frozen=True, slots=True)
class RenderTheme:
    theme_id: str
    label: str
    is_dark: bool
    tokens: dict[str, str]


def _silver_frost_cyan() -> RenderTheme:
    return RenderTheme(
        theme_id="silver_frost_cyan",
        label="Silver Frost Cyan",
        is_dark=True,
        tokens={
            "canvas_bg": "#070e17",
            "header_fill": "#0f1824",
            "legend_fill": "#132234",
            "focus": "#8cefff",
            "legend_stroke": "#d8ecff",
            "header_stroke": "#c8def4",
            "header_title": "#f5fbff",
            "header_meta": "#c1d0df",
            "text_main": "#e0edf9",
            "text_soft": "#b8cade",
            "footer_text": "#98adc2",
            "chip_light": "#eff8ff",
            "muted_stroke": "#bdd1e6",
            "badge_out": "#4fd4df",
            "warning_fill": "#8ea7bc",
            "warning_stroke": "#d9c6a3",
            "muted_text": "#9fb4c7",
            "halo_a": "#eff7ff",
            "halo_b": "#8cefff",
        },
    )


def _night_ink() -> RenderTheme:
    return RenderTheme(
        theme_id="night_ink",
        label="Night Ink",
        is_dark=True,
        tokens={
            "canvas_bg": "#060911",
            "header_fill": "#0b1220",
            "legend_fill": "#131d33",
            "focus": "#63c9ff",
            "legend_stroke": "#5f7796",
            "header_stroke": "#506a88",
            "header_title": "#edf4ff",
            "header_meta": "#9bb0c9",
            "text_main": "#d9e7fb",
            "text_soft": "#a5b8d1",
            "footer_text": "#8fa2ba",
            "chip_light": "#e8f3ff",
            "muted_stroke": "#4f6788",
            "badge_out": "#52d6c2",
            "warning_fill": "#584126",
            "warning_stroke": "#d4ad7d",
            "muted_text": "#8ea0b8",
            "halo_a": "#5bc3ff",
            "halo_b": "#7c9cff",
        },
    )


THEMES: tuple[RenderTheme, ...] = (
    _silver_frost_cyan(),
    _night_ink(),
)

THEME_REGISTRY: dict[str, RenderTheme] = {theme.theme_id: theme for theme in THEMES}
THEME_LABELS: tuple[str, ...] = tuple(theme.label for theme in THEMES)
_THEME_LABEL_TO_ID: dict[str, str] = {theme.label.lower(): theme.theme_id for theme in THEMES}


def normalize_theme(theme: str | None) -> str:
    cleaned = clean_text(theme).lower()
    if not cleaned:
        return DEFAULT_THEME_ID
    if cleaned in THEME_REGISTRY:
        return cleaned
    if cleaned in _THEME_LABEL_TO_ID:
        return _THEME_LABEL_TO_ID[cleaned]
    return DEFAULT_THEME_ID


def resolve_theme(theme: str | None) -> RenderTheme:
    theme_id = normalize_theme(theme)
    return THEME_REGISTRY.get(theme_id, THEME_REGISTRY[DEFAULT_THEME_ID])
