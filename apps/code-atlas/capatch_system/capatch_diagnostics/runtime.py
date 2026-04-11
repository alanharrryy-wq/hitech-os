from __future__ import annotations

"""API pública del dominio capatch_diagnostics."""

from pathlib import Path
from typing import Any

from plugin_lib.redaction_utils import redact_mapping

from capatch_policy.confidence import annotate_session_confidence
from capatch_policy.decision_ledger import write_operator_trust_outputs
from capatch_policy.intervention import evaluate_intervention_gates

from ._contracts import DEFAULT_COMMAND_TIMEOUT_SECONDS, DEFAULT_REPORT_BUNDLE_FORMAT, RUNTIME_PROFILES
from .budgets import build_diagnostic_budget
from .evidence_graph import annotate_evidence_graph
from .loader import initialize_plugin_runtime, normalize_plugin_state
from .noise_filters import mark_session_noise
from .phase_runner import phase_order_for_mode, run_phase, seed_foundation_artifacts
from .reporting import write_session_reports, write_support_bundle
from .session import DiagnosticSession, Recommendation, make_session_id, utc_now_iso
from .targeting import build_environment_summary, detect_app_kind, resolve_target_path


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


def _select_runtime_profile(execution_mode: str) -> tuple[str, list[str]]:
    if execution_mode == "apply-fixes":
        return "full", list(RUNTIME_PROFILES["full"])
    return "diagnostic", list(RUNTIME_PROFILES["diagnostic"])


def _build_options(args: Any, *, execution_mode: str) -> dict[str, Any]:
    profile_name, components = _select_runtime_profile(execution_mode)
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
            "runtime_profile_name": profile_name,
            "runtime_profile_components": components,
            "execution_mode": execution_mode,
        }
    )


def build_session(args: Any, base_dir: Path, plugin_state: dict[str, Any]) -> DiagnosticSession:
    normalized_state = normalize_plugin_state(plugin_state, base_dir=base_dir)
    target_path = resolve_target_path(base_dir, getattr(args, "target_path", None))
    app_kind = detect_app_kind(target_path, getattr(args, "app_kind", None))
    execution_mode = derive_execution_mode(args)
    environment_summary = build_environment_summary(base_dir, target_path, app_kind, plugin_state=normalized_state)
    environment_summary["plugin_runtime"] = redact_mapping(
        {
            "runtime_status": normalized_state.get("runtime_status", {}),
            "capability_map": normalized_state.get("capability_map", {}),
        }
    )
    return DiagnosticSession(
        session_id=make_session_id(),
        started_at=utc_now_iso(),
        root_dir=str(base_dir.resolve()),
        target_path=str(target_path.resolve()),
        app_kind=app_kind,
        execution_mode=execution_mode,
        enabled_plugin_ids=[
            str(item.get("plugin_id"))
            for item in normalized_state.get("active_plugins", [])
            if isinstance(item, dict) and item.get("plugin_id")
        ],
        environment_summary=environment_summary,
        options=_build_options(args, execution_mode=execution_mode),
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
    plugin_state = normalize_plugin_state(plugin_state, base_dir=base_dir)
    session.options["plugin_runtime_status"] = redact_mapping(plugin_state.get("runtime_status", {}))
    session.options["plugin_capability_map"] = redact_mapping(plugin_state.get("capability_map", {}))
    if not target_path.exists():
        session.errors.append(f"Target path no existe: {target_path}")
        session.finish()
        return session

    seed_foundation_artifacts(session, base_dir, target_path, plugin_state=plugin_state)
    include_verify = bool(session.options.get("include_tests")) or bool(session.options.get("include_build"))

    runtime_status = plugin_state.get("runtime_status") if isinstance(plugin_state.get("runtime_status"), dict) else {}
    if runtime_status.get("rejected_plugins"):
        session.warnings.append(
            f"Plugin runtime degradado: rejected_plugins={runtime_status.get('rejected_plugins')}"
        )

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
    _finalize_autofix_session_state(session)
    session.finish()
    return session


def _finalize_autofix_session_state(session: DiagnosticSession) -> None:
    bridge_results = list((session.options or {}).get('autofix_bridge_results') or [])
    if session.execution_mode != 'apply-fixes':
        return
    if not bridge_results:
        return
    failed = [f"{item.get('proposal_id')}:{item.get('execution_status')}" for item in bridge_results if not bool(item.get('execution_ok', False))]
    applied = [item for item in bridge_results if item.get('execution_status') == 'applied']
    if failed:
        session.errors.append('Autofix Bridge failures: ' + ', '.join(failed))
    elif not applied:
        session.warnings.append('Apply-fixes terminó sin cambios efectivos del Autofix Bridge.')


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
    state = normalize_plugin_state(plugin_state, base_dir=base_dir) if plugin_state else initialize_plugin_runtime(base_dir)
    session = build_session(args, base_dir, state)
    session = run_session(session, state)
    run_session_reports(base_dir, session)
    return 1 if session.errors else 0
