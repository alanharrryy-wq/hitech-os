from __future__ import annotations

from ..common.helpers import clean_text


ICON_GLYPHS: dict[str, str] = {
    "workspace": "◈",
    "overview": "◍",
    "actions": "⚙",
    "status": "●",
    "details": "▤",
    "activity": "◎",
    "preview": "◧",
    "output": "▦",
    "search": "⌕",
    "play": "▶",
    "pause": "‖",
    "stop": "■",
    "refresh": "↻",
    "settings": "⚙",
    "folder": "▣",
    "file": "▧",
    "chart": "◰",
    "table": "▥",
    "console": "⌨",
    "panel": "▤",
    "spark": "✦",
    "check": "✓",
    "close": "×",
    "warning": "⚠",
}


def resolve_icon(icon: str | None) -> str:
    key = clean_text(icon).lower()
    if not key:
        return ""
    return ICON_GLYPHS.get(key, key[:1])


def icon_text(label: str, icon: str | None = None) -> str:
    glyph = resolve_icon(icon)
    clean_label = clean_text(label)
    if glyph and clean_label:
        return f"{glyph}  {clean_label}"
    if glyph:
        return glyph
    return clean_label

