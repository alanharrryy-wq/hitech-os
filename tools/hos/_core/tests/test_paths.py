from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos._core.paths import (
    ForbiddenRegistry,
    assert_within,
    is_within,
    safe_join,
)


class PathsTests(unittest.TestCase):
    def test_safe_join_disallows_traversal(self) -> None:
        base = Path("C:/tmp/demo")
        with self.assertRaises(ValueError):
            safe_join(base, "../bad")

    def test_is_within_true_for_child(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            child = root / "a" / "b.txt"
            child.parent.mkdir(parents=True, exist_ok=True)
            child.write_text("ok", encoding="utf-8")
            self.assertTrue(is_within(root, child))
            self.assertEqual(assert_within(root, child), child.resolve())

    def test_registry_matches_prefix(self) -> None:
        registry = ForbiddenRegistry(entries=("tools/_local", "docs/_root_archive"))
        self.assertTrue(registry.is_forbidden("tools/_local/data.txt"))
        self.assertTrue(registry.is_forbidden("docs/_root_archive/2026/a.md"))
        self.assertFalse(registry.is_forbidden("docs/system/a.md"))


if __name__ == "__main__":
    unittest.main()

