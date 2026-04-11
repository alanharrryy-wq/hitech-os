from __future__ import annotations

import unittest

from pya.contracts.index_contracts import build_query_index_entry
from pya.contracts.registry_contracts import build_boundary_entry, build_module_registry_entry
from pya.contracts.switch_contracts import build_switch_registry_entry, build_switch_resolution
from pya.engines.contract_validator.engine import ContractValidatorEngine

from tests.helpers import build_context, load_manifest, read_json


class ContractValidatorEngineTests(unittest.TestCase):
    def test_schema_invalid_and_broken_references_reported(self) -> None:
        temp_dir, context = build_context()
        try:
            module = build_module_registry_entry(
                module_id="mod_a",
                name="app.service",
                kind="python_module",
                area="app",
                status="canonical",
                source_of_truth="scanner",
                confidence=0.9,
                declared_by=["registry_builder"],
                observed_in=["app/service.py"],
                tags=["python"],
                boundaries=["missing_boundary"],
                switches=["missing_switch"],
                contracts=[],
                artifacts=[],
                updated_at=context.execution_time,
                snapshot_id=context.execution_id,
            )
            bad_boundary = build_boundary_entry(
                source_module_id="missing_mod",
                target_id="external:json",
                target_type="external",
                boundary_type="import",
                source_of_truth="scanner",
                status="canonical",
                evidence={"source_path": "app/service.py", "import": "json"},
                snapshot_id=context.execution_id,
                updated_at=context.execution_time,
            )
            switch_entry = build_switch_registry_entry(
                switch_id="sw_1",
                target_type="module",
                target_id="mod_a",
                default_value=True,
                applicable_rules=[],
                allowed_overrides=[],
                rollout={"strategy": "static"},
                metadata={},
                state="canonical",
                updated_at=context.execution_time,
            )
            resolution = build_switch_resolution(
                switch_id="sw_1",
                target_type="module",
                target_id="mod_wrong",
                evaluated_context={},
                default_value=True,
                resolved_value=False,
                decision_source="default",
                precedence_path=["default"],
                justification="default",
                timestamp=context.execution_time,
                state="effective",
            )
            index_entry = build_query_index_entry(
                entity_type="module",
                entity_id="mod_a",
                lookup_keys=["app.service"],
                registry_source="module_registry",
                snapshot_id=context.execution_id,
                updated_at=context.execution_time,
            )
            context.storage.write_registry("registry_builder", "module_registry", [module])
            context.storage.write_registry("registry_builder", "boundary_registry", [bad_boundary])
            context.storage.write_registry("registry_builder", "contract_registry", [])
            context.storage.write_registry("registry_builder", "switch_registry", [switch_entry])
            context.storage.write_registry("switch_engine", "switch_resolutions", [resolution])
            context.storage.write_index("registry_builder", "query_index", [index_entry])
            engine = ContractValidatorEngine(manifest=load_manifest("contract_validator"))
            engine.run(context)
            report = read_json(context.paths.registries / "validation_report.json")
            severities = {item["severity"] for item in report["violations"]}
            self.assertIn("error", severities)
            self.assertIn("critical", severities)
        finally:
            temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
