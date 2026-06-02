"""Preview-only controlled action contracts.

No execution in V1 completion pack.
"""
from __future__ import annotations
from typing import Any
ALLOWED_PREVIEW_TYPES = {'diagnostic','report','intake_plan','rollback_plan','manual_checklist'}
BLOCKED_EXECUTION_TYPES = {'deploy','db_write','delete','git_push','execute_script','install_dependency'}

def normalize_action_request(payload: dict[str, Any] | None) -> dict[str, Any]:
    p = dict(payload or {})
    kind = str(p.get('type') or 'manual_checklist').lower()
    if kind in BLOCKED_EXECUTION_TYPES: blocked = True
    else: blocked = False
    if kind not in ALLOWED_PREVIEW_TYPES: kind = 'manual_checklist'
    return {'type': kind, 'title': str(p.get('title') or 'Safe action preview')[:160], 'blocked': blocked, 'requested_raw_type': str(p.get('type') or ''), 'steps': list(p.get('steps') or [])[:20] if isinstance(p.get('steps'), list) else []}
