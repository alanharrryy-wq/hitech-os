from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from forgeos.shared.pyside6_glass.data import (
    DataQuery,
    execute_data_query,
    list_data_providers,
    _clear_data_provider_registry_for_tests,
)
from forgeos.shared.pyside6_glass.data_providers import register_builtin_data_providers


class BuiltinDataProvidersTests(unittest.TestCase):
    def setUp(self) -> None:
        _clear_data_provider_registry_for_tests()

    def test_register_builtin_providers_and_query_mock(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sqlite_path = Path(temp_dir) / "demo.sqlite3"
            register_builtin_data_providers(local_sqlite_path=sqlite_path)
            providers = {item.provider_id for item in list_data_providers()}
            self.assertIn("builtin.mock_dashboard", providers)
            self.assertIn("builtin.local_sqlite", providers)

            ready = execute_data_query(DataQuery.create("builtin.mock_dashboard", query_id="live_metrics"))
            self.assertEqual(ready.normalized_state(), "ready")
            self.assertGreaterEqual(len(ready.metrics), 1)

            empty = execute_data_query(
                DataQuery.create(
                    "builtin.mock_dashboard",
                    query_id="live_metrics",
                    params={"simulate_state": "empty"},
                )
            )
            self.assertEqual(empty.normalized_state(), "empty")

            failed = execute_data_query(
                DataQuery.create(
                    "builtin.mock_dashboard",
                    query_id="live_metrics",
                    params={"simulate_state": "error"},
                )
            )
            self.assertEqual(failed.normalized_state(), "error")
            self.assertIsNotNone(failed.error)

            stale = execute_data_query(
                DataQuery.create(
                    "builtin.mock_dashboard",
                    query_id="live_metrics",
                    params={"simulate_state": "stale"},
                )
            )
            self.assertEqual(stale.normalized_state(), "stale")
            self.assertTrue(stale.is_stale())

            sqlite_health = execute_data_query(DataQuery.create("builtin.local_sqlite", query_id="service_health"))
            self.assertEqual(sqlite_health.normalized_state(), "ready")
            self.assertGreaterEqual(len(sqlite_health.rows), 1)


if __name__ == "__main__":
    unittest.main()
