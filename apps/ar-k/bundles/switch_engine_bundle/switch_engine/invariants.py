"""Determinism and traceability checks."""

from __future__ import annotations

import copy

from switch_engine.models import SwitchEntry
from switch_engine.resolver import resolve_switch_entries


def assert_deterministic(entries: list[SwitchEntry], overrides: dict[str, object], timestamp: str) -> str:
    first = resolve_switch_entries(copy.deepcopy(entries), dict(overrides), timestamp)
    second = resolve_switch_entries(copy.deepcopy(entries), dict(overrides), timestamp)
    if first != second:
        raise AssertionError("Resolution is not deterministic")
    return first[3]


def assert_traceability(trace: list[dict[str, object]]) -> None:
    for record in trace:
        if not record["precedence_path"]:
            raise AssertionError("Trace record is missing precedence path")
        if record["decision_source"] not in {"default", "switch_id", "target_id"}:
            raise AssertionError(f"Unexpected decision source: {record['decision_source']}")


def assert_read_only_hashes(before: dict[str, str | None], after: dict[str, str | None]) -> None:
    if before != after:
        raise AssertionError(f"Canonical input hashes changed: {before} != {after}")
