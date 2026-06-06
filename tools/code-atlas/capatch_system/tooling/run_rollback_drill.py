#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_audit import apply_rollback, finalize_run, preview_rollback, start_run
from capatch_audit.telemetry import enrich_payload, write_telemetry_report
from capatch_contracts import build_operation_spec
from capatch_engine import apply as engine_apply
from capatch_engine import preflight


def _backup_root(root_dir: Path) -> Path:
    modern = root_dir / ".capatch" / "backups" / "patches"
    legacy = root_dir / "_chatgpt_patch_backups"
    if modern.exists():
        modern.mkdir(parents=True, exist_ok=True)
        return modern
    legacy.mkdir(parents=True, exist_ok=True)
    return legacy


class _Ctx:
    def __init__(self, root_dir: Path, checkpoint_name: str) -> None:
        self.root_dir = root_dir
        self.backup_dir = _backup_root(root_dir)
        self.checkpoint_dir = self.backup_dir / checkpoint_name
        self.dry_run = False
        self.auto_support = True
        self.invocation_mode = "patch-run"
        self.run_id = checkpoint_name
        self.trace_id = f"trace::{checkpoint_name}"


def _write_report(output_dir: Path, stem: str, payload: dict[str, Any]) -> dict[str, str]:
    lines = [
        "## rollback summary",
        "",
        f"- conflict_preview_detected: {payload['conflict_preview_detected']}",
        f"- multi_run_restore_ok: {payload['multi_run_restore_ok']}",
        f"- dirty_tree_detected: {payload['dirty_tree_detected']}",
    ]
    return write_telemetry_report(output_dir, stem, payload, lines)


def _run_patch(ctx: _Ctx, *, relative_file: str, old_text: str, new_text: str, label: str):
    operations = [
        build_operation_spec(
            {
                "type": "EnsureReplaceExactOnce",
                "label": label,
                "file": relative_file,
                "old_text": old_text,
                "new_text": new_text,
            }
        )
    ]
    pf = preflight(ctx, operations)
    record = start_run(
        ctx,
        pf,
        {"risk_level": "low", "risk_tier": "safe", "required_verifiers": ["python-parse", "python-compile-smoke", "python-import-smoke"]},
    )
    results = engine_apply(ctx, operations)
    finalized = finalize_run(record, results, [])
    return pf, finalized


def run_rollback_drill(base_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="capatch_rollback_drill_") as tmp_dir:
        root = Path(tmp_dir)
        (root / "pkg").mkdir(parents=True, exist_ok=True)
        target = root / "pkg" / "service.py"
        original = "def compute() -> int:\n    return 41\n"
        target.write_text(original, encoding="utf-8", newline="")

        ctx1 = _Ctx(root, "rollback_drill_first")
        _pf1, run1 = _run_patch(ctx1, relative_file="pkg/service.py", old_text="    return 41\n", new_text="    return 42\n", label="meaning-42")
        after_run1 = target.read_text(encoding="utf-8")

        ctx2 = _Ctx(root, "rollback_drill_second")
        _pf2, run2 = _run_patch(ctx2, relative_file="pkg/service.py", old_text="    return 42\n", new_text="    return 43\n", label="meaning-43")
        target.write_text("def compute() -> int:\n    return 99\n", encoding="utf-8", newline="")

        preview = preview_rollback(run_id=run2.run_id, root_dir=root)
        restored_second = apply_rollback(run_id=run2.run_id, root_dir=root)
        after_restore_second = target.read_text(encoding="utf-8")

        restored_first = apply_rollback(run_id=run1.run_id, root_dir=root)
        after_restore_first = target.read_text(encoding="utf-8")

        payload = enrich_payload(
            {
                "name": "rollback_drill",
                "status": "passed",
                "duration_ms": round((time.perf_counter() - started) * 1000.0, 3),
                "run_ids": [run1.run_id, run2.run_id],
                "trace_ids": [run1.trace_id, run2.trace_id],
                "conflict_preview_detected": bool(preview.conflicts_with_current_tree),
                "dirty_tree_detected": bool(preview.conflicts_with_current_tree),
                "multi_run_restore_ok": after_restore_second == after_run1 and after_restore_first == original,
                "after_run1": after_run1,
                "after_restore_second": after_restore_second,
                "after_restore_first": after_restore_first,
                "rollback_preview": preview.rollback_id,
                "rollback_apply_last": restored_second["rollback_id"],
                "rollback_apply_first": restored_first["rollback_id"],
                "checkpoint_dir": run2.rollback_target,
            },
            root_dir=base_dir,
            artifact_kind="telemetry-report",
            artifact_scope="reports/telemetry/rollback_drill",
            run_id=run2.run_id,
            checkpoint_id=Path(run2.rollback_target).name if run2.rollback_target else None,
            trace_id=run2.trace_id,
        )
        if not payload["conflict_preview_detected"] or not payload["multi_run_restore_ok"]:
            payload["status"] = "failed"
    if output_dir is not None:
        payload["report_paths"] = _write_report(output_dir, "rollback_drill", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    output_dir = ROOT / "reports" / "telemetry"
    payload = run_rollback_drill(ROOT, output_dir)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
