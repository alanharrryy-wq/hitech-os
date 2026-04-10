from __future__ import annotations

"""API pública del dominio capatch_diagnostics."""

from pathlib import Path
from typing import Any

from plugin_lib.redaction_utils import redact_mapping

from ._contracts import DEFAULT_COMMAND_TIMEOUT_SECONDS, DEFAULT_REPORT_BUNDLE_FORMAT
from .budgets import build_diagnostic_budget
from .evidence_graph import annotate_evidence_graph
from .loader import initialize_plugin_runtime
from .phase_runner import phase_order_for_mode, run_phase, seed_foundation_artifacts
from .reporting import write_session_reports, write_support_bundle
from .session import DiagnosticSession, Recommendation, make_session_id, utc_now_iso
from .targeting import build_environment_summary, detect_app_kind, resolve_target_path

try:  # pragma: no cover - bridge a otra subparte si ya existe
    from capatch_policy.confidence import annotate_session_confidence  # type: ignore
except Exception:  # pragma: no cover
    try:
        from core_confidence_engine import annotate_session_confidence  # type: ignore
    except Exception:  # pragma: no cover
        def annotate_session_confidence(session: DiagnosticSession, base_dir: Path) -> dict[str, Any]:
            return {"session_id": session.session_id, "status": "policy-not-wired"}

try:  # pragma: no cover - bridge a otra subparte si ya existe
    from capatch_policy.decision_ledger import write_operator_trust_outputs  # type: ignore
except Exception:  # pragma: no cover
    try:
        from core_decision_ledger import write_operator_trust_outputs  # type: ignore
    except Exception:  # pragma: no cover
        def write_operator_trust_outputs(base_dir: Path, session: DiagnosticSession) -> dict[str, str]:
            return {}

try:  # pragma: no cover - bridge a otra subparte si ya existe
    from capatch_policy.intervention import evaluate_intervention_gates  # type: ignore
except Exception:  # pragma: no cover
    try:
        from core_intervention_gates import evaluate_intervention_gates  # type: ignore
    except Exception:  # pragma: no cover
        def evaluate_intervention_gates(session: DiagnosticSession, base_dir: Path) -> dict[str, Any]:
            return {"status": "caution", "allow_apply": False, "risk_tier": "guarded", "checks": []}

try:  # pragma: no cover - bridge a helper preexistente
    from core_noise_filters import mark_session_noise  # type: ignore
except Exception:  # pragma: no cover
    def mark_session_noise(session: DiagnosticSession, base_dir: Path, target_path: Path) -> DiagnosticSession:
        return session


def derive_execution_mode(args: Any) -> str:
    if getattr(args, "verify_only", False):
        return "verify-only"
    if getattr(args, "collect_only", False):
        return "collect-only"
    if getattr(args, "support_bundle", False):
        return "support-bundle"
    if getattr(args, "apply_fixes", False):
        return "apply-fixes"
    if getattr(args, "fix_plan", False):
        return "fix-plan"
    return "diagnose"


def _build_options(args: Any) -> dict[str, Any]:
    return redact_mapping(
        {
            "bundle_format": getattr(args, "bundle_format", DEFAULT_REPORT_BUNDLE_FORMAT),
            "collect_only": bool(getattr(args, "collect_only", False)),
            "verify_only": bool(getattr(args, "verify_only", False)),
            "support_bundle": bool(getattr(args, "support_bundle", False)),
            "fix_plan": bool(getattr(args, "fix_plan", False)),
            "apply_fixes": bool(getattr(args, "apply_fixes", False)),
            "dry_diagnose": bool(getattr(args, "dry_diagnose", False)),
            "include_logs": bool(getattr(args, "include_logs", False)),
            "include_processes": bool(getattr(args, "include_processes", False)),
            "include_ports": bool(getattr(args, "include_ports", False)),
            "include_git": bool(getattr(args, "include_git", False)),
            "include_build": bool(getattr(args, "include_build", False)),
            "include_tests": bool(getattr(args, "include_tests", False)),
            "command_timeout_seconds": int(
                getattr(args, "command_timeout_seconds", DEFAULT_COMMAND_TIMEOUT_SECONDS) or DEFAULT_COMMAND_TIMEOUT_SECONDS
            ),
        }
    )


