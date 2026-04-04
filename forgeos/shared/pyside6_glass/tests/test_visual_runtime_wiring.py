from __future__ import annotations

import os
import unittest

from PySide6.QtWidgets import QApplication

from pyside6_glass.appearance import (
    AppearanceCoordinator,
    AppearanceProfile,
    EffectsProfile,
    VisualIntelligenceContext,
)
from pyside6_glass.config import GlassTemplateConfig, GlassThemeConfig, GlassVisualScaleConfig
from pyside6_glass.runtime import GlassWorkspaceRuntime
from pyside6_glass.template import GlassPanelTemplate
from pyside6_glass.visual_runtime import create_visual_runtime


class VisualRuntimeWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        cls.app = QApplication.instance() or QApplication([])

    def test_template_reacts_to_bound_coordinator(self) -> None:
        template = GlassPanelTemplate(apply_stylesheet=True)
        coordinator = AppearanceCoordinator()
        template.set_appearance_coordinator(coordinator, apply_current=True)
        coordinator.update_profile(theme_id='obsidian_ice', density='compact')
        snapshot = template.appearance_snapshot()
        self.assertIsNotNone(snapshot)
        assert snapshot is not None
        self.assertEqual(snapshot.profile.theme_id, 'obsidian_ice')
        self.assertEqual(template._density, 'compact')
        template.deleteLater()

    def test_runtime_syncs_resolved_config_into_appearance_coordinator(self) -> None:
        config = GlassTemplateConfig(
            theme=GlassThemeConfig(
                theme_id='obsidian_ice',
                density='compact',
                visual_scale=GlassVisualScaleConfig(
                    border_strength_scale=1.15,
                    surface_opacity_scale=1.08,
                    blur_intensity_scale=0.75,
                    elevation_scale=1.2,
                ),
            )
        )
        template = GlassPanelTemplate(apply_stylesheet=True)
        runtime = GlassWorkspaceRuntime(template, explicit_config=config)
        runtime.apply_resolved_config()
        snapshot = runtime.appearance_snapshot()
        self.assertEqual(snapshot.profile.theme_id, 'obsidian_ice')
        self.assertEqual(snapshot.profile.density, 'compact')
        self.assertAlmostEqual(snapshot.profile.blur_intensity_scale, 0.75)
        self.assertAlmostEqual(template._border_strength_scale, 1.15)
        template.deleteLater()

    def test_create_visual_runtime_applies_appearance_preset(self) -> None:
        template = GlassPanelTemplate(apply_stylesheet=True)
        bundle = create_visual_runtime(template, appearance_preset='dashboard_dense')
        self.assertEqual(bundle.appearance.preset_name, 'dashboard_dense')
        self.assertEqual(bundle.runtime.appearance_snapshot().profile.density, 'compact')
        template.deleteLater()

    def test_runtime_applies_visual_intelligence_context(self) -> None:
        template = GlassPanelTemplate(apply_stylesheet=True)
        bundle = create_visual_runtime(
            template,
            visual_context=VisualIntelligenceContext(
                requested_visual_level='showcase',
                data_state='stale',
                performance_sensitive=True,
                experience_mode='monitoring',
                source='test',
            ),
        )
        diagnostics = bundle.runtime.diagnostics()
        self.assertEqual(diagnostics.get('effective_visual_level'), 'performance')
        self.assertEqual(diagnostics.get('visual_context_data_state'), 'stale')
        template.deleteLater()


if __name__ == '__main__':
    unittest.main()
