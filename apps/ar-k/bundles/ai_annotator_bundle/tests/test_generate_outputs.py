
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.example_builder import generate_outputs
from core.write_limits import assert_example_output_dir, assert_only_annotation_artifacts, is_allowed_verification_output


class GenerateOutputsTests(unittest.TestCase):
    def test_generated_outputs_exist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            summary = generate_outputs(out, limit=12)
            self.assertEqual(summary['annotation_count'], 12)
            for name in ['annotations.json', 'annotation_index.json', 'annotation_summary.json']:
                self.assertTrue((out / name).exists())
            annotations = json.loads((out / 'annotations.json').read_text(encoding='utf-8'))
            self.assertTrue(all(item['advisory_only'] for item in annotations))

    def test_example_outputs_stay_inside_verification_surface(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            out = root / '.ark_install' / 'ai_annotator_bundle' / 'verification_outputs' / 'case-001'
            assert_example_output_dir(out, root)
            generate_outputs(out, limit=3)
            assert_only_annotation_artifacts(out.glob('*.json'))
            for name in ['annotations.json', 'annotation_index.json', 'annotation_summary.json']:
                self.assertTrue(is_allowed_verification_output(out / name, root))


if __name__ == '__main__':
    unittest.main()
