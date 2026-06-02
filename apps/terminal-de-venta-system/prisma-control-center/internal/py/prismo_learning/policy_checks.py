"""Governance policy checks for learning outputs."""
from __future__ import annotations
from typing import Any

BLOCKED_ACTIONS = {'deploy','git_push','db_write','secret_read','delete','execute_zip','install_dependency'}

def check_learning_policy(payload: dict[str, Any]) -> dict[str, Any]:
    actions = set(str(a).lower() for a in (payload.get('actions') or [])) if isinstance(payload.get('actions'), list) else set()
    blocked = sorted(actions & BLOCKED_ACTIONS)
    ok = not blocked and payload.get('mutation_allowed') is False and payload.get('read_only') is True
    return {'ok': ok, 'blocked_actions': blocked, 'read_only_required': True, 'mutation_allowed_required': False}
