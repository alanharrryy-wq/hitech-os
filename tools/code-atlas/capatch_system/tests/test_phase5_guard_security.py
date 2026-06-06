from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from capatch_fs.guards import ensure_mutable_target
from capatch_ops.base import CapatchError


@unittest.skipIf(os.name == "nt", "symlink behavior varies on Windows CI")
class Phase5GuardSecurityTests(unittest.TestCase):
    def test_reject_symlink_target(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_guard_") as tmp_dir:
            workspace = Path(tmp_dir)
            real = workspace / "real.txt"
            real.write_text("x\n", encoding="utf-8")
            link = workspace / "link.txt"
            link.symlink_to(real)
            with self.assertRaises(CapatchError):
                ensure_mutable_target(workspace, link)

    def test_reject_path_outside_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_guard_") as tmp_dir:
            workspace = Path(tmp_dir)
            outside = workspace.parent / "outside.txt"
            with self.assertRaises(CapatchError):
                ensure_mutable_target(workspace, outside)
