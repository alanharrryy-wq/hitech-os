import pytest

pytest.importorskip('PySide6')

from pyside6_glass.appearance import resolve_appearance_tokens
from pyside6_glass.config import GlassTemplateConfig, GlassThemeConfig, GlassVisualScaleConfig
from pyside6_glass.theme_resolver import appearance_from_template_config, resolve_appearance


def test_appearance_from_template_config_builds_tokens():
    config = GlassTemplateConfig(
        theme=GlassThemeConfig(
            theme_id='silver_frost_cyan',
            density='compact',
            visual_scale=GlassVisualScaleConfig(
                border_strength_scale=1.25,
                surface_opacity_scale=1.12,
            ),
        )
    )
    resolved = appearance_from_template_config(config)
    assert resolved.tokens.border_strength_scale == 1.25
    assert resolved.tokens.surface_opacity_scale == 1.12
    assert resolved.tokens.theme_id == 'silver_frost_cyan'


def test_resolve_appearance_returns_provenance_for_appearance_fields():
    overrides = GlassTemplateConfig(
        theme=GlassThemeConfig(
            visual_scale=GlassVisualScaleConfig(border_strength_scale=1.3)
        )
    )
    resolved = resolve_appearance(runtime_overrides=overrides)
    assert resolved.provenance['border_strength_scale'] == 'runtime_overrides'


def test_tokens_can_feed_existing_stylesheet_builder():
    config = GlassTemplateConfig()
    resolved = appearance_from_template_config(config)
    kwargs = resolved.tokens.to_stylesheet_kwargs()
    assert kwargs['theme_id'] == 'silver_frost_cyan'
    assert kwargs['tab_variant'] == 'glass'
    assert kwargs['density'] == 'comfortable'
