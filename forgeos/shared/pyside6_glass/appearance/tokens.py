from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .profile import AppearanceProfile, EffectsProfile


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _duration_for_level(level: str) -> int:
    mapping = {
        'off': 0,
        'subtle': 120,
        'standard': 170,
        'rich': 240,
    }
    return mapping.get(str(level or '').strip().lower(), 170)


@dataclass(frozen=True, slots=True)
class AppearanceTokens:
    theme_id: str
    density: str
    typography_scale: str
    tab_density: str
    tab_variant: str
    border_strength_scale: float
    surface_opacity_scale: float
    blur_intensity_scale: float
    elevation_scale: float
    corner_radius_scale: float
    glow_intensity: float
    shadow_blur: float
    shadow_alpha: int
    shadow_offset_y: float
    highlight_strength: float
    neon_intensity: float
    gaussian_softness: float
    noise_strength: float
    motion_enabled: bool
    motion_duration_ms: int

    def to_stylesheet_kwargs(self) -> dict[str, Any]:
        return {
            'theme_id': self.theme_id,
            'density': self.density,
            'typography_scale': self.typography_scale,
            'tab_density': self.tab_density,
            'tab_variant': self.tab_variant,
            'border_strength_scale': self.border_strength_scale,
            'surface_opacity_scale': self.surface_opacity_scale,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def resolve_appearance_tokens(
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
) -> AppearanceTokens:
    normalized_profile = profile.normalized()
    normalized_effects = (effects or EffectsProfile.from_appearance(normalized_profile)).normalized()
    shadow_depth = _clamp(normalized_effects.shadow_depth * max(0.0, normalized_profile.elevation_scale), 0.0, 3.0)
    shadow_blur = round(16.0 + (shadow_depth * 14.0), 2)
    shadow_alpha = int(round(36 + (shadow_depth * 32)))
    shadow_offset_y = round(3.0 + (shadow_depth * 4.0), 2)
    motion_enabled = (
        normalized_effects.motion_enabled
        and not normalized_profile.reduced_motion
        and normalized_profile.animation_level != 'off'
    )
    return AppearanceTokens(
        theme_id=normalized_profile.theme_id,
        density=normalized_profile.density,
        typography_scale=normalized_profile.typography_scale,
        tab_density=normalized_profile.tab_density,
        tab_variant=normalized_profile.tab_variant,
        border_strength_scale=round(_clamp(normalized_profile.border_strength_scale, 0.2, 2.5), 4),
        surface_opacity_scale=round(_clamp(normalized_profile.surface_opacity_scale, 0.3, 1.6), 4),
        blur_intensity_scale=round(_clamp(normalized_profile.blur_intensity_scale, 0.0, 3.0), 4),
        elevation_scale=round(_clamp(normalized_profile.elevation_scale, 0.0, 3.0), 4),
        corner_radius_scale=round(_clamp(normalized_profile.corner_radius_scale, 0.3, 3.0), 4),
        glow_intensity=round(_clamp(normalized_effects.glow_intensity, 0.0, 2.0), 4),
        shadow_blur=shadow_blur,
        shadow_alpha=max(0, min(255, shadow_alpha)),
        shadow_offset_y=shadow_offset_y,
        highlight_strength=round(_clamp(normalized_effects.highlight_strength, 0.0, 2.0), 4),
        neon_intensity=round(_clamp(normalized_effects.neon_intensity, 0.0, 3.0), 4),
        gaussian_softness=round(_clamp(normalized_effects.gaussian_softness, 0.0, 1.0), 4),
        noise_strength=round(_clamp(normalized_effects.noise_strength, 0.0, 1.0), 4),
        motion_enabled=motion_enabled,
        motion_duration_ms=_duration_for_level(normalized_profile.animation_level) if motion_enabled else 0,
    )


__all__ = [
    'AppearanceTokens',
    'resolve_appearance_tokens',
]
