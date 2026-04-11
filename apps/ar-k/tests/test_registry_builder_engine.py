from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pya.contracts.signal_contract import build_signal
from pya.engines.registry_builder.engine import RegistryBuilderEngine

from tests.helpers import build_context, build_frontend_target, load_manifest, read_json


class RegistryBuilderEngineTests(unittest.TestCase):
    def test_stable_identity_and_snapshot(self) -> None:
        temp_dir, context = build_context()
        try:
            from pya.engines.scanner.engine import ScannerEngine
            ScannerEngine(manifest=load_manifest("scanner")).run(context)
            engine = RegistryBuilderEngine(manifest=load_manifest("registry_builder"))
            engine.run(context)
            module_registry = read_json(context.paths.registries / "module_registry.json")
            snapshot_files = list(context.paths.snapshots.glob("*.json"))
            self.assertGreater(len(module_registry), 0)
            self.assertEqual(module_registry[0]["module_id"], module_registry[0]["module_id"])
            self.assertTrue(snapshot_files)
        finally:
            temp_dir.cleanup()

    def test_merge_rules_detect_conflict(self) -> None:
        temp_dir, context = build_context()
        try:
            duplicate_signals = [
                build_signal(
                    signal_type="module_candidate",
                    source_path="a.py",
                    producer="scanner",
                    state="candidate",
                    confidence=0.8,
                    evidence={"imports": [], "exports": []},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    module_name="dup.module",
                ),
                build_signal(
                    signal_type="module_candidate",
                    source_path="b.py",
                    producer="scanner",
                    state="candidate",
                    confidence=0.8,
                    evidence={"imports": [], "exports": []},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    module_name="dup.module",
                ),
            ]
            context.storage.write_registry("scanner", "signals", duplicate_signals)
            engine = RegistryBuilderEngine(manifest=load_manifest("registry_builder"))
            engine.run(context)
            summary = read_json(context.paths.artifacts / "metrics" / "registry_build_summary.json")
            self.assertEqual(len(summary["conflicts"]), 1)
        finally:
            temp_dir.cleanup()

    def test_frontend_surface_candidates_become_canonical_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = build_frontend_target(Path(temp))
            temp_dir, context = build_context(target=target)
            try:
                from pya.engines.scanner.engine import ScannerEngine
                ScannerEngine(manifest=load_manifest("scanner")).run(context)
                engine = RegistryBuilderEngine(manifest=load_manifest("registry_builder"))
                engine.run(context)
                module_registry = read_json(context.paths.registries / "module_registry.json")
                boundary_registry = read_json(context.paths.registries / "boundary_registry.json")
                query_index = read_json(context.paths.indices / "query_index.json")
                self.assertTrue(any(item["kind"] == "entrypoint" for item in module_registry))
                self.assertTrue(any(item["kind"] == "component" for item in module_registry))
                self.assertTrue(any(item["boundary_type"] == "desktop_bridge_boundary" for item in boundary_registry))
                self.assertTrue(any("route-aware" in item["lookup_keys"] for item in query_index))
            finally:
                temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
