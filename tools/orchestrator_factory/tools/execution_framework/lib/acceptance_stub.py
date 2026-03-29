"""Acceptance report stub factory for one-button v1.2 exports.

This module centralizes the creation of a schema-compatible acceptance report
when no integration bundles are present at export time. The implementation is
intentionally stdlib-only and aligned with acceptance_result.schema.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def build_acceptance_stub(
    *,
    project_id: str,
    run_id: str,
    round_id: str,
    generated_at_utc: Optional[str] = None,
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    resolved_notes = notes if notes is not None else [
        'Acceptance report stub emitted because no integration bundles were present at session export time.'
    ]
    return {
        'schema_version': '1.0',
        'project_id': project_id,
        'run_id': run_id,
        'round_id': round_id,
        'generated_at_utc': generated_at_utc or utc_now_iso(),
        'overall_status': 'pending',
        'package_results': [],
        'has_bundles': False,
        'accepted_bundles': [],
        'rejected_bundles': [],
        'notes': list(resolved_notes),
    }
