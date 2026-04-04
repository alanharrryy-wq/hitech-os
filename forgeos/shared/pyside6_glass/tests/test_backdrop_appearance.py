from __future__ import annotations

import os
import unittest

from PySide6.QtWidgets import QApplication

from pyside6_glass.appearance import AppearanceProfile, EffectsProfile
from pyside6_glass.backdrop import FrostedGlassBackdrop


class BackdropAppearanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
        cls.app = QApplication.instance() or QApplication([])

    def test_apply_appearance_updates_runtime_scalars(self) -> None:
        backdrop = FrostedGlassBackdrop(theme_id='silver_frost_cyan')
        profile = AppearanceProfile(
            theme_id='obsidian_ice',
            blur_intensity_scale=0.5,
            surface_opacity_scale=1.12,
            border_strength_scale=1.25,
            corner_radius_scale=1.15,
        )
        effects = EffectsProfile.from_appearance(profile).with_updates(
            glow_intensity=0.32,
            highlight_strength=0.27,
            motion_enabled=False,
        )
        backdrop.apply_appearance(profile, effects)
        self.assertEqual(backdrop._theme_id, 'obsidian_ice')
        self.assertAlmostEqual(backdrop._surface_opacity_scale, 1.12)
        self.assertAlmostEqual(backdrop._border_strength_scale, 1.25)
        self.assertFalse(backdrop._motion_enabled)
        backdrop.deleteLater()


if __name__ == '__main__':
    unittest.main()
