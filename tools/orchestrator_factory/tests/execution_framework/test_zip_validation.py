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

    def test_bundle_with_unsafe_archive_path_is_rejected(self):
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
            bundle = tmp / "bundle_unsafe.zip"
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("notes/summary.md", "x")
                zf.writestr("payload/services/api/file.json", payload)
                zf.writestr("../escape.txt", "bad")
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
            self.assertFalse(result["ok"])
            self.assertTrue(any(item["code"] in {"unsafe_archive_member", "unsafe_archive"} for item in result["structure_errors"]))

    def test_bundle_signature_required_rejects_missing_signature(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "repo"
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "configs/execution_framework/system_config.json").write_text(
                json.dumps(
                    {
                        "active_package_ids": ["03-service-contracts-and-orchestration"],
                        "bundle_security": {
                            "require_manifest_signature": True,
                            "signature_algorithm": "hmac-sha256",
                            "signature_env_var": "UEF_BUNDLE_SIGNING_KEY",
                        },
                    }
                ),
                encoding="utf-8",
            )
            (repo / "configs/execution_framework/path_policies.json").write_text(
                json.dumps(
                    {
                        "03-service-contracts-and-orchestration": {
                            "allowed_paths": ["services/api/**"],
                            "forbidden_paths": [],
                        }
                    }
                ),
                encoding="utf-8",
            )
            payload = b'{"ok": true}\n'
            digest = sha256(payload).hexdigest()
            bundle = tmp / "bundle_unsigned.zip"
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("notes/summary.md", "x")
                zf.writestr("payload/services/api/file.json", payload)
                zf.writestr(
                    "bundle_manifest.json",
                    json.dumps(
                        {
                            "schema_version": "1.0",
                            "project_id": "prj-demo",
                            "run_id": "run-prj-demo-20260327-01",
                            "round_id": "rd-001",
                            "package_id": "03-service-contracts-and-orchestration",
                            "bundle_id": "b1",
                            "bundle_version": 1,
                            "created_at_utc": "2026-03-27T00:00:00Z",
                            "status": "submitted",
                            "payload_files": [
                                {
                                    "repo_path": "services/api/file.json",
                                    "sha256": digest,
                                    "size_bytes": len(payload),
                                }
                            ],
                        }
                    ),
                )
                zf.writestr(
                    "package_report.json",
                    json.dumps(
                        {
                            "schema_version": "1.0",
                            "project_id": "prj-demo",
                            "run_id": "run-prj-demo-20260327-01",
                            "round_id": "rd-001",
                            "package_id": "03-service-contracts-and-orchestration",
                            "bundle_id": "b1",
                            "summary": "ok",
                            "status": "submitted",
                            "highlights": [],
                            "known_gaps": [],
                        }
                    ),
                )
            result = validate_bundle_zip(bundle, repo)
            self.assertFalse(result["ok"])
            self.assertTrue(any(item["code"] == "missing_manifest_signature" for item in result["schema_errors"]))

    def test_bundle_with_missing_waiver_ref_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            repo = tmp / "repo"
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "schemas/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "configs/execution_framework/system_config.json").write_text(json.dumps({"active_package_ids": ["03-service-contracts-and-orchestration"]}), encoding="utf-8")
            (repo / "configs/execution_framework/path_policies.json").write_text(
                json.dumps(
                    {
                        "03-service-contracts-and-orchestration": {
                            "allowed_paths": ["services/api/**"],
                            "forbidden_paths": [],
                        }
                    }
                ),
                encoding="utf-8",
            )
            (repo / "schemas/execution_framework/waiver_request.schema.json").write_text(
                json.dumps({"name": "waiver_request", "required_fields": {"waiver_id": "string", "decision_status": "string"}}),
                encoding="utf-8",
            )
            payload = b'{"ok": true}\n'
            digest = sha256(payload).hexdigest()
            bundle = tmp / "bundle_missing_waiver.zip"
            with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                zf.writestr("notes/summary.md", "x")
                zf.writestr("payload/services/api/file.json", payload)
                zf.writestr(
                    "bundle_manifest.json",
                    json.dumps(
                        {
                            "schema_version": "1.0",
                            "project_id": "prj-demo",
                            "run_id": "run-prj-demo-20260327-01",
                            "round_id": "rd-001",
                            "package_id": "03-service-contracts-and-orchestration",
                            "bundle_id": "b1",
                            "bundle_version": 1,
                            "created_at_utc": "2026-03-27T00:00:00Z",
                            "status": "submitted",
                            "waiver_refs": ["ops/runs/run-prj-demo-20260327-01/rounds/rd-001/reports/waivers/missing.json"],
                            "payload_files": [
                                {
                                    "repo_path": "services/api/file.json",
                                    "sha256": digest,
                                    "size_bytes": len(payload),
                                }
                            ],
                        }
                    ),
                )
                zf.writestr(
                    "package_report.json",
                    json.dumps(
                        {
                            "schema_version": "1.0",
                            "project_id": "prj-demo",
                            "run_id": "run-prj-demo-20260327-01",
                            "round_id": "rd-001",
                            "package_id": "03-service-contracts-and-orchestration",
                            "bundle_id": "b1",
                            "summary": "ok",
                            "status": "submitted",
                            "highlights": [],
                            "known_gaps": [],
                        }
                    ),
                )
            result = validate_bundle_zip(bundle, repo)
            self.assertFalse(result["ok"])
            self.assertTrue(any(item["code"] == "missing_waiver_ref" for item in result["schema_errors"]))


if __name__ == "__main__":
    unittest.main()
