import json
import unittest
from pathlib import Path

from forge_kernel import (
    PackageLayer,
    PackageManifest,
    PackagingGate,
    compute_integrity_hash,
)


class PackagingHardeningPhase7Tests(unittest.TestCase):
    def test_all_packages_have_manifest_bom_and_rollback(self) -> None:
        forgeos_root = Path(__file__).resolve().parents[3]
        packages_root = forgeos_root / "packages"
        package_dirs = [
            packages_root / "platform" / "forge_kernel",
            packages_root / "platform" / "forge_commons",
            packages_root / "products" / "repo_analyzer",
            packages_root / "products" / "cloudflare_guardian",
            packages_root / "products" / "orchestrator_bridge",
        ]
        gate = PackagingGate()

        for package_dir in package_dirs:
            manifest_path = package_dir / "PACKAGE_MANIFEST.json"
            bom_path = package_dir / "BOM.md"
            rollback_path = package_dir / "ROLLBACK_PLAN.md"
            release_notes_path = package_dir / "RELEASE_NOTES.md"

            self.assertTrue(manifest_path.exists(), f"missing {manifest_path}")
            self.assertTrue(bom_path.exists(), f"missing {bom_path}")
            self.assertTrue(rollback_path.exists(), f"missing {rollback_path}")
            self.assertTrue(release_notes_path.exists(), f"missing {release_notes_path}")

            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            source_anchor = forgeos_root / data["source_anchor"]
            self.assertTrue(source_anchor.exists(), f"source anchor missing: {source_anchor}")
            verified_hash = compute_integrity_hash(source_anchor)

            manifest = PackageManifest(
                package_id=data["package_id"],
                layer=PackageLayer(data["layer"]),
                owner=data["owner"],
                version=data["version"],
                required_kernel_range=data["required_kernel_range"],
                integrity_hash=data["integrity_hash"],
            )
            result = gate.validate(
                manifest=manifest,
                kernel_version="0.1.0",
                verified_integrity_hash=verified_hash,
            )
            self.assertTrue(result.approved, f"package gate failed for {manifest.package_id}")

    def test_compatibility_matrix_exists(self) -> None:
        forgeos_root = Path(__file__).resolve().parents[3]
        matrix_path = forgeos_root / "packages" / "COMPATIBILITY_MATRIX.md"
        self.assertTrue(matrix_path.exists(), "compatibility matrix is required")


if __name__ == "__main__":
    unittest.main()
