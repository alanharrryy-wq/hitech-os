"""Deterministic resolver that mirrors Ar-k switch precedence."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from switch_engine.models import ResolutionResult, SwitchEntry


def _stable_hash(payload: object) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def resolve_switch_entries(entries: Iterable[SwitchEntry], overrides: dict[str, object], timestamp: str) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str], str]:
    resolutions: list[dict[str, object]] = []
    trace: list[dict[str, object]] = []
    warnings: list[str] = []
    for entry in sorted(entries, key=lambda item: item.switch_id):
        resolved_value = entry.default_value
        decision_source = "default"
        precedence_path = ["default"]
        justification = "Resolved from switch default value."
        override_key = None
        override_used = None
        if entry.switch_id in overrides:
            override_key = entry.switch_id
            override_used = overrides[entry.switch_id]
            precedence_path.append("switch_id")
            decision_source = "switch_id"
        elif entry.target_id in overrides:
            override_key = entry.target_id
            override_used = overrides[entry.target_id]
            precedence_path.append("target_id")
            decision_source = "target_id"
        if override_used is not None:
            if isinstance(override_used, bool):
                resolved_value = override_used
                justification = f"Resolved from {decision_source} override."
            else:
                warnings.append(
                    f"Invalid override for {entry.switch_id}: expected bool, got {type(override_used).__name__}"
                )
                decision_source = "default"
                precedence_path = ["default", "invalid_override_ignored"]
                justification = "Invalid override ignored; default retained."
        resolution = ResolutionResult(
            switch_id=entry.switch_id,
            target_type=entry.target_type,
            target_id=entry.target_id,
            default_value=entry.default_value,
            resolved_value=resolved_value,
            decision_source=decision_source,
            precedence_path=tuple(precedence_path),
            justification=justification,
            override_key=override_key,
        )
        resolutions.append(
            {
                "switch_id": resolution.switch_id,
                "target_type": resolution.target_type,
                "target_id": resolution.target_id,
                "default_value": resolution.default_value,
                "resolved_value": resolution.resolved_value,
                "decision_source": resolution.decision_source,
                "precedence_path": list(resolution.precedence_path),
                "justification": resolution.justification,
                "timestamp": timestamp,
            }
        )
        trace.append(
            {
                "switch_id": resolution.switch_id,
                "decision_source": resolution.decision_source,
                "resolved_value": resolution.resolved_value,
                "precedence_path": list(resolution.precedence_path),
                "evaluated_override_key": resolution.override_key,
                "warning": warnings[-1] if warnings and warnings[-1].startswith(f"Invalid override for {entry.switch_id}") else None,
            }
        )
    deterministic_hash = _stable_hash({"resolutions": resolutions, "trace": trace, "warnings": warnings})
    return resolutions, trace, warnings, deterministic_hash
