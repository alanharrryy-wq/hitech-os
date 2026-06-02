# PRISMO Learning Core Completion Pack F4-F9
"""Self verification for PRISMO Learning Core completion pack."""
from __future__ import annotations
import compileall
from pathlib import Path
from typing import Any
from .api import (
    learning_status_payload, learning_recommend_protocol_payload, learning_graph_payload,
    learning_patterns_payload, learning_authority_payload, learning_f3_status_payload,
    learning_safe_summary_payload, learning_technical_drawer_payload, learning_feedback_stats_payload,
    learning_compaction_status_payload, learning_governance_status_payload,
    learning_context_enrichment_payload, learning_action_status_payload, learning_action_preview_payload,
    learning_completion_status_payload,
)
from .contracts import validate_read_only_envelope

def _check_payload(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    ok, errors = validate_read_only_envelope(payload)
    return {"name": name, "ok": bool(ok and isinstance(payload, dict)), "errors": errors, "status": payload.get("status")}

def run_verify() -> dict[str, Any]:
    here = Path(__file__).resolve().parent
    checks = [{"name":"py_compile","ok":bool(compileall.compile_dir(str(here),quiet=1,force=True))}]
    samples = [
        ("status_contract", learning_status_payload(public=True)),
        ("recommend_contract", learning_recommend_protocol_payload("playwright fail sync", public=True)),
        ("graph_contract", learning_graph_payload(public=True)),
        ("patterns_contract", learning_patterns_payload(public=True)),
        ("authority_contract", learning_authority_payload(public=True)),
        ("f3_status_contract", learning_f3_status_payload(public=True)),
        ("safe_summary_contract", learning_safe_summary_payload(public=True)),
        ("technical_drawer_contract", learning_technical_drawer_payload(public=False)),
        ("feedback_stats_contract", learning_feedback_stats_payload(public=True)),
        ("compaction_status_contract", learning_compaction_status_payload(public=True)),
        ("governance_status_contract", learning_governance_status_payload(public=True)),
        ("context_enrichment_contract", learning_context_enrichment_payload("sync fail", public=True)),
        ("action_status_contract", learning_action_status_payload(public=True)),
        ("action_preview_contract", learning_action_preview_payload({"type":"db_write"}, public=True)),
        ("completion_status_contract", learning_completion_status_payload(public=True)),
    ]
    checks += [_check_payload(name, payload) for name, payload in samples]
    ok = all(c.get("ok") for c in checks)
    return {"ok": ok, "status": "PASS" if ok else "FAIL", "checks": checks, "read_only": True, "mutation_allowed": False}
if __name__ == "__main__":
    import json; print(json.dumps(run_verify(), ensure_ascii=False, indent=2))
