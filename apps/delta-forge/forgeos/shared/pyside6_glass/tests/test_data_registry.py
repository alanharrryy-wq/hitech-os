from __future__ import annotations

import unittest

from forgeos.shared.pyside6_glass.data import (
    DataProviderMeta,
    DataQuery,
    DataResult,
    FunctionDataProvider,
    describe_data_provider,
    execute_data_query,
    get_data_provider,
    list_data_providers,
    register_data_provider,
    _clear_data_provider_registry_for_tests,
)


class DataRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_data_provider_registry_for_tests()

    def test_register_and_execute_query(self) -> None:
        provider = FunctionDataProvider(
            meta=DataProviderMeta(provider_id="custom.mock", title="Custom Mock Provider"),
            handler=lambda query: DataResult.success(
                query,
                summary={"ok": True},
                metrics={"items": 3},
                rows=[{"id": "row-1", "state": "ready"}],
            ),
        )
        register_data_provider(provider)

        query = DataQuery.create("custom.mock", query_id="default")
        result = execute_data_query(query)
        self.assertEqual(result.normalized_state(), "ready")
        self.assertEqual(result.metrics.get("items"), 3)
        self.assertEqual(len(result.rows), 1)

    def test_missing_provider_returns_structured_error(self) -> None:
        query = DataQuery.create("missing.provider", query_id="default")
        result = execute_data_query(query)
        self.assertEqual(result.normalized_state(), "error")
        self.assertIsNotNone(result.error)
        self.assertEqual(result.error.code, "provider_not_found")

    def test_provider_listing_and_describe(self) -> None:
        provider = FunctionDataProvider(
            meta=DataProviderMeta(
                provider_id="custom.describe",
                title="Describe Provider",
                capabilities=("query.metrics",),
                requirements=("none",),
            ),
            handler=lambda query: DataResult.empty(query),
        )
        register_data_provider(provider)
        self.assertIsNotNone(get_data_provider("custom.describe"))

        listed = list_data_providers()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0].provider_id, "custom.describe")

        described = describe_data_provider("custom.describe")
        self.assertTrue(described.get("registered"))
        self.assertEqual(described.get("meta", {}).get("provider_id"), "custom.describe")


if __name__ == "__main__":
    unittest.main()

