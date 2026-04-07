from __future__ import annotations

import unittest

from forgeos.shared.pyside6_glass.charts import (
    GlassChartPalette,
    GlassChartStyle,
    _clear_chart_catalog_for_tests,
    get_chart_palette,
    get_chart_style,
    list_chart_palettes,
    list_chart_styles,
    register_builtin_chart_catalog,
    register_chart_palette,
    register_chart_style,
)


class ChartCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_chart_catalog_for_tests()

    def test_builtin_chart_catalog_registers_palettes_and_styles(self) -> None:
        styles = register_builtin_chart_catalog(force=True)
        palettes = list_chart_palettes()
        self.assertGreaterEqual(len(palettes), 8)
        self.assertGreaterEqual(len(styles), 18)
        self.assertIsNotNone(get_chart_palette("silver_frost"))
        self.assertIsNotNone(get_chart_style("silver_line"))

    def test_custom_style_registration_requires_existing_palette(self) -> None:
        register_chart_palette(
            GlassChartPalette(
                palette_id="unit_palette",
                title="Unit Palette",
                description="unit test palette",
                colors=("#ffffff", "#8cefff", "#d7e1ff"),
            ),
            override=True,
        )
        style = register_chart_style(
            GlassChartStyle(
                style_id="unit_style",
                title="Unit Style",
                description="unit test style",
                palette_id="unit_palette",
                default_mode="line",
            ),
            override=True,
        )
        self.assertEqual(style.style_id, "unit_style")
        self.assertEqual(style.palette_id, "unit_palette")
        self.assertEqual(list_chart_styles()[0].style_id, "unit_style")


if __name__ == "__main__":
    unittest.main()
