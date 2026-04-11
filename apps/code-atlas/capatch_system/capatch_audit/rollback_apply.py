from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from .history import append_history_event
from .renderers import ensure_report_tree, sha256_file, write_json, write_text
from .rollback_preview import preview_rollback
from .run_store import load_run


_APPLY_SCHEMA_VERSION = "1.0.0"


def _verify_restored_files(*, root_dir: Path, checkpoint_path: Path, restored_files: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative_path in restored_files:
        current_hash = sha256_file(root_dir / relative_path)
        checkpoint_hash = sha256_file(checkpoint_path / relative_path)
        rows.append(
            {
                "relative_path": relative_path,
                "current_hash": current_hash,
                "checkpoint_hash": checkpoint_hash,
                "ok": bool(current_hash and checkpoint_hash and current_hash == checkpoint_hash),
            }
        )
    return rows


def _mark_run_rolled_back(*, root_dir: Path, run_id: str | None) -> None:
    if not run_id or run_id == "manual":
        return
    record = load_run(str(run_id), root_dir=root_dir)
    if record is None:
        return
    record.patch_status = "rolled_back"
    record.system_status = "rolled_back"
    path_value = root_dir / "reports/patch_runs" / f"{record.run_id}.json"
    md_value = root_dir / "reports/patch_runs" / f"{record.run_id}.md"
    from .manifest import patch_run_record_to_dict
    from .renderers import render_patch_run_md

    write_json(path_value, patch_run_record_to_dict(record))
    write_text(md_value, render_patch_run_md(record))


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
    restored_files.sort()
    verification = _verify_restored_files(root_dir=root_dir, checkpoint_path=checkpoint_path, restored_files=restored_files)
    verified_hashes = all(item.get("ok") for item in verification) if verification else False
    event = {
        "schema_version": _APPLY_SCHEMA_VERSION,
        "rollback_id": f"rollback_apply_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "source_run_id": preview.source_run_id,
        "checkpoint_id": checkpoint_path.name,
        "checkpoint_path": str(checkpoint_path),
        "restored_files": restored_files,
        "conflicts_with_current_tree": preview.conflicts_with_current_tree,
        "verification": verification,
        "verified_hashes": verified_hashes,
        "status": "restored" if verified_hashes else "restored_with_warnings",
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    ensure_report_tree(root_dir)
    write_json(root_dir / "reports/rollback" / f"{event['rollback_id']}.json", event)
    lines = ["# Rollback apply", "", f"- status: `{event['status']}`", f"- verified_hashes: `{event['verified_hashes']}`", "", "## Restored files", ""]
    lines.extend([f"- `{item}`" for item in restored_files] or ["- none"])
    lines.extend(["", "## Verification", ""])
    lines.extend([f"- `{item['relative_path']}` ok=`{item['ok']}`" for item in verification] or ["- none"])
    write_text(root_dir / "reports/rollback" / f"{event['rollback_id']}.md", "\n".join(lines).rstrip() + "\n")
    append_history_event(
        root_dir,
        {
            "timestamp": event["timestamp"],
            "event_type": "rollback",
            "run_id": preview.source_run_id,
            "checkpoint_id": checkpoint_path.name,
            "status": "rolled_back" if verified_hashes else "failed",
            "detail": f"Restored {len(restored_files)} file(s); verified_hashes={verified_hashes}",
        },
    )
    _mark_run_rolled_back(root_dir=root_dir, run_id=preview.source_run_id)
    return event
