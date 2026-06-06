# CODE_ATLAS_MOTOR_HUB_MODULE_V01
"""Result/failure artifact discovery for Motor Hub."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT_ROOT = Path(r"F:\descargasf")


def find_latest_result_zip(output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> Path | None:
    return _find_latest_zip(output_root, ("* result.zip", "*result.zip"))


def find_latest_fail_zip(output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> Path | None:
    return _find_latest_zip(output_root, ("* fail.zip", "*fail.zip", "* diagnostic.zip", "*diagnostic.zip"))


def _find_latest_zip(output_root: str | Path, patterns: Iterable[str]) -> Path | None:
    root = Path(output_root)
    if not root.exists():
        return None

    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(path for path in root.glob(pattern) if path.is_file())

    if not candidates:
        return None

    return max(candidates, key=lambda path: path.stat().st_mtime)
