from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Callable

from PySide6.QtGui import QColor

from .contracts import DEFAULT_THEME_ID
from .theme import get_theme_manifest

if TYPE_CHECKING:
    from .backdrop import _GlassPalette


_RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _clean_token(value: Any, fallback: str = "") -> str:
    token = str(value or "").strip()
    return token or fallback


def _qcolor_from_value(value: Any, alpha: float = 1.0) -> QColor:
    cleaned = _clean_token(value)
    color = QColor(cleaned or "#808080")
    if not color.isValid():
        color = QColor("#808080")
    color.setAlphaF(max(0.0, min(1.0, float(alpha))))
    return color


def _qcolor_from_token(value: Any, *, fallback: str = "#808080") -> QColor:
    cleaned = _clean_token(value, fallback)
    color = QColor(cleaned)
    if not color.isValid():
        color = QColor(fallback)
    return color


def _hex_from_token(value: Any, *, fallback: str = "#808080") -> str:
    cleaned = _clean_token(value, fallback)
    match = _RGBA_PATTERN.match(cleaned)
    if match is not None:
        r_raw, g_raw, b_raw, alpha_raw = match.groups()
        return f"#{max(0, min(255, int(r_raw))):02x}{max(0, min(255, int(g_raw))):02x}{max(0, min(255, int(b_raw))):02x}"
    color = QColor(cleaned)
    if not color.isValid():
        color = QColor(fallback)
    return color.name(QColor.HexRgb)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    text = _clean_token(value).lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return (127, 127, 127)
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except Exception:
        return (127, 127, 127)


def _mix_hex(a: str, b: str, ratio: float) -> str:
    ratio = _clamp(ratio, 0.0, 1.0)
    ar, ag, ab = _hex_to_rgb(a)
    br, bg, bb = _hex_to_rgb(b)
    rr = int(round((ar * (1.0 - ratio)) + (br * ratio)))
    rg = int(round((ag * (1.0 - ratio)) + (bg * ratio)))
    rb = int(round((ab * (1.0 - ratio)) + (bb * ratio)))
    return f"#{rr:02x}{rg:02x}{rb:02x}"


def _is_silver_theme_id(theme_id: str) -> bool:
    lowered = _clean_token(theme_id, DEFAULT_THEME_ID).lower()
    return any(tag in lowered for tag in ("silver", "frost", "argent", "mercury"))


def _resolve_palette_token(palette: object, key: str, fallback: str) -> str:
    return _hex_from_token(getattr(palette, key, ""), fallback=fallback)


def _resolve_bridge_tokens(theme_id: str) -> tuple[dict[str, str], bool]:
    manifest = get_theme_manifest(theme_id)
    palette = manifest.palette
    t = {
        "canvas_bg": _resolve_palette_token(palette, "canvas_bg", _resolve_palette_token(palette, "shell_bottom", "#0f1824")),
        "header_fill": _resolve_palette_token(palette, "header_fill", _resolve_palette_token(palette, "shell_top", "#1a2836")),
        "legend_fill": _resolve_palette_token(palette, "legend_fill", _resolve_palette_token(palette, "card_top", "#1f2f42")),
        "focus": _resolve_palette_token(palette, "focus", _resolve_palette_token(palette, "accent", "#7dd3fc")),
        "legend_stroke": _resolve_palette_token(palette, "legend_stroke", _resolve_palette_token(palette, "card_border", "#d5e2f4")),
        "header_stroke": _resolve_palette_token(palette, "header_stroke", _resolve_palette_token(palette, "shell_border", "#d5e2f4")),
        "halo_a": _resolve_palette_token(palette, "halo_a", _resolve_palette_token(palette, "accent", "#22d3ee")),
        "halo_b": _resolve_palette_token(palette, "halo_b", _resolve_palette_token(palette, "button_border", "#8b5cf6")),
    }
    dark = bool(getattr(manifest, "is_dark", _qcolor_from_token(t["canvas_bg"]).lightnessF() < 0.52))
    return t, dark


