from __future__ import annotations

import importlib.util

import unittest
from pathlib import Path

from pya.contracts.contract_registry import get_contract_registry_entries
from pya.contracts.event_contracts import build_event, validate_event
from pya.contracts.signal_contract import build_signal, validate_signal
from pya.kernel.barriers import BARRIER_REQUIREMENTS
from pya.system.execution import CANONICAL_STAGE_ORDER
from pya.system.ownership import OWNERSHIP_MATRIX, may_write
from pya.system.root_manifest import get_root_manifest

from tests.helpers import project_root


class SystemKernelContractsTests(unittest.TestCase):
    def test_root_manifest_has_required_planes(self) -> None:
        manifest = get_root_manifest()
        self.assertEqual(manifest["canonical_stage_order"], CANONICAL_STAGE_ORDER)
        self.assertIn("ownership_policy", manifest)
        self.assertIn("contract_versions", manifest)
        self.assertIn("determinism_policy", manifest)

    def test_event_contract_validation_basic(self) -> None:
        event = build_event(
            name="scanner.completed",
            producer="scanner",
            target="sample",
            payload={"ok": True},
            severity="info",
            timestamp="2026-04-11T00:00:00Z",
        )
        validate_event(event)
        bad = dict(event)
        bad["severity"] = "loud"
        with self.assertRaises(Exception):
            validate_event(bad)

    def test_signal_contract_validation_basic(self) -> None:
        signal = build_signal(
            signal_type="file_observed",
            source_path="app/service.py",
            producer="scanner",
            state="observed",
            confidence=1.0,
            evidence={"kind": "python"},
            snapshot_id="run_1",
            created_at="2026-04-11T00:00:00Z",
        )
        validate_signal(signal)
        bad = dict(signal)
        bad["state"] = "canonical"
        with self.assertRaises(Exception):
            validate_signal(bad)

    def test_barrier_and_stage_order_sanity(self) -> None:
        self.assertEqual(list(BARRIER_REQUIREMENTS.keys()), CANONICAL_STAGE_ORDER)
        self.assertIn("signals", BARRIER_REQUIREMENTS["registry"])

    def test_ownership_write_path_sanity(self) -> None:
        writers = {name: policy["writer"] for name, policy in OWNERSHIP_MATRIX.items()}
        self.assertEqual(writers["module_registry"], "registry_builder")
        self.assertTrue(may_write("switch_engine", "switch_resolutions"))
        self.assertFalse(may_write("scanner", "module_registry"))

    def test_readme_parallel_instructions_exist(self) -> None:
        readme = (project_root() / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Developing the 5 engines in parallel", readme)
        self.assertIn("scanner", readme.lower())

    def test_contract_registry_modules_are_importable(self) -> None:
        for entry in get_contract_registry_entries():
            self.assertIsNotNone(importlib.util.find_spec(entry["module"]), msg=entry["module"])


if __name__ == "__main__":
    unittest.main()
