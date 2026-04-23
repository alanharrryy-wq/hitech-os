from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pya.engines.scanner.engine import ScannerEngine

from tests.helpers import build_context, build_frontend_target, build_noisy_frontend_target, load_manifest, read_json


class ScannerEngineTests(unittest.TestCase):
    def test_engine_runs_and_emits_signals(self) -> None:
        temp_dir, context = build_context()
        try:
            engine = ScannerEngine(manifest=load_manifest("scanner"))
            result = engine.run(context)
            signals = read_json(context.paths.registries / "signals.json")
            inventory = read_json(context.paths.artifacts / "inventory" / "scanner_inventory.json")
            self.assertGreater(len(signals), 0)
            self.assertGreater(len(inventory), 0)
            self.assertIn("signals", result.execution_summary["registries_written"])
        finally:
            temp_dir.cleanup()

    def test_tolerates_parse_defect(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "pkg").mkdir()
            (target / "pkg" / "ok.py").write_text("import json\n", encoding="utf-8")
            (target / "pkg" / "bad.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
            temp_dir, context = build_context(target=target)
            try:
                engine = ScannerEngine(manifest=load_manifest("scanner"))
                engine.run(context)
                signals = read_json(context.paths.registries / "signals.json")
                bad_signals = [
                    item
                    for item in signals
                    if item["source_path"].endswith("bad.py") and item["state"] == "ambiguous"
                ]
                self.assertTrue(bad_signals)
            finally:
                temp_dir.cleanup()

    def test_detects_frontend_observation_slice(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = build_frontend_target(Path(temp))
            temp_dir, context = build_context(target=target)
            try:
                engine = ScannerEngine(manifest=load_manifest("scanner"))
                engine.run(context)
                inventory = read_json(context.paths.artifacts / "inventory" / "scanner_inventory.json")
                metrics = read_json(context.paths.artifacts / "metrics" / "scanner_metrics.json")
                routes = read_json(context.paths.artifacts / "routes" / "route_candidates.json")
                boundaries = read_json(context.paths.artifacts / "boundaries" / "boundary_candidates.json")
                signals = read_json(context.paths.registries / "signals.json")
                self.assertTrue(any(item["surface_kind"] == "entrypoint" for item in inventory))
                self.assertTrue(any(item["surface_kind"] == "component" for item in inventory))
                self.assertGreaterEqual(metrics["route_candidate_count"], 2)
                self.assertGreaterEqual(metrics["boundary_candidate_count"], 4)
                self.assertTrue(any(item["route_path"] == "/" for item in routes))
                self.assertTrue(any(item["boundary_kind"] == "desktop_bridge_boundary" for item in boundaries))
                self.assertTrue(any(item["signal_type"] == "boundary_candidate" for item in signals))
            finally:
                temp_dir.cleanup()

    def test_skips_vendor_dirs_and_does_not_escape_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = build_frontend_target(Path(temp) / "app")
            nm = target / "node_modules" / ".pnpm" / "pkg" / "node_modules" / "dep"
            nm.mkdir(parents=True, exist_ok=True)
            (nm / "index.d.ts").write_text("export type X = string\n", encoding="utf-8")
            temp_dir, context = build_context(target=target)
            try:
                engine = ScannerEngine(manifest=load_manifest("scanner"))
                engine.run(context)
                inventory = read_json(context.paths.artifacts / "inventory" / "scanner_inventory.json")
                metrics = read_json(context.paths.artifacts / "metrics" / "scanner_metrics.json")
                self.assertFalse(any("node_modules" in item["path"] for item in inventory))
                self.assertGreaterEqual(metrics["skipped_vendor_dir_count"], 1)
                self.assertEqual(metrics["skipped_external_path_count"], 0)
            finally:
                temp_dir.cleanup()

    def test_noise_paths_stay_observed_but_not_promoted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = build_noisy_frontend_target(Path(temp))
            temp_dir, context = build_context(target=target)
            try:
                engine = ScannerEngine(manifest=load_manifest("scanner"))
                engine.run(context)
                inventory = read_json(context.paths.artifacts / "inventory" / "scanner_inventory.json")
                metrics = read_json(context.paths.artifacts / "metrics" / "scanner_metrics.json")
                signals = read_json(context.paths.registries / "signals.json")
                self.assertTrue(any(item["path"].startswith("docs/") and item["canonical_source"] is False for item in inventory))
                self.assertTrue(any(item["path"].startswith("reports/") and item["canonical_source"] is False for item in inventory))
                self.assertTrue(any(item["path"].startswith("tests/") and item["canonical_source"] is False for item in inventory))
                self.assertTrue(any(item["path"].startswith("tools/") and item["canonical_source"] is False for item in inventory))
                self.assertTrue(any(item["signal_type"] == "file_observed" and item["source_path"].startswith("docs/") for item in signals))
                self.assertTrue(any(item["signal_type"] == "file_observed" and item["source_path"].startswith("tests/") for item in signals))
                self.assertFalse(any(item["signal_type"] == "module_candidate" and item["source_path"].startswith("docs/") for item in signals))
                self.assertFalse(any(item["signal_type"] == "module_candidate" and item["source_path"].startswith("reports/") for item in signals))
                self.assertFalse(any(item["signal_type"] == "module_candidate" and item["source_path"].startswith("tests/") for item in signals))
                self.assertFalse(any(item["signal_type"] == "module_candidate" and item["source_path"].startswith("tools/") for item in signals))
                self.assertGreaterEqual(metrics["skipped_noncanonical_surface_count"], 3)
            finally:
                temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
