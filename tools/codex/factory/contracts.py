from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import CONTRACTS_DIR, INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, read_json, write_json, write_text
from .config import load_factory_config
from .schemas import validate_payload

WORKER_REQUIRED_FILES: tuple[str, ...] = (
    "STATUS.json",
    "SUMMARY.md",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "SUGGESTIONS.md",
    "SCOPE_LOCK.json",
    "HANDOFF_NOTE.json",
    "LOGS/INDEX.json",
)

INTEGRATOR_REQUIRED_FILES: tuple[str, ...] = (
    "STATUS.json",
    "FINAL_REPORT.txt",
    "FILES_CHANGED.json",
    "DIFF.patch",
    "MERGE_PLAN.md",
    "LOGS/INDEX.json",
)


def registry_path() -> Path:
    return CONTRACTS_DIR / "contracts_registry.json"


def load_registry() -> dict[str, Any]:
    payload = read_json(registry_path())
    errors = validate_payload("contracts_registry", payload)
    if errors:
        joined = "\n".join(errors)
        raise ValueError(f"contracts registry invalid:\n{joined}")
    return payload


def run_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id


def bundle_dir(run_id: str, worker: str) -> Path:
    return run_dir(run_id) / worker


def _default_worker_status(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "contract_version": 2,
        "run_id": run_id,
        "worker_id": worker,
        "status": "PENDING",
        "noop": False,
        "noop_reason": "",
        "noop_ack": "",
        "started_at": "",
        "ended_at": "",
        "required_checks": [],
        "optional_checks": [],
        "errors": [],
        "warnings": [],
        "artifacts": [],
    }


def _default_files_changed(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "owner": worker,
        "changes": [],
        "noop": True,
        "noop_reason": "scaffold placeholder: worker has not declared changes",
        "noop_ack": worker,
    }


def _default_scope_lock(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "allowed_globs": [f"{worker.lower()}/**"],
        "blocked_globs": [],
        "allow_shared_paths": [],
    }


def _default_handoff(run_id: str, worker: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "worker_id": worker,
        "summary": "",
        "decisions": [],
        "risks": [],
        "next_actions": [],
    }


def _default_log_index(run_id: str, owner: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "owner": owner,
        "logs": [],
    }


def scaffold_worker_bundle(run_id: str, worker: str) -> dict[str, Any]:
    target = bundle_dir(run_id, worker)
    ensure_dir(target)
    ensure_dir(target / "LOGS")

    created: list[str] = []

    files_payload: dict[str, Any] = {
        "STATUS.json": _default_worker_status(run_id, worker),
        "FILES_CHANGED.json": _default_files_changed(run_id, worker),
        "SCOPE_LOCK.json": _default_scope_lock(run_id, worker),
        "HANDOFF_NOTE.json": _default_handoff(run_id, worker),
        "LOGS/INDEX.json": _default_log_index(run_id, worker),
    }

    for name, payload in files_payload.items():
        path = target / name
        if not path.exists():
            write_json(path, payload)
            created.append(path.as_posix())

    text_files = {
        "SUMMARY.md": f"# {worker} Summary\n\n- Run ID: `{run_id}`\n- Worker: `{worker}`\n- Status: pending\n",
        "SUGGESTIONS.md": f"# {worker} Suggestions\n\n- None yet.\n",
        "DIFF.patch": "",
    }
    for name, text in text_files.items():
        path = target / name
        if not path.exists():
            write_text(path, text)
            created.append(path.as_posix())

    return {
        "worker": worker,
        "bundle_dir": target.as_posix(),
        "created": sorted(created),
    }


