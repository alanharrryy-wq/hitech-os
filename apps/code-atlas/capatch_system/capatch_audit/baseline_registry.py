from __future__ import annotations

import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capatch_contracts.versions import BASELINE_SCHEMA_VERSION

from .history import append_history_event
from .renderers import read_json, render_baseline_md, sha256_file, write_json, write_text


@dataclass(slots=True)
class BaselineRecord:
    baseline_id: str
    label: str
    created_at: str
    root_dir: str
    git_branch: str | None
    git_head: str | None
    target_files: list[str]
    hashes: dict[str, str]
    verification_snapshot: list[dict[str, Any]]
    notes: str
    source_run_id: str | None = None
    source_checkpoint_id: str | None = None
    checkpoint_path: str | None = None
    blessed_at_utc: str | None = None
    blessed_by: str | None = None
    verification_summary: dict[str, Any] | None = None
    baseline_kind: str = "official"


_INDEX_SCHEMA_VERSION = "2.0.0"


def baseline_record_to_dict(record: BaselineRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload["schema_version"] = BASELINE_SCHEMA_VERSION
    return payload


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _index_path(root_dir: Path) -> Path:
    return Path(root_dir).resolve() / "reports/baselines/index.json"


def _load_index(root_dir: Path) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    payload = read_json(
        _index_path(root_dir),
        {
            "schema_version": _INDEX_SCHEMA_VERSION,
            "baseline_schema_version": BASELINE_SCHEMA_VERSION,
            "root_dir": str(root_dir),
            "updated_at": None,
            "baselines": [],
        },
    )
    if not isinstance(payload, dict):
        payload = {
            "schema_version": _INDEX_SCHEMA_VERSION,
            "baseline_schema_version": BASELINE_SCHEMA_VERSION,
            "root_dir": str(root_dir),
            "updated_at": None,
            "baselines": [],
        }
    payload.setdefault("schema_version", _INDEX_SCHEMA_VERSION)
    payload.setdefault("baseline_schema_version", BASELINE_SCHEMA_VERSION)
    payload.setdefault("root_dir", str(root_dir))
    payload.setdefault("updated_at", None)
    rows = payload.get("baselines")
    payload["baselines"] = [dict(item) for item in list(rows or []) if isinstance(item, dict)]
    return payload


def _checkpoint_meta_path(root_dir: Path, checkpoint_id: str) -> Path:
    return Path(root_dir).resolve() / "reports/checkpoints" / f"{checkpoint_id}.json"


def _next_baseline_id(root_dir: Path) -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidate = f"baseline_{stamp}"
    path_value = Path(root_dir).resolve() / "reports/baselines" / f"{candidate}.json"
    if not path_value.exists():
        return candidate
    suffix = 2
    while True:
        candidate = f"baseline_{stamp}_{suffix:02d}"
        path_value = Path(root_dir).resolve() / "reports/baselines" / f"{candidate}.json"
        if not path_value.exists():
            return candidate
        suffix += 1


def _coerce_snapshot(values: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in list(values or []):
        if isinstance(item, dict):
            rows.append(dict(item))
    return rows


def _verification_summary(snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(snapshot)
    failed = 0
    passed = 0
    verifier_ids: list[str] = []
    for item in snapshot:
        verifier_id = str(item.get("verifier_id") or item.get("name") or "")
        if verifier_id:
            verifier_ids.append(verifier_id)
        if bool(item.get("ok")):
            passed += 1
        else:
            failed += 1
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "verifier_ids": sorted(set(verifier_ids)),
        "clean": bool(total > 0 and failed == 0),
    }


def _current_hashes(root_dir: Path, target_files: list[str]) -> dict[str, str]:
    rows: dict[str, str] = {}
    for relative_path in sorted({str(item) for item in list(target_files or []) if str(item)}):
        rows[relative_path] = sha256_file(root_dir / relative_path) or ""
    return rows


def _checkpoint_hashes(root_dir: Path, checkpoint_path: Path, target_files: list[str]) -> dict[str, str]:
    rows: dict[str, str] = {}
    for relative_path in sorted({str(item) for item in list(target_files or []) if str(item)}):
        rows[relative_path] = sha256_file(checkpoint_path / relative_path) or ""
    return rows


def _update_index(root_dir: Path, record: BaselineRecord) -> None:
    index_payload = _load_index(root_dir)
    rows = [item for item in index_payload.get("baselines", []) if item.get("baseline_id") != record.baseline_id]
    rows.append(
        {
            "baseline_id": record.baseline_id,
            "label": record.label,
            "created_at": record.created_at,
            "blessed_at_utc": record.blessed_at_utc,
            "target_files": list(record.target_files),
            "git_branch": record.git_branch,
            "git_head": record.git_head,
            "source_run_id": record.source_run_id,
            "source_checkpoint_id": record.source_checkpoint_id,
            "baseline_kind": record.baseline_kind,
            "clean_verification": bool((record.verification_summary or {}).get("clean")),
        }
    )
    rows.sort(key=lambda item: str(item.get("blessed_at_utc") or item.get("created_at") or ""), reverse=True)
    index_payload["baselines"] = rows
    index_payload["updated_at"] = _utc_now_iso()
    write_json(_index_path(root_dir), index_payload)


def _write_record(root_dir: Path, record: BaselineRecord) -> BaselineRecord:
    base_dir = Path(root_dir).resolve() / "reports/baselines"
    write_json(base_dir / f"{record.baseline_id}.json", baseline_record_to_dict(record))
    write_text(base_dir / f"{record.baseline_id}.md", render_baseline_md(record))
    _update_index(root_dir, record)
    append_history_event(
        root_dir,
        {
            "timestamp": record.blessed_at_utc or record.created_at,
            "event_type": "baseline",
            "run_id": record.source_run_id,
            "checkpoint_id": record.source_checkpoint_id,
            "status": "created",
            "detail": f"{record.baseline_id} ({record.label})",
        },
    )
    return record


def write_baseline(
    root_dir: Path,
    *,
    label: str,
    target_files: list[str],
    verification_snapshot: list[dict[str, Any]] | None = None,
    notes: str = "",
    git_branch: str | None = None,
    git_head: str | None = None,
    source_run_id: str | None = None,
    source_checkpoint_id: str | None = None,
    checkpoint_path: str | None = None,
    blessed_by: str | None = None,
    baseline_kind: str = "official",
) -> BaselineRecord:
    root_dir = Path(root_dir).resolve()
    baseline_id = _next_baseline_id(root_dir)
    snapshot = _coerce_snapshot(verification_snapshot)
    record = BaselineRecord(
        baseline_id=baseline_id,
        label=str(label),
        created_at=_utc_now_iso(),
        root_dir=str(root_dir),
        git_branch=git_branch,
        git_head=git_head,
        target_files=sorted({str(item) for item in list(target_files or []) if str(item)}),
        hashes=_current_hashes(root_dir, target_files),
        verification_snapshot=snapshot,
        notes=str(notes or ""),
        source_run_id=source_run_id,
        source_checkpoint_id=source_checkpoint_id,
        checkpoint_path=str(checkpoint_path) if checkpoint_path else None,
        blessed_at_utc=_utc_now_iso(),
        blessed_by=str(blessed_by) if blessed_by else None,
        verification_summary=_verification_summary(snapshot),
        baseline_kind=str(baseline_kind or "official"),
    )
    return _write_record(root_dir, record)


def promote_run_to_baseline(
    root_dir: Path,
    *,
    run_id: str,
    label: str,
    notes: str = "",
    blessed_by: str | None = None,
) -> BaselineRecord:
    root_dir = Path(root_dir).resolve()
    run_payload = read_json(root_dir / "reports/patch_runs" / f"{run_id}.json", None)
    if not isinstance(run_payload, dict):
        raise FileNotFoundError(f"Run no existe: {run_id}")
    if str(run_payload.get("patch_status") or "") == "failed":
        raise ValueError("No se puede promover run con patch_status=failed")
    if str(run_payload.get("system_status") or "") not in {"verified"}:
        raise ValueError("No se puede promover run sin verify limpia")
    checkpoint_target = str(run_payload.get("rollback_target") or "")
    checkpoint_id = Path(checkpoint_target).name if checkpoint_target else None
    return write_baseline(
        root_dir,
        label=label,
        target_files=[str(item) for item in list(run_payload.get("target_files") or [])],
        verification_snapshot=[dict(item) for item in list(run_payload.get("verifier_results") or []) if isinstance(item, dict)],
        notes=notes,
        git_branch=run_payload.get("git_branch"),
        git_head=run_payload.get("git_head"),
        source_run_id=str(run_payload.get("run_id") or run_id),
        source_checkpoint_id=checkpoint_id,
        checkpoint_path=checkpoint_target or None,
        blessed_by=blessed_by,
        baseline_kind="promoted-run",
    )


def promote_checkpoint_to_baseline(
    root_dir: Path,
    *,
    checkpoint_id: str,
    label: str,
    source_run_id: str | None = None,
    target_files: list[str] | None = None,
    verification_snapshot: list[dict[str, Any]] | None = None,
    notes: str = "",
    git_branch: str | None = None,
    git_head: str | None = None,
    blessed_by: str | None = None,
) -> BaselineRecord:
    root_dir = Path(root_dir).resolve()
    checkpoint_meta = read_json(_checkpoint_meta_path(root_dir, checkpoint_id), None)
    if not isinstance(checkpoint_meta, dict):
        raise FileNotFoundError(f"Checkpoint no existe: {checkpoint_id}")
    checkpoint_path = Path(str(checkpoint_meta.get("checkpoint_path") or "")).resolve()
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint path no existe: {checkpoint_path}")
    snapshot = _coerce_snapshot(verification_snapshot)
    summary = _verification_summary(snapshot)
    if snapshot and not summary.get("clean"):
        raise ValueError("No se puede bendecir baseline desde verificación sucia")
    target_files = [str(item) for item in list(target_files or checkpoint_meta.get("target_files") or [])]
    baseline_id = _next_baseline_id(root_dir)
    record = BaselineRecord(
        baseline_id=baseline_id,
        label=str(label),
        created_at=_utc_now_iso(),
        root_dir=str(root_dir),
        git_branch=git_branch,
        git_head=git_head,
        target_files=sorted({str(item) for item in target_files if str(item)}),
        hashes=_checkpoint_hashes(root_dir, checkpoint_path, target_files),
        verification_snapshot=snapshot,
        notes=str(notes or ""),
        source_run_id=source_run_id or str(checkpoint_meta.get("run_id") or "") or None,
        source_checkpoint_id=checkpoint_id,
        checkpoint_path=str(checkpoint_path),
        blessed_at_utc=_utc_now_iso(),
        blessed_by=str(blessed_by) if blessed_by else None,
        verification_summary=summary,
        baseline_kind="promoted-checkpoint",
    )
    return _write_record(root_dir, record)


def load_baseline(root_dir: Path, baseline_id: str) -> BaselineRecord | None:
    payload = read_json(Path(root_dir).resolve() / "reports/baselines" / f"{baseline_id}.json", None)
    if not isinstance(payload, dict):
        return None
    payload.pop("schema_version", None)
    payload.setdefault("source_run_id", None)
    payload.setdefault("source_checkpoint_id", None)
    payload.setdefault("checkpoint_path", None)
    payload.setdefault("blessed_at_utc", None)
    payload.setdefault("blessed_by", None)
    payload.setdefault("verification_summary", None)
    payload.setdefault("baseline_kind", "official")
    return BaselineRecord(**payload)


def list_baselines(root_dir: Path) -> list[dict[str, Any]]:
    payload = _load_index(Path(root_dir).resolve())
    rows = [item for item in payload.get("baselines", []) if isinstance(item, dict)]
    rows.sort(key=lambda item: str(item.get("blessed_at_utc") or item.get("created_at") or ""), reverse=True)
    return rows


def compare_baseline(root_dir: Path, baseline_id: str) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    record = load_baseline(root_dir, baseline_id)
    if record is None:
        raise FileNotFoundError(f"Baseline no existe: {baseline_id}")
    current_hashes = _current_hashes(root_dir, record.target_files)
    drifts: list[dict[str, Any]] = []
    for relative_path in record.target_files:
        expected = str(record.hashes.get(relative_path) or "")
        current = str(current_hashes.get(relative_path) or "")
        if expected != current:
            drifts.append(
                {
                    "relative_path": relative_path,
                    "expected_hash": expected,
                    "current_hash": current,
                }
            )
    return {
        "baseline_id": record.baseline_id,
        "label": record.label,
        "drift_count": len(drifts),
        "drifted": bool(drifts),
        "drifts": drifts,
        "clean_verification": bool((record.verification_summary or {}).get("clean")),
    }


def restore_baseline(root_dir: Path, baseline_id: str) -> dict[str, Any]:
    root_dir = Path(root_dir).resolve()
    record = load_baseline(root_dir, baseline_id)
    if record is None:
        raise FileNotFoundError(f"Baseline no existe: {baseline_id}")
    checkpoint_path = Path(str(record.checkpoint_path or "")).resolve()
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint de baseline no existe: {checkpoint_path}")
    restored_files: list[str] = []
    for relative_path in record.target_files:
        source = checkpoint_path / relative_path
        destination = root_dir / relative_path
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored_files.append(relative_path)
    compare_payload = compare_baseline(root_dir, baseline_id)
    status = "restored" if not compare_payload["drifted"] else "partial"
    append_history_event(
        root_dir,
        {
            "timestamp": _utc_now_iso(),
            "event_type": "baseline-restore",
            "run_id": record.source_run_id,
            "checkpoint_id": record.source_checkpoint_id,
            "status": status,
            "detail": f"{record.baseline_id} restored",
        },
    )
    return {
        "baseline_id": record.baseline_id,
        "label": record.label,
        "status": status,
        "restored_files": restored_files,
        "compare": compare_payload,
    }
