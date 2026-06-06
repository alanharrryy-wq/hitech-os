from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from capatch_contracts import build_operation_spec
from capatch_engine import preflight
from tests.qa_testkit import make_ctx


class PreflightConflictHardeningTests(unittest.TestCase):
    def test_large_batch_with_high_density_duplicate_exact_match_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_conflict_batch_') as tmp_dir:
            root = Path(tmp_dir)
            (root / 'pkg').mkdir(parents=True, exist_ok=True)
            (root / 'pkg' / 'service.py').write_text(
                '\n'.join(['value = 41' for _ in range(30)]) + '\n',
                encoding='utf-8',
                newline='',
            )
            operations = [
                build_operation_spec(
                    {
                        'type': 'EnsureReplaceExactOnce',
                        'label': f'batch-{index}',
                        'file': 'pkg/service.py',
                        'old_text': 'value = 41',
                        'new_text': f'value = {42 + index}',
                    }
                )
                for index in range(20)
            ]
            report = preflight(make_ctx(root), operations)
            self.assertFalse(report.ok)
            reasons = [row['reason'] for row in report.conflicts]
            self.assertIn('duplicate_exact_text_match', reasons)

    def test_duplicate_exact_text_match_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_conflict_exact_") as tmp_dir:
            root = Path(tmp_dir)
            (root / "pkg").mkdir(parents=True, exist_ok=True)
            (root / "pkg" / "service.py").write_text(
                "def compute() -> int:\n    return 41\n    return 41\n",
                encoding="utf-8",
                newline="",
            )
            operations = [
                build_operation_spec(
                    {
                        "type": "EnsureReplaceExactOnce",
                        "label": "first",
                        "file": "pkg/service.py",
                        "old_text": "    return 41\n",
                        "new_text": "    return 42\n",
                    }
                ),
                build_operation_spec(
                    {
                        "type": "EnsureReplaceExactOnce",
                        "label": "second",
                        "file": "pkg/service.py",
                        "old_text": "    return 41\n",
                        "new_text": "    return 43\n",
                    }
                ),
            ]
            report = preflight(make_ctx(root), operations)
            reasons = [row["reason"] for row in report.conflicts]
            self.assertIn("duplicate_exact_text_match", reasons)
            self.assertFalse(report.ok)

    def test_normalize_with_additional_mutations_stays_flagged(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_conflict_normalize_") as tmp_dir:
            root = Path(tmp_dir)
            (root / "notes.txt").write_text("hello\r\n", encoding="utf-8", newline="")
            operations = [
                build_operation_spec(
                    {
                        "type": "NormalizeFile",
                        "label": "normalize",
                        "file": "notes.txt",
                        "line_ending": "LF",
                        "ensure_final_newline": True,
                        "strip_trailing_spaces": True,
                    }
                ),
                build_operation_spec(
                    {
                        "type": "ReplaceExactOnce",
                        "label": "replace",
                        "file": "notes.txt",
                        "old_text": "hello\r\n",
                        "new_text": "hola\n",
                    }
                ),
            ]
            report = preflight(make_ctx(root), operations)
            reasons = [row["reason"] for row in report.conflicts]
            self.assertIn("normalize_with_additional_mutations", reasons)


if __name__ == "__main__":
    unittest.main()
