"""Rollback planning text for preview-only actions."""
from __future__ import annotations
from typing import Any

def rollback_plan_for(action: dict[str, Any]) -> dict[str, Any]:
    return {'available': True, 'mode': 'plan_only', 'steps': ['Confirm no execution happened.', 'Use existing package ROLLBACK.ps1 for installed files if needed.', 'Review result/fail ZIP before further changes.'], 'read_only': True, 'mutation_allowed': False}
