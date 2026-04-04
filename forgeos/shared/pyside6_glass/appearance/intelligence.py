from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..data import DataState
from .levels import resolve_visual_level
from .presets import get_appearance_preset
from .profile import AppearanceProfile, EffectsProfile


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def _blend(current: float, target: float, ratio: float) -> float:
    t = _clamp(ratio, 0.0, 1.0)
    return (float(current) * (1.0 - t)) + (float(target) * t)


def _normalize_mode(value: Any) -> str:
    token = str(value or 'default').strip().lower()
    return token or 'default'


def _normalize_data_state(value: Any) -> str:
    token = str(value or DataState.READY).strip().lower()
    return DataState.normalize(token, default=DataState.READY)


@dataclass(frozen=True, slots=True)
class VisualIntelligenceContext:
    experience_mode: str = 'default'
    requested_visual_level: str = 'standard'
    preferred_preset: str | None = None
    data_state: str = DataState.READY
    reduced_motion: bool = False
    high_contrast_mode: bool = False
    data_density_bias: float = 0.0
    performance_sensitive: bool = False
    source: str = 'runtime'

    def normalized(self) -> 'VisualIntelligenceContext':
        preferred = str(self.preferred_preset or '').strip().lower() or None
        return VisualIntelligenceContext(
            experience_mode=_normalize_mode(self.experience_mode),
            requested_visual_level=str(self.requested_visual_level or 'standard').strip().lower() or 'standard',
            preferred_preset=preferred,
            data_state=_normalize_data_state(self.data_state),
            reduced_motion=bool(self.reduced_motion),
            high_contrast_mode=bool(self.high_contrast_mode),
            data_density_bias=_clamp(self.data_density_bias, -1.0, 1.0),
            performance_sensitive=bool(self.performance_sensitive),
            source=str(self.source or 'runtime').strip() or 'runtime',
        )


@dataclass(frozen=True, slots=True)
class VisualIntelligenceBundle:
    profile: AppearanceProfile
    effects: EffectsProfile
    preset_name: str | None
    requested_level: str
    effective_level: str
    source: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            'profile': self.profile.to_dict(),
            'effects': self.effects.to_dict(),
            'preset_name': self.preset_name,
            'requested_level': self.requested_level,
            'effective_level': self.effective_level,
            'source': self.source,
            'metadata': dict(self.metadata),
        }


def _select_preset(context: VisualIntelligenceContext) -> str:
    if context.preferred_preset:
        return context.preferred_preset
    if context.requested_visual_level == 'showcase':
        return 'orchestrator_lab'
    if context.experience_mode in {'dashboard', 'operator', 'monitoring', 'analyst'}:
        return 'dashboard_dense'
    if context.experience_mode in {'presentation', 'review'} or context.reduced_motion:
        return 'presentation_low_motion'
    if context.requested_visual_level == 'premium':
        return 'frosted_focus'
    return 'neutral'


def _merge_preset_profile(base: AppearanceProfile, preset: AppearanceProfile, *, mode: str) -> AppearanceProfile:
    if mode in {'dashboard', 'operator', 'monitoring', 'analyst'}:
        return base.with_updates(
            density=preset.density,
            tab_density=preset.tab_density,
            spacing_scale=_blend(base.spacing_scale, preset.spacing_scale, 0.6),
            padding_scale=_blend(base.padding_scale, preset.padding_scale, 0.65),
            data_density_bias=max(base.data_density_bias, preset.data_density_bias),
            blur_intensity_scale=_blend(base.blur_intensity_scale, preset.blur_intensity_scale, 0.55),
            elevation_scale=_blend(base.elevation_scale, preset.elevation_scale, 0.45),
        )
    if mode in {'presentation', 'review'}:
        return base.with_updates(
            typography_scale=preset.typography_scale,
            animation_level=preset.animation_level,
            reduced_motion=base.reduced_motion or preset.reduced_motion,
            spacing_scale=max(base.spacing_scale, preset.spacing_scale),
            blur_intensity_scale=_blend(base.blur_intensity_scale, preset.blur_intensity_scale, 0.5),
        )
    if mode in {'focus', 'editor', 'inspector'}:
        return base.with_updates(
            border_strength_scale=max(base.border_strength_scale, preset.border_strength_scale),
            elevation_scale=_blend(base.elevation_scale, preset.elevation_scale, 0.4),
            surface_opacity_scale=_blend(base.surface_opacity_scale, preset.surface_opacity_scale, 0.35),
        )
    return base.with_updates(
        blur_intensity_scale=_blend(base.blur_intensity_scale, preset.blur_intensity_scale, 0.35),
        elevation_scale=_blend(base.elevation_scale, preset.elevation_scale, 0.35),
        border_strength_scale=_blend(base.border_strength_scale, preset.border_strength_scale, 0.35),
        surface_opacity_scale=_blend(base.surface_opacity_scale, preset.surface_opacity_scale, 0.25),
    )


