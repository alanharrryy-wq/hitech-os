from __future__ import annotations

from pathlib import Path

def normalize_relpath(relpath: str) -> str:
    normalized = relpath.replace("\\", "/").strip("/").strip()
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized

def assert_safe_relative_path(relpath: str) -> str:
    normalized = normalize_relpath(relpath)
    if not normalized or normalized.startswith("../") or "/../" in normalized or normalized == "..":
        raise ValueError(f"Unsafe relative path: {relpath}")
    return normalized

def assert_within_directory(root: str | Path, target: str | Path) -> Path:
    root_path = Path(root).resolve()
    target_path = Path(target).resolve()
    if root_path not in target_path.parents and target_path != root_path:
        raise ValueError(f"{target_path} escapes {root_path}")
    return target_path
