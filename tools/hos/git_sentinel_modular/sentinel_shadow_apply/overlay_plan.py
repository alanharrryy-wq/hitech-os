from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .safe_paths import assert_safe_relative_path

def build_overlay_plan(mutations: Mapping[str, str] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(mutations, Mapping):
        return [
            {"relpath": assert_safe_relative_path(path), "content": content, "action": "upsert"}
            for path, content in mutations.items()
        ]
    plan: list[dict[str, Any]] = []
    for item in mutations:
        relpath = assert_safe_relative_path(item["relpath"])
        plan.append({**item, "relpath": relpath, "action": item.get("action", "upsert")})
    return plan
