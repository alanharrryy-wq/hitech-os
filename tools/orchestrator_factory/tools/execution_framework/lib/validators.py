from __future__ import annotations

from typing import Any
from .common import Issue, is_safe_relative_path, match_any, normalize_relpath


TYPE_MAP = {
    "string": str,
    "integer": int,
    "array": list,
    "object": dict,
}


def validate_required_fields(data: dict[str, Any], required: dict[str, str], label: str) -> list[Issue]:
    issues: list[Issue] = []
    for key, type_name in required.items():
        if key not in data:
            issues.append(Issue("missing_field", f"{label}: missing required field '{key}'"))
            continue
        expected = TYPE_MAP[type_name]
        if not isinstance(data[key], expected):
            issues.append(Issue("wrong_type", f"{label}: field '{key}' must be {type_name}"))
    return issues


def validate_payload_items(payload_items: list[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    for index, item in enumerate(payload_items):
        if not isinstance(item, dict):
            issues.append(Issue("wrong_type", f"payload_files[{index}] must be an object"))
            continue
        for key in ["repo_path", "sha256", "size_bytes"]:
            if key not in item:
                issues.append(Issue("missing_field", f"payload_files[{index}] missing '{key}'"))
        if "repo_path" in item:
            if not isinstance(item["repo_path"], str):
                issues.append(Issue("wrong_type", f"payload_files[{index}].repo_path must be string"))
            else:
                path = normalize_relpath(item["repo_path"])
                if not is_safe_relative_path(path):
                    issues.append(Issue("invalid_path", "repo_path must be a safe repo-relative path", path=path))
        if "sha256" in item and isinstance(item["sha256"], str):
            if len(item["sha256"]) != 64 or any(ch not in "0123456789abcdef" for ch in item["sha256"].lower()):
                issues.append(Issue("invalid_sha256", f"payload_files[{index}].sha256 must be a lowercase or uppercase hex sha256 digest"))
        if "size_bytes" in item:
            if not isinstance(item["size_bytes"], int) or item["size_bytes"] < 0:
                issues.append(Issue("invalid_size", f"payload_files[{index}].size_bytes must be a non-negative integer"))
    return issues


def validate_against_patterns(paths: list[str], allowed: list[str], forbidden: list[str]) -> list[Issue]:
    issues: list[Issue] = []
    for path in paths:
        normalized = normalize_relpath(path)
        if forbidden and match_any(normalized, forbidden):
            issues.append(Issue("forbidden_path", f"Path '{normalized}' matches a forbidden path", path=normalized))
            continue
        if allowed and not match_any(normalized, allowed):
            issues.append(Issue("ownership_violation", f"Path '{normalized}' is outside allowed ownership", path=normalized))
    return issues
