from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class BundleToolingTests(unittest.TestCase):
    def test_generate_example_outputs(self) -> None:
        bundle_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tempdir:
            cmd = [
                sys.executable,
                str(bundle_root / 'tools' / 'generate_example_outputs.py'),
                '--output-dir',
                tempdir,
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            payload = json.loads(result.stdout)
            self.assertIn('switch_decision_registry.json', payload)
            self.assertTrue(Path(payload['switch_decision_trace.json']).exists())


if __name__ == '__main__':
    unittest.main()
