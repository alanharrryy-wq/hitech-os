from __future__ import annotations

import unittest

from pya.contracts.switch_contracts import build_switch_registry_entry
from pya.engines.switch_engine.engine import SwitchEngine, resolve_switch_entries

from tests.helpers import build_context, load_manifest, read_json


class SwitchEngineTests(unittest.TestCase):
    def test_precedence_prefers_switch_id_override(self) -> None:
        entry = build_switch_registry_entry(
            switch_id="module.enabled:abc",
            target_type="module",
            target_id="abc",
            default_value=False,
            applicable_rules=["default_true"],
            allowed_overrides=["switch_id", "target_id"],
            rollout={"strategy": "static"},
            metadata={},
            state="canonical",
            updated_at="2026-04-11T00:00:00Z",
        )
        resolutions, _, _ = resolve_switch_entries([entry], {"module.enabled:abc": True, "abc": False}, "2026-04-11T00:00:00Z")
        self.assertTrue(resolutions[0]["resolved_value"])
        self.assertEqual(resolutions[0]["decision_source"], "switch_id")

    def test_invalid_override_is_ignored(self) -> None:
        temp_dir, context = build_context()
        try:
            context.storage.write_registry(
                "registry_builder",
                "switch_registry",
                [
                    build_switch_registry_entry(
                        switch_id="module.enabled:abc",
                        target_type="module",
                        target_id="abc",
                        default_value=True,
                        applicable_rules=["default_true"],
                        allowed_overrides=["switch_id"],
                        rollout={"strategy": "static"},
                        metadata={},
                        state="canonical",
                        updated_at=context.execution_time,
                    )
                ],
            )
            context.config.switch_overrides = {"module.enabled:abc": "yes"}
            engine = SwitchEngine(manifest=load_manifest("switch_engine"))
            result = engine.run(context)
            resolutions = read_json(context.paths.registries / "switch_resolutions.json")
            self.assertTrue(resolutions[0]["resolved_value"])
            self.assertIn("switch_resolutions", result.execution_summary["registries_written"])
        finally:
            temp_dir.cleanup()

    def test_batch_consistent(self) -> None:
        entries = [
            build_switch_registry_entry(
                switch_id="b", target_type="module", target_id="b", default_value=True,
                applicable_rules=[], allowed_overrides=[], rollout={"strategy": "static"}, metadata={}, state="canonical", updated_at="2026-04-11T00:00:00Z",
            ),
            build_switch_registry_entry(
                switch_id="a", target_type="module", target_id="a", default_value=True,
                applicable_rules=[], allowed_overrides=[], rollout={"strategy": "static"}, metadata={}, state="canonical", updated_at="2026-04-11T00:00:00Z",
            ),
        ]
        resolutions, _, _ = resolve_switch_entries(entries, {}, "2026-04-11T00:00:00Z")
        self.assertEqual([item["switch_id"] for item in resolutions], ["a", "b"])


if __name__ == "__main__":
    unittest.main()
