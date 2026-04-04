from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .profile import AppearanceBundle, AppearanceProfile, EffectsProfile


@dataclass(frozen=True, slots=True)
class AppearancePreset:
    name: str
    description: str
    profile: AppearanceProfile
    effects: EffectsProfile

    def bundle(self) -> AppearanceBundle:
        return AppearanceBundle(
            profile=self.profile.normalized(),
            effects=self.effects.normalized(),
        )


_PRESET_FACTORIES: dict[str, Callable[[], AppearancePreset]] = {}


def _register_builtin(name: str, factory: Callable[[], AppearancePreset]) -> None:
    _PRESET_FACTORIES[name] = factory


def register_appearance_preset(
    name: str,
    *,
    factory: Callable[[], AppearancePreset] | None = None,
    preset: AppearancePreset | None = None,
    override: bool = False,
) -> None:
    normalized = str(name or '').strip().lower()
    if not normalized:
        raise ValueError('preset name is required')
    if not override and normalized in _PRESET_FACTORIES:
        raise ValueError(f"appearance preset '{normalized}' already registered")
    if factory is None and preset is None:
        raise ValueError('factory or preset is required')

    if factory is None:
        snapshot = preset

        def factory() -> AppearancePreset:
            assert snapshot is not None
            return AppearancePreset(
                name=snapshot.name,
                description=snapshot.description,
                profile=snapshot.profile.normalized(),
                effects=snapshot.effects.normalized(),
            )

    _PRESET_FACTORIES[normalized] = factory


def list_appearance_presets() -> tuple[str, ...]:
    return tuple(sorted(_PRESET_FACTORIES.keys()))


def get_appearance_preset(name: str = 'neutral') -> AppearancePreset:
    normalized = str(name or 'neutral').strip().lower()
    factory = _PRESET_FACTORIES.get(normalized)
    if factory is None:
        factory = _PRESET_FACTORIES['neutral']
    preset = factory()
    return AppearancePreset(
        name=str(preset.name or normalized).strip().lower(),
        description=str(preset.description or '').strip(),
        profile=preset.profile.normalized(),
        effects=preset.effects.normalized(),
    )


def _neutral() -> AppearancePreset:
    profile = AppearanceProfile()
    return AppearancePreset(
        name='neutral',
        description='Baseline glass profile aligned with the current framework defaults.',
        profile=profile,
        effects=EffectsProfile.from_appearance(profile),
    )


def _frosted_focus() -> AppearancePreset:
    profile = AppearanceProfile(
        surface_opacity_scale=1.08,
        blur_intensity_scale=1.15,
        border_strength_scale=1.05,
        elevation_scale=1.05,
    )
    effects = EffectsProfile.from_appearance(profile).with_updates(
        glow_intensity=0.22,
        highlight_strength=0.22,
        gaussian_softness=0.52,
    )
    return AppearancePreset(
        name='frosted_focus',
        description='Softer surfaces and stronger separation for premium glass shells.',
        profile=profile,
        effects=effects,
    )


def _dashboard_dense() -> AppearancePreset:
    profile = AppearanceProfile(
        density='compact',
        tab_density='compact',
        typography_scale='md',
        spacing_scale=0.94,
        padding_scale=0.92,
        surface_opacity_scale=1.14,
        border_strength_scale=1.14,
        blur_intensity_scale=0.82,
        elevation_scale=1.18,
        data_density_bias=0.32,
        experience_mode='dashboard',
    )
    effects = EffectsProfile.from_appearance(profile).with_updates(
        shadow_depth=1.2,
        glow_intensity=0.16,
        highlight_strength=0.14,
    )
    return AppearancePreset(
        name='dashboard_dense',
        description='Tighter density and crisper separation for data-heavy workspaces.',
        profile=profile,
        effects=effects,
    )


def _presentation_low_motion() -> AppearancePreset:
    profile = AppearanceProfile(
        density='extended',
        typography_scale='xl',
        blur_intensity_scale=0.65,
        border_strength_scale=1.08,
        surface_opacity_scale=1.06,
        reduced_motion=True,
        animation_level='subtle',
        experience_mode='presentation',
    )
    effects = EffectsProfile.from_appearance(profile).with_updates(
        motion_enabled=False,
        shadow_depth=0.8,
        glow_intensity=0.12,
    )
    return AppearancePreset(
        name='presentation_low_motion',
        description='Large typography and calmer motion for projector or review contexts.',
        profile=profile,
        effects=effects,
    )


def _neon_focus() -> AppearancePreset:
    profile = AppearanceProfile(
        surface_opacity_scale=1.02,
        blur_intensity_scale=1.18,
        elevation_scale=1.1,
        border_strength_scale=1.12,
    )
    effects = EffectsProfile.from_appearance(profile).with_updates(
        glow_intensity=0.34,
        neon_intensity=0.55,
        highlight_strength=0.26,
        gaussian_softness=0.58,
    )
    return AppearancePreset(
        name='neon_focus',
        description='Accent-forward mode prepared for glow and neon rendering in later rounds.',
        profile=profile,
        effects=effects,
    )


def _orchestrator_lab() -> AppearancePreset:
    profile = AppearanceProfile(
        theme_id='orchestrator_lab',
        density='comfortable',
        tab_density='comfortable',
        typography_scale='lg',
        experience_mode='focus',
        spacing_scale=1.08,
        padding_scale=1.10,
        icon_scale=1.06,
        control_height_scale=1.04,
        corner_radius_scale=1.08,
        border_strength_scale=1.22,
        surface_opacity_scale=1.12,
        blur_intensity_scale=1.44,
        elevation_scale=1.26,
        breathing_room_scale=1.12,
    )
    effects = EffectsProfile.from_appearance(profile).with_updates(
        glow_intensity=0.46,
        shadow_depth=1.28,
        highlight_strength=0.34,
        neon_intensity=0.72,
        gaussian_softness=0.72,
        noise_strength=0.08,
        motion_enabled=True,
        backdrop_blur_enabled=True,
        shadow_enabled=True,
        use_accent_for_glow=True,
    )
    return AppearancePreset(
        name='orchestrator_lab',
        description='Experimental lab mode for orchestrators, high-contrast shells, premium FX and new UI trials.',
        profile=profile,
        effects=effects,
    )


_register_builtin('neutral', _neutral)
_register_builtin('frosted_focus', _frosted_focus)
_register_builtin('dashboard_dense', _dashboard_dense)
_register_builtin('presentation_low_motion', _presentation_low_motion)
_register_builtin('neon_focus', _neon_focus)
_register_builtin('orchestrator_lab', _orchestrator_lab)


__all__ = [
    'AppearancePreset',
    'get_appearance_preset',
    'list_appearance_presets',
    'register_appearance_preset',
]
