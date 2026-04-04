from PySide6.QtWidgets import QApplication, QFrame

from pyside6_glass.appearance import AppearanceProfile, AppearanceSnapshot, EffectsProfile
from pyside6_glass.rendering import apply_surface_role, install_surface_renderer, sync_surface_renderer


def _app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_surface_renderer_installs_overlay_and_syncs_properties():
    _app()
    widget = QFrame()
    apply_surface_role(widget, role='panel_data', variant='panel', emphasis='high', fx_level='rich')
    install_surface_renderer(widget)
    snapshot = AppearanceSnapshot(
        profile=AppearanceProfile(theme_id='silver_frost_cyan'),
        effects=EffectsProfile.from_appearance(AppearanceProfile()),
        source='test',
    )
    sync_surface_renderer(widget, snapshot)
    assert widget.property('visualRole') == 'panel_data'
    assert widget.property('visualVariant') == 'panel'
    assert widget.property('visualFxLevel') == 'rich'
    assert widget.property('visualGlowIntensity') is not None
