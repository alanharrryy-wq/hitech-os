from __future__ import annotations

import unittest

from forgeos.shared.pyside6_glass.data import DataQuery, DataResult, DataState, RefreshPolicy


class DataResultStateTests(unittest.TestCase):
    def test_success_without_content_normalizes_to_empty(self) -> None:
        query = DataQuery.create("provider.alpha", query_id="empty_case")
        result = DataResult.success(query)
        self.assertEqual(result.normalized_state(), DataState.EMPTY)

    def test_invalid_state_normalizes_to_ready(self) -> None:
        query = DataQuery.create("provider.alpha", query_id="state_case")
        result = DataResult(
            provider_id=query.provider_id,
            query_id=query.query_id,
            state="UNKNOWN_STATE",
            refresh_policy=RefreshPolicy(),
        )
        self.assertEqual(result.normalized_state(), DataState.READY)

    def test_refresh_policy_normalization(self) -> None:
        policy = RefreshPolicy(mode="invalid", interval_ms=10, stale_after_ms=10, max_retries=-5, jitter_ms=-1)
        normalized = policy.normalized()
        self.assertEqual(normalized.mode, "manual")
        self.assertGreaterEqual(normalized.interval_ms, 250)
        self.assertGreaterEqual(normalized.stale_after_ms, 500)
        self.assertEqual(normalized.max_retries, 0)
        self.assertEqual(normalized.jitter_ms, 0)

    def test_stale_result_builder(self) -> None:
        query = DataQuery.create("provider.alpha", query_id="stale_case")
        result = DataResult.stale(query, summary={"note": "stale"})
        self.assertEqual(result.normalized_state(), DataState.STALE)
        self.assertTrue(result.is_stale())


if __name__ == "__main__":
    unittest.main()
