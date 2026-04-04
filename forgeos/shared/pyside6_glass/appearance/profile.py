from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

from ..config import GlassTemplateConfig, GlassThemeConfig, GlassVisualScaleConfig
from ..contracts import (
    DEFAULT_THEME_ID,
    SUPPORTED_ANIMATION_LEVELS,
    SUPPORTED_DENSITY,
    SUPPORTED_EXPERIENCE_MODES,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_VARIANTS,
    SUPPORTED_TYPOGRAPHY_SCALE,
)


def _choice(value: str | None, allowed: tuple[str, ...], default: str) -> str:
    normalized = str(value or '').strip().lower()
    if normalized in allowed:
        return normalized
    return default


def _clamp(value: float, minimum: float, maximum: float, default: float) -> float:
    try:
        parsed = float(value)
    except Exception:
        parsed = float(default)
    return max(minimum, min(maximum, parsed))


@dataclass(frozen=True, slots=True)
class AppearanceProfile:
    """Normalized visual control plane for the framework.

    This profile is intentionally smaller and more stable than the full
    ``GlassTemplateConfig`` tree. It concentrates the values that affect
    theme selection, density, typography, and visual scaling so runtime
    systems can react to one object instead of spelunking through nested
    config every time a visual preference changes.
    """

    theme_id: str = DEFAULT_THEME_ID
    density: str = 'comfortable'
    typography_scale: str = 'lg'
    tab_density: str = 'comfortable'
    tab_variant: str = 'glass'
    experience_mode: str = 'default'
    animation_level: str = 'standard'
    reduced_motion: bool = False
    high_contrast_mode: bool = False
    spacing_scale: float = 1.0
    padding_scale: float = 1.0
    icon_scale: float = 1.0
    control_height_scale: float = 1.0
    corner_radius_scale: float = 1.0
    border_strength_scale: float = 1.0
    surface_opacity_scale: float = 1.0
    blur_intensity_scale: float = 1.0
    elevation_scale: float = 1.0
    breathing_room_scale: float = 1.0
    data_density_bias: float = 0.0

    def normalized(self) -> AppearanceProfile:
        return replace(
            self,
            theme_id=str(self.theme_id or DEFAULT_THEME_ID).strip().lower() or DEFAULT_THEME_ID,
            density=_choice(self.density, SUPPORTED_DENSITY, 'comfortable'),
            typography_scale=_choice(self.typography_scale, SUPPORTED_TYPOGRAPHY_SCALE, 'lg'),
            tab_density=_choice(self.tab_density, SUPPORTED_TAB_DENSITY, 'comfortable'),
            tab_variant=_choice(self.tab_variant, SUPPORTED_TAB_VARIANTS, 'glass'),
            experience_mode=_choice(self.experience_mode, SUPPORTED_EXPERIENCE_MODES, 'default'),
            animation_level=_choice(self.animation_level, SUPPORTED_ANIMATION_LEVELS, 'standard'),
            spacing_scale=_clamp(self.spacing_scale, 0.2, 3.0, 1.0),
            padding_scale=_clamp(self.padding_scale, 0.2, 3.0, 1.0),
            icon_scale=_clamp(self.icon_scale, 0.4, 3.0, 1.0),
            control_height_scale=_clamp(self.control_height_scale, 0.4, 3.0, 1.0),
            corner_radius_scale=_clamp(self.corner_radius_scale, 0.3, 3.0, 1.0),
            border_strength_scale=_clamp(self.border_strength_scale, 0.2, 2.5, 1.0),
            surface_opacity_scale=_clamp(self.surface_opacity_scale, 0.3, 1.6, 1.0),
            blur_intensity_scale=_clamp(self.blur_intensity_scale, 0.0, 3.0, 1.0),
            elevation_scale=_clamp(self.elevation_scale, 0.0, 3.0, 1.0),
            breathing_room_scale=_clamp(self.breathing_room_scale, 0.2, 3.0, 1.0),
            data_density_bias=_clamp(self.data_density_bias, -1.0, 1.0, 0.0),
        )

    def with_updates(self, **changes: Any) -> AppearanceProfile:
        return replace(self, **changes).normalized()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.normalized())

    @classmethod
    def from_visual_scale(
        cls,
        visual_scale: GlassVisualScaleConfig,
        *,
        theme_id: str = DEFAULT_THEME_ID,
        density: str = 'comfortable',
        typography_scale: str = 'lg',
        tab_density: str = 'comfortable',
        tab_variant: str = 'glass',
        experience_mode: str = 'default',
        animation_level: str = 'standard',
        reduced_motion: bool = False,
        high_contrast_mode: bool = False,
    ) -> AppearanceProfile:
        return cls(
            theme_id=theme_id,
            density=density,
            typography_scale=typography_scale,
            tab_density=tab_density,
            tab_variant=tab_variant,
            experience_mode=experience_mode,
            animation_level=animation_level,
            reduced_motion=bool(reduced_motion),
            high_contrast_mode=bool(high_contrast_mode),
            spacing_scale=visual_scale.spacing_scale,
            padding_scale=visual_scale.padding_scale,
            icon_scale=visual_scale.icon_scale,
            control_height_scale=visual_scale.control_height_scale,
            corner_radius_scale=visual_scale.corner_radius_scale,
            border_strength_scale=visual_scale.border_strength_scale,
            surface_opacity_scale=visual_scale.surface_opacity_scale,
            blur_intensity_scale=visual_scale.blur_intensity_scale,
            elevation_scale=visual_scale.elevation_scale,
            breathing_room_scale=visual_scale.breathing_room_scale,
            data_density_bias=visual_scale.data_density_bias,
        ).normalized()

    @classmethod
    def from_theme_config(
        cls,
        theme: GlassThemeConfig,
        *,
        high_contrast_mode: bool = False,
    ) -> AppearanceProfile:
        visual_scale = theme.visual_scale.normalized()
        animation = theme.animation.normalized()
        return cls.from_visual_scale(
            visual_scale,
            theme_id=theme.theme_id,
            density=theme.density,
            typography_scale=theme.typography.scale,
            tab_density=theme.density,
            tab_variant='glass',
            experience_mode=theme.experience_mode,
            animation_level=animation.level,
            reduced_motion=animation.reduced_motion,
            high_contrast_mode=high_contrast_mode,
        )

    @classmethod
    def from_template_config(cls, config: GlassTemplateConfig) -> AppearanceProfile:
        normalized = config.normalized()
        return cls.from_visual_scale(
            normalized.theme.visual_scale,
            theme_id=normalized.theme.theme_id,
            density=normalized.theme.density,
            typography_scale=normalized.theme.typography.scale,
            tab_density=normalized.tabs.density,
            tab_variant=normalized.tabs.variant,
            experience_mode=normalized.theme.experience_mode,
            animation_level=normalized.theme.animation.level,
            reduced_motion=normalized.theme.animation.reduced_motion,
            high_contrast_mode=normalized.accessibility.high_contrast_mode,
        )


