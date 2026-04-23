from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.count_bundle_mix import inspect_path
from tools.generate_example_outputs import generate_example_outputs


class BundleToolsTests(unittest.TestCase):
    def test_generate_example_outputs_creates_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / '.ark_install' / 'scanner_bundle' / 'verification_outputs' / 'manual'
            written = generate_example_outputs(output_root)
            self.assertTrue(written)
            self.assertTrue(all(path.suffix == '.json' for path in written))
            self.assertTrue(all(str(path).startswith(str(output_root)) for path in written))

    def test_mix_counter_understands_directory(self) -> None:
        stats = inspect_path(Path(__file__).resolve().parents[1])
        self.assertGreater(stats['file_count'], 0)
        self.assertGreater(stats['py_ratio'], 0.9)


if __name__ == '__main__':
    unittest.main()