def build_session(args: Any, base_dir: Path, plugin_state: dict[str, Any]) -> DiagnosticSession:
    target_path = resolve_target_path(base_dir, getattr(args, "target_path", None))
    app_kind = detect_app_kind(target_path, getattr(args, "app_kind", None))
    execution_mode = derive_execution_mode(args)
    return DiagnosticSession(
        session_id=make_session_id(),
        started_at=utc_now_iso(),
        root_dir=str(base_dir.resolve()),
        target_path=str(target_path.resolve()),
        app_kind=app_kind,
        execution_mode=execution_mode,
        enabled_plugin_ids=[
            str(item.get("plugin_id"))
            for item in plugin_state.get("active_plugins", [])
            if isinstance(item, dict) and item.get("plugin_id")
        ],
        environment_summary=build_environment_summary(base_dir, target_path, app_kind),
        options=_build_options(args),
        budgets=build_diagnostic_budget(args),
    )


def _maybe_append_default_recommendation(session: DiagnosticSession) -> None:
    if session.recommendations:
        return
    session.add_recommendation(
        Recommendation(
            recommendation_id="runtime.next-step",
            title="Construir collectors y analyzers base",
            rationale="La base diagnóstica ya corre, pero esta ronda aún no trae suficiente especialización en todos los frentes.",
            priority="high",
            source_plugin="runtime",
            actions=[
                "Agregar collectors y analyzers faltantes de acuerdo con el spec.",
                "Usar --support-bundle para revisar el bundle fundacional generado por esta ronda.",
                "Conectar capatch_policy cuando la subparte E materialice sus APIs públicas.",
            ],
        )
    )


def run_session(session: DiagnosticSession, plugin_state: dict[str, Any]) -> DiagnosticSession:
    base_dir = Path(session.root_dir)
    target_path = Path(session.target_path)
    if not target_path.exists():
        session.errors.append(f"Target path no existe: {target_path}")
        session.finish()
        return session

    seed_foundation_artifacts(session, base_dir, target_path, plugin_state=plugin_state)
    include_verify = bool(session.options.get("include_tests")) or bool(session.options.get("include_build"))

    for phase in phase_order_for_mode(session.execution_mode, include_verify=include_verify):
        if phase == "fix":
            gate_payload = evaluate_intervention_gates(session, base_dir)
            session.options["intervention_gates"] = gate_payload
            if session.execution_mode == "apply-fixes" and not gate_payload.get("allow_apply", False):
                session.warnings.append(
                    f"Intervention gates bloquearon apply-fixes: status={gate_payload.get('status')} risk_tier={gate_payload.get('risk_tier')}"
                )
                continue
        run_phase(session, plugin_state, phase)
        if phase == "fix" and session.execution_mode == "apply-fixes":
            session.options["fix_bridge_ran"] = True

    _maybe_append_default_recommendation(session)
    annotate_evidence_graph(session)
    annotate_session_confidence(session, base_dir=base_dir)
    mark_session_noise(session, base_dir=base_dir, target_path=target_path)
    session.finish()
    return session


def run_session_reports(base_dir: Path, session: DiagnosticSession) -> dict[str, Any]:
    written: dict[str, Any] = {}
    written.update(write_session_reports(base_dir, session))
    if bool(session.options.get("support_bundle", False)) or session.execution_mode in {
        "diagnose",
        "collect-only",
        "fix-plan",
        "apply-fixes",
        "support-bundle",
    }:
        written.update(write_support_bundle(base_dir, session, bundle_format=str(session.options.get("bundle_format", "md") or "md")))
    written.update(write_operator_trust_outputs(base_dir, session) or {})
    return written


def run_diagnostic_command(args: Any, *, base_dir: Path, plugin_state: dict[str, Any] | None = None) -> int:
    state = plugin_state or initialize_plugin_runtime(base_dir)
    session = build_session(args, base_dir, state)
    session = run_session(session, state)
    run_session_reports(base_dir, session)
    return 1 if session.errors else 0
