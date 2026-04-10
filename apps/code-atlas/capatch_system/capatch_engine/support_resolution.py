from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from capatch_contracts.operations import OperationSpec, SUPPORT_FIELDS_BY_OPERATION
from capatch_ops.base import (
    build_support_candidates,
    format_suggestion_preview,
    normalize_match_candidate,
    normalize_trailing_spaces_per_line,
    strip_outer_blank_lines,
)


@dataclass(slots=True, frozen=True)
class SupportResolution:
    field_name: str
    original_value: str
    resolved_value: str
    strategy: str


def find_support_resolution(content: str, field_name: str, needle: str) -> SupportResolution | None:
    if needle == "":
        return None
    needle_line_count = max(1, needle.count("\n") + 1)
    candidates = build_support_candidates(content, max_lines=max(needle_line_count + 2, 8), target_line_count=needle_line_count, max_candidates=3200)
    if not candidates:
        return None
    strategies = [
        ("trim_bordes", lambda value: value.strip()),
        ("rstrip_por_linea", normalize_trailing_spaces_per_line),
        ("blank_lines_borde", strip_outer_blank_lines),
        ("whitespace_colapsado", normalize_match_candidate),
    ]
    for strategy_name, normalizer in strategies:
        normalized_needle = normalizer(needle)
        if normalized_needle == "":
            continue
        matches: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            if normalizer(candidate) != normalized_needle:
                continue
            if candidate in seen:
                continue
            seen.add(candidate)
            if content.count(candidate) != 1:
                continue
            matches.append(candidate)
        if len(matches) == 1:
            candidate = matches[0]
            if candidate != needle:
                return SupportResolution(field_name=field_name, original_value=needle, resolved_value=candidate, strategy=strategy_name)
    return None


def has_partial_whitespace_overlap(content: str, needle: str) -> bool:
    if needle == "":
        return False
    first = content.find(needle)
    if first < 0:
        return False
    second = content.find(needle, first + len(needle))
    if second >= 0:
        return False
    before = content[first - 1] if first > 0 else ""
    after_index = first + len(needle)
    after = content[after_index] if after_index < len(content) else ""
    return before in {" ", "\t"} or after in {" ", "\t"}


def materialize_support_payload(ctx: object, target: Path, content: str, operation: OperationSpec) -> tuple[dict[str, Any], list[str]]:
    if not bool(getattr(ctx, "auto_support", False)):
        return dict(operation.payload), []
    payload = dict(operation.payload)
    notes: list[str] = []
    preferred_partial_strategies = {"rstrip_por_linea", "blank_lines_borde"}
    for field_name in SUPPORT_FIELDS_BY_OPERATION.get(operation.type, ()): 
        raw_value = payload.get(field_name)
        if raw_value is None:
            continue
        field_value = str(raw_value)
        resolution = find_support_resolution(content, field_name, field_value)
        if resolution is None:
            continue
        should_apply = field_value not in content
        if not should_apply and resolution.strategy in preferred_partial_strategies:
            should_apply = True
        if not should_apply and resolution.strategy == "trim_bordes" and has_partial_whitespace_overlap(content, field_value):
            should_apply = True
        if not should_apply:
            continue
        payload[field_name] = resolution.resolved_value
        notes.append(f"{field_name}:{resolution.strategy} ({format_suggestion_preview(field_value)} -> {format_suggestion_preview(resolution.resolved_value)})")
    return payload, notes
