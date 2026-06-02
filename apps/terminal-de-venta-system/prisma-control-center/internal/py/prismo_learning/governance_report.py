"""Markdown report for governance bridge."""
from __future__ import annotations
from typing import Any

def governance_markdown(payload: dict[str, Any]) -> str:
    canon = payload.get('canon') or {}; rel = payload.get('release_train') or {}
    return '\n'.join([
        '# PRISMO Governance Bridge', '',
        f"Status: {payload.get('status')}",
        f"Canon evidence: {canon.get('canon_count',0)}",
        f"Release train evidence: {rel.get('release_train_evidence',0)}",
        f"Alignment: {rel.get('alignment','unknown')}", '',
        'Runtime remains read-only. mutation_allowed=false.', ''
    ])
