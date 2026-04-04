from __future__ import annotations

from dataclasses import dataclass

from .palette_registry import GlassPalette


@dataclass(frozen=True, slots=True)
class ChromeMaterialSpec:
    chrome_top: str
    chrome_bottom: str
    chrome_border: str
    button_top: str
    button_bottom: str
    button_border: str
    text_primary: str
    accent: str
    accent_soft: str


def build_chrome_spec(palette: GlassPalette) -> ChromeMaterialSpec:
    return ChromeMaterialSpec(
        chrome_top=palette.chrome_top,
        chrome_bottom=palette.chrome_bottom,
        chrome_border=palette.chrome_border,
        button_top=palette.button_top,
        button_bottom=palette.button_bottom,
        button_border=palette.button_border,
        text_primary=palette.text_primary,
        accent=palette.accent,
        accent_soft=palette.accent_soft,
    )


__all__ = ["ChromeMaterialSpec", "build_chrome_spec"]
