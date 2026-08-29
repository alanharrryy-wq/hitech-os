from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from sync_sentinel.evidence import build_bundle


class EvidenceTests(unittest.TestCase):
    def test_k_bundle_is_atomic_readable_and_manifested(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            bundle, count, _ = build_bundle(root, {"status": "PASS_TEST", "repoHead": "abc", "productionCertified": False})
            self.assertEqual(count, 0)
            self.assertTrue(bundle.is_file())
            with zipfile.ZipFile(bundle) as zf:
                names = set(zf.namelist())
                self.assertIn("SYNC_SENTINEL_REPORT.json", names)
                self.assertIn("SYNC_SENTINEL_MANIFEST.json", names)
                payload = json.loads(zf.read("SYNC_SENTINEL_REPORT.json"))
                self.assertFalse(payload["productionCertified"])

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
