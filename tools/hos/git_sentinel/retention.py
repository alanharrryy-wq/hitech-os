#!/usr/bin/env python3
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .config import SentinelConfig


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([path for path in root.rglob("*") if path.is_file()], key=lambda item: item.as_posix())


def _remove_empty_dirs(root: Path) -> int:
    if not root.exists():
        return 0
    removed = 0
    directories = sorted([path for path in root.rglob("*") if path.is_dir()], key=lambda item: len(item.parts), reverse=True)
    for directory in directories:
        try:
            directory.rmdir()
            removed += 1
        except OSError:
            continue
    return removed


def _prune_target(root: Path, max_age_days: int, max_files: int) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=True)
    now_epoch = float(time.time())
    max_age_seconds = max(1, int(max_age_days)) * 86400
    max_kept_files = max(1, int(max_files))

    files = _iter_files(root)
    by_recency = sorted(files, key=lambda item: item.stat().st_mtime if item.exists() else 0.0, reverse=True)

    to_delete: dict[Path, str] = {}
    for path in by_recency:
        try:
            age_seconds = max(0, now_epoch - float(path.stat().st_mtime))
        except OSError:
            continue
        if age_seconds > max_age_seconds:
            to_delete[path] = "max_age"

    retained = [path for path in by_recency if path not in to_delete]
    if len(retained) > max_kept_files:
        for path in retained[max_kept_files:]:
            to_delete[path] = "max_files"

    deleted_files = 0
    deleted_bytes = 0
    failed_files = 0
    reasons: dict[str, int] = {"max_age": 0, "max_files": 0}
    for path, reason in sorted(to_delete.items(), key=lambda item: item[0].as_posix()):
        try:
            size = int(path.stat().st_size)
        except OSError:
            size = 0
        try:
            path.unlink(missing_ok=True)
            deleted_files += 1
            deleted_bytes += size
            reasons[reason] = reasons.get(reason, 0) + 1
        except OSError:
            failed_files += 1

    deleted_dirs = _remove_empty_dirs(root)
    return {
        "path": root.as_posix(),
        "scannedFiles": len(files),
        "deletedFiles": deleted_files,
        "deletedBytes": deleted_bytes,
        "failedFiles": failed_files,
        "deletedDirs": deleted_dirs,
        "reasons": reasons,
        "maxAgeDays": int(max_age_days),
        "maxFiles": int(max_files),
    }


def apply_retention_policy(config: SentinelConfig) -> dict[str, Any]:
    if not bool(config.retention_enabled):
        return {
            "enabled": False,
            "targets": [],
            "summary": {
                "deletedFiles": 0,
                "deletedBytes": 0,
                "failedFiles": 0,
                "deletedDirs": 0,
            },
        }

    targets = [
        ("reports", config.report_dir),
        ("telemetry", config.telemetry_dir),
        ("logs", config.log_dir),
        ("quarantine", config.quarantine_dir),
    ]
    details = [
        {
            "kind": kind,
            **_prune_target(
                root=path.resolve(),
                max_age_days=int(config.retention_max_age_days),
                max_files=int(config.retention_max_files_per_dir),
            ),
        }
        for kind, path in targets
    ]

    deleted_files = sum(int(row.get("deletedFiles", 0)) for row in details)
    deleted_bytes = sum(int(row.get("deletedBytes", 0)) for row in details)
    failed_files = sum(int(row.get("failedFiles", 0)) for row in details)
    deleted_dirs = sum(int(row.get("deletedDirs", 0)) for row in details)

    return {
        "enabled": True,
        "targets": details,
        "summary": {
            "deletedFiles": deleted_files,
            "deletedBytes": deleted_bytes,
            "failedFiles": failed_files,
            "deletedDirs": deleted_dirs,
        },
    }
