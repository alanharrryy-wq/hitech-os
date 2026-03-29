from __future__ import annotations

def normalize_relpath(path: str) -> str:
    return path.replace("\\", "/").strip("/")

def _prefix_match(path: str, prefixes: list[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)

def classify_path(path: str) -> str:
    normalized = normalize_relpath(path)
    if _prefix_match(normalized, ["docs/", "tests/"]):
        return "low"
    if _prefix_match(normalized, ["configs/", "shared/"]):
        return "medium"
    return "high"

def classify_many(paths: list[str]) -> dict[str, list[str]]:
    grouped = {"low": [], "medium": [], "high": []}
    for path in paths:
        grouped[classify_path(path)].append(normalize_relpath(path))
    return grouped
