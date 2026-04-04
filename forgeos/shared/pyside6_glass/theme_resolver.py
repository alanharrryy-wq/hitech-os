from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .appearance import AppearanceProfile, AppearanceTokens, EffectsProfile, resolve_appearance_tokens
from .config import GlassResolvedConfig, GlassTemplateConfig, resolve_template_config_with_provenance
from .theme import build_stylesheet


@dataclass(frozen=True, slots=True)
class ResolvedAppearance:
    profile: AppearanceProfile
    effects: EffectsProfile
    tokens: AppearanceTokens
    resolved_config: GlassResolvedConfig | None = None
    provenance: dict[str, str] = field(default_factory=dict)

    def stylesheet_kwargs(self) -> dict[str, Any]:
        return self.tokens.to_stylesheet_kwargs()

    def build_stylesheet(self) -> str:
        return build_stylesheet(**self.stylesheet_kwargs())

    def to_dict(self) -> dict[str, Any]:
        return {
            'profile': self.profile.to_dict(),
            'effects': self.effects.to_dict(),
            'tokens': self.tokens.to_dict(),
            'provenance': dict(self.provenance),
        }


def _appearance_provenance(resolved: GlassResolvedConfig) -> dict[str, str]:
    fields = {
        'theme.theme_id': 'theme_id',
        'theme.density': 'density',
        'theme.typography.scale': 'typography_scale',
        'tabs.density': 'tab_density',
        'tabs.variant': 'tab_variant',
        'theme.experience_mode': 'experience_mode',
        'theme.animation.level': 'animation_level',
        'theme.animation.reduced_motion': 'reduced_motion',
        'accessibility.high_contrast_mode': 'high_contrast_mode',
        'theme.visual_scale.spacing_scale': 'spacing_scale',
        'theme.visual_scale.padding_scale': 'padding_scale',
        'theme.visual_scale.icon_scale': 'icon_scale',
        'theme.visual_scale.control_height_scale': 'control_height_scale',
        'theme.visual_scale.corner_radius_scale': 'corner_radius_scale',
        'theme.visual_scale.border_strength_scale': 'border_strength_scale',
        'theme.visual_scale.surface_opacity_scale': 'surface_opacity_scale',
        'theme.visual_scale.blur_intensity_scale': 'blur_intensity_scale',
        'theme.visual_scale.elevation_scale': 'elevation_scale',
        'theme.visual_scale.breathing_room_scale': 'breathing_room_scale',
        'theme.visual_scale.data_density_bias': 'data_density_bias',
    }
    return {
        alias: source
        for path, alias in fields.items()
        if (source := resolved.source_for(path)) is not None
    }


def stylesheet_kwargs_from_profile(profile: AppearanceProfile) -> dict[str, Any]:
    return resolve_appearance_tokens(profile).to_stylesheet_kwargs()


def appearance_from_template_config(config: GlassTemplateConfig) -> ResolvedAppearance:
    profile = AppearanceProfile.from_template_config(config)
    effects = EffectsProfile.from_appearance(profile)
    tokens = resolve_appearance_tokens(profile, effects)
    return ResolvedAppearance(profile=profile, effects=effects, tokens=tokens)


def resolve_appearance(
    config: GlassTemplateConfig | None = None,
    *,
    preset: str | None = None,
    framework_defaults: GlassTemplateConfig | None = None,
    theme_defaults: GlassTemplateConfig | None = None,
    app_overrides: GlassTemplateConfig | None = None,
    workspace_overrides: GlassTemplateConfig | None = None,
    runtime_overrides: GlassTemplateConfig | None = None,
) -> ResolvedAppearance:
    resolved = resolve_template_config_with_provenance(
        config=config,
        preset=preset,
        framework_defaults=framework_defaults,
        theme_defaults=theme_defaults,
        app_overrides=app_overrides,
        workspace_overrides=workspace_overrides,
        runtime_overrides=runtime_overrides,
    )
    profile = AppearanceProfile.from_template_config(resolved.config)
    effects = EffectsProfile.from_appearance(profile)
    tokens = resolve_appearance_tokens(profile, effects)
    return ResolvedAppearance(
        profile=profile,
        effects=effects,
        tokens=tokens,
        resolved_config=resolved,
        provenance=_appearance_provenance(resolved),
    )


__all__ = [
    'ResolvedAppearance',
    'appearance_from_template_config',
    'resolve_appearance',
    'stylesheet_kwargs_from_profile',
]
