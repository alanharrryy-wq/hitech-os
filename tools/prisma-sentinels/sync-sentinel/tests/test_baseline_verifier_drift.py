from __future__ import annotations

import unittest

from sync_sentinel.model import Check, Verdict
from sync_sentinel.probes import (
    CATALOG_KNOWN_BASELINE_FAILURES,
    PC_INGEST_KNOWN_BASELINE_FAILURE,
    reconcile_static_probe_baseline_drift,
)


def runtime_journey_check(*, all_negative: bool = True) -> Check:
    fixtures = {
        letter: {"status": "PASS" if all_negative or letter != "B" else "FAIL"}
        for letter in "ABCDEFGHIJKL"
    }
    return Check(
        "isolated_real_code_journeys",
        Verdict.PASS,
        "runtime passed",
        {
            "journeys": {
                "ok": True,
                "journeyA": {"persistedCanonicalEquality": True},
                "journeyB": {
                    "bootstrap": {"reason": "applied"},
                    "delta": {"reason": "applied"},
                    "stockInvariant": {
                        "tabletLocalStockBeforeDelta": 17,
                        "tabletLocalStockAfterDelta": 17,
                    },
                },
                "negativeFixtures": {"ok": True, "fixtures": fixtures},
            }
        },
    )


class BaselineVerifierDriftTests(unittest.TestCase):
    def test_known_pc_ingest_false_positive_requires_runtime_proof(self):
        native = Check(
            "pc_sync_ingest_persistence_contract",
            Verdict.FAIL,
            "native verifier failed",
            {"nativeResult": {"checks": [
                {"name": "route uses durable persistIngestPayload", "ok": True},
                {"name": PC_INGEST_KNOWN_BASELINE_FAILURE, "ok": False},
            ]}},
        )
        reconciled, records = reconcile_static_probe_baseline_drift([native], runtime_journey_check())
        self.assertEqual(reconciled[0].verdict, Verdict.PASS)
        self.assertTrue(reconciled[0].evidence["baselineVerifierDrift"])
        self.assertEqual(records[0]["nativeVerifierVerdict"], "FAIL")

    def test_pc_ingest_drift_does_not_pass_without_negative_b(self):
        native = Check(
            "pc_sync_ingest_persistence_contract",
            Verdict.FAIL,
            "native verifier failed",
            {"nativeResult": {"checks": [{"name": PC_INGEST_KNOWN_BASELINE_FAILURE, "ok": False}]}},
        )
        reconciled, records = reconcile_static_probe_baseline_drift([native], runtime_journey_check(all_negative=False))
        self.assertEqual(reconciled[0].verdict, Verdict.FAIL)
        self.assertEqual(records, [])

    def test_unexpected_pc_ingest_failure_stays_fail(self):
        native = Check(
            "pc_sync_ingest_persistence_contract",
            Verdict.FAIL,
            "native verifier failed",
            {"nativeResult": {"checks": [
                {"name": PC_INGEST_KNOWN_BASELINE_FAILURE, "ok": False},
                {"name": "new regression", "ok": False},
            ]}},
        )
        reconciled, records = reconcile_static_probe_baseline_drift([native], runtime_journey_check())
        self.assertEqual(reconciled[0].verdict, Verdict.FAIL)
        self.assertEqual(records, [])

    def test_known_catalog_copy_drift_requires_real_catalog_proof(self):
        native = Check(
            "pc_to_tablet_catalog_delta_closure",
            Verdict.FAIL,
            "native verifier failed",
            {"nativeResult": {"failures": sorted(CATALOG_KNOWN_BASELINE_FAILURES), "warnings": []}},
        )
        reconciled, records = reconcile_static_probe_baseline_drift([native], runtime_journey_check())
        self.assertEqual(reconciled[0].verdict, Verdict.PASS)
        self.assertEqual(records[0]["classification"], "KNOWN_BASELINE_VERIFIER_DRIFT")

    def test_catalog_extra_failure_stays_fail(self):
        native = Check(
            "pc_to_tablet_catalog_delta_closure",
            Verdict.FAIL,
            "native verifier failed",
            {"nativeResult": {"failures": sorted(CATALOG_KNOWN_BASELINE_FAILURES | {"unexpected schema regression"}), "warnings": []}},
        )
        reconciled, records = reconcile_static_probe_baseline_drift([native], runtime_journey_check())
        self.assertEqual(reconciled[0].verdict, Verdict.FAIL)
        self.assertEqual(records, [])


if __name__ == "__main__":
    unittest.main()
