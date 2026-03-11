from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory import common, config, contracts  # noqa: E402


class WorkerTaxonomyTests(unittest.TestCase):
    def test_legacy_aliases_resolve_to_canonical_ids(self) -> None:
        self.assertEqual("A_core", common.canonical_worker_id("A_worker"))
        self.assertEqual("B_tooling", common.canonical_worker_id("B_worker"))
        self.assertEqual("C_features", common.canonical_worker_id("C_worker"))
        self.assertEqual("D_validation", common.canonical_worker_id("D_worker"))
        self.assertEqual("Z_aggregator", common.canonical_worker_id("Z_integrator"))

    def test_canonicalize_workers_accepts_legacy_inputs(self) -> None:
        parsed = common.canonicalize_workers(
            ["Z_integrator", "C_worker", "A_worker", "B_worker", "D_worker"],
            include_integrator=True,
        )
        self.assertEqual(
            ["A_core", "B_tooling", "C_features", "D_validation", "Z_aggregator"],
            parsed,
        )

    def test_default_config_keeps_b_tooling_and_c_features_semantics(self) -> None:
        payload = config.default_factory_config()

        self.assertEqual("C_features", payload["run"]["visual_baseline_owner"])
        self.assertIn("tools/**", payload["workers"]["allowlist_globs"]["B_tooling"])
        self.assertIn("apps/**", payload["workers"]["allowlist_globs"]["C_features"])
        self.assertIn("docs/visual-baselines/**", payload["workers"]["allowlist_globs"]["C_features"])
        self.assertIn("tools/_local/visual/**", payload["workers"]["allowlist_globs"]["C_features"])

    def test_load_config_canonicalizes_legacy_worker_keys(self) -> None:
        base = config.default_factory_config()
        base["run"]["visual_baseline_owner"] = "C_worker"
        base["workers"]["allowlist_globs"] = {
            "B_worker": ["tools/**"],
            "C_worker": ["apps/**"],
        }
        base["workers"]["denylist_globs"] = {
            "B_worker": [".git/**"],
            "C_worker": [".git/**"],
        }

        with tempfile.TemporaryDirectory(prefix="worker_taxonomy_config_") as temp_dir:
            path = Path(temp_dir) / "factory.config.json"
            path.write_text(json.dumps(base, indent=2, sort_keys=True), encoding="utf-8")
            loaded = config.load_factory_config(config_path=path.as_posix(), strict=True)

        self.assertEqual("C_features", loaded["run"]["visual_baseline_owner"])
        self.assertIn("B_tooling", loaded["workers"]["allowlist_globs"])
        self.assertIn("C_features", loaded["workers"]["allowlist_globs"])
        self.assertNotIn("B_worker", loaded["workers"]["allowlist_globs"])
        self.assertNotIn("C_worker", loaded["workers"]["allowlist_globs"])

    def test_resolve_bundle_dir_prefers_existing_legacy_folder(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worker_taxonomy_runs_") as temp_dir:
            runs_dir = Path(temp_dir) / "runs"
            legacy = runs_dir / "factory_legacy_case" / "B_worker"
            legacy.mkdir(parents=True, exist_ok=True)

            with patch.object(common, "RUNS_DIR", runs_dir):
                resolved = common.resolve_bundle_dir("factory_legacy_case", "B_tooling", prefer_existing=True)

            self.assertEqual(legacy, resolved)

    def test_scaffold_emits_canonical_ids_and_gravity_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="worker_taxonomy_scaffold_") as temp_dir:
            runs_dir = Path(temp_dir) / "runs"
            runs_dir.mkdir(parents=True, exist_ok=True)
            run_id = "factory_taxonomy_scaffold"

            with patch.object(common, "RUNS_DIR", runs_dir), patch.object(contracts, "RUNS_DIR", runs_dir):
                worker_bundle = contracts.scaffold_worker_bundle(run_id, "B_worker")
                integrator_bundle = contracts.scaffold_integrator_bundle(run_id)

            self.assertEqual("B_tooling", worker_bundle["worker"])
            self.assertEqual("Z_aggregator", integrator_bundle["worker"])

            worker_status = common.read_json(runs_dir / run_id / "B_tooling" / "STATUS.json")
            self.assertEqual("B_tooling", worker_status.get("worker_id"))

            integrator_root = runs_dir / run_id / "Z_aggregator"
            for filename in (
                "GRAVITY_REPORT.json",
                "PROTECTED_NODES.json",
                "IMPACT_CONE_REPORT.json",
                "DEPENDENCY_DIFF.json",
                "DISPATCH_RECOMMENDATIONS.json",
            ):
                self.assertTrue((integrator_root / filename).exists(), filename)


if __name__ == "__main__":
    unittest.main()
