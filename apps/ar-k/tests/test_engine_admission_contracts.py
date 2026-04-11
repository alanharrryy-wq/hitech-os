from __future__ import annotations

import copy
import unittest

from pya.system.admission import admit_engine_manifest
from pya.system.root_manifest import get_root_manifest

from tests.helpers import load_manifest


class EngineAdmissionTests(unittest.TestCase):
    def test_canonical_manifests_are_admitted(self) -> None:
        root_manifest = get_root_manifest()
        for name in ["scanner", "registry_builder", "switch_engine", "contract_validator", "ai_annotator"]:
            manifest = load_manifest(name)
            decision = admit_engine_manifest(manifest, root_manifest)
            self.assertTrue(decision.admitted, msg=f"{name}: {decision.reasons}")

    def test_invalid_writer_is_rejected(self) -> None:
        root_manifest = get_root_manifest()
        manifest = copy.deepcopy(load_manifest("scanner"))
        manifest["registries_touched"]["writes"] = ["module_registry"]
        decision = admit_engine_manifest(manifest, root_manifest)
        self.assertFalse(decision.admitted)
        self.assertTrue(any("sovereign writer" in reason for reason in decision.reasons))

    def test_invalid_stage_is_rejected(self) -> None:
        root_manifest = get_root_manifest()
        manifest = copy.deepcopy(load_manifest("scanner"))
        manifest["stage"] = "weird"
        decision = admit_engine_manifest(manifest, root_manifest)
        self.assertFalse(decision.admitted)


if __name__ == "__main__":
    unittest.main()
