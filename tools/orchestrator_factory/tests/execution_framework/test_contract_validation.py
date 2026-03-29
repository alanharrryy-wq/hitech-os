from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

import validate_framework_contracts as vfc


class ContractValidationTests(unittest.TestCase):
    def test_validate_passes_for_minimal_valid_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "schemas/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "templates/execution_framework/run").mkdir(parents=True, exist_ok=True)
            (repo / "configs/execution_framework/system_config.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
            (repo / "schemas/execution_framework/run_manifest.schema.json").write_text(
                json.dumps({"name": "run_manifest", "required_fields": {"run_id": "string"}}), encoding="utf-8"
            )
            (repo / "templates/execution_framework/run/run_manifest.template.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")

            result = vfc.validate(repo)
            self.assertTrue(result["ok"])

    def test_validate_fails_for_invalid_semver(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "schemas/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "templates/execution_framework/run").mkdir(parents=True, exist_ok=True)
            (repo / "configs/execution_framework/system_config.json").write_text(json.dumps({"schema_version": "version-one"}), encoding="utf-8")
            (repo / "schemas/execution_framework/run_manifest.schema.json").write_text(
                json.dumps({"name": "run_manifest", "required_fields": {"run_id": "string"}}), encoding="utf-8"
            )
            (repo / "templates/execution_framework/run/run_manifest.template.json").write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")

            result = vfc.validate(repo)
            self.assertFalse(result["ok"])
            self.assertTrue(any(item["code"] == "invalid_schema_version" for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
