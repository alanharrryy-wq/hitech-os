
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.qa_testkit import apply_ops, make_ctx, write_text

from capatch_audit import apply_rollback, finalize_run, load_run, preview_rollback, start_run
from capatch_verify.registry import run_required_verifiers


class AuditRollbackTests(unittest.TestCase):
    def test_apply_finalize_preview_and_rollback_restore_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="capatch_audit_rollback_") as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / "pkg"
            pkg.mkdir(parents=True, exist_ok=True)
            target = pkg / "service.py"
            original = "def compute() -> int:\n    return 41\n"
            write_text(target, original)

            rows = [
                {
                    "type": "EnsureReplaceExactOnce",
                    "label": "meaning-42",
                    "file": "pkg/service.py",
                    "old_text": "    return 41\n",
                    "new_text": "    return 42\n",
                }
            ]
            ctx = make_ctx(root)
            ops = [row for row in rows]
            _ctx, parsed_ops, pf, _pv, results = apply_ops(root, ops)
            record = start_run(ctx, pf, {"risk_level": "low", "risk_tier": "safe", "required_verifiers": ["python-parse", "python-compile-smoke", "python-import-smoke"]})
            verifier_rows = run_required_verifiers(
                [str(target)],
                ["python-parse", "python-import-smoke"],
                {"root_dir": str(root)},
            )
            finalized = finalize_run(record, results, verifier_rows)

            self.assertEqual("applied", finalized.patch_status)
            self.assertEqual("verified", finalized.system_status)
            self.assertEqual("def compute() -> int:\n    return 42\n", target.read_text(encoding="utf-8"))

            loaded = load_run(finalized.run_id, root_dir=root)
            self.assertIsNotNone(loaded)
            preview = preview_rollback(run_id=finalized.run_id, root_dir=root)
            self.assertTrue(preview.restore_ok)

            restored = apply_rollback(run_id=finalized.run_id, root_dir=root)
            self.assertEqual("restored", restored["status"])
            self.assertEqual(original, target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
