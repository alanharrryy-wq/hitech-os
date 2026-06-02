# PRISMO Learning Core V1.2 F3
# Generated package: prismo learn3 3005 1128 fix1
# Operation model: pattern-miner + authority-brain, local store writes only, read-only against repo/DB/secrets.
# Standard library only.

"""Public API payload functions for panel_3150 integration."""
from __future__ import annotations
from typing import Any
from .constants import ENGINE_NAME, SCHEMA_VERSION
from .contracts import validate_read_only_envelope
from .diagnostics import diagnostic_snapshot, safe_error
from .evidence_registry import load_registry, query_evidence
from .feedback_loop import record_feedback
from .graph_builder import graph_from_registry
from .pattern_reporter import high_priority_patterns, load_patterns
from .authority_resolver import resolve_authority
from .authority_store import load_authority_summary
from .public_redaction import endpoint_payload
from .recommendation_engine import recommend
from .runtime_probe import probe_runtime
from .tools_status import tool_status
from .endpoint_contracts import endpoint_contracts
from .evidence_intake import intake_status, collect_candidates, run_intake
from .intake_policy import IntakeLimits
from .f3_engine import build_f3_report, f3_status

from .safe_ui_governor import build_safe_ui_payload, build_technical_drawer_payload
from .feedback_stats import feedback_stats_status
from .compaction_engine import compaction_status, run_compaction
from .governance_bridge import governance_status
from .context_enrichment import context_enrichment_payload
from .controlled_action_layer import controlled_action_preview, controlled_action_status
from .f4_to_f9_engine import completion_status, build_completion_report

def _finalize(payload: dict[str, Any], public: bool = False) -> dict[str, Any]:
    payload.setdefault("ok", True); payload.setdefault("read_only", True); payload.setdefault("mutation_allowed", False)
    ok, errors = validate_read_only_envelope(payload)
    if not ok: payload.update({"contract_errors": errors, "ok": False, "status": "contract_error"})
    return endpoint_payload(payload, public=public)

