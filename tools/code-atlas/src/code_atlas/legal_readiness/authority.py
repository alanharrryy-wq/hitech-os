from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from .io_utils import sha256_file


AUTHORITY_REQUIREMENTS = {
    "legmesh1": "PASS_AUTHORITY_READY_FOR_PACKAGE_DESIGN",
    "ndclgl1": "PASS_NDC_LEGAL_EXTENSION_INSTALLED",
    "motlgl1": "PASS_MOTOR_LEGAL_ADAPTER_INSTALLED",
    "mamlegal1": "PASS_MAM_LEGAL_ADAPTER_INSTALLED",
}


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
        "path": str(path),
        "name": path.name,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "mtime_ns": path.stat().st_mtime_ns,
    }
    try:
        with zipfile.ZipFile(path, "r") as archive:
            member, manifest = _read_json_member(
                archive,
                (
                    "RUN_MANIFEST.json",
                    "LEGAL_RUN_MANIFEST.json",
                    "MAM_LEGAL1_INSTALL_STATE.json",
                    "MOTOR_LEGAL1_INSTALL_STATE.json",
                ),
            )
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


def validate_authority_chain(output_root: str | Path, *, require_mamastrophic: bool = True) -> dict[str, Any]:
    root = Path(output_root)
    errors: list[str] = []
    warnings: list[str] = []
    chain: dict[str, Any] = {}
    for prefix, expected in AUTHORITY_REQUIREMENTS.items():
        if prefix == "mamlegal1" and not require_mamastrophic:
            continue
        row = find_latest_authority(root, prefix, expected)
        if row is None:
            errors.append(f"MISSING_AUTHORITY:{prefix}:{expected}")
        else:
            chain[prefix] = row

    return {
        "schema": "CODE_ATLAS_LEGAL_AUTHORITY_CHAIN_V1",
        "status": "PASS" if not errors else "FAIL",
        "output_root": str(root),
        "chain": chain,
        "warnings": warnings,
        "errors": errors,
    }
