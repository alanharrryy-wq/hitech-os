from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..contracts import SUPPORTED_VISUAL_LEVELS
from .profile import AppearanceProfile, EffectsProfile


_DENSE_OPERATING_MODES = {'operator', 'monitoring', 'dashboard'}


def normalize_visual_level(value: Any, default: str = 'standard') -> str:
    token = str(value or '').strip().lower()
    if token in SUPPORTED_VISUAL_LEVELS:
        return token
    return default


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def resolve_effective_visual_level(
    requested_level: Any,
    *,
    experience_mode: Any = 'default',
    reduced_motion: bool = False,
    high_contrast_mode: bool = False,
    data_density_bias: float = 0.0,
    performance_sensitive: bool = False,
) -> str:
    level = normalize_visual_level(requested_level, 'standard')
    mode = str(experience_mode or 'default').strip().lower()
    density_bias = _clamp(float(data_density_bias), -1.0, 1.0)
    if performance_sensitive:
        level = 'performance'
    elif mode in _DENSE_OPERATING_MODES and density_bias >= 0.25 and level in {'premium', 'showcase'}:
        level = 'performance'
    elif mode in _DENSE_OPERATING_MODES and density_bias >= 0.5 and level == 'standard':
        level = 'performance'
    if high_contrast_mode and level == 'showcase':
        level = 'premium'
    if reduced_motion:
        if level == 'showcase':
            level = 'premium'
        elif level == 'premium':
            level = 'standard'
    return level


def _profile_for_level(profile: AppearanceProfile, level: str) -> AppearanceProfile:
    normalized = profile.normalized()
    if level == 'performance':
        return normalized.with_updates(
            animation_level='off' if normalized.reduced_motion else 'subtle',
            spacing_scale=min(normalized.spacing_scale, 1.0),
            padding_scale=min(normalized.padding_scale, 1.0),
            blur_intensity_scale=min(normalized.blur_intensity_scale, 0.7),
            elevation_scale=min(normalized.elevation_scale, 0.95),
            breathing_room_scale=min(normalized.breathing_room_scale, 1.0),
            data_density_bias=max(normalized.data_density_bias, 0.3),
        )
    if level == 'standard':
        return normalized.with_updates(
            animation_level='off' if normalized.reduced_motion else ('standard' if normalized.animation_level == 'rich' else normalized.animation_level),
            blur_intensity_scale=_clamp(normalized.blur_intensity_scale, 0.55, 1.25),
            elevation_scale=_clamp(normalized.elevation_scale, 0.55, 1.35),
            breathing_room_scale=_clamp(normalized.breathing_room_scale, 0.85, 1.25),
        )
    if level == 'premium':
        return normalized.with_updates(
            animation_level='off' if normalized.reduced_motion else ('rich' if normalized.animation_level == 'off' else normalized.animation_level),
            blur_intensity_scale=max(normalized.blur_intensity_scale, 0.9),
            elevation_scale=max(normalized.elevation_scale, 0.95),
            border_strength_scale=max(normalized.border_strength_scale, 1.02),
            surface_opacity_scale=max(normalized.surface_opacity_scale, 1.02),
            breathing_room_scale=max(normalized.breathing_room_scale, 0.95),
        )
    # showcase
    return normalized.with_updates(
        animation_level='off' if normalized.reduced_motion else 'rich',
        blur_intensity_scale=max(normalized.blur_intensity_scale, 1.1),
        elevation_scale=max(normalized.elevation_scale, 1.15),
        border_strength_scale=max(normalized.border_strength_scale, 1.08),
        surface_opacity_scale=max(normalized.surface_opacity_scale, 1.04),
        breathing_room_scale=max(normalized.breathing_room_scale, 1.0),
    )


