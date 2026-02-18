from __future__ import annotations

import os
import random
import string
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.path_guard import (  # noqa: E402
    PathGuardError,
    canonical_path_key,
    detect_scope_violations_for_paths,
    ensure_within_root,
    is_protected_path,
    normalize_path_list,
    normalize_rel_path,
    validate_files_changed_entries,
)


class PathGuardTests(unittest.TestCase):
    def test_normalize_rel_path_mixed_separators(self) -> None:
        value = normalize_rel_path(r"Apps\Demo/Feature.ts")
        self.assertEqual("apps/demo/feature.ts", value)

    def test_normalize_rejects_absolute_posix(self) -> None:
        with self.assertRaises(PathGuardError):
            normalize_rel_path("/etc/passwd")

    def test_normalize_rejects_windows_drive(self) -> None:
        with self.assertRaises(PathGuardError):
            normalize_rel_path(r"C:\windows\system32\cmd.exe")

    def test_normalize_rejects_unc(self) -> None:
        with self.assertRaises(PathGuardError):
            normalize_rel_path(r"\\server\share\file.txt")

    def test_normalize_rejects_traversal(self) -> None:
        with self.assertRaises(PathGuardError):
            normalize_rel_path(r"..\..\secret.txt")

    def test_normalize_unicode_path(self) -> None:
        value = normalize_rel_path("docs/naive-cafe/mañana.md")
        self.assertEqual("docs/naive-cafe/mañana.md", value)

    def test_normalize_long_path(self) -> None:
        long_name = "a" * 250
        value = normalize_rel_path(f"docs/{long_name}.txt")
        self.assertTrue(value.startswith("docs/"))

    def test_canonical_path_key_casefolds(self) -> None:
        self.assertEqual("apps/test/file.ts", canonical_path_key("Apps/Test/File.ts"))
        self.assertEqual(canonical_path_key("A/B/C"), canonical_path_key("a\\b\\c"))

    def test_is_protected_path(self) -> None:
        self.assertTrue(is_protected_path(".git/config"))
        self.assertTrue(is_protected_path(".env"))
        self.assertTrue(is_protected_path(".github/workflows/factory.yml"))
        self.assertFalse(is_protected_path("apps/demo/main.ts"))

    def test_ensure_within_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="path_guard_root_") as temp_dir:
            root = Path(temp_dir)
            safe = ensure_within_root(root, "apps/demo/file.ts")
            self.assertTrue(str(safe).startswith(str(root)))

    def test_ensure_within_root_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="path_guard_escape_") as temp_dir:
            root = Path(temp_dir)
            with self.assertRaises(PathGuardError):
                ensure_within_root(root, "../../outside.txt")

    def test_validate_files_changed_entries_collects_issues(self) -> None:
        cleaned, issues = validate_files_changed_entries(
            [
                {"path": "apps/demo/a.ts", "change_type": "modified", "reason": "ok", "sha256": "1"},
                {"path": "../../bad.ts", "change_type": "modified", "reason": "bad", "sha256": "2"},
            ],
            worker="A_worker",
        )
        self.assertEqual(1, len(cleaned))
        self.assertEqual(1, len(issues))
        self.assertEqual("A_worker", issues[0].worker)

    def test_scope_violation_detection(self) -> None:
        violations = detect_scope_violations_for_paths(
            worker="A_worker",
            paths=["apps/demo/a.ts", ".git/config", "docs/private/note.md"],
            allow_globs=["apps/**"],
            deny_globs=["docs/private/**"],
            enforce_protected=True,
        )
        reasons = [item.reason for item in violations]
        self.assertIn("protected path", reasons)
        self.assertIn("outside allowlist", reasons)
        self.assertIn("matched denylist", reasons)

    def test_normalize_path_list_deterministic(self) -> None:
        values = normalize_path_list(["b\\x.ts", "a/x.ts", "b/x.ts", "a\\x.ts"])
        self.assertEqual(["a/x.ts", "b/x.ts"], values)

    def test_property_random_path_normalization_stable(self) -> None:
        rng = random.Random(20260218)
        alphabet = string.ascii_letters + string.digits + "_-"
        for _ in range(200):
            parts = []
            for _segment in range(rng.randint(1, 5)):
                segment = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))
                parts.append(segment)
            if rng.random() < 0.5:
                raw = "/".join(parts)
            else:
                raw = "\\".join(parts)
            normalized_1 = normalize_rel_path(raw)
            normalized_2 = normalize_rel_path(raw)
            self.assertEqual(normalized_1, normalized_2)

    def test_slow_long_path_roundtrip(self) -> None:
        if os.getenv("FACTORY_SLOW_TESTS", "").strip() not in {"1", "true", "TRUE"}:
            self.skipTest("slow tests disabled")
        raw = "docs/" + "/".join(["segment"] * 120) + "/file.txt"
        normalized = normalize_rel_path(raw)
        self.assertTrue(normalized.endswith("/file.txt"))


if __name__ == "__main__":
    unittest.main()

