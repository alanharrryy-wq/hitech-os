# PRISMO Learning Core Completion Pack F4-F9
"""Noise budgets for safe UI presentation.

The backend may know hundreds of facts. Safe UI intentionally shows only a few.
"""
from __future__ import annotations
from typing import Any

DEFAULT_SAFE_BUDGET = {
    "visible_cards": 3,
    "visible_patterns": 3,
    "visible_evidence": 5,
    "visible_warnings": 3,
    "visible_badges": 3,
    "graph_nodes": 12,
    "graph_edges": 16,
}
PERITO_BUDGET = {
    "visible_cards": 8,
    "visible_patterns": 25,
    "visible_evidence": 80,
    "visible_warnings": 20,
    "visible_badges": 8,
    "graph_nodes": 80,
    "graph_edges": 120,
}

def budget_for_mode(mode: str | None = None) -> dict[str, int]:
    if (mode or '').lower() in {'perito','technical','full','debug'}:
        return dict(PERITO_BUDGET)
    return dict(DEFAULT_SAFE_BUDGET)

def take(rows: list[Any] | tuple[Any, ...] | None, key: str, mode: str | None = None) -> list[Any]:
    rows = list(rows or [])
    return rows[:budget_for_mode(mode).get(key, 5)]
