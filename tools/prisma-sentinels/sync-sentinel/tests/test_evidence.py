from __future__ import annotations

import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from sync_sentinel.evidence import REQUIRED_FAULT_ZONES, build_bundle


class EvidenceTests(unittest.TestCase):
    def test_k_bundle_is_atomic_readable_and_manifested(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            journeys = root / "SYNC_JOURNEYS.json"
            journeys.write_text(json.dumps({
                "startedAt": "2026-08-30T10:00:00+00:00",
                "finishedAt": "2026-08-30T10:00:02+00:00",
                "negativeFixtures": {
                    "schemaVersion": "prisma.sync-sentinel.negative-fixtures.v1",
                    "ok": True,
                    "fixtures": {letter: {"status": "PASS"} for letter in "ABCDEFGHIJKL"},
                },
            }), encoding="utf-8")
            env = {
                "SYNC_SENTINEL_CANONICAL_HEAD": "canonical-123",
                "SYNC_SENTINEL_PRODUCT_TARGET": "product-456",
                "SYNC_SENTINEL_EVIDENCE_BASE": "evidence-789",
            }
            with mock.patch.dict(os.environ, env, clear=False):
                bundle, count, _ = build_bundle(root, {"status": "PASS_TEST", "repoHead": "product-456", "productionCertified": False}, [journeys])
            self.assertEqual(count, 0)
            self.assertTrue(bundle.is_file())
            with zipfile.ZipFile(bundle) as zf:
                names = set(zf.namelist())
                required = {
                    "SYNC_SENTINEL_REPORT.json",
                    "SYNC_SENTINEL_MANIFEST.json",
                    "SYNC_SUMMARY.json",
                    "SYNC_MATRIX.csv",
                    "SYNC_FAILURE_LOCALIZATION.json",
                    "SYNC_TIMELINE.json",
                    "SYNC_ASSERTIONS.json",
                    "SYNC_ENVIRONMENT_SANITIZED.json",
                    "SYNC_CONTRACTS.json",
                    "SYNC_EVIDENCE_INDEX.json",
                    "SYNC_NEGATIVE_FIXTURES.json",
                    "CONTINUATION.md",
                }
                self.assertTrue(required.issubset(names), required - names)
                payload = json.loads(zf.read("SYNC_SENTINEL_REPORT.json"))
                self.assertFalse(payload["productionCertified"])
                self.assertEqual(payload["CANONICAL_HEAD"], "canonical-123")
                self.assertEqual(payload["PRODUCT_TARGET"], "product-456")
                self.assertEqual(payload["EVIDENCE_BASE"], "evidence-789")
                self.assertEqual(payload["runtimeTiming"]["durationMs"], 2000)
                localization = json.loads(zf.read("SYNC_FAILURE_LOCALIZATION.json"))
                self.assertFalse(localization["unknownMayPass"])
                self.assertEqual(set(localization["requiredFaultZones"]), set(REQUIRED_FAULT_ZONES))
                negative = json.loads(zf.read("SYNC_NEGATIVE_FIXTURES.json"))
                self.assertTrue(negative["ok"])

    def test_l_bundle_sanitizes_secret_before_zip(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            extra = root / "runtime.log"
            extra.write_text("password=ultrasecret12345678\n", encoding="utf-8")
            bundle, count, _ = build_bundle(root, {"status": "FAIL_TEST"}, [extra])
            self.assertEqual(count, 0)
            with zipfile.ZipFile(bundle) as zf:
                self.assertNotIn("ultrasecret12345678", zf.read("runtime.log").decode())
                manifest = json.loads(zf.read("SYNC_SENTINEL_MANIFEST.json"))
                self.assertGreaterEqual(manifest["sanitizedFindingCount"], 1)
                self.assertEqual(manifest["remainingSecretFindings"], 0)
