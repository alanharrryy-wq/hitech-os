from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path
from typing import Any, Mapping

from .io_utils import sha256_file


DEFAULT_MANIFEST_CANDIDATES = (
    "RUN_MANIFEST.json",
    "LEGAL_RUN_MANIFEST.json",
    "INSTALL_STATE.json",
    "MANIFEST.json",
)


def _read_json_member(archive: zipfile.ZipFile, candidates: tuple[str, ...]) -> tuple[str | None, dict[str, Any] | None]:
    names = archive.namelist()
    for candidate in candidates:
        exact = [name for name in names if name == candidate or name.endswith("/" + candidate)]
        for name in sorted(exact, key=len):
            try:
                value = json.loads(archive.read(name).decode("utf-8-sig", errors="replace"))
                if isinstance(value, dict):
                    return name, value
            except Exception:
                continue
    return None, None


def inspect_result_zip(path: Path) -> dict[str, Any]:
    row: dict[str, Any] = {
        "name": path.name,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "mtime_ns": path.stat().st_mtime_ns,
    }
    try:
        with zipfile.ZipFile(path, "r") as archive:
            member, manifest = _read_json_member(archive, DEFAULT_MANIFEST_CANDIDATES)
            row["manifest_member"] = member
            row["manifest"] = manifest
            row["entry_count"] = len(archive.namelist())
    except Exception as exc:
        row["error"] = f"{type(exc).__name__}:{exc}"
    return row


def find_latest_authority(output_root: Path, prefix: str, expected_status: str) -> dict[str, Any] | None:
    candidates = sorted(
        [path for path in output_root.glob(f"{prefix}*result.zip") if path.is_file()],
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    for path in candidates:
        row = inspect_result_zip(path)
        status = str((row.get("manifest") or {}).get("status") or "")
        if status == expected_status:
            row["status"] = status
            return row
    return None


def _requirements_from_env() -> dict[str, str]:
    raw = str(os.environ.get("CODE_ATLAS_AUTHORITY_REQUIREMENTS_JSON", "")).strip()
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("INVALID_CODE_ATLAS_AUTHORITY_REQUIREMENTS_JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("CODE_ATLAS_AUTHORITY_REQUIREMENTS_JSON_MUST_BE_OBJECT")
    return {str(key): str(status) for key, status in value.items() if str(key).strip() and str(status).strip()}


def validate_authority_chain(
    output_root: str | Path,
    *,
    requirements: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    root = Path(output_root)
    configured = dict(requirements) if requirements is not None else _requirements_from_env()
    errors: list[str] = []
    chain: dict[str, Any] = {}
    for prefix, expected in configured.items():
        row = find_latest_authority(root, str(prefix), str(expected))
        if row is None:
            errors.append(f"MISSING_AUTHORITY:{prefix}:{expected}")
        else:
            chain[str(prefix)] = row

    return {
        "schema": "CODE_ATLAS_LEGAL_AUTHORITY_CHAIN_V2",
        "status": "PASS" if not errors else "FAIL",
        "configuration": "CALLER_CONFIGURED" if configured else "NOT_REQUIRED_BY_NEUTRAL_DEFAULT",
        "requirement_count": len(configured),
        "chain": chain,
        "warnings": [],
        "errors": errors,
    }
