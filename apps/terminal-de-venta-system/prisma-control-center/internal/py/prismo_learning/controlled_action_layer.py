"""Controlled Action Layer facade, preview-only in V1."""
from __future__ import annotations
from typing import Any
from .action_preview import build_action_preview

def controlled_action_preview(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_action_preview(payload)

def controlled_action_status() -> dict[str, Any]:
    return {'ok': True, 'status':'preview_only', 'phase':'F9 Controlled Action Layer', 'execution_enabled': False, 'blocked_operations':['deploy','git_push','db_write','delete','execute_script','install_dependency'], 'read_only': True, 'mutation_allowed': False}
