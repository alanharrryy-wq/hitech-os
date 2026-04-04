from PySide6.QtWidgets import QApplication

from pyside6_glass.appearance import AppearanceProfile, AppearanceSnapshot, EffectsProfile
from pyside6_glass.backdrop import FrostedGlassBackdrop


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_backdrop_accepts_snapshot_without_legacy_bridge():
    _app()
    backdrop = FrostedGlassBackdrop(theme_id='silver_frost_cyan')
    profile = AppearanceProfile(theme_id='obsidian_ice', blur_intensity_scale=1.2, surface_opacity_scale=1.1)
    effects = EffectsProfile.from_appearance(profile).with_updates(glow_intensity=0.4, noise_strength=0.2)
    snapshot = AppearanceSnapshot(profile=profile, effects=effects, source='test')
    backdrop.apply_appearance(snapshot)
    assert backdrop.snapshot.profile.theme_id == 'obsidian_ice'
    assert backdrop.snapshot.effects.glow_intensity == effects.glow_intensity
