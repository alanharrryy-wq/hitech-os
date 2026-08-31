from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sync_sentinel.watch import build_summary, classify_paths, load_contract


class SyncSentinelWatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_contract()

    def test_unrelated_css_is_none(self) -> None:
        result = classify_paths([
            "apps/terminal-de-venta-system/products/mobile/app/components/foo.module.css",
            "docs/unrelated-note.md",
        ], self.contract)
        self.assertEqual(result["impact"], "NONE")
        self.assertEqual(result["wakeFiles"], [])

    def test_sentinel_readme_is_scan(self) -> None:
        result = classify_paths(["tools/prisma-sentinels/sync-sentinel/README.md"], self.contract)
        self.assertEqual(result["impact"], "SCAN")

    def test_runtime_owners_are_certify(self) -> None:
        paths = [
            "apps/terminal-de-venta-system/products/tablet/app/src/server/sync/dispatcher.ts",
            "apps/terminal-de-venta-system/products/pc/app/src/server/services/sync-ingest.service.ts",
            "apps/terminal-de-venta-system/products/mobile/app/src/lib/prisma-app/mobile-security/context.ts",
            "apps/terminal-de-venta-system/prisma/schema.prisma",
            "pnpm-lock.yaml",
        ]
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(classify_paths([path], self.contract)["impact"], "CERTIFY")

    def test_watch_workflow_wakes_itself_with_or_without_dot_prefix(self) -> None:
        paths = [
            ".github/workflows/prisma-sync-sentinel-watch.yml",
            "./.github/workflows/prisma-sync-sentinel-watch.yml",
        ]
        for path in paths:
            with self.subTest(path=path):
                result = classify_paths([path], self.contract)
                self.assertEqual(result["impact"], "CERTIFY")
                self.assertEqual(result["wakeFiles"], [".github/workflows/prisma-sync-sentinel-watch.yml"])

    def test_certify_wins_over_scan(self) -> None:
        result = classify_paths([
            "tools/prisma-sentinels/sync-sentinel/README.md",
            "apps/terminal-de-venta-system/products/mobile/app/app/api/mobile/v1/read-models/sync-source-health/route.ts",
        ], self.contract)
        self.assertEqual(result["impact"], "CERTIFY")

    def test_windows_path_normalizes(self) -> None:
        result = classify_paths([r"apps\terminal-de-venta-system\products\tablet\app\src\server\sync\dispatcher.ts"], self.contract)
        self.assertEqual(result["impact"], "CERTIFY")

    def test_weekly_and_evidence_contract(self) -> None:
        self.assertEqual(self.contract["weeklySchedule"], "17 10 * * 1")
        self.assertEqual(self.contract["artifacts"]["retentionDays"], 30)
        self.assertFalse(self.contract["policy"]["passOpensIssue"])
        self.assertFalse(self.contract["policy"]["productionCertified"])
        self.assertTrue(self.contract["policy"]["unknownFailsClosed"])
        self.assertEqual(self.contract["canonicalRuntimes"]["mobile"], 3140)

    def test_summary_localizes_first_failed_check(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = {
                "status": "FAIL_SYNC_CERTIFICATION",
                "checks": [
                    {"id": "head_lock", "verdict": "PASS", "detail": "ok"},
                    {"id": "mobile_runtime_3140_journeys", "verdict": "FAIL", "detail": "runtime failed"},
                    {"id": "capsule_cleanup", "verdict": "PASS", "detail": "cleanup"},
                ],
                "facts": {"sourceDrift": False, "cleanupPass": True, "orphanProcesses": False, "liveDbTouched": False},
            }
            (root / "certify.log").write_text(json.dumps(payload), encoding="utf-8")
            summary = build_summary({
                "impact": "CERTIFY",
                "head": "abc",
                "base": "def",
                "event": "pull_request",
                "wakeFiles": ["x"],
            }, root)
            self.assertIn("mobile_runtime_3140_journeys", summary)
            self.assertIn("head_lock", summary)
            self.assertIn("sourceDrift", summary)
            self.assertIn("runtime failed", summary)

    def test_summary_recognizes_self_test_pass_token(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "self-test.log").write_text("Ran 20 tests\nOK\nPASS_SYNC_SENTINEL_SELF_TEST\n", encoding="utf-8")
            summary = build_summary({
                "impact": "SCAN",
                "head": "abc",
                "base": "def",
                "event": "pull_request",
                "wakeFiles": ["tools/prisma-sentinels/sync-sentinel/README.md"],
            }, root)
            self.assertIn("PASS_SYNC_SENTINEL_SELF_TEST", summary)
            self.assertNotIn("Failed stage: `self-test`", summary)

    def test_certify_pass_can_reconcile_preliminary_scan_but_keeps_it_visible(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "self-test.log").write_text("PASS_SYNC_SENTINEL_SELF_TEST\n", encoding="utf-8")
            (root / "scan.log").write_text(json.dumps({
                "status": "FAIL_SYNC_SCAN",
                "checks": [{"id": "legacy_native_probe", "verdict": "FAIL", "detail": "known baseline signature"}],
            }), encoding="utf-8")
            (root / "diagnose.log").write_text(json.dumps({"status": "PASS_SYNC_DIAGNOSIS", "checks": []}), encoding="utf-8")
            (root / "certify.log").write_text(json.dumps({
                "status": "PASS_SYNC_CERTIFICATION",
                "checks": [{"id": "runtime_backed_reconciliation", "verdict": "PASS", "detail": "exact signature reconciled"}],
            }), encoding="utf-8")
            summary = build_summary({
                "impact": "CERTIFY",
                "head": "abc",
                "base": "def",
                "event": "pull_request",
                "wakeFiles": ["x"],
            }, root)
            self.assertIn("FAIL_SYNC_SCAN", summary)
            self.assertIn("PASS_SYNC_CERTIFICATION", summary)
            self.assertIn("strict runtime-backed exact-signature reconciliation", summary)
            self.assertNotIn("Causal failure localization", summary)


if __name__ == "__main__":
    unittest.main()
