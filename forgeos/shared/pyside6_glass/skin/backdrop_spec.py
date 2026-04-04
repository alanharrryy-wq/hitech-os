from __future__ import annotations

from dataclasses import dataclass
import re

from PySide6.QtGui import QColor

from ..appearance import AppearanceSnapshot, resolve_appearance_tokens
from .palette_registry import get_palette

_RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _qcolor(token: str, *, alpha_override: float | None = None) -> QColor:
    value = str(token or "").strip()
    match = _RGBA_PATTERN.match(value)
    if match is not None:
        r_raw, g_raw, b_raw, alpha_raw = match.groups()
        color = QColor(
            max(0, min(255, int(r_raw))),
            max(0, min(255, int(g_raw))),
            max(0, min(255, int(b_raw))),
        )
        alpha = float(alpha_override) if alpha_override is not None else float(alpha_raw)
        color.setAlphaF(_clamp(alpha, 0.0, 1.0))
        return color
    color = QColor(value)
    if alpha_override is not None:
        color.setAlphaF(_clamp(alpha_override, 0.0, 1.0))
    return color


def _mix(a: QColor, b: QColor, ratio: float) -> QColor:
    t = _clamp(ratio, 0.0, 1.0)
    inv = 1.0 - t
    return QColor(
        int((a.red() * inv) + (b.red() * t)),
        int((a.green() * inv) + (b.green() * t)),
        int((a.blue() * inv) + (b.blue() * t)),
        int((a.alpha() * inv) + (b.alpha() * t)),
    )


@dataclass(frozen=True, slots=True)
class BackdropMaterialSpec:
    canvas_top: QColor
    canvas_bottom: QColor
    wash: QColor
    border: QColor
    line: QColor
    sheen: QColor
    orb_a: QColor
    orb_b: QColor
    orb_c: QColor
    sparkle: QColor
    star_soft: QColor
    star_bright: QColor


def build_backdrop_spec(theme_id: str, snapshot: AppearanceSnapshot) -> BackdropMaterialSpec:
    palette = get_palette(theme_id)
    tokens = resolve_appearance_tokens(snapshot.profile, snapshot.effects)
    blur_bias = _clamp(tokens.blur_intensity_scale / 3.0, 0.0, 1.0)
    glow_bias = _clamp(tokens.glow_intensity / 2.0, 0.0, 1.0)
    neon_bias = _clamp(tokens.neon_intensity / 3.0, 0.0, 1.0)

    shell_top = _qcolor(palette.shell_top)
    shell_bottom = _qcolor(palette.shell_bottom)
    chrome_top = _qcolor(palette.chrome_top, alpha_override=0.08 + (0.08 * glow_bias))
    chrome_bottom = _qcolor(palette.chrome_bottom, alpha_override=0.06 + (0.06 * blur_bias))
    border = _qcolor(palette.shell_border, alpha_override=0.18 + (0.10 * snapshot.profile.border_strength_scale / 2.5))
    accent = _qcolor(palette.accent)
    accent_soft = _qcolor(palette.accent_soft, alpha_override=0.12 + (0.10 * glow_bias))

    canvas_top = _mix(shell_top, chrome_top, 0.16 + (0.08 * glow_bias))
    canvas_bottom = _mix(shell_bottom, chrome_bottom, 0.08 + (0.10 * blur_bias))
    wash = _mix(chrome_top, accent_soft, 0.5)
    wash.setAlphaF(0.045 + (0.035 * snapshot.profile.surface_opacity_scale / 1.6))
    line = _mix(border, accent_soft, 0.35)
    line.setAlphaF(0.08 + (0.05 * snapshot.profile.border_strength_scale / 2.5))
    sheen = QColor(255, 255, 255, int(round(28 + (32 * snapshot.effects.highlight_strength))))

    orb_a = QColor(accent)
    orb_a.setAlphaF(0.12 + (0.10 * glow_bias))
    orb_b = QColor(border)
    orb_b.setAlphaF(0.09 + (0.08 * blur_bias))
    orb_c = QColor(accent_soft)
    orb_c.setAlphaF(0.07 + (0.07 * neon_bias))

    sparkle = QColor(255, 255, 255, int(round(160 + (48 * glow_bias))))
    star_soft = QColor(255, 255, 255, int(round(20 + (40 * blur_bias))))
    star_bright = QColor(255, 255, 255, int(round(70 + (70 * glow_bias))))
    return BackdropMaterialSpec(
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


__all__ = ["BackdropMaterialSpec", "build_backdrop_spec"]
