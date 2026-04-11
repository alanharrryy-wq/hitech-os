from __future__ import annotations

from typing import Any


def build_planner_input(preflight_report: Any, risk_summary: dict[str, Any], operations: list[Any]) -> dict[str, Any]:
    target_files = list(getattr(preflight_report, 'target_files', []) or [])
    anchor_diagnostics = dict(getattr(preflight_report, 'anchor_diagnostics', {}) or {})
    surface_summary = dict(getattr(preflight_report, 'surface_summary', {}) or {})
    operation_types: list[str] = []
    for item in list(operations or []):
        value = getattr(item, 'type', None)
        if value is None and isinstance(item, dict):
            value = item.get('type')
        if value:
            operation_types.append(str(value))
    return {
        'target_files': target_files,
        'target_file_count': len(target_files),
        'risk_level': str((risk_summary or {}).get('risk_level') or 'low').lower(),
        'blocked_reasons': list((risk_summary or {}).get('blocked_reasons') or []),
        'fragile_anchor_count': int(anchor_diagnostics.get('fragile_anchor_operation_count', 0) or 0),
        'exact_anchor_count': int(anchor_diagnostics.get('exact_anchor_operation_count', 0) or 0),
        'structural_candidate_files': list(surface_summary.get('structural_candidate_files') or []),
        'operation_types': operation_types,
    }
