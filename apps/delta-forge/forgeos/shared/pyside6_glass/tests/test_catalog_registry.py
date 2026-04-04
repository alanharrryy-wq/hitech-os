from __future__ import annotations

import unittest

from forgeos.shared.pyside6_glass.catalog import (
    GlassCatalogEntry,
    _clear_catalog_registry_for_tests,
    get_catalog_entry,
    list_catalog_categories,
    list_catalog_entries,
    list_catalog_tags,
    register_builtin_catalog_entries,
    register_catalog_entry,
)


class CatalogRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_catalog_registry_for_tests()

    def test_register_and_query_custom_entry(self) -> None:
        register_catalog_entry(
            entry_id="custom.alpha",
            title="Custom Alpha",
            subtitle="custom subtitle",
            description="custom description",
            category="Custom",
            tags=("alpha", "custom"),
            keywords=("hello", "world"),
            best_for="Custom best-for note",
            use_when="Custom use-when note",
            sort_order=5,
            status="preview",
            required_capabilities=("catalog.read",),
        )

        entry = get_catalog_entry("custom.alpha", include_builtins=False)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.title, "Custom Alpha")
        self.assertEqual(entry.best_for, "Custom best-for note")
        self.assertEqual(entry.use_when, "Custom use-when note")

        all_entries = list_catalog_entries(include_builtins=False)
        self.assertEqual(len(all_entries), 1)
        self.assertEqual(all_entries[0].entry_id, "custom.alpha")

        categories = list_catalog_categories(include_builtins=False)
        self.assertEqual(categories, ("Custom",))
        tags = list_catalog_tags(include_builtins=False)
        self.assertEqual(tags, ("alpha", "custom"))

        search_hits = list_catalog_entries(search="hello", include_builtins=False)
        self.assertEqual(len(search_hits), 1)
        self.assertEqual(search_hits[0].entry_id, "custom.alpha")
        tag_hits = list_catalog_entries(tags=("alpha",), include_builtins=False)
        self.assertEqual(len(tag_hits), 1)
        capability_hits = list_catalog_entries(
            required_capabilities=("catalog.read",),
            include_builtins=False,
        )
        self.assertEqual(len(capability_hits), 1)

    def test_duplicate_registration_requires_override(self) -> None:
        entry = GlassCatalogEntry(entry_id="duplicate.entry", title="Duplicate")
        register_catalog_entry(entry=entry)
        with self.assertRaises(ValueError):
            register_catalog_entry(entry=entry)
        register_catalog_entry(entry=entry, override=True)
        self.assertIsNotNone(get_catalog_entry("duplicate.entry", include_builtins=False))

    def test_builtin_registration_provides_substantial_catalog(self) -> None:
        register_builtin_catalog_entries()
        entries = list_catalog_entries()
        self.assertGreaterEqual(len(entries), 30)
        categories = set(list_catalog_categories())
        self.assertTrue(
            {
                "Compositions",
                "Presets",
                "Themes",
                "Primitives",
                "Controls & Assets",
                "Runtime & Integration",
                "Data Dashboards",
            }.issubset(categories)
        )
        data_entries = list_catalog_entries(category="Data Dashboards")
        asset_entries = list_catalog_entries(category="Controls & Assets")
        self.assertGreaterEqual(len(data_entries), 12)
        self.assertGreaterEqual(len(asset_entries), 10)


if __name__ == "__main__":
    unittest.main()
