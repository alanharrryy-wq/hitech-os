from __future__ import annotations

from pathlib import Path

def normalize_relpath(path: str) -> str:
    return path.replace("\\", "/").strip("/")

def assert_safe_relpath(path: str) -> str:
    normalized = normalize_relpath(path)
    if not normalized or normalized.startswith("../") or "/../" in normalized:
        raise ValueError(f"Unsafe relpath: {path}")
    return normalized

def is_protected_path(path: str, protected_prefixes: list[str] | tuple[str, ...]) -> bool:
    normalized = normalize_relpath(path)
    return any(normalized.startswith(prefix) for prefix in protected_prefixes)

def resolve_target_path(target_root: str | Path, relpath: str) -> Path:
    root = Path(target_root).resolve()
    target = (root / assert_safe_relpath(relpath)).resolve()
    if root not in target.parents and target != root:
        raise ValueError(f"{target} escapes {root}")
    return target
