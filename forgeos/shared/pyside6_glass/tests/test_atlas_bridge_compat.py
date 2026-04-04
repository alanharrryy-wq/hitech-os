from dataclasses import dataclass

from pyside6_glass.atlas_styles import build_app_stylesheet
from pyside6_glass.atlas_theme_bridge import resolve_atlas_glass_palette


@dataclass(frozen=True)
class _PaletteProbe:
    canvas_top: object
    canvas_bottom: object
    wash: object
    border: object
    line: object
    sheen: object
    orb_a: object
    orb_b: object
    orb_c: object
    sparkle: object
    star_soft: object
    star_bright: object


def test_atlas_styles_still_returns_css():
    css = build_app_stylesheet('silver_frost_cyan')
    assert 'QFrame#WindowChrome' in css
    assert 'QPushButton' in css


def test_atlas_bridge_still_resolves_palette_payload():
    payload = resolve_atlas_glass_palette('silver_frost_cyan', 'selector', palette_factory=_PaletteProbe)
    assert payload.canvas_top is not None
    assert payload.border is not None
    assert payload.orb_a is not None
