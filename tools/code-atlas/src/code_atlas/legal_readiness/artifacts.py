from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any, Iterable

from .io_utils import sha256_file


MANIFEST_CANDIDATES = (
    "LEGAL_RUN_MANIFEST.json",
    "RUN_MANIFEST.json",
    "MAM_LEGAL1_INSTALL_STATE.json",
    "MOTOR_LEGAL1_INSTALL_STATE.json",
)


def snapshot_zip_files(output_root: str | Path) -> dict[str, dict[str, Any]]:
    root = Path(output_root)
    result: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return result
    for path in root.glob("*.zip"):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
            result[str(path.resolve()).lower()] = {
                "path": str(path.resolve()),
                "name": path.name,
                "size_bytes": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
            }
        except OSError:
            continue
    return result


def _read_manifest(path: Path) -> tuple[str | None, dict[str, Any] | None]:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            for candidate in MANIFEST_CANDIDATES:
                hits = [name for name in names if name == candidate or name.endswith("/" + candidate)]
                for name in sorted(hits, key=len):
                    try:
                        value = json.loads(archive.read(name).decode("utf-8-sig", errors="replace"))
                        if isinstance(value, dict):
                            return name, value
                    except Exception:
                        continue
    except Exception:
        pass
    return None, None


def inspect_artifact(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    stat = target.stat()
    member, manifest = _read_manifest(target)
    return {
        "path": str(target.resolve()),
        "name": target.name,
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(target),
        "manifest_member": member,
        "manifest": manifest,
        "valid_zip": zipfile.is_zipfile(target),
    }


def discover_stage_artifact(
    *,
    output_root: str | Path,
    before: dict[str, dict[str, Any]],
    expected_prefixes: Iterable[str],
) -> dict[str, Any] | None:
    root = Path(output_root)
    prefixes = tuple(value.lower() for value in expected_prefixes)
    candidates: list[Path] = []
    for path in root.glob("*.zip"):
        if not path.is_file():
            continue
        low_name = path.name.lower()
        if prefixes and not any(low_name.startswith(prefix) for prefix in prefixes):
            continue
        key = str(path.resolve()).lower()
        previous = before.get(key)
        stat = path.stat()
        if previous is None or previous.get("mtime_ns") != stat.st_mtime_ns or previous.get("size_bytes") != stat.st_size:
            candidates.append(path)
    if not candidates:
        return None
    selected = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    return inspect_artifact(selected)


def manifest_status(artifact: dict[str, Any] | None) -> str:
    if not artifact:
        return ""
    manifest = artifact.get("manifest") or {}
    return str(manifest.get("status") or "")
