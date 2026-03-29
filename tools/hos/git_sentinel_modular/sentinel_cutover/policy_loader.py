from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

_DEFAULT_POLICY = {'risk_weights': {'low': 1, 'medium': 2, 'high': 3}, 'needs_smoke': True}

def default_policy() -> dict[str, Any]:
    return json.loads(json.dumps(_DEFAULT_POLICY))

def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

def load_policy(path: str | Path | None = None, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    policy = default_policy()
    if path:
        file_payload = json.loads(Path(path).read_text(encoding="utf-8"))
        policy = _deep_merge(policy, file_payload)
    if overrides:
        policy = _deep_merge(policy, overrides)
    return policy