@dataclass(frozen=True, slots=True)
class EffectsProfile:
    """High-level visual FX controls.

    Values are dimensionless on purpose. Later rounds can translate them to
    concrete ``QGraphicsEffect`` or ``QPainter`` values without exposing raw
    widget implementation details to the rest of the framework.
    """

    glow_intensity: float = 0.18
    shadow_depth: float = 1.0
    highlight_strength: float = 0.18
    neon_intensity: float = 0.0
    gaussian_softness: float = 0.45
    noise_strength: float = 0.0
    motion_enabled: bool = True
    backdrop_blur_enabled: bool = True
    shadow_enabled: bool = True
    use_accent_for_glow: bool = True

    def normalized(self) -> EffectsProfile:
        return replace(
            self,
            glow_intensity=_clamp(self.glow_intensity, 0.0, 2.0, 0.18),
            shadow_depth=_clamp(self.shadow_depth, 0.0, 3.0, 1.0),
            highlight_strength=_clamp(self.highlight_strength, 0.0, 2.0, 0.18),
            neon_intensity=_clamp(self.neon_intensity, 0.0, 3.0, 0.0),
            gaussian_softness=_clamp(self.gaussian_softness, 0.0, 1.0, 0.45),
            noise_strength=_clamp(self.noise_strength, 0.0, 1.0, 0.0),
        )

    def with_updates(self, **changes: Any) -> EffectsProfile:
        return replace(self, **changes).normalized()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self.normalized())

    @classmethod
    def from_appearance(cls, profile: AppearanceProfile) -> EffectsProfile:
        normalized = profile.normalized()
        motion_enabled = not normalized.reduced_motion and normalized.animation_level != 'off'
        glow_base = 0.16 + (0.06 if normalized.high_contrast_mode else 0.0)
        gaussian_softness = 0.30 + (0.12 * min(1.0, normalized.blur_intensity_scale))
        highlight_strength = 0.16 + (0.04 * max(0.0, normalized.surface_opacity_scale - 1.0))
        return cls(
            glow_intensity=glow_base,
            shadow_depth=max(0.0, normalized.elevation_scale),
            highlight_strength=highlight_strength,
            neon_intensity=0.0,
            gaussian_softness=gaussian_softness,
            noise_strength=0.0,
            motion_enabled=motion_enabled,
            backdrop_blur_enabled=normalized.blur_intensity_scale > 0.0,
            shadow_enabled=normalized.elevation_scale > 0.0,
            use_accent_for_glow=True,
        ).normalized()


@dataclass(frozen=True, slots=True)
class AppearanceSnapshot:
    profile: AppearanceProfile
    effects: EffectsProfile
    preset_name: str | None = None
    source: str = 'manual'

    def to_dict(self) -> dict[str, Any]:
        return {
            'profile': self.profile.to_dict(),
            'effects': self.effects.to_dict(),
            'preset_name': self.preset_name,
            'source': str(self.source or 'manual'),
        }


@dataclass(frozen=True, slots=True)
class AppearanceBundle:
    profile: AppearanceProfile
    effects: EffectsProfile

    def normalized(self) -> AppearanceBundle:
        return AppearanceBundle(
            profile=self.profile.normalized(),
            effects=self.effects.normalized(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            'profile': self.profile.to_dict(),
            'effects': self.effects.to_dict(),
        }


def appearance_from_mapping(payload: Mapping[str, Any]) -> AppearanceBundle:
    profile_payload = payload.get('profile') or {}
    effects_payload = payload.get('effects') or {}
    profile = AppearanceProfile(**dict(profile_payload)).normalized()
    effects = EffectsProfile(**dict(effects_payload)).normalized()
    return AppearanceBundle(profile=profile, effects=effects)


__all__ = [
    'AppearanceBundle',
    'AppearanceProfile',
    'AppearanceSnapshot',
    'EffectsProfile',
    'appearance_from_mapping',
]
