from __future__ import annotations

import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.reports import build_acceptance_result


class AcceptanceLogicTests(unittest.TestCase):
    def test_conflict_rejects_both_packages(self):
        reports = [
            {"bundle_manifest": {"package_id": "01-identity-access-and-trust", "bundle_id": "b1", "payload_files": [{"repo_path": "apps/app/auth.py"}]}, "schema_errors": [], "structure_errors": [], "ownership_errors": [], "payload_mismatches": [], "warnings": []},
            {"bundle_manifest": {"package_id": "03-service-contracts-and-orchestration", "bundle_id": "b2", "payload_files": [{"repo_path": "apps/app/auth.py"}]}, "schema_errors": [], "structure_errors": [], "ownership_errors": [], "payload_mismatches": [], "warnings": []},
        ]
        overlap = {"ok": False, "conflicts": [{"path": "apps/app/auth.py", "packages": ["01-identity-access-and-trust", "03-service-contracts-and-orchestration"]}]}
        acceptance = build_acceptance_result("prj-demo", "run-prj-demo-20260327-01", "rd-001", reports, overlap)
        self.assertEqual(acceptance["overall_status"], "reject")
        self.assertTrue(all(item["status"] == "reject" for item in acceptance["package_results"]))


if __name__ == "__main__":
    unittest.main()
