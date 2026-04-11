from __future__ import annotations

import unittest

from pya.contracts.registry_contracts import build_module_registry_entry
from pya.contracts.switch_contracts import build_switch_resolution
from pya.engines.ai_annotator.engine import AIAnnotatorEngine

from tests.helpers import build_context, load_manifest, read_json


class AIAnnotatorEngineTests(unittest.TestCase):
    def test_annotation_shape_and_non_canonical_behavior(self) -> None:
        temp_dir, context = build_context()
        try:
            module = build_module_registry_entry(
                module_id="mod_a",
                name="app.service",
                kind="python_module",
                area="app",
                status="candidate",
                source_of_truth="scanner",
                confidence=0.7,
                declared_by=["registry_builder"],
                observed_in=["app/service.py"],
                tags=["python"],
                boundaries=[],
                switches=["module.enabled:mod_a"],
                contracts=[],
                artifacts=[],
                updated_at=context.execution_time,
                snapshot_id=context.execution_id,
            )
            context.storage.write_registry("registry_builder", "module_registry", [module])
            context.storage.write_registry("registry_builder", "boundary_registry", [])
            context.storage.write_registry("contract_validator", "validation_report", {"summary": {"status": "validated"}, "violations": [{"entity_id": "mod_a", "severity": "warning"}]})
            context.storage.write_registry(
                "switch_engine",
                "switch_resolutions",
                [
                    build_switch_resolution(
                        switch_id="module.enabled:mod_a",
                        target_type="module",
                        target_id="mod_a",
                        evaluated_context={},
                        default_value=True,
                        resolved_value=True,
                        decision_source="default",
                        precedence_path=["default"],
                        justification="default",
                        timestamp=context.execution_time,
                        state="effective",
                    )
                ],
            )
            engine = AIAnnotatorEngine(manifest=load_manifest("ai_annotator"))
            result = engine.run(context)
            annotations = read_json(context.paths.registries / "annotations.json")
            self.assertEqual(result.execution_summary["registries_written"], ["annotations"])
            self.assertTrue(annotations[0]["summary"])
            self.assertLessEqual(annotations[0]["confidence"], 0.89)
            self.assertIn("ambiguous", annotations[0]["rationale"].lower())
            module_registry = read_json(context.paths.registries / "module_registry.json")
            self.assertEqual(module_registry[0]["status"], "candidate")
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