def learning_status_payload(public: bool = False) -> dict[str, Any]:
    try:
        registry = load_registry(); f3 = f3_status()
        return _finalize({"ok": True, "status": "available", "engine": ENGINE_NAME, "schema_version": SCHEMA_VERSION, "phase": "F4-F9 Completion Pack", "read_only": True, "mutation_allowed": False, "evidence_count": len(registry.get("records", [])), "pattern_count": f3.get("pattern_count", 0), "authority_ready": bool(f3.get("authority_summary")), "runtime_probe": probe_runtime(), "tools": tool_status(public=public), "endpoints": endpoint_contracts()}, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_STATUS_ERROR", str(exc)), public)

def learning_evidence_index_payload(public: bool = False, limit: int = 80) -> dict[str, Any]:
    try: rows=query_evidence({}, limit=limit); return _finalize({"ok": True, "status": "available", "records": rows, "count": len(rows), "read_only": True, "mutation_allowed": False}, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_EVIDENCE_INDEX_ERROR", str(exc)), public)

def learning_recommend_protocol_payload(query: str = "", public: bool = False) -> dict[str, Any]:
    try: return _finalize(recommend(query or "learning status"), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_RECOMMEND_PROTOCOL_ERROR", str(exc)), public)

def learning_insights_payload(public: bool = False) -> dict[str, Any]:
    try:
        pats=high_priority_patterns(40); auth=load_authority_summary()
        return _finalize({"ok": True, "status": "available", "patterns": pats, "count": len(pats), "authority_summary": {"record_count": auth.get("record_count", 0), "average_top_authority_score": auth.get("average_top_authority_score", 0)}, "read_only": True, "mutation_allowed": False}, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_INSIGHTS_ERROR", str(exc)), public)

def learning_graph_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(graph_from_registry(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_GRAPH_ERROR", str(exc)), public)

def learning_patterns_payload(public: bool = False) -> dict[str, Any]:
    try: payload=load_patterns(); payload.update({"ok": True, "status": "available"}); return _finalize(payload, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_PATTERNS_ERROR", str(exc)), public)

def learning_authority_payload(public: bool = False) -> dict[str, Any]:
    try: payload=resolve_authority(None); payload.update({"ok": True, "status": "available"}); return _finalize(payload, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_AUTHORITY_ERROR", str(exc)), public)

def learning_f3_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(f3_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_F3_STATUS_ERROR", str(exc)), public)

def learning_f3_run_payload(public: bool = False) -> dict[str, Any]:
    if public: return _finalize({"ok": False, "status": "blocked", "blocked": True, "block_reason": "PUBLIC_F3_RUN_BLOCKED", "read_only": True, "mutation_allowed": False}, public)
    try: return _finalize(build_f3_report(), public=False)
    except Exception as exc: return _finalize(safe_error("LEARNING_F3_RUN_ERROR", str(exc)), public=False)

def learning_feedback_payload(payload: dict[str, Any] | None = None, public: bool = False) -> dict[str, Any]:
    if public: return _finalize({"ok": False, "status": "blocked", "blocked": True, "block_reason": "PUBLIC_FEEDBACK_BLOCKED", "read_only": True, "mutation_allowed": False}, public)
    try: return _finalize(record_feedback(payload or {}), public=False)
    except Exception as exc: return _finalize(safe_error("LEARNING_FEEDBACK_ERROR", str(exc)), public=False)

def learning_diagnostic_payload(public: bool = False) -> dict[str, Any]: return _finalize(diagnostic_snapshot(public=public), public=public)
def learning_intake_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(intake_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_INTAKE_STATUS_ERROR", str(exc)), public)
def learning_intake_plan_payload(public: bool = False, max_files_per_root: int = 3500) -> dict[str, Any]:
    try:
        payload = collect_candidates(limits=IntakeLimits(max_files_per_root=max_files_per_root)); payload.update({"read_only": True, "mutation_allowed": False}); return _finalize(payload, public)
    except Exception as exc: return _finalize(safe_error("LEARNING_INTAKE_PLAN_ERROR", str(exc)), public)
def learning_intake_run_payload(public: bool = False, max_files_per_root: int = 3500) -> dict[str, Any]:
    if public: return _finalize({"ok": False, "status": "blocked", "blocked": True, "block_reason": "PUBLIC_INTAKE_RUN_BLOCKED", "read_only": True, "mutation_allowed": False}, public)
    try:
        payload = run_intake(limits=IntakeLimits(max_files_per_root=max_files_per_root)); payload.update({"read_only": True, "mutation_allowed": False}); return _finalize(payload, public=False)
    except Exception as exc: return _finalize(safe_error("LEARNING_INTAKE_RUN_ERROR", str(exc)), public=False)


def learning_safe_summary_payload(mode: str | None = 'safe', public: bool = True) -> dict[str, Any]:
    try: return _finalize(build_safe_ui_payload(mode=mode, public=public), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_SAFE_SUMMARY_ERROR", str(exc)), public)

def learning_technical_drawer_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(build_technical_drawer_payload(mode='perito', public=public), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_TECHNICAL_DRAWER_ERROR", str(exc)), public)

def learning_feedback_stats_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(feedback_stats_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_FEEDBACK_STATS_ERROR", str(exc)), public)

def learning_compaction_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(compaction_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_COMPACTION_STATUS_ERROR", str(exc)), public)

def learning_compaction_run_payload(public: bool = False) -> dict[str, Any]:
    if public: return _finalize({"ok": False, "status": "blocked", "blocked": True, "block_reason": "PUBLIC_COMPACTION_RUN_BLOCKED", "read_only": True, "mutation_allowed": False}, public)
    try: return _finalize(run_compaction(), public=False)
    except Exception as exc: return _finalize(safe_error("LEARNING_COMPACTION_RUN_ERROR", str(exc)), public=False)

def learning_governance_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(governance_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_GOVERNANCE_STATUS_ERROR", str(exc)), public)

def learning_context_enrichment_payload(query: str = '', public: bool = False) -> dict[str, Any]:
    try: return _finalize(context_enrichment_payload(query), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_CONTEXT_ENRICHMENT_ERROR", str(exc)), public)

def learning_action_preview_payload(payload: dict[str, Any] | None = None, public: bool = False) -> dict[str, Any]:
    try: return _finalize(controlled_action_preview(payload or {}), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_ACTION_PREVIEW_ERROR", str(exc)), public)

def learning_action_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(controlled_action_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_ACTION_STATUS_ERROR", str(exc)), public)

def learning_completion_status_payload(public: bool = False) -> dict[str, Any]:
    try: return _finalize(completion_status(), public)
    except Exception as exc: return _finalize(safe_error("LEARNING_COMPLETION_STATUS_ERROR", str(exc)), public)

def learning_completion_run_payload(public: bool = False) -> dict[str, Any]:
    if public: return _finalize({"ok": False, "status": "blocked", "blocked": True, "block_reason": "PUBLIC_COMPLETION_RUN_BLOCKED", "read_only": True, "mutation_allowed": False}, public)
    try: return _finalize(build_completion_report(), public=False)
    except Exception as exc: return _finalize(safe_error("LEARNING_COMPLETION_RUN_ERROR", str(exc)), public=False)
