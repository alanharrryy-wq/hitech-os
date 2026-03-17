from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.config import (  # noqa: E402
    _deep_merge,
    default_factory_config,
    load_factory_config,
    load_config_file,
    resolve_config_path,
    validate_config,
)


class FactoryConfigTests(unittest.TestCase):
    def test_default_config_validates(self) -> None:
        payload = default_factory_config()
        self.assertEqual([], validate_config(payload))

    def test_precedence_defaults_file_env_cli(self) -> None:
        with tempfile.TemporaryDirectory(prefix="config_precedence_") as temp_dir:
            path = Path(temp_dir) / "factory.config.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": 2,
                        "contract_version": 2,
                        "run": {
                            "kind": "factory",
                            "run_prefix": "from_file",
                            "branch_prefix": "file/branch",
                            "base_ref": "FILE_HEAD",
                            "strict_collision_mode": False,
                            "allow_identical_patch_overlap": False,
                            "quarantine_on_suspicious_bundle": True,
                        },
                        "paths": {
                            "repo_root": "file_repo",
                            "runs_dir": "file_runs",
                            "worktrees_dir": "file_worktrees",
                        },
                        "workers": default_factory_config()["workers"],
                        "security": default_factory_config()["security"],
                        "feature_flags": default_factory_config()["feature_flags"],
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            env = {
                "FACTORY_RUN__RUN_PREFIX": "from_env",
                "FACTORY_RUN__BASE_REF": "ENV_HEAD",
                "FACTORY_FEATURE_FLAGS__ENABLE_QUARANTINE": "true",
            }
            cli = {"run": {"run_prefix": "from_cli"}}
            payload = load_factory_config(config_path=path.as_posix(), env=env, cli_overrides=cli, strict=True)

            self.assertEqual("from_cli", payload["run"]["run_prefix"])
            self.assertEqual("ENV_HEAD", payload["run"]["base_ref"])
            self.assertEqual("file/branch", payload["run"]["branch_prefix"])
            self.assertTrue(payload["feature_flags"]["enable_quarantine"])

    def test_resolve_config_path_explicit(self) -> None:
        with tempfile.TemporaryDirectory(prefix="config_path_") as temp_dir:
            explicit = Path(temp_dir) / "abc.json"
            resolved = resolve_config_path(explicit.as_posix())
            self.assertEqual(explicit.resolve(strict=False), resolved)

    def test_load_missing_config_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="config_missing_") as temp_dir:
            missing = Path(temp_dir) / "missing.json"
            payload = load_config_file(missing)
            self.assertEqual({}, payload)

    def test_invalid_config_rejected_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="config_invalid_") as temp_dir:
            path = Path(temp_dir) / "bad.config.json"
            path.write_text(json.dumps({"run": {"strict_collision_mode": "nope"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_factory_config(config_path=path.as_posix(), strict=True)

    def test_non_strict_returns_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory(prefix="config_nonstrict_") as temp_dir:
            path = Path(temp_dir) / "bad.config.json"
            path.write_text(json.dumps({"run": {"strict_collision_mode": "nope"}}), encoding="utf-8")
            payload = load_factory_config(config_path=path.as_posix(), strict=False)
            self.assertIn("_validation_errors", payload)
            self.assertGreater(len(payload["_validation_errors"]), 0)

    def test_deep_merge_is_deterministic(self) -> None:
        left = {"a": {"b": 1}, "x": 1}
        right = {"a": {"c": 2}, "y": 3}
        merged_1 = _deep_merge(left, right)
        merged_2 = _deep_merge(left, right)
        self.assertEqual(merged_1, merged_2)
        self.assertEqual({"a": {"b": 1, "c": 2}, "x": 1, "y": 3}, merged_1)


if __name__ == "__main__":
    unittest.main()
