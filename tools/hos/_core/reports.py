#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .stable_json import write_json
from .stable_text import write_text


@dataclass(frozen=True)
class ReportRoots:
    docs_system: Path
    local_reports: Path


def detect_report_roots(repo_root: Path) -> ReportRoots:
    return ReportRoots(
        docs_system=(repo_root / "docs/system").resolve(),
        local_reports=(repo_root / "tools/_local/reports").resolve(),
    )


def timestamp_slug() -> str:
    fixed = os.getenv("HOS_FIXED_TIMESTAMP")
    if fixed:
        return fixed
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def write_markdown_report(
    repo_root: Path,
    file_name: str,
    content: str,
    local: bool = False,
    subdir: str | None = None,
) -> Path:
    roots = detect_report_roots(repo_root)
    base = roots.local_reports if local else roots.docs_system
    if subdir:
        base = base / subdir
    path = base / file_name
    write_text(path, content, trailing_newline=True)
    return path


def write_json_report(
    repo_root: Path,
    file_name: str,
    payload: Any,
    local: bool = False,
    subdir: str | None = None,
) -> Path:
    roots = detect_report_roots(repo_root)
    base = roots.local_reports if local else roots.docs_system
    if subdir:
        base = base / subdir
    path = base / file_name
    write_json(path, payload, indent=2, sort_keys=True)
    return path

