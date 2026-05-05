from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pya.contracts.signal_contract import build_signal
from pya.engines.registry_builder.engine import RegistryBuilderEngine

from tests.helpers import build_context, build_frontend_target, build_noisy_frontend_target, load_manifest, read_json


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

    def test_noise_paths_do_not_become_canonical_modules(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = build_noisy_frontend_target(Path(temp))
            temp_dir, context = build_context(target=target)
            try:
                from pya.engines.scanner.engine import ScannerEngine
                ScannerEngine(manifest=load_manifest("scanner")).run(context)
                engine = RegistryBuilderEngine(manifest=load_manifest("registry_builder"))
                engine.run(context)
                module_registry = read_json(context.paths.registries / "module_registry.json")
                summary = read_json(context.paths.artifacts / "metrics" / "registry_build_summary.json")
                names = {item["name"] for item in module_registry}
                self.assertFalse(any(name.startswith("docs.") for name in names))
                self.assertFalse(any(name.startswith("reports.") for name in names))
                self.assertFalse(any(name.startswith("_dependency_graphs.") for name in names))
                self.assertFalse(any(name.startswith("tests.") for name in names))
                self.assertFalse(any(name.startswith("tools.") for name in names))
                self.assertFalse(any(name.endswith(".README") for name in names))
                self.assertEqual(summary["skipped_module_candidate_paths"], [])
            finally:
                temp_dir.cleanup()

    def test_non_product_module_candidates_are_filtered_with_reason(self) -> None:
        temp_dir, context = build_context()
        try:
            signals = [
                build_signal(
                    signal_type="module_candidate",
                    source_path="tests/payments.i18n.contract.test.ts",
                    producer="scanner",
                    state="candidate",
                    confidence=0.7,
                    evidence={"surface_kind": "module", "canonical_source": True},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    module_name="tests.payments.i18n.contract.test",
                    tags=["typescript", "module"],
                ),
                build_signal(
                    signal_type="module_candidate",
                    source_path="tools/enforce_i18n_guardrails.py",
                    producer="scanner",
                    state="candidate",
                    confidence=0.7,
                    evidence={"surface_kind": "python_module", "canonical_source": True},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    module_name="tools.enforce_i18n_guardrails",
                    tags=["python", "module"],
                ),
                build_signal(
                    signal_type="module_candidate",
                    source_path="src/lib/i18n/use-t.ts",
                    producer="scanner",
                    state="candidate",
                    confidence=0.7,
                    evidence={"surface_kind": "module", "canonical_source": True},
                    snapshot_id=context.execution_id,
                    created_at=context.execution_time,
                    module_name="src.lib.i18n.use_t",
                    tags=["typescript", "module"],
                ),
            ]
            context.storage.write_registry("scanner", "signals", signals)
            engine = RegistryBuilderEngine(manifest=load_manifest("registry_builder"))
            engine.run(context)
            module_registry = read_json(context.paths.registries / "module_registry.json")
            summary = read_json(context.paths.artifacts / "metrics" / "registry_build_summary.json")
            names = {item["name"] for item in module_registry}
            self.assertEqual(names, {"src.lib.i18n.use_t"})
            self.assertEqual(
                summary["skipped_module_candidate_paths"],
                ["tests/payments.i18n.contract.test.ts", "tools/enforce_i18n_guardrails.py"],
            )
            self.assertEqual(summary["skipped_module_candidate_reasons"]["non_product:tests"], 1)
            self.assertEqual(summary["skipped_module_candidate_reasons"]["non_product:tooling"], 1)
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
