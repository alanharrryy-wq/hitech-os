from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .history import append_history_event
from .renderers import ensure_report_tree, read_json, render_rollback_preview_md, write_json, write_text
from .rollback_preview import RollbackPreview, build_conflict_rows, rollback_preview_to_dict
from .run_store import load_run


def _resolve_checkpoint_payload(*, root_dir: Path, run_id: str | None, checkpoint_id: str | None) -> tuple[dict[str, Any], dict[str, Any] | None]:
    root_dir = Path(root_dir).resolve()
    if run_id:
        record = load_run(run_id, root_dir=root_dir)
        if record is None:
            raise FileNotFoundError(f"Run no existe: {run_id}")
        if not record.rollback_target:
            raise FileNotFoundError(f"Run {run_id} no tiene rollback_target")
        checkpoint_path = Path(record.rollback_target)
        checkpoint_id = checkpoint_path.name
        return {
            "checkpoint_id": checkpoint_id,
            "checkpoint_path": str(checkpoint_path),
            "root_dir": str(root_dir),
            "run_id": run_id,
            "target_files": list(record.target_files),
        }, {
            "run_id": record.run_id,
            "operation_results": list(record.operation_results),
        }
    if not checkpoint_id:
        raise FileNotFoundError("Se requiere run_id o checkpoint_id")
    checkpoint_meta = read_json(root_dir / "reports/checkpoints" / f"{checkpoint_id}.json", None)
    if not isinstance(checkpoint_meta, dict):
        raise FileNotFoundError(f"Checkpoint no existe: {checkpoint_id}")
    return checkpoint_meta, None


def preview_rollback(*, run_id: str | None = None, checkpoint_id: str | None = None, root_dir: Path | None = None) -> RollbackPreview:
    root_dir = Path(root_dir or Path.cwd()).resolve()
    checkpoint_meta, run_payload = _resolve_checkpoint_payload(root_dir=root_dir, run_id=run_id, checkpoint_id=checkpoint_id)
    checkpoint_path = Path(checkpoint_meta["checkpoint_path"]).resolve()
    files_to_restore: list[str] = []
    warnings: list[str] = []
    if checkpoint_path.exists():
        files_to_restore = [item.relative_to(checkpoint_path).as_posix() for item in checkpoint_path.rglob("*") if item.is_file()]
    else:
        warnings.append(f"checkpoint missing: {checkpoint_path}")
    expected_after_hashes: dict[str, str | None] = {}
    if run_payload:
        for item in run_payload.get("operation_results", []):
            if not isinstance(item, dict):
                continue
            target_path = str(item.get("target_path") or "")
            if not target_path:
                continue
            try:
                relative_path = Path(target_path).resolve().relative_to(root_dir).as_posix()
            except Exception:
                continue
            expected_after_hashes[relative_path] = item.get("after_hash")
    conflicts = build_conflict_rows(root_dir=root_dir, files_to_restore=files_to_restore, expected_after_hashes=expected_after_hashes)
    rollback_id = f"rollback_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    preview = RollbackPreview(
        rollback_id=rollback_id,
        source_run_id=str((run_payload or {}).get("run_id") or checkpoint_meta.get("run_id") or "manual"),
        checkpoint_path=str(checkpoint_path),
        files_to_restore=files_to_restore,
        conflicts_with_current_tree=conflicts,
        restore_ok=checkpoint_path.exists(),
        warnings=warnings,
    )
    ensure_report_tree(root_dir)
    write_json(root_dir / "reports/rollback" / f"{rollback_id}.json", rollback_preview_to_dict(preview))
    write_text(root_dir / "reports/rollback" / f"{rollback_id}.md", render_rollback_preview_md(preview))
    return preview


def apply_rollback(*, run_id: str | None = None, checkpoint_id: str | None = None, root_dir: Path | None = None) -> dict[str, Any]:
    root_dir = Path(root_dir or Path.cwd()).resolve()
    preview = preview_rollback(run_id=run_id, checkpoint_id=checkpoint_id, root_dir=root_dir)
    checkpoint_path = Path(preview.checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint no existe: {checkpoint_path}")
    restored_files: list[str] = []
    for source in checkpoint_path.rglob("*"):
        if not source.is_file():
            continue
        relative_path = source.relative_to(checkpoint_path)
        target = root_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        restored_files.append(relative_path.as_posix())
    event = {
        "rollback_id": f"rollback_apply_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "source_run_id": preview.source_run_id,
        "checkpoint_id": checkpoint_path.name,
        "checkpoint_path": str(checkpoint_path),
        "restored_files": restored_files,
        "conflicts_with_current_tree": preview.conflicts_with_current_tree,
        "status": "restored",
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    ensure_report_tree(root_dir)
    write_json(root_dir / "reports/rollback" / f"{event['rollback_id']}.json", event)
    write_text(
        root_dir / "reports/rollback" / f"{event['rollback_id']}.md",
        "# Rollback apply\n\n" + "\n".join([f"- `{item}`" for item in restored_files] or ["- none"]) + "\n",
    )
    append_history_event(
        root_dir,
        {
            "timestamp": event["timestamp"],
            "event_type": "rollback",
            "run_id": preview.source_run_id,
            "checkpoint_id": checkpoint_path.name,
            "status": event["status"],
            "detail": f"Restored {len(restored_files)} file(s)",
        },
    )
    return event
