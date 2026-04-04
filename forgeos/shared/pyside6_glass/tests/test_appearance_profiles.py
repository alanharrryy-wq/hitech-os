import pytest

pytest.importorskip('PySide6')

from pyside6_glass.appearance import AppearanceProfile, EffectsProfile
from pyside6_glass.config import GlassTemplateConfig, GlassThemeConfig, GlassVisualScaleConfig


def test_appearance_profile_normalizes_invalid_choices_and_scales():
    profile = AppearanceProfile(
        theme_id='  SILVER_FROST_CYAN ',
        density='wild',
        typography_scale='xxl',
        tab_density='nope',
        tab_variant='broken',
        spacing_scale=99,
        surface_opacity_scale=-4,
        data_density_bias=4,
    ).normalized()

    assert profile.theme_id == 'silver_frost_cyan'
    assert profile.density == 'comfortable'
    assert profile.typography_scale == 'lg'
    assert profile.tab_density == 'comfortable'
    assert profile.tab_variant == 'glass'
    assert profile.spacing_scale == 3.0
    assert profile.surface_opacity_scale == 0.3
    assert profile.data_density_bias == 1.0


def test_effects_profile_from_appearance_disables_motion_when_reduced_motion():
    profile = AppearanceProfile(reduced_motion=True, animation_level='standard')
    effects = EffectsProfile.from_appearance(profile)
    assert effects.motion_enabled is False
    assert effects.backdrop_blur_enabled is True


def test_appearance_profile_from_template_config_uses_nested_values():
    config = GlassTemplateConfig(
        theme=GlassThemeConfig(
            theme_id='silver_frost_cyan',
            density='compact',
            visual_scale=GlassVisualScaleConfig(
                border_strength_scale=1.2,
                surface_opacity_scale=1.1,
                blur_intensity_scale=0.8,
            ),
        )
    )
    profile = AppearanceProfile.from_template_config(config)
    assert profile.theme_id == 'silver_frost_cyan'
    assert profile.density == 'compact'
    assert profile.border_strength_scale == 1.2
    assert profile.surface_opacity_scale == 1.1
    assert profile.blur_intensity_scale == 0.8
