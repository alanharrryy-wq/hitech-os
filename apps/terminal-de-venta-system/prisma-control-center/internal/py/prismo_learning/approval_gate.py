"""Approval gate: execution is blocked in V1."""
from __future__ import annotations
from typing import Any

def approval_gate(payload: dict[str, Any]) -> dict[str, Any]:
    return {'approved_for_execution': False, 'execution_supported': False, 'reason': 'PRISMO Learning V1 is preview-only for actions.', 'read_only': True, 'mutation_allowed': False}
