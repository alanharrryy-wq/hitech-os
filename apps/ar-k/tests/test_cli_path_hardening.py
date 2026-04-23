from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pya.kernel.identity import normalize_relpath, path_is_within_root
from pya.tools.pya import _validate_cli_path_argument


class CliPathHardeningTests(unittest.TestCase):
    def test_placeholder_target_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, 'placeholder token detected'):
            _validate_cli_path_argument('target', Path('<REAL_FRONTEND_TARGET>'))

    def test_path_outside_root_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'root'
            root.mkdir()
            inside = root / 'inside.txt'
            inside.write_text('ok', encoding='utf-8')
            outside = Path(temp) / 'outside.txt'
            outside.write_text('nope', encoding='utf-8')
            self.assertTrue(path_is_within_root(inside, root))
            self.assertFalse(path_is_within_root(outside, root))

    def test_normalize_relpath_message_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'root'
            root.mkdir()
            outside = Path(temp) / 'outside.txt'
            outside.write_text('x', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'path escapes target root'):
                normalize_relpath(outside, root)