def _merge_preset_effects(base: EffectsProfile, preset: EffectsProfile, *, level: str) -> EffectsProfile:
    ratio = {
        'performance': 0.15,
        'standard': 0.28,
        'premium': 0.45,
        'showcase': 0.62,
    }.get(level, 0.28)
    return base.with_updates(
        glow_intensity=_blend(base.glow_intensity, preset.glow_intensity, ratio),
        shadow_depth=_blend(base.shadow_depth, preset.shadow_depth, ratio * 0.9),
        highlight_strength=_blend(base.highlight_strength, preset.highlight_strength, ratio),
        neon_intensity=_blend(base.neon_intensity, preset.neon_intensity, ratio),
        gaussian_softness=_blend(base.gaussian_softness, preset.gaussian_softness, ratio * 0.8),
        noise_strength=_blend(base.noise_strength, preset.noise_strength, min(0.6, ratio)),
        motion_enabled=base.motion_enabled and preset.motion_enabled,
    )


def _apply_data_state_modulation(
    profile: AppearanceProfile,
    effects: EffectsProfile,
    *,
    data_state: str,
) -> tuple[AppearanceProfile, EffectsProfile]:
    if data_state == DataState.LOADING:
        return profile, effects.with_updates(
            glow_intensity=max(effects.glow_intensity, 0.12),
            highlight_strength=max(effects.highlight_strength, 0.12),
        )
    if data_state == DataState.EMPTY:
        return profile.with_updates(
            elevation_scale=min(profile.elevation_scale, 1.05),
            blur_intensity_scale=min(profile.blur_intensity_scale, 1.0),
        ), effects.with_updates(
            glow_intensity=min(effects.glow_intensity, 0.18),
            neon_intensity=min(effects.neon_intensity, 0.08),
        )
    if data_state == DataState.ERROR:
        return profile.with_updates(
            border_strength_scale=max(profile.border_strength_scale, 1.12),
            surface_opacity_scale=max(profile.surface_opacity_scale, 1.0),
        ), effects.with_updates(
            glow_intensity=max(effects.glow_intensity, 0.24),
            highlight_strength=max(effects.highlight_strength, 0.22),
            neon_intensity=max(effects.neon_intensity, 0.12),
        )
    if data_state == DataState.STALE:
        return profile.with_updates(
            border_strength_scale=max(profile.border_strength_scale, 1.08),
            blur_intensity_scale=min(profile.blur_intensity_scale, 1.0),
        ), effects.with_updates(
            glow_intensity=max(effects.glow_intensity, 0.2),
            neon_intensity=min(effects.neon_intensity, 0.16),
        )
    return profile, effects


def select_visual_bundle(
    context: VisualIntelligenceContext,
    *,
    base_profile: AppearanceProfile | None = None,
    base_effects: EffectsProfile | None = None,
) -> VisualIntelligenceBundle:
    normalized_context = context.normalized()
    selected_preset_name = _select_preset(normalized_context)
    selected_preset = get_appearance_preset(selected_preset_name)

    start_profile = (base_profile or selected_preset.profile).normalized()
    start_effects = (base_effects or EffectsProfile.from_appearance(start_profile)).normalized()

    merged_profile = _merge_preset_profile(start_profile, selected_preset.profile, mode=normalized_context.experience_mode)
    merged_profile = merged_profile.with_updates(
        experience_mode=normalized_context.experience_mode,
        reduced_motion=bool(start_profile.reduced_motion or normalized_context.reduced_motion),
        high_contrast_mode=bool(start_profile.high_contrast_mode or normalized_context.high_contrast_mode),
        data_density_bias=normalized_context.data_density_bias,
    )
    merged_effects = _merge_preset_effects(
        start_effects,
        selected_preset.effects,
        level=normalized_context.requested_visual_level,
    )
    if merged_profile.reduced_motion:
        merged_effects = merged_effects.with_updates(motion_enabled=False)

    state_profile, state_effects = _apply_data_state_modulation(
        merged_profile,
        merged_effects,
        data_state=normalized_context.data_state,
    )
    level_resolution = resolve_visual_level(
        state_profile,
        state_effects,
        requested_level=normalized_context.requested_visual_level,
        performance_sensitive=normalized_context.performance_sensitive,
    )

    final_profile = level_resolution.profile.with_updates(
        experience_mode=normalized_context.experience_mode,
        reduced_motion=state_profile.reduced_motion,
        high_contrast_mode=state_profile.high_contrast_mode,
        data_density_bias=state_profile.data_density_bias,
    )
    final_effects = level_resolution.effects.with_updates(
        motion_enabled=(
            level_resolution.effects.motion_enabled
            and not final_profile.reduced_motion
            and final_profile.animation_level != 'off'
        )
    )
    source = (
        f"visual_intelligence:"
        f"mode={normalized_context.experience_mode};"
        f"state={normalized_context.data_state};"
        f"level={level_resolution.effective_level}"
    )
    return VisualIntelligenceBundle(
        profile=final_profile.normalized(),
        effects=final_effects.normalized(),
        preset_name=selected_preset.name,
        requested_level=level_resolution.requested_level,
        effective_level=level_resolution.effective_level,
        source=source,
        metadata={
            'context_source': normalized_context.source,
            'experience_mode': normalized_context.experience_mode,
            'data_state': normalized_context.data_state,
            'requested_visual_level': level_resolution.requested_level,
            'effective_visual_level': level_resolution.effective_level,
            'selected_preset': selected_preset.name,
            'performance_sensitive': normalized_context.performance_sensitive,
        },
    )


__all__ = [
    'VisualIntelligenceBundle',
    'VisualIntelligenceContext',
    'select_visual_bundle',
]

