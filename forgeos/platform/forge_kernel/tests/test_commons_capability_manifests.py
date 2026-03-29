import json
import unittest
from pathlib import Path

from forge_kernel import KernelBootstrap


class CommonsCapabilityManifestTests(unittest.TestCase):
    def test_commons_registry_and_manifests_are_consistent(self) -> None:
        forgeos_root = Path(__file__).resolve().parents[3]
        commons_root = forgeos_root / "platform" / "forge_commons"
        registry_path = commons_root / "CAPABILITY_REGISTRY.json"
        self.assertTrue(registry_path.exists(), "commons capability registry must exist")

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        capabilities = registry["capabilities"]
        self.assertEqual(len(capabilities), 5)

        kernel_contracts = {
            definition.contract_id
            for definition in KernelBootstrap.start().contracts.known_contracts()
        }

        for item in capabilities:
            capability_dir = commons_root / item["directory"]
            manifest_path = capability_dir / "CAPABILITY_MANIFEST.json"
            self.assertTrue(manifest_path.exists(), f"manifest missing for {item['directory']}")

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["capability_id"], item["capability_id"])
            self.assertEqual(manifest["owner"], item["owner"])
            self.assertIn("state_authority", manifest)
            self.assertIn("lifecycle", manifest)
            self.assertIn("contract_bindings", manifest)
            self.assertIn("packaging", manifest)

            for binding in manifest["contract_bindings"]:
                if binding["status"] == "registered":
                    self.assertIn(
                        binding["contract_id"],
                        kernel_contracts,
                        f"registered contract {binding['contract_id']} must exist in kernel runtime",
                    )


if __name__ == "__main__":
    unittest.main()
