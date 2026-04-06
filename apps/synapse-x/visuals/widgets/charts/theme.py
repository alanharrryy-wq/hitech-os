from __future__ import annotations

from dataclasses import dataclass

from ...themes.catalog import resolve_theme


@dataclass(frozen=True, slots=True)
class ChartFoundationPalette:
    text_primary: str
    accent: str
    text_muted: str
    tab_text: str


def get_palette(theme_id: str) -> ChartFoundationPalette:
    theme = resolve_theme(theme_id)
    tokens = theme.tokens
    return ChartFoundationPalette(
        text_primary=tokens["text_main"],
        accent=tokens["focus"],
        text_muted=tokens["muted_text"],
        tab_text=tokens.get("text_soft", tokens.get("header_meta", tokens["text_main"])),
    )


__all__ = ["ChartFoundationPalette", "get_palette"]
