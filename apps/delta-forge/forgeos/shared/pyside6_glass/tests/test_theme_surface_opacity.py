from __future__ import annotations

import re
import unittest

from forgeos.shared.pyside6_glass.theme import _scale_rgba_alpha, build_stylesheet


class ThemeSurfaceOpacityTests(unittest.TestCase):
    def test_scale_rgba_alpha_reduces_alpha(self) -> None:
        value = _scale_rgba_alpha("rgba(20, 33, 54, 0.92)", 0.62)
        self.assertEqual(value, "rgba(20, 33, 54, 0.57)")

    def test_scale_rgba_alpha_keeps_non_rgba_token(self) -> None:
        value = _scale_rgba_alpha("#8cefff", 0.62)
        self.assertEqual(value, "#8cefff")

    def test_build_stylesheet_applies_surface_opacity_scale(self) -> None:
        css = build_stylesheet("silver_frost_cyan", surface_opacity_scale=0.62)
        shell_match = re.search(
            r"QFrame#Shell \{\s+background: qlineargradient\([^)]*stop:0 (rgba\([^)]*\))",
            css,
            re.MULTILINE,
        )
        self.assertIsNotNone(shell_match)
        self.assertEqual(shell_match.group(1), "rgba(13, 14, 18, 0.558)")


if __name__ == "__main__":
    unittest.main()
