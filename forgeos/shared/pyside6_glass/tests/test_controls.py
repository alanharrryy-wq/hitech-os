from __future__ import annotations

import os
import unittest

from PySide6.QtWidgets import QApplication

from forgeos.shared.pyside6_glass.controls import create_button, list_button_variants


class ControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_button_variant_normalization(self) -> None:
        button = create_button("Action", variant="outline")
        self.assertEqual(button.property("variant"), "ghost")
        button.deleteLater()

    def test_list_button_variants_includes_subtle(self) -> None:
        variants = list_button_variants()
        self.assertIn("subtle", variants)
        self.assertIn("primary", variants)


if __name__ == "__main__":
    unittest.main()
