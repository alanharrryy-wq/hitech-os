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

from ._contracts import PLUGIN_PAYLOAD_SCHEMA_VERSION, RUNTIME_PHASES
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
PHASE_TO_PLUGIN_KIND = {
    "resolve-target": "target-detector",
    "collect": "collector",
    "enrich": "context-enricher",
    "analyze": "analyzer",
    "recommend": "recommender",
    "fix": "fixer",
    "verify": "verifier",
    "export": "exporter",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def safe_json(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False)
    except Exception:
        return repr(data)


def _dedupe_strings(values: list[Any]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered


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
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        payload["metadata"] = metadata
        if payload.get("excerpt") is not None:
            payload["excerpt"] = str(payload.get("excerpt"))[:4000]
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
        value.evidence_refs = _dedupe_strings(list(value.evidence_refs or []))
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
        payload.setdefault("detail", str(payload.get("detail") or ""))
        payload.setdefault("source_plugin", plugin_id)
        payload.setdefault("evidence_refs", [])
        payload["evidence_refs"] = _dedupe_strings(list(payload.get("evidence_refs") or []))
        payload.setdefault("probable_causes", [])
        payload.setdefault("tags", [])
        payload.setdefault("metadata", payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})
        payload.setdefault("confidence", float(payload.get("confidence") or 0.0))
        payload.setdefault("confidence_score", payload.get("confidence_score"))
        payload.setdefault("confidence_reason", str(payload.get("confidence_reason") or "plugin payload"))
        payload.setdefault("cross_signal_support", [])
        payload["cross_signal_support"] = _dedupe_strings(list(payload.get("cross_signal_support") or []))
        payload.setdefault("contradictions", [])
        payload["contradictions"] = _dedupe_strings(list(payload.get("contradictions") or []))
        payload["evidence_count"] = len(payload["evidence_refs"])
        return Finding(**payload)
    if isinstance(value, str):
        return Finding(
            finding_id=f"{plugin_id}.finding.{fallback_counter}",
            severity="info",
            category="diagnostics",
            title=f"Finding from {plugin_id}",
            detail=value,
            source_plugin=plugin_id,
            confidence_reason="plugin payload",
        )
    return None


def normalize_recommendation(plugin_id: str, value: Any, fallback_counter: int) -> Recommendation | None:
    if isinstance(value, Recommendation):
        value.priority = normalize_priority(value.priority)
        value.evidence_refs = _dedupe_strings(list(value.evidence_refs or []))
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("recommendation_id", f"{plugin_id}.recommendation.{fallback_counter}")
        payload.setdefault("title", payload.get("title") or f"Recommendation from {plugin_id}")
        payload.setdefault("rationale", str(payload.get("rationale") or ""))
        payload["priority"] = normalize_priority(payload.get("priority"))
        payload.setdefault("source_plugin", plugin_id)
        payload.setdefault("actions", ensure_list(payload.get("actions")))
        payload.setdefault("risks", ensure_list(payload.get("risks")))
        payload.setdefault("prerequisites", ensure_list(payload.get("prerequisites")))
        payload.setdefault("evidence_refs", _dedupe_strings(list(payload.get("evidence_refs") or [])))
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
        metadata = value.metadata if isinstance(value.metadata, dict) else {}
        metadata["evidence_refs"] = _dedupe_strings(list(metadata.get("evidence_refs", []) or []))
        metadata["cross_signal_support"] = _dedupe_strings(list(metadata.get("cross_signal_support", []) or []))
        metadata["contradictions"] = _dedupe_strings(list(metadata.get("contradictions", []) or []))
        value.metadata = metadata
        value.evidence_count = len(metadata["evidence_refs"])
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("proposal_id", f"{plugin_id}.fix.{fallback_counter}")
        payload.setdefault("title", payload.get("title") or f"Fix proposal from {plugin_id}")
        payload.setdefault("rationale", str(payload.get("rationale") or ""))
        payload.setdefault("affected_paths", ensure_list(payload.get("affected_paths")))
        payload.setdefault("commands", ensure_list(payload.get("commands")))
        payload.setdefault("ops_payload", ensure_list(payload.get("ops_payload")))
        payload["risk_level"] = normalize_risk_level(payload.get("risk_level"))
        payload.setdefault("reversible", bool(payload.get("reversible", True)))
        payload.setdefault("verification_steps", ensure_list(payload.get("verification_steps")))
        payload.setdefault("source_plugin", plugin_id)
        metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
        metadata["evidence_refs"] = _dedupe_strings(list(metadata.get("evidence_refs", []) or []))
        metadata["cross_signal_support"] = _dedupe_strings(list(metadata.get("cross_signal_support", []) or []))
        metadata["contradictions"] = _dedupe_strings(list(metadata.get("contradictions", []) or []))
        payload["metadata"] = metadata
        payload["risk_tier"] = normalize_risk_tier(payload.get("risk_tier"))
        payload.setdefault("confidence_score", payload.get("confidence_score"))
        payload.setdefault("confidence_reason", str(payload.get("confidence_reason") or "plugin payload"))
        payload["evidence_count"] = len(metadata["evidence_refs"])
        payload.setdefault("cross_signal_support", metadata["cross_signal_support"])
        payload.setdefault("contradictions", metadata["contradictions"])
        payload.setdefault("applicability_predicates", ensure_list(payload.get("applicability_predicates")))
        payload.setdefault("rollback_recipe", ensure_list(payload.get("rollback_recipe")))
        payload.setdefault("verification_recipe", ensure_list(payload.get("verification_recipe")))
        payload.setdefault("family", str(payload.get("family") or "general"))
        return FixProposal(**payload)
    return None


def normalize_verification(plugin_id: str, value: Any, fallback_counter: int) -> VerificationResult | None:
    if isinstance(value, VerificationResult):
        value.evidence_refs = _dedupe_strings(list(value.evidence_refs or []))
        value.severity_if_failed = normalize_severity(value.severity_if_failed, default="error")
        return value
    if isinstance(value, dict):
        payload = dict(value)
        payload.setdefault("verifier_id", f"{plugin_id}.verification.{fallback_counter}")
        payload.setdefault("ok", bool(payload.get("ok", True)))
        payload.setdefault("title", payload.get("title") or f"Verification from {plugin_id}")
        payload.setdefault("detail", str(payload.get("detail") or ""))
        payload.setdefault("source_plugin", plugin_id)
        payload.setdefault("evidence_refs", _dedupe_strings(list(payload.get("evidence_refs") or [])))
        payload.setdefault("metrics", payload.get("metrics") if isinstance(payload.get("metrics"), dict) else {})
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


def _plugin_manifest(plugin_state: dict[str, Any], plugin_id: str) -> dict[str, Any]:
    manifests = plugin_state.get("manifests")
    if isinstance(manifests, dict):
        payload = manifests.get(plugin_id)
        if isinstance(payload, dict):
            return payload
    return {}


def validate_plugin_payload(plugin_state: dict[str, Any], plugin_id: str, phase: str, result: Any) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    if result is None:
        return {
            "plugin_id": plugin_id,
            "plugin_kind": PHASE_TO_PLUGIN_KIND[phase],
            "plugin_phase": phase,
            "schema_version": PLUGIN_PAYLOAD_SCHEMA_VERSION,
        }, warnings
    if not isinstance(result, dict):
        return {
            "plugin_id": plugin_id,
            "plugin_kind": PHASE_TO_PLUGIN_KIND[phase],
            "plugin_phase": phase,
            "schema_version": PLUGIN_PAYLOAD_SCHEMA_VERSION,
            "raw_payload_type": type(result).__name__,
        }, warnings
    payload = dict(result)
    manifest = _plugin_manifest(plugin_state, plugin_id)
    declared_kind = str(payload.get("plugin_kind") or manifest.get("plugin_kind") or PHASE_TO_PLUGIN_KIND[phase]).strip()
    declared_phase = str(payload.get("plugin_phase") or phase).strip()
    if declared_phase != phase:
        warnings.append(f"plugin_phase ajustado de {declared_phase!r} a {phase!r}")
    payload["plugin_id"] = plugin_id
    payload["plugin_kind"] = declared_kind
    payload["plugin_phase"] = phase
    payload["schema_version"] = str(payload.get("schema_version") or PLUGIN_PAYLOAD_SCHEMA_VERSION)
    if payload["schema_version"] != PLUGIN_PAYLOAD_SCHEMA_VERSION:
        warnings.append(
            f"schema_version {payload['schema_version']!r} incompatible; se normaliza a {PLUGIN_PAYLOAD_SCHEMA_VERSION!r}"
        )
        payload["schema_version"] = PLUGIN_PAYLOAD_SCHEMA_VERSION
    for key in ["artifacts", "findings", "recommendations", "fixes", "verification_results"]:
        if key in payload and payload[key] is not None and not isinstance(payload[key], list):
            payload[key] = ensure_list(payload[key])
            warnings.append(f"{key} normalizado a lista")
    if "skip_reason" in payload and payload.get("skip_reason") is not None:
        payload["skip_reason"] = trim_text(payload.get("skip_reason"))
    if "summary" in payload and payload.get("summary") is not None:
        payload["summary"] = trim_text(payload.get("summary"))
    metadata = payload.get("metadata")
    if metadata is None:
        payload["metadata"] = {}
    elif not isinstance(metadata, dict):
        payload["metadata"] = {"raw_metadata": safe_json(metadata)}
        warnings.append("metadata normalizado a mapping")
    return payload, warnings


def _attach_default_evidence(produced_artifact_ids: list[str], *, finding: Finding | None = None, recommendation: Recommendation | None = None, fix: FixProposal | None = None, verification: VerificationResult | None = None) -> None:
    refs = _dedupe_strings(produced_artifact_ids)
    if finding is not None and not finding.evidence_refs:
        finding.evidence_refs = refs
        finding.evidence_count = len(refs)
    if recommendation is not None and not recommendation.evidence_refs:
        recommendation.evidence_refs = refs
    if verification is not None and not verification.evidence_refs:
        verification.evidence_refs = refs
    if fix is not None:
        metadata = fix.metadata if isinstance(fix.metadata, dict) else {}
        if not metadata.get("evidence_refs"):
            metadata["evidence_refs"] = refs
            fix.metadata = metadata
            fix.evidence_count = len(refs)


def _summarize_record(record: PluginExecutionRecord, payload: dict[str, Any] | None = None) -> str:
    if payload and payload.get("skip_reason"):
        return f"skip_reason={payload['skip_reason']}"
    parts: list[str] = []
    if record.produced_artifacts:
        parts.append(f"artifacts={len(record.produced_artifacts)}")
    if record.produced_findings:
        parts.append(f"findings={len(record.produced_findings)}")
    if record.produced_recommendations:
        parts.append(f"recommendations={len(record.produced_recommendations)}")
    if record.produced_fixes:
        parts.append(f"fixes={len(record.produced_fixes)}")
    if record.produced_verifications:
        parts.append(f"verifications={len(record.produced_verifications)}")
    return " | ".join(parts) if parts else record.summary


def ingest_callback_output(session: DiagnosticSession, plugin_state: dict[str, Any], phase: str, plugin_id: str, result: Any, record: PluginExecutionRecord) -> None:
    if result is None:
        return
    payload_dict, payload_warnings = validate_plugin_payload(plugin_state, plugin_id, phase, result)
    for warning in payload_warnings:
        session.warnings.append(f"{plugin_id}: {warning}")
    if isinstance(result, dict):
        result = payload_dict
    produced_artifact_ids: list[str] = []

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
                    produced_artifact_ids.append(artifact.artifact_id)
        if "findings" in result:
            for index, item in enumerate(ensure_list(result.get("findings")), start=1):
                finding = normalize_finding(plugin_id, item, index)
                if finding:
                    _attach_default_evidence(produced_artifact_ids, finding=finding)
                    session.add_finding(finding)
                    record.produced_findings.append(finding.finding_id)
        if "recommendations" in result:
            for index, item in enumerate(ensure_list(result.get("recommendations")), start=1):
                recommendation = normalize_recommendation(plugin_id, item, index)
                if recommendation:
                    _attach_default_evidence(produced_artifact_ids, recommendation=recommendation)
                    session.add_recommendation(recommendation)
                    record.produced_recommendations.append(recommendation.recommendation_id)
        if "fixes" in result:
            for index, item in enumerate(ensure_list(result.get("fixes")), start=1):
                fix = normalize_fix(plugin_id, item, index)
                if fix:
                    _attach_default_evidence(produced_artifact_ids, fix=fix)
                    session.add_fix(fix)
                    record.produced_fixes.append(fix.proposal_id)
        if "verification_results" in result:
            for index, item in enumerate(ensure_list(result.get("verification_results")), start=1):
                verification = normalize_verification(plugin_id, item, index)
                if verification:
                    _attach_default_evidence(produced_artifact_ids, verification=verification)
                    session.add_verification(verification)
                    record.produced_verifications.append(verification.verifier_id)
        if result.get("summary"):
            record.summary = trim_text(result.get("summary"))
        elif result.get("skip_reason"):
            record.summary = f"skip_reason={trim_text(result.get('skip_reason'))}"
        record.summary = _summarize_record(record, payload=result)
        return

    if isinstance(result, list):
        for index, item in enumerate(result, start=1):
            artifact = normalize_artifact(plugin_id, item, index)
            if artifact:
                session.add_artifact(artifact, phase=phase)
                record.produced_artifacts.append(artifact.artifact_id)
                produced_artifact_ids.append(artifact.artifact_id)
                continue
            finding = normalize_finding(plugin_id, item, index)
            if finding:
                _attach_default_evidence(produced_artifact_ids, finding=finding)
                session.add_finding(finding)
                record.produced_findings.append(finding.finding_id)
                continue
            recommendation = normalize_recommendation(plugin_id, item, index)
            if recommendation:
                _attach_default_evidence(produced_artifact_ids, recommendation=recommendation)
                session.add_recommendation(recommendation)
                record.produced_recommendations.append(recommendation.recommendation_id)
                continue
        record.summary = _summarize_record(record)
        return

    finding = normalize_finding(plugin_id, result, 1)
    if finding:
        _attach_default_evidence(produced_artifact_ids, finding=finding)
        session.add_finding(finding)
        record.produced_findings.append(finding.finding_id)
        record.summary = _summarize_record(record)


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
    if record.summary:
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
                base_dir=Path(session.root_dir),
                target_path=Path(session.target_path),
                plugin_state=plugin_state,
                capability_map=plugin_state.get("capability_map", {}),
                artifacts=session.artifacts,
                findings=session.findings,
                recommendations=session.recommendations,
                fix_proposals=session.fix_proposals,
                verification_results=session.verification_results,
                options=session.options,
                budgets=session.budgets,
                environment_summary=session.environment_summary,
            )
            ingest_callback_output(session, plugin_state, phase, plugin_id, result, record)
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

    capability_map = plugin_state.get("capability_map") if isinstance(plugin_state.get("capability_map"), dict) else {}
    runtime_status = plugin_state.get("runtime_status") if isinstance(plugin_state.get("runtime_status"), dict) else {}
    session.add_artifact(
        DiagnosticArtifact(
            artifact_id="runtime.plugin-capability-map",
            category="diagnostics",
            source_plugin="runtime",
            summary="Mapa real de capacidades del runtime y coverage por fase.",
            mime_type="application/json",
            metadata=capability_map,
            excerpt=safe_json(capability_map)[:3000],
        ),
        phase="resolve-target",
    )
    session.add_artifact(
        DiagnosticArtifact(
            artifact_id="runtime.plugin-runtime-status",
            category="diagnostics",
            source_plugin="runtime",
            summary="Estado real del loader de plugins: activos, rechazados, duplicados y disabled.",
            mime_type="application/json",
            metadata=runtime_status,
            excerpt=safe_json(runtime_status)[:1500],
        ),
        phase="resolve-target",
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
