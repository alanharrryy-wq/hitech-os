from __future__ import annotations

from dataclasses import dataclass
import re

from .palette_registry import GlassPalette

_RGBA_PATTERN = re.compile(
    r"^rgba\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*([01](?:\.\d+)?)\s*\)$",
    re.IGNORECASE,
)


def _scale_rgba_alpha(color: str, scale: float) -> str:
    token = str(color or "").strip()
    match = _RGBA_PATTERN.match(token)
    if match is None:
        return token
    r_raw, g_raw, b_raw, alpha_raw = match.groups()
    r = max(0, min(255, int(r_raw)))
    g = max(0, min(255, int(g_raw)))
    b = max(0, min(255, int(b_raw)))
    alpha = max(0.0, min(1.0, float(alpha_raw) * float(scale)))
    alpha_text = f"{alpha:.3f}".rstrip("0").rstrip(".")
    return f"rgba({r}, {g}, {b}, {alpha_text})"


def apply_surface_opacity_scale(palette: GlassPalette, scale: float) -> GlassPalette:
    if abs(float(scale) - 1.0) < 0.0001:
        return palette
    surface_keys = (
        "shell_top",
        "shell_bottom",
        "chrome_top",
        "chrome_bottom",
        "card_top",
        "card_bottom",
        "accent_soft",
        "button_top",
        "button_bottom",
        "danger_top",
        "danger_bottom",
        "warning_top",
        "warning_bottom",
        "success_top",
        "success_bottom",
        "input_bg",
        "progress_bg",
        "tab_bg",
        "tab_active_bg",
        "tab_hold_bg",
        "tab_pending_bg",
        "tab_warning_bg",
    )
    overrides = {key: _scale_rgba_alpha(getattr(palette, key), scale) for key in surface_keys}
    return palette.with_overrides(overrides)


@dataclass(frozen=True, slots=True)
class SurfaceMaterialSpec:
    palette: GlassPalette
    border_px: int
    tab_border_style: str
    tab_radius: int


def build_surface_material_spec(
    palette: GlassPalette,
    *,
    border_strength_scale: float = 1.0,
    surface_opacity_scale: float = 1.0,
    tab_variant: str = "glass",
    tab_radius: int = 12,
    pill_radius: int = 999,
) -> SurfaceMaterialSpec:
    border_scale = max(0.5, min(2.0, float(border_strength_scale)))
    surface_scale = max(0.5, min(1.4, float(surface_opacity_scale)))
    scaled_palette = apply_surface_opacity_scale(palette, surface_scale)
    variant = str(tab_variant or "glass").strip().lower()
    is_pill = variant == "pill"
    tab_border_style = "solid" if variant in {"standard", "glass"} else "none"
    return SurfaceMaterialSpec(
        palette=scaled_palette,
        border_px=max(1, int(round(1 * border_scale))),
        tab_border_style=tab_border_style,
        tab_radius=pill_radius if is_pill else tab_radius,
    )


__all__ = [
    "SurfaceMaterialSpec",
    "apply_surface_opacity_scale",
    "build_surface_material_spec",
]
