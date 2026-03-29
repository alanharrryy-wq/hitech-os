import json
import tempfile
import unittest
from pathlib import Path

from forge_commons import ExportArtifactsCapability
from forge_commons.lifecycle import CapabilityRuntimeState


class ExportArtifactsCapabilityTests(unittest.TestCase):
    def test_export_bundle_creates_zip_and_manifest(self) -> None:
        capability = ExportArtifactsCapability()
        capability.activate()
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            source_file = temp_root / "sample.txt"
            source_file.write_text("hello", encoding="utf-8")
            result = capability.export_bundle(
                output_dir=str(temp_root / "out"),
                bundle_name="artifact_bundle",
                manifest={"name": "artifact_bundle", "version": "0.1.0"},
                file_paths=[str(source_file)],
            )
            self.assertTrue(Path(result.bundle_path).exists())
            self.assertTrue(Path(result.manifest_path).exists())
            manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
            self.assertEqual(manifest["name"], "artifact_bundle")
            self.assertEqual(result.included_files, 1)

    def test_dispose_transitions_to_disposed(self) -> None:
        capability = ExportArtifactsCapability()
        capability.activate()
        state = capability.dispose()
        self.assertEqual(state, CapabilityRuntimeState.DISPOSED)


if __name__ == "__main__":
    unittest.main()