def resolve_atlas_glass_palette(
    theme_id: str,
    variant: str,
    *,
    palette_factory: Callable[..., "_GlassPalette"],
) -> "_GlassPalette":
    t, dark = _resolve_bridge_tokens(theme_id)
    silver_theme = _is_silver_theme_id(theme_id)

    selector_variant = _clean_token(variant).lower() != "progress"

    if silver_theme:
        canvas_top = _qcolor_from_value("#04070d", 1.0)
        canvas_bottom = _qcolor_from_value("#0f1824", 1.0)
        wash = _qcolor_from_value("#eef6ff", 0.022 if selector_variant else 0.028)
        border = _qcolor_from_value("#e8f6ff", 0.20 if selector_variant else 0.16)
        line = _qcolor_from_value("#8cefff", 0.05)
        sheen = _qcolor_from_value("#ffffff", 0.08)
        orb_a = _qcolor_from_value("#eff7ff", 0.18 if selector_variant else 0.14)
        orb_b = _qcolor_from_value("#8cefff", 0.15 if selector_variant else 0.12)
        orb_c = _qcolor_from_value("#d7e1ff", 0.10 if selector_variant else 0.08)
        sparkle = _qcolor_from_value("#ffffff", 0.88)
        star_soft = _qcolor_from_value("#eef6ff", 0.18)
        star_bright = _qcolor_from_value("#ffffff", 0.62)

        return palette_factory(
            canvas_top=canvas_top,
            canvas_bottom=canvas_bottom,
            wash=wash,
            border=border,
            line=line,
            sheen=sheen,
            orb_a=orb_a,
            orb_b=orb_b,
            orb_c=orb_c,
            sparkle=sparkle,
            star_soft=star_soft,
            star_bright=star_bright,
        )

    canvas_top = _qcolor_from_value(
        _mix_hex(t["canvas_bg"], t["header_fill"], 0.18 if dark else 0.05),
        1.0,
    )
    canvas_bottom = _qcolor_from_value(
        _mix_hex(t["canvas_bg"], t["legend_fill"], 0.32 if dark else 0.10),
        1.0,
    )
    wash = _qcolor_from_value(
        _mix_hex(t["header_fill"], t["legend_fill"], 0.50 if dark else 0.20),
        0.30 if dark else 0.76,
    )
    border = _qcolor_from_value(
        _mix_hex(t["focus"], t["legend_stroke"], 0.26 if dark else 0.12),
        0.26 if dark else 0.42,
    )
    line = _qcolor_from_value(t["header_stroke"], 0.10 if dark else 0.18)
    sheen = _qcolor_from_value("#ffffff", 0.09 if dark else 0.16)
    orb_a = _qcolor_from_value(
        t["halo_a"],
        0.22 if selector_variant and dark else 0.16 if selector_variant else 0.18 if dark else 0.12,
    )
    orb_b = _qcolor_from_value(
        t["halo_b"],
        0.16 if selector_variant and dark else 0.11 if selector_variant else 0.14 if dark else 0.10,
    )
    orb_c = _qcolor_from_value(
        t["focus"],
        0.14 if dark else 0.09,
    )
    sparkle = _qcolor_from_value("#ffffff", 0.34 if dark else 0.42)
    star_soft = _qcolor_from_value("#ffffff", 0.12 if dark else 0.18)
    star_bright = _qcolor_from_value("#ffffff", 0.28 if dark else 0.34)

    return palette_factory(
        canvas_top=canvas_top,
        canvas_bottom=canvas_bottom,
        wash=wash,
        border=border,
        line=line,
        sheen=sheen,
        orb_a=orb_a,
        orb_b=orb_b,
        orb_c=orb_c,
        sparkle=sparkle,
        star_soft=star_soft,
        star_bright=star_bright,
    )
