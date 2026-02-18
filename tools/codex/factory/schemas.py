from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import SCHEMAS_DIR, read_json
from .schema_engine import validate_instance

SCHEMA_INDEX: dict[str, str] = {
    "worker_bundle_status": "worker_bundle_status.schema.json",
    "integrator_status": "integrator_status.schema.json",
    "files_changed": "files_changed.schema.json",
    "scope_lock": "scope_lock.schema.json",
    "run_ledger": "run_ledger.schema.json",
    "run_ledger_event": "run_ledger_event.schema.json",
    "run_manifest": "run_manifest.schema.json",
    "handoff_note": "handoff_note.schema.json",
    "log_index": "log_index.schema.json",
    "contracts_registry": "contracts_registry.schema.json",
    "factory_config": "factory_config.schema.json",
}


def schema_path(name: str) -> Path:
    if name not in SCHEMA_INDEX:
        raise KeyError(f"Unknown schema key: {name}")
    return SCHEMAS_DIR / SCHEMA_INDEX[name]


def load_schema(name: str) -> dict[str, Any]:
    return read_json(schema_path(name))


def validate_payload(name: str, payload: Any) -> list[str]:
    schema = load_schema(name)
    return validate_instance(payload, schema)


def validate_file(name: str, path: Path) -> list[str]:
    payload = read_json(path)
    return validate_payload(name, payload)


def contracts_check() -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for key in sorted(SCHEMA_INDEX):
        candidate = schema_path(key)
        payload = read_json(candidate)
        error_count = len(validate_instance(payload, {"type": "object"}))
        results.append(
            {
                "schema": key,
                "path": str(candidate),
                "status": "PASS" if error_count == 0 else "FAIL",
                "errors": error_count,
            }
        )
    failed = [entry for entry in results if entry["status"] != "PASS"]
    return {
        "status": "PASS" if not failed else "BLOCKED",
        "total": len(results),
        "failed": len(failed),
        "results": results,
    }