def _effects_for_level(
    effects: EffectsProfile,
    *,
    level: str,
    reduced_motion: bool,
) -> EffectsProfile:
    normalized = effects.normalized()
    if level == 'performance':
        return normalized.with_updates(
            glow_intensity=min(normalized.glow_intensity, 0.14),
            shadow_depth=min(normalized.shadow_depth, 0.8),
            highlight_strength=min(normalized.highlight_strength, 0.14),
            neon_intensity=min(normalized.neon_intensity, 0.0),
            gaussian_softness=min(normalized.gaussian_softness, 0.42),
            noise_strength=min(normalized.noise_strength, 0.0),
            motion_enabled=False if reduced_motion else normalized.motion_enabled,
        )
    if level == 'standard':
        return normalized.with_updates(
            glow_intensity=_clamp(normalized.glow_intensity, 0.1, 0.28),
            shadow_depth=_clamp(normalized.shadow_depth, 0.65, 1.35),
            highlight_strength=_clamp(normalized.highlight_strength, 0.12, 0.24),
            neon_intensity=min(normalized.neon_intensity, 0.35),
            gaussian_softness=_clamp(normalized.gaussian_softness, 0.25, 0.58),
            noise_strength=min(normalized.noise_strength, 0.08),
            motion_enabled=False if reduced_motion else normalized.motion_enabled,
        )
    if level == 'premium':
        return normalized.with_updates(
            glow_intensity=max(normalized.glow_intensity, 0.2),
            shadow_depth=max(normalized.shadow_depth, 0.95),
            highlight_strength=max(normalized.highlight_strength, 0.2),
            neon_intensity=min(max(normalized.neon_intensity, 0.05), 0.65),
            gaussian_softness=max(normalized.gaussian_softness, 0.42),
            noise_strength=min(max(normalized.noise_strength, 0.01), 0.16),
            motion_enabled=False if reduced_motion else normalized.motion_enabled,
        )
    # showcase
    return normalized.with_updates(
        glow_intensity=max(normalized.glow_intensity, 0.26),
        shadow_depth=max(normalized.shadow_depth, 1.05),
        highlight_strength=max(normalized.highlight_strength, 0.24),
        neon_intensity=min(max(normalized.neon_intensity, 0.22), 0.92),
        gaussian_softness=max(normalized.gaussian_softness, 0.5),
        noise_strength=min(max(normalized.noise_strength, 0.04), 0.22),
        motion_enabled=False if reduced_motion else normalized.motion_enabled,
    )


@dataclass(frozen=True, slots=True)
class VisualLevelResolution:
    requested_level: str
    effective_level: str
    profile: AppearanceProfile
    effects: EffectsProfile
    source: str = 'visual_level'

    def to_dict(self) -> dict[str, Any]:
        return {
            'requested_level': self.requested_level,
            'effective_level': self.effective_level,
            'profile': self.profile.to_dict(),
            'effects': self.effects.to_dict(),
            'source': self.source,
        }


def resolve_visual_level(
    profile: AppearanceProfile,
    effects: EffectsProfile | None = None,
    *,
    requested_level: Any = 'standard',
    performance_sensitive: bool = False,
) -> VisualLevelResolution:
    normalized_profile = profile.normalized()
    normalized_effects = (effects or EffectsProfile.from_appearance(normalized_profile)).normalized()
    effective = resolve_effective_visual_level(
        requested_level,
        experience_mode=normalized_profile.experience_mode,
        reduced_motion=normalized_profile.reduced_motion,
        high_contrast_mode=normalized_profile.high_contrast_mode,
        data_density_bias=normalized_profile.data_density_bias,
        performance_sensitive=performance_sensitive,
    )
    next_profile = _profile_for_level(normalized_profile, effective)
    next_effects = _effects_for_level(
        normalized_effects,
        level=effective,
        reduced_motion=next_profile.reduced_motion or next_profile.animation_level == 'off',
    )
    return VisualLevelResolution(
        requested_level=normalize_visual_level(requested_level, 'standard'),
        effective_level=effective,
        profile=next_profile,
        effects=next_effects,
        source=f'visual_level:{effective}',
    )


__all__ = [
    'VisualLevelResolution',
    'normalize_visual_level',
    'resolve_effective_visual_level',
    'resolve_visual_level',
]

