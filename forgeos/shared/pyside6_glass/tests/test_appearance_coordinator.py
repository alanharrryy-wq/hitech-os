import pytest

pytest.importorskip('PySide6')

from pyside6_glass.appearance import AppearanceCoordinator


def test_coordinator_applies_presets_and_tracks_snapshot():
    coordinator = AppearanceCoordinator(preset_name='dashboard_dense')
    snapshot = coordinator.snapshot()
    assert snapshot.preset_name == 'dashboard_dense'
    assert snapshot.profile.density == 'compact'


def test_coordinator_update_profile_clears_preset_name():
    coordinator = AppearanceCoordinator(preset_name='frosted_focus')
    coordinator.update_profile(surface_opacity_scale=1.2)
    assert coordinator.preset_name is None
    assert coordinator.profile().surface_opacity_scale == 1.2


def test_coordinator_reset_restores_defaults():
    coordinator = AppearanceCoordinator()
    coordinator.update_profile(surface_opacity_scale=1.2)
    coordinator.reset()
    assert coordinator.profile().surface_opacity_scale == 1.0
