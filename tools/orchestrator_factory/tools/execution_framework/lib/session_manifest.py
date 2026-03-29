"""Session manifest builder for one-button v1.2 exports.

The payload produced here is used both as:
1) `session/session_manifest.json` staged inside the canonical ZIP, and
2) the starting shape for the external `<session_id>.manifest.json` sidecar.

For export integrity, final ZIP hash/size authority lives in the external sidecar.
The internal ZIP manifest is intentionally allowed to carry placeholder values for
self-referential artifact checksum fields.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from session_state import PlannedSession


class SessionManifestBuilder:
    def build(
        self,
        *,
        plan: PlannedSession,
        launcher_version: str,
        status: str,
        checks: Dict[str, str],
        idempotency_key: str,
        idempotency_decision: str,
        context_hashes: Dict[str, str],
        lock_id: Optional[str],
        lock_path: str,
        lock_pid: int,
        lock_host: str,
        session_zip_path: str,
        session_zip_sha256: str,
        session_zip_size_bytes: int,
        handoff_copy_path: Optional[str],
        issues: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            'schema_version': '1.0',
            'session_id': plan.session_id,
            'launcher_version': launcher_version,
            'created_at_utc': plan.created_at_utc,
            'session_mode': plan.session_mode,
            'policy': plan.policy,
            'status': status,
            'project': {
                'project_id': plan.project_id,
                'project_name': plan.project_name,
                'initiative_type': plan.initiative_type,
            },
            'run': {
                'run_id': plan.run_id,
                'action': self._resolve_run_action(plan),
            },
            'round': {
                'round_id': plan.round_id,
                'parent_round_id': plan.parent_round_id,
            },
            'intent': {
                'raw': plan.intent_raw,
                'normalized': plan.intent_normalized,
            },
            'checks': {
                'contracts': checks.get('contracts', 'pass'),
                'smoke': checks.get('smoke', 'pass'),
                'readiness_stage_install': checks.get('readiness_stage_install', 'ready'),
                'readiness_stage_round': checks.get('readiness_stage_round', 'ready'),
            },
            'idempotency': {
                'key': idempotency_key,
                'decision': idempotency_decision,
                'context_hashes': context_hashes,
            },
            'lock': {
                'lock_id': lock_id,
                'lock_path': lock_path,
                'pid': lock_pid,
                'host': lock_host,
            },
            'artifacts': {
                'session_zip_path': session_zip_path,
                'session_zip_sha256': session_zip_sha256,
                'session_zip_size_bytes': session_zip_size_bytes,
                'handoff_copy_path': handoff_copy_path,
            },
            'issues': issues,
        }

    @staticmethod
    def _resolve_run_action(plan: PlannedSession) -> str:
        if plan.session_mode == 'new_project':
            return 'create_new_run'
        if plan.policy == 'upgrade':
            return 'create_new_run'
        return 'reuse_existing_run'
