from pyside6_glass.appearance import AppearanceProfile, EffectsProfile, resolve_appearance_tokens
from pyside6_glass.rendering.glass_painter import GlassSurfaceSpec, build_surface_spec


def test_build_surface_spec_returns_valid_payload():
    profile = AppearanceProfile(theme_id='silver_frost_cyan', surface_opacity_scale=1.1, border_strength_scale=1.2)
    effects = EffectsProfile.from_appearance(profile).with_updates(glow_intensity=0.3, neon_intensity=0.25)
    tokens = resolve_appearance_tokens(profile, effects)
    spec = build_surface_spec(profile.theme_id, tokens, role='panel_metrics', variant='panel', emphasis='high')
    assert isinstance(spec, GlassSurfaceSpec)
    assert spec.radius > 0
    assert spec.border_width >= 1.0
    assert spec.glow_opacity > 0.0
