from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ark_contract_validator_bundle.tools.generate_example_outputs import generate


class GenerateExampleOutputsTests(unittest.TestCase):
    def test_generate_outputs_stays_ready_for_verify_examples(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate(Path(tmpdir))
            self.assertEqual(result['overall_status'], 'READY')
            summary = json.loads((Path(tmpdir) / 'validator_summary.json').read_text(encoding='utf-8'))
            self.assertEqual(summary['overall_status'], 'READY')
