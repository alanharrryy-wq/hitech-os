from __future__ import annotations

"""Compatibility shim for legacy Atlas palette resolution.

New code should not depend on this module. It survives only so older callers
can still obtain a backdrop-compatible atmosphere palette while the refactor
lands across the rest of the repo.
"""

import re
from typing import TYPE_CHECKING, Any, Callable

from PySide6.QtGui import QColor

from .contracts import DEFAULT_THEME_ID
from .theme import get_theme_manifest

if TYPE_CHECKING:
    from .backdrop import _AtmospherePalette

_RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _clean_token(value: Any, fallback: str = '') -> str:
    token = str(value or '').strip()
    return token or fallback


def _qcolor_from_token(value: Any, *, fallback: str = '#808080', alpha_override: float | None = None) -> QColor:
    cleaned = _clean_token(value, fallback)
    match = _RGBA_PATTERN.match(cleaned)
    if match is not None:
        r_raw, g_raw, b_raw, alpha_raw = match.groups()
        color = QColor(
            max(0, min(255, int(r_raw))),
            max(0, min(255, int(g_raw))),
            max(0, min(255, int(b_raw))),
        )
        alpha = float(alpha_override) if alpha_override is not None else float(alpha_raw)
        color.setAlphaF(max(0.0, min(1.0, alpha)))
        return color
    color = QColor(cleaned)
    if not color.isValid():
        color = QColor(fallback)
    if alpha_override is not None:
        color.setAlphaF(max(0.0, min(1.0, float(alpha_override))))
    return color


def _mix(a: QColor, b: QColor, ratio: float) -> QColor:
    t = max(0.0, min(1.0, float(ratio)))
    inv = 1.0 - t
    return QColor(
        int((a.red() * inv) + (b.red() * t)),
        int((a.green() * inv) + (b.green() * t)),
        int((a.blue() * inv) + (b.blue() * t)),
        int((a.alpha() * inv) + (b.alpha() * t)),
    )


def resolve_atlas_glass_palette(
    theme_id: str,
    variant: str,
    *,
    palette_factory: Callable[..., '_AtmospherePalette'],
) -> '_AtmospherePalette':
    manifest = get_theme_manifest(theme_id or DEFAULT_THEME_ID)
    palette = manifest.palette
    selector_variant = _clean_token(variant, 'selector').lower() != 'progress'

    shell_top = _qcolor_from_token(getattr(palette, 'shell_top', '#51545b'))
    shell_bottom = _qcolor_from_token(getattr(palette, 'shell_bottom', '#3d4046'))
    chrome_top = _qcolor_from_token(getattr(palette, 'chrome_top', '#ffffff'), alpha_override=0.12)
    chrome_bottom = _qcolor_from_token(getattr(palette, 'chrome_bottom', '#e4e9f0'), alpha_override=0.08)
    border = _qcolor_from_token(getattr(palette, 'shell_border', '#f2f5f8'))
    accent = _qcolor_from_token(getattr(palette, 'accent', '#e2e6eb'))
    accent_soft = _qcolor_from_token(getattr(palette, 'accent_soft', '#d7dce4'), alpha_override=0.18)

    canvas_top = _mix(shell_top, chrome_top, 0.18)
    canvas_bottom = _mix(shell_bottom, chrome_bottom, 0.10)
    wash = _mix(chrome_top, chrome_bottom, 0.5)
    wash.setAlphaF(0.05 if selector_variant else 0.07)
    line = _mix(border, accent_soft, 0.35)
    line.setAlphaF(0.10)
    sheen = QColor(255, 255, 255, 36)
    orb_a = QColor(accent)
    orb_a.setAlphaF(0.18 if selector_variant else 0.15)
    orb_b = QColor(border)
    orb_b.setAlphaF(0.15 if selector_variant else 0.11)
    orb_c = QColor(accent_soft)
    orb_c.setAlphaF(0.10)
    sparkle = QColor(255, 255, 255, 190)
    star_soft = QColor(255, 255, 255, 48)
    star_bright = QColor(255, 255, 255, 112)

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


__all__ = ['resolve_atlas_glass_palette']
