from __future__ import annotations

import os
import unittest

from PySide6.QtWidgets import QApplication

from forgeos.shared.pyside6_glass.assets import (
    CollapsibleSection,
    CompactToolbar,
    ControlCard,
    EnhancedSlider,
    FilterChipBar,
    GlassSegmentedControl,
    HeroPanel,
    MiniLegend,
    ParameterPanel,
    SearchCommandBar,
    StatPill,
    StatusPill,
    TogglePill,
)


class AssetsSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_assets_instantiation_and_basic_interaction(self) -> None:
        segmented = GlassSegmentedControl((("a", "A"), ("b", "B")), selected="a")
        self.assertEqual(segmented.value(), "a")
        segmented.set_value("b")
        self.assertEqual(segmented.value(), "b")

        toggle = TogglePill("On", "Off", checked=True)
        self.assertTrue(toggle.isChecked())

        chips = FilterChipBar()
        chips.add_chip("all", "All", checked=True)
        chips.add_chip("warn", "Warning")
        self.assertIn("all", chips.selected_values())

        search = SearchCommandBar(placeholder="Search")
        search.input.setText("hello")
        self.assertEqual(search.text(), "hello")

        toolbar = CompactToolbar("Toolbar")
        toolbar.add_action("Refresh")
        toolbar.add_icon_action(icon_name="refresh-cw", tooltip="Refresh")

        card = ControlCard("Controls")
        card.content.addWidget(StatusPill("Ready", kind="success"))
        card.content.addWidget(StatPill("Throughput", "120/min"))

        slider = EnhancedSlider("Rate", value=42)
        self.assertEqual(slider.slider.value(), 42)

        section = CollapsibleSection("Advanced", collapsed=False)
        section.set_collapsed(True)
        self.assertFalse(section.body_host.isVisible())

        panel = ParameterPanel("Params")
        panel.add_text_field("Scope", placeholder="core")
        panel.add_slider("Refresh", value=10)
        panel.add_toggle("Enabled", checked=True)

        legend = MiniLegend()
        legend.add_status("Healthy", "success")
        legend.add_status("Warning", "warning")

        hero = HeroPanel("Control Center", subtitle="Operations")
        self.assertIsNotNone(hero)

        for widget in (
            segmented,
            toggle,
            chips,
            search,
            toolbar,
            card,
            slider,
            section,
            panel,
            legend,
            hero,
        ):
            widget.deleteLater()


if __name__ == "__main__":
    unittest.main()

