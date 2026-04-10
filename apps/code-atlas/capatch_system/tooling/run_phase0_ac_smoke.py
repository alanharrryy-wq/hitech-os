#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from capatch_audit import apply_rollback, finalize_run, list_baselines, list_checkpoints, load_run, preview_rollback, start_run, write_baseline
from capatch_contracts import MANDATORY_OUTPUT_FILES, PATCH_OPERATION_TYPES, SEMANTIC_OPERATION_TYPES, build_operation_spec


class _Ctx:
    def __init__(self, root_dir: Path, checkpoint_dir: Path) -> None:
        self.root_dir = root_dir
        self.checkpoint_dir = checkpoint_dir
        self.invocation_mode = "patch-run"
        self.run_id = None


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="capatch_phase0_ac_") as tmp_dir:
        root_dir = Path(tmp_dir)
        (root_dir / "pkg").mkdir(parents=True, exist_ok=True)
        target_file = root_dir / "pkg/example.py"
        target_file.write_text("print('before')\n", encoding="utf-8")
        checkpoint_dir = root_dir / "_chatgpt_patch_backups/checkpoint_demo"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        (checkpoint_dir / "pkg").mkdir(parents=True, exist_ok=True)
        (checkpoint_dir / "pkg/example.py").write_text("print('before')\n", encoding="utf-8")

        op = build_operation_spec(
            {
                "type": "ReplaceExactOnce",
                "label": "swap-print",
                "file": "pkg/example.py",
                "old_text": "print('before')",
            }
        )
        assert op.type in PATCH_OPERATION_TYPES + SEMANTIC_OPERATION_TYPES
        assert set(MANDATORY_OUTPUT_FILES)

        ctx = _Ctx(root_dir=root_dir, checkpoint_dir=checkpoint_dir)
        preflight = {
            "target_files": ["pkg/example.py"],
            "operation_count": 1,
            "mutating_operation_count": 1,
            "read_only_operation_count": 0,
        }
        record = start_run(ctx, preflight, {"risk_level": "low", "risk_tier": "safe"})
        target_file.write_text("print('after')\n", encoding="utf-8")
        finalized = finalize_run(
            record,
            [
                {
                    "operation_label": "swap-print",
                    "operation_type": "ReplaceExactOnce",
                    "target_path": str(target_file),
                    "patch_status": "applied",
                    "message": "swap-print OK",
                    "before_hash": None,
                    "after_hash": None,
                    "preview_hash": None,
                    "bytes_before": None,
                    "bytes_after": target_file.stat().st_size,
                    "changed_line_count": 1,
                    "support_notes": [],
                }
            ],
            [{"verifier_id": "builtin.python", "ok": True, "title": "parse", "detail": "ok"}],
        )
        assert finalized.patch_status == "applied"
        assert finalized.system_status == "verified"

        loaded = load_run(finalized.run_id, root_dir=root_dir)
        assert loaded is not None and loaded.run_id == finalized.run_id
        preview = preview_rollback(run_id=finalized.run_id, root_dir=root_dir)
        assert preview.restore_ok is True
        applied = apply_rollback(run_id=finalized.run_id, root_dir=root_dir)
        assert applied["status"] == "restored"
        assert target_file.read_text(encoding="utf-8") == "print('before')\n"

        baseline = write_baseline(root_dir, label="demo", target_files=["pkg/example.py"], verification_snapshot=[{"ok": True}])
        assert baseline.baseline_id
        assert list_baselines(root_dir)
        assert list_checkpoints(root_dir)
        print(
            json.dumps(
                {
                    "run_id": finalized.run_id,
                    "rollback_preview": preview.rollback_id,
                    "rollback_apply": applied["rollback_id"],
                    "baseline_id": baseline.baseline_id,
                },
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
