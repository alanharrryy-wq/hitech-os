import unittest

from forge_kernel import PackageLayer, PackageManifest, PackagingGate


class PackagingGateTests(unittest.TestCase):
    def test_manifest_is_approved_when_compatible(self) -> None:
        gate = PackagingGate()
        manifest = PackageManifest(
            package_id="pkg.kernel.base",
            layer=PackageLayer.KERNEL,
            owner="forge_kernel",
            version="0.1.0",
            required_kernel_range=">=0.1.0,<1.0.0",
            integrity_hash="sha256:abc123",
        )
        result = gate.validate(
            manifest=manifest,
            kernel_version="0.1.0",
            verified_integrity_hash="sha256:abc123",
        )
        self.assertTrue(result.approved)
        self.assertEqual(result.reasons, ())

    def test_manifest_rejected_on_compatibility_and_integrity(self) -> None:
        gate = PackagingGate()
        manifest = PackageManifest(
            package_id="pkg.commons.sample",
            layer=PackageLayer.COMMONS,
            owner="forge_commons",
            version="1.2.0",
            required_kernel_range=">=2.0.0,<3.0.0",
            integrity_hash="sha256:expected",
        )
        result = gate.validate(
            manifest=manifest,
            kernel_version="0.1.0",
            verified_integrity_hash="sha256:actual",
        )
        self.assertFalse(result.approved)
        self.assertGreaterEqual(len(result.reasons), 2)


if __name__ == "__main__":
    unittest.main()
