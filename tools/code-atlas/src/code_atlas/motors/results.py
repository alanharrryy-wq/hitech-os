# CODE_ATLAS_MOTOR_HUB_MODULE_V02
"""Result/failure artifact discovery with environment-neutral defaults."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def default_output_root() -> Path:
    raw = os.environ.get("CODE_ATLAS_OUTPUT_ROOT") or os.environ.get("CODE_ATLAS_RESULT_ROOT")
    return Path(raw).expanduser() if raw else Path.cwd() / "code-atlas-out"


DEFAULT_OUTPUT_ROOT = default_output_root()


def find_latest_result_zip(output_root: str | Path | None = None) -> Path | None:
    return _find_latest_zip(output_root or default_output_root(), ("* result.zip", "*result.zip"))


def find_latest_fail_zip(output_root: str | Path | None = None) -> Path | None:
    return _find_latest_zip(output_root or default_output_root(), ("* fail.zip", "*fail.zip", "* diagnostic.zip", "*diagnostic.zip"))


def _find_latest_zip(output_root: str | Path, patterns: Iterable[str]) -> Path | None:
    root = Path(output_root)
    if not root.exists():
        return None
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(path for path in root.glob(pattern) if path.is_file())
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None
