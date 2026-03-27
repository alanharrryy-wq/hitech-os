from __future__ import annotations

import json
import sys
import tempfile
import zipfile
from hashlib import sha256
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.bundles import validate_bundle_zip


class ZipValidationTests(unittest.TestCase):
    def test_valid_bundle_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "repo"
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "configs/execution_framework/system_config.json").write_text(json.dumps({"active_package_ids": ["03-service-contracts-and-orchestration"]}), encoding="utf-8")
            (repo / "configs/execution_framework/path_policies.json").write_text(json.dumps({
                "03-service-contracts-and-orchestration": {
                    "allowed_paths": ["services/api/**"],
                    "forbidden_paths": []
                }
            }), encoding="utf-8")
            payload = b'{"ok": true}\n'
            digest = sha256(payload).hexdigest()
            bundle = tmp / "bundle.zip"
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("notes/summary.md", "x")
                zf.writestr("payload/services/api/file.json", payload)
                zf.writestr("bundle_manifest.json", json.dumps({
                    "schema_version": "1.0",
                    "project_id": "prj-demo",
                    "run_id": "run-prj-demo-20260327-01",
                    "round_id": "rd-001",
                    "package_id": "03-service-contracts-and-orchestration",
                    "bundle_id": "b1",
                    "bundle_version": 1,
                    "created_at_utc": "2026-03-27T00:00:00Z",
                    "status": "submitted",
                    "payload_files": [{
                        "repo_path": "services/api/file.json",
                        "sha256": digest,
                        "size_bytes": len(payload)
                    }]
                }))
                zf.writestr("package_report.json", json.dumps({
                    "schema_version": "1.0",
                    "project_id": "prj-demo",
                    "run_id": "run-prj-demo-20260327-01",
                    "round_id": "rd-001",
                    "package_id": "03-service-contracts-and-orchestration",
                    "bundle_id": "b1",
                    "summary": "ok",
                    "status": "submitted",
                    "highlights": [],
                    "known_gaps": []
                }))
            result = validate_bundle_zip(bundle, repo)
            self.assertTrue(result["ok"])


if __name__ == "__main__":
    unittest.main()
