from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .renderers import ensure_report_tree, read_json, render_rollback_preview_md, sha256_file, write_json, write_text
from .run_store import load_run


@dataclass(slots=True)
class RollbackPreview:
    rollback_id: str
    source_run_id: str
    checkpoint_path: str
    files_to_restore: list[str]
    conflicts_with_current_tree: list[dict[str, Any]]
    restore_ok: bool
    warnings: list[str]


_PREVIEW_SCHEMA_VERSION = "1.0.0"


def rollback_preview_to_dict(preview: RollbackPreview) -> dict[str, Any]:
    payload = asdict(preview)
    payload["schema_version"] = _PREVIEW_SCHEMA_VERSION
    return payload


def build_conflict_rows(*, root_dir: Path, files_to_restore: list[str], expected_after_hashes: dict[str, str | None]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for relative_path in files_to_restore:
        current_hash = sha256_file(root_dir / relative_path)
        expected_hash = expected_after_hashes.get(relative_path)
        if expected_hash and current_hash and current_hash != expected_hash:
            rows.append(
                {
                    "relative_path": relative_path,
                    "current_hash": current_hash,
                    "expected_hash": expected_hash,
                }
            )
    return rows


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
        files_to_restore = sorted(
            item.relative_to(checkpoint_path).as_posix() for item in checkpoint_path.rglob("*") if item.is_file()
        )
        if not files_to_restore:
            warnings.append(f"checkpoint empty: {checkpoint_path}")
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
    conflicts = build_conflict_rows(
        root_dir=root_dir,
        files_to_restore=files_to_restore,
        expected_after_hashes=expected_after_hashes,
    )
    rollback_id = f"rollback_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    preview = RollbackPreview(
        rollback_id=rollback_id,
        source_run_id=str((run_payload or {}).get("run_id") or checkpoint_meta.get("run_id") or "manual"),
        checkpoint_path=str(checkpoint_path),
        files_to_restore=files_to_restore,
        conflicts_with_current_tree=conflicts,
        restore_ok=checkpoint_path.exists() and bool(files_to_restore),
        warnings=warnings,
    )
    ensure_report_tree(root_dir)
    write_json(root_dir / "reports/rollback" / f"{rollback_id}.json", rollback_preview_to_dict(preview))
    write_text(root_dir / "reports/rollback" / f"{rollback_id}.md", render_rollback_preview_md(preview))
    return preview
