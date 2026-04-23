"""Executable exclusion policy with explicit reports_real coverage."""

from __future__ import annotations

from pathlib import PurePosixPath, PureWindowsPath

from contracts.shared_canon import EXCLUDED_PARTS

TEMP_SUFFIXES = (".tmp", ".temp", ".cache", ".pyc", ".pyo", ".coverage")


def _parts(path: str) -> tuple[str, ...]:
    if "\\" in path:
        return tuple(part for part in PureWindowsPath(path).parts if part not in ("/", "\\"))
    return tuple(part for part in PurePosixPath(path).parts if part not in ("/",))


def should_exclude(path: str) -> bool:
    parts = {part.strip() for part in _parts(path)}
    lowered = {part.lower() for part in parts}
    if lowered & {part.lower() for part in EXCLUDED_PARTS}:
        return True
    return path.lower().endswith(TEMP_SUFFIXES)


def exclusion_reason(path: str) -> str | None:
    lowered_parts = {part.lower() for part in _parts(path)}
    for part in sorted(EXCLUDED_PARTS):
        if part.lower() in lowered_parts:
            return f"excluded path segment: {part}"
    if path.lower().endswith(TEMP_SUFFIXES):
        return "excluded generated or temporary suffix"
    return None


def examples() -> dict[str, bool]:
    return {
        "apps/ar-k/reports_real/switch_decision_trace.json": should_exclude("apps/ar-k/reports_real/switch_decision_trace.json"),
        "apps/ar-k/reports/artifacts/decision_trace.json": should_exclude("apps/ar-k/reports/artifacts/decision_trace.json"),
        "apps/ar-k/pya/engines/switch_engine/engine.py": should_exclude("apps/ar-k/pya/engines/switch_engine/engine.py"),
        "apps/ar-k/.ark_install/switch_engine_bundle/last_apply.json": should_exclude("apps/ar-k/.ark_install/switch_engine_bundle/last_apply.json"),
    }