def scaffold_integrator_bundle(run_id: str) -> dict[str, Any]:
    worker = INTEGRATOR
    target = bundle_dir(run_id, worker)
    ensure_dir(target)
    ensure_dir(target / "LOGS")

    created: list[str] = []
    json_files = {
        "STATUS.json": {
            "schema_version": 1,
            "contract_version": 2,
            "run_id": run_id,
            "worker_id": worker,
            "status": "PENDING",
            "noop": False,
            "noop_reason": "",
            "noop_ack": "",
            "started_at": "",
            "ended_at": "",
            "required_checks": [],
            "optional_checks": [],
            "errors": [],
            "warnings": [],
            "artifacts": [],
        },
        "FILES_CHANGED.json": {
            "schema_version": 1,
            "run_id": run_id,
            "owner": worker,
            "changes": [],
            "noop": True,
            "noop_reason": "scaffold placeholder: integrator has not declared changes",
            "noop_ack": worker,
        },
        "LOGS/INDEX.json": _default_log_index(run_id, worker),
    }

    for name, payload in json_files.items():
        path = target / name
        if not path.exists():
            write_json(path, payload)
            created.append(path.as_posix())

    text_files = {
        "FINAL_REPORT.txt": "# Final Report\n\nPending integration.\n",
        "MERGE_PLAN.md": "# Merge Plan\n\nPending integration.\n",
        "DIFF.patch": "",
    }
    for name, payload in text_files.items():
        path = target / name
        if not path.exists():
            write_text(path, payload)
            created.append(path.as_posix())

    return {
        "worker": worker,
        "bundle_dir": target.as_posix(),
        "created": sorted(created),
    }


def scaffold_all_bundles(run_id: str, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    result = {
        "run_id": run_id,
        "workers": [],
    }
    for worker in chosen:
        result["workers"].append(scaffold_worker_bundle(run_id, worker))
    result["integrator"] = scaffold_integrator_bundle(run_id)
    return result


def validate_bundle_shape(run_id: str, worker: str) -> list[str]:
    target = bundle_dir(run_id, worker)
    cfg = load_factory_config(strict=False)
    worker_files = cfg.get("workers", {}).get("required_worker_files", list(WORKER_REQUIRED_FILES))
    integrator_files = cfg.get("workers", {}).get("required_integrator_files", list(INTEGRATOR_REQUIRED_FILES))
    required = tuple(worker_files) if worker != INTEGRATOR else tuple(integrator_files)
    errors: list[str] = []
    if not target.exists():
        return [f"missing bundle directory: {target.as_posix()}"]
    for name in required:
        path = target / name
        if not path.exists():
            errors.append(f"missing required artifact: {path.as_posix()}")
    return errors


def validate_bundle_schemas(run_id: str, worker: str) -> list[str]:
    target = bundle_dir(run_id, worker)
    errors: list[str] = []

    status_path = target / "STATUS.json"
    if status_path.exists():
        status_payload = read_json(status_path)
        schema_name = "integrator_status" if worker == INTEGRATOR else "worker_bundle_status"
        status_errors = validate_payload(schema_name, status_payload)
        errors.extend([f"STATUS.json: {item}" for item in status_errors])

    files_changed_path = target / "FILES_CHANGED.json"
    if files_changed_path.exists():
        files_changed_payload = read_json(files_changed_path)
        errors.extend([f"FILES_CHANGED.json: {item}" for item in validate_payload("files_changed", files_changed_payload)])

    if worker != INTEGRATOR:
        scope_lock_path = target / "SCOPE_LOCK.json"
        handoff_path = target / "HANDOFF_NOTE.json"
        if scope_lock_path.exists():
            errors.extend([f"SCOPE_LOCK.json: {item}" for item in validate_payload("scope_lock", read_json(scope_lock_path))])
        if handoff_path.exists():
            errors.extend([f"HANDOFF_NOTE.json: {item}" for item in validate_payload("handoff_note", read_json(handoff_path))])

    log_index_path = target / "LOGS" / "INDEX.json"
    if log_index_path.exists():
        errors.extend([f"LOGS/INDEX.json: {item}" for item in validate_payload("log_index", read_json(log_index_path))])

    return errors


def validate_bundle(run_id: str, worker: str) -> dict[str, Any]:
    shape_errors = validate_bundle_shape(run_id, worker)
    schema_errors = [] if shape_errors else validate_bundle_schemas(run_id, worker)
    all_errors = [*shape_errors, *schema_errors]
    return {
        "run_id": run_id,
        "worker": worker,
        "status": "PASS" if not all_errors else "BLOCKED",
        "errors": all_errors,
    }


def validate_run(run_id: str, workers: list[str] | None = None) -> dict[str, Any]:
    chosen = workers or list(WORKERS)
    results = [validate_bundle(run_id, worker) for worker in chosen]
    results.append(validate_bundle(run_id, INTEGRATOR))
    blocked = [entry for entry in results if entry["status"] != "PASS"]
    return {
        "run_id": run_id,
        "status": "PASS" if not blocked else "BLOCKED",
        "results": results,
        "blocked": len(blocked),
    }
