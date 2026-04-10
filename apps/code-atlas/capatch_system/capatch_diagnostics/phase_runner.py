from __future__ import annotations

"""Phase runner y normalización de outputs de plugins."""

import inspect
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from plugin_lib.fs_utils import list_files_limited, safe_file_size
from plugin_lib.log_utils import summarize_candidate_logs, tail_file_text
from plugin_lib.redaction_utils import redact_mapping

from ._contracts import RUNTIME_PHASES
from .normalization import ensure_list, normalize_priority, normalize_risk_level, normalize_risk_tier, normalize_severity, trim_text
from .session import (
    DiagnosticArtifact,
    DiagnosticSession,
    Finding,
    FixProposal,
    PluginExecutionRecord,
    Recommendation,
    VerificationResult,
)

Callback = Callable[..., Any]
PHASE_TO_STATE_KEY = {
    "resolve-target": "target_detectors",
    "collect": "collectors",
    "enrich": "context_enrichers",
    "analyze": "analyzers",
    "recommend": "recommenders",
    "fix": "fixers",
    "verify": "verifiers",
    "export": "exporters",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_json(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return repr(data)


def state_callbacks(plugin_state: dict[str, Any], key: str) -> list[dict[str, Any]]:
    raw = plugin_state.get(key, [])
    if not isinstance(raw, list):
        return []
    cleaned: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        if "plugin_id" not in item or "func" not in item:
            continue
        cleaned.append(item)
    return cleaned


def call_callback(func: Callback, **payload: Any) -> Any:
    signature = inspect.signature(func)
    accepted: dict[str, Any] = {}
    accepts_kwargs = False
    for parameter in signature.parameters.values():
        if parameter.kind == inspect.Parameter.VAR_KEYWORD:
            accepts_kwargs = True
            continue
        if parameter.kind in {inspect.Parameter.VAR_POSITIONAL}:
            continue
        if parameter.name in payload:
            accepted[parameter.name] = payload[parameter.name]
    if accepts_kwargs:
        accepted = payload
    return func(**accepted)


def normalize_artifact(plugin_id: str, value: Any, fallback_counter: int) -> DiagnosticArtifact | None:
    if isinstance(value, DiagnosticArtifact):
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("artifact_id", f"{plugin_id}.artifact.{fallback_counter}")
        payload.setdefault("category", "diagnostics")
        payload.setdefault("source_plugin", plugin_id)
        payload.setdefault("summary", "")
        return DiagnosticArtifact(**payload)
    if isinstance(value, (str, Path)):
        return DiagnosticArtifact(
            artifact_id=f"{plugin_id}.artifact.{fallback_counter}",
            category="diagnostics",
            source_plugin=plugin_id,
            path=str(value),
            summary=str(value),
        )
    return None


def normalize_finding(plugin_id: str, value: Any, fallback_counter: int) -> Finding | None:
    if isinstance(value, Finding):
        value.severity = normalize_severity(value.severity)
        if value.confidence_score is None:
            value.confidence_score = value.confidence
        if not value.confidence_reason:
            value.confidence_reason = "plugin payload"
        value.evidence_count = len(value.evidence_refs or [])
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("finding_id", f"{plugin_id}.finding.{fallback_counter}")
        payload["severity"] = normalize_severity(payload.get("severity"))
        payload.setdefault("category", "diagnostics")
        payload.setdefault("title", payload.get("title") or f"Finding from {plugin_id}")
        payload.setdefault("detail", payload.get("detail") or "")
        payload.setdefault("source_plugin", plugin_id)
        payload.setdefault("confidence_score", payload.get("confidence", 0.0))
        payload.setdefault("confidence_reason", payload.get("confidence_reason") or "plugin payload")
        payload.setdefault("evidence_count", len(payload.get("evidence_refs") or []))
        return Finding(**payload)
    if isinstance(value, str):
        return Finding(
            finding_id=f"{plugin_id}.finding.{fallback_counter}",
            severity="info",
            category="note",
            title=f"Finding from {plugin_id}",
            detail=value,
            source_plugin=plugin_id,
            confidence_score=0.0,
            confidence_reason="string payload",
        )
    return None


def normalize_recommendation(plugin_id: str, value: Any, fallback_counter: int) -> Recommendation | None:
    if isinstance(value, Recommendation):
        value.priority = normalize_priority(value.priority)
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("recommendation_id", f"{plugin_id}.recommendation.{fallback_counter}")
        payload.setdefault("title", payload.get("title") or f"Recommendation from {plugin_id}")
        payload.setdefault("rationale", payload.get("rationale") or "")
        payload.setdefault("source_plugin", plugin_id)
        payload["priority"] = normalize_priority(payload.get("priority"))
        return Recommendation(**payload)
    if isinstance(value, str):
        return Recommendation(
            recommendation_id=f"{plugin_id}.recommendation.{fallback_counter}",
            title=f"Recommendation from {plugin_id}",
            rationale=value,
            source_plugin=plugin_id,
        )
    return None


def normalize_fix(plugin_id: str, value: Any, fallback_counter: int) -> FixProposal | None:
    if isinstance(value, FixProposal):
        value.risk_level = normalize_risk_level(value.risk_level)
        value.risk_tier = normalize_risk_tier(value.risk_tier)
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("proposal_id", f"{plugin_id}.fix.{fallback_counter}")
        payload.setdefault("title", payload.get("title") or f"Fix proposal from {plugin_id}")
        payload.setdefault("rationale", payload.get("rationale") or "")
        payload.setdefault("source_plugin", plugin_id)
        payload["risk_level"] = normalize_risk_level(payload.get("risk_level"))
        payload["risk_tier"] = normalize_risk_tier(payload.get("risk_tier"))
        payload.setdefault("confidence_reason", payload.get("confidence_reason") or "plugin payload")
        payload.setdefault("evidence_count", len(payload.get("metadata", {}).get("evidence_refs", [])) if isinstance(payload.get("metadata"), dict) else 0)
        payload.setdefault("family", payload.get("family") or "general")
        return FixProposal(**payload)
    return None


def normalize_verification(plugin_id: str, value: Any, fallback_counter: int) -> VerificationResult | None:
    if isinstance(value, VerificationResult):
        value.severity_if_failed = normalize_severity(value.severity_if_failed, default="error")
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("verifier_id", f"{plugin_id}.verification.{fallback_counter}")
        payload.setdefault("ok", bool(payload.get("ok", True)))
        payload.setdefault("title", payload.get("title") or f"Verification from {plugin_id}")
        payload.setdefault("detail", payload.get("detail") or "")
        payload.setdefault("source_plugin", plugin_id)
        payload["severity_if_failed"] = normalize_severity(payload.get("severity_if_failed"), default="error")
        payload.setdefault("verification_class", payload.get("verification_class") or "diagnostic")
        return VerificationResult(**payload)
    if isinstance(value, str):
        return VerificationResult(
            verifier_id=f"{plugin_id}.verification.{fallback_counter}",
            ok=True,
            title=f"Verification from {plugin_id}",
            detail=value,
            source_plugin=plugin_id,
        )
    return None


def ingest_callback_output(session: DiagnosticSession, phase: str, plugin_id: str, result: Any, record: PluginExecutionRecord) -> None:
    if result is None:
        return
    if isinstance(result, dict):
        if result.get("warning"):
            session.warnings.append(f"{plugin_id}: {result['warning']}")
        if result.get("error"):
            session.errors.append(f"{plugin_id}: {result['error']}")
        if "artifacts" in result:
            for index, item in enumerate(ensure_list(result.get("artifacts")), start=1):
                artifact = normalize_artifact(plugin_id, item, index)
                if artifact:
                    session.add_artifact(artifact, phase=phase)
                    record.produced_artifacts.append(artifact.artifact_id)
        if "findings" in result:
            for index, item in enumerate(ensure_list(result.get("findings")), start=1):
                finding = normalize_finding(plugin_id, item, index)
                if finding:
                    session.add_finding(finding)
                    record.produced_findings.append(finding.finding_id)
        if "recommendations" in result:
            for index, item in enumerate(ensure_list(result.get("recommendations")), start=1):
                recommendation = normalize_recommendation(plugin_id, item, index)
                if recommendation:
                    session.add_recommendation(recommendation)
                    record.produced_recommendations.append(recommendation.recommendation_id)
        if "fixes" in result:
            for index, item in enumerate(ensure_list(result.get("fixes")), start=1):
                fix = normalize_fix(plugin_id, item, index)
                if fix:
                    session.add_fix(fix)
                    record.produced_fixes.append(fix.proposal_id)
        if "verification_results" in result:
            for index, item in enumerate(ensure_list(result.get("verification_results")), start=1):
                verification = normalize_verification(plugin_id, item, index)
                if verification:
                    session.add_verification(verification)
                    record.produced_verifications.append(verification.verifier_id)
        if result.get("summary"):
            record.summary = trim_text(result.get("summary"))
        return

    if isinstance(result, list):
        for index, item in enumerate(result, start=1):
            artifact = normalize_artifact(plugin_id, item, index)
            if artifact:
                session.add_artifact(artifact, phase=phase)
                record.produced_artifacts.append(artifact.artifact_id)
        return

    finding = normalize_finding(plugin_id, result, 1)
    if finding:
        session.add_finding(finding)
        record.produced_findings.append(finding.finding_id)


def _ensure_stub_trace(session: DiagnosticSession, phase: str, plugin_id: str, record: PluginExecutionRecord) -> None:
    produced_anything = any(
        [
            record.produced_artifacts,
            record.produced_findings,
            record.produced_recommendations,
            record.produced_fixes,
            record.produced_verifications,
        ]
    )
    if produced_anything:
        if not record.summary:
            record.summary = "plugin ejecutado con payload normalizado"
        return

    stub_finding = Finding(
        finding_id=f"{plugin_id}.stub.{phase}",
        severity="info",
        category="diagnostics",
        title=f"{plugin_id} ejecutó fase {phase} sin payload persistido",
        detail="Se conserva execution record para cumplir la regla de stubs del runtime diagnóstico.",
        source_plugin=plugin_id,
        confidence_score=0.0,
        confidence_reason="stub automático",
    )
    session.add_finding(stub_finding)
    record.produced_findings.append(stub_finding.finding_id)
    if not record.summary:
        record.summary = "skip_reason=plugin no produjo artifacts/findings/recommendations/fixes/verifications"


def run_phase(session: DiagnosticSession, plugin_state: dict[str, Any], phase: str) -> None:
    state_key = PHASE_TO_STATE_KEY[phase]
    callbacks = state_callbacks(plugin_state, state_key)
    for item in callbacks:
        plugin_id = str(item["plugin_id"])
        func = item["func"]
        started_perf = time.perf_counter()
        started_at = utc_now()
        record = PluginExecutionRecord(
            plugin_id=plugin_id,
            phase=phase,
            ok=True,
            started_at=started_at,
            ended_at=started_at,
            duration_ms=0,
        )
        try:
            result = call_callback(
                func,
                session=session,
                phase=phase,
                artifacts=session.artifacts,
                findings=session.findings,
                recommendations=session.recommendations,
                fix_proposals=session.fix_proposals,
                verification_results=session.verification_results,
                options=session.options,
                budgets=session.budgets,
            )
            ingest_callback_output(session, phase, plugin_id, result, record)
        except Exception as exc:
            record.ok = False
            record.error = f"{type(exc).__name__}: {exc}"
            session.errors.append(f"{plugin_id} ({phase}): {record.error}")
        finally:
            ended_at = utc_now()
            record.ended_at = ended_at
            record.duration_ms = int((time.perf_counter() - started_perf) * 1000)
            _ensure_stub_trace(session, phase, plugin_id, record)
            session.add_record(record)


def seed_foundation_artifacts(session: DiagnosticSession, base_dir: Path, target_path: Path, *, plugin_state: dict[str, Any]) -> None:
    inventory = redact_mapping(session.environment_summary)
    session.add_artifact(
        DiagnosticArtifact(
            artifact_id="runtime.environment-summary",
            category="diagnostics",
            source_plugin="runtime",
            summary="Resumen inicial del host, target y herramientas disponibles.",
            mime_type="application/json",
            metadata=inventory,
            excerpt=safe_json(inventory)[:2000],
        ),
        phase="collect",
    )

    if target_path.exists() and target_path.is_dir():
        top_files = list_files_limited(target_path, limit=40)
        session.add_artifact(
            DiagnosticArtifact(
                artifact_id="runtime.target-topology",
                category="system",
                source_plugin="runtime",
                summary="Primer vistazo del target path con archivos/carpetas relevantes.",
                mime_type="application/json",
                metadata={"items": top_files},
                excerpt=safe_json(top_files)[:2000],
            ),
            phase="collect",
        )

        candidate_logs = summarize_candidate_logs(target_path)
        if candidate_logs:
            session.add_artifact(
                DiagnosticArtifact(
                    artifact_id="runtime.log-candidates",
                    category="logs",
                    source_plugin="runtime",
                    summary="Candidatos de logs detectados por heurística base.",
                    mime_type="application/json",
                    metadata={"items": candidate_logs},
                    excerpt=safe_json(candidate_logs)[:2000],
                ),
                phase="collect",
            )
            first_existing = next((Path(item["path"]) for item in candidate_logs if Path(item["path"]).exists()), None)
            if first_existing:
                excerpt = tail_file_text(
                    first_existing,
                    max_lines=session.budgets.max_log_lines,
                    max_bytes=session.budgets.max_log_bytes,
                )
                session.add_artifact(
                    DiagnosticArtifact(
                        artifact_id="runtime.log-tail-sample",
                        category="logs",
                        source_plugin="runtime",
                        summary=f"Tail base del log detectado: {first_existing.name}",
                        path=str(first_existing),
                        bytes=safe_file_size(first_existing),
                        excerpt=excerpt,
                    ),
                    phase="collect",
                )

    if not state_callbacks(plugin_state, "collectors"):
        session.warnings.append(
            "Diagnostic Runtime v6 scaffold activo, pero aún no hay collectors especializados registrados."
        )


def phase_order_for_mode(execution_mode: str, include_verify: bool = False) -> list[str]:
    order: list[str] = ["resolve-target"]
    if execution_mode != "verify-only":
        order.extend(["collect", "enrich"])
        if execution_mode != "collect-only":
            order.extend(["analyze", "recommend"])
            if execution_mode in {"fix-plan", "apply-fixes"}:
                order.append("fix")
    if execution_mode in {"verify-only", "diagnose", "apply-fixes"} or include_verify:
        order.append("verify")
    order.append("export")
    return [phase for phase in RUNTIME_PHASES if phase in order]
