from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from sync_sentinel.safety import ensure_below, ensure_temp_db, sanitize_text, scan_secrets_text, snapshots_equal


class SafetyTests(unittest.TestCase):
    def test_a_path_traversal_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(RuntimeError):
                ensure_below(root.parent / "escape.db", root, "escape")

    def test_b_non_sqlite_temp_db_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(RuntimeError):
                ensure_temp_db(root / "x.txt", root, "db")

    def test_c_temp_db_allowed_under_owned_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = ensure_temp_db(root / "nested/x.db", root, "db")
            self.assertTrue(str(p).startswith(str(root.resolve())))

    def test_d_secret_detection_and_sanitization(self):
        text = "token=supersecretvalue12345\nAuthorization: Bearer abcdefghijklmnop"
        self.assertTrue(scan_secrets_text(text))
        clean = sanitize_text(text)
        self.assertNotIn("supersecretvalue12345", clean)
        self.assertNotIn("abcdefghijklmnop", clean)

    def test_e_snapshot_equality_is_strict(self):
        self.assertTrue(snapshots_equal({"x": 1}, {"x": 1}))
        self.assertFalse(snapshots_equal({"x": 1}, {"x": 2}))
