from __future__ import annotations

"""Modelos canónicos de la sesión diagnóstica para Fase 0 / ownership D."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._contracts import (
    DEFAULT_MAX_ARTIFACT_FILES,
    DEFAULT_MAX_LOG_BYTES,
    DEFAULT_MAX_LOG_LINES,
    DEFAULT_MAX_TAIL_FILES,
)
from .normalization import normalize_jsonable


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


@dataclass(slots=True)
class DiagnosticBudget:
    max_log_lines: int = DEFAULT_MAX_LOG_LINES
    max_log_bytes: int = DEFAULT_MAX_LOG_BYTES
    max_artifact_files: int = DEFAULT_MAX_ARTIFACT_FILES
    max_tail_files: int = DEFAULT_MAX_TAIL_FILES

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class DiagnosticArtifact:
    artifact_id: str
    category: str
    source_plugin: str
    path: str | None = None
    mime_type: str = "text/plain"
    bytes: int | None = None
    created_at: str = field(default_factory=utc_now_iso)
    retention_policy: str = "session"
    is_sensitive: bool = False
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    excerpt: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class Finding:
    finding_id: str
    severity: str
    category: str
    title: str
    detail: str
    evidence_refs: list[str] = field(default_factory=list)
    probable_causes: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source_plugin: str = "runtime"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence_score: float | None = None
    confidence_reason: str = ""
    evidence_count: int = 0
    cross_signal_support: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class Recommendation:
    recommendation_id: str
    title: str
    rationale: str
    priority: str = "normal"
    source_plugin: str = "runtime"
    actions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class FixProposal:
    proposal_id: str
    title: str
    rationale: str
    affected_paths: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    ops_payload: list[dict[str, Any]] = field(default_factory=list)
    risk_level: str = "low"
    reversible: bool = True
    verification_steps: list[str] = field(default_factory=list)
    source_plugin: str = "runtime"
    metadata: dict[str, Any] = field(default_factory=dict)
    risk_tier: str = "guarded"
    confidence_score: float | None = None
    confidence_reason: str = ""
    evidence_count: int = 0
    cross_signal_support: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    applicability_predicates: list[dict[str, Any]] = field(default_factory=list)
    rollback_recipe: list[dict[str, Any]] = field(default_factory=list)
    verification_recipe: list[dict[str, Any]] = field(default_factory=list)
    family: str = "general"

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class VerificationResult:
    verifier_id: str
    ok: bool
    title: str
    detail: str
    source_plugin: str = "runtime"
    checked_at: str = field(default_factory=utc_now_iso)
    evidence_refs: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    severity_if_failed: str = "error"
    verification_class: str = "diagnostic"

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class PluginExecutionRecord:
    plugin_id: str
    phase: str
    ok: bool
    started_at: str
    ended_at: str
    duration_ms: int
    summary: str = ""
    error: str | None = None
    produced_artifacts: list[str] = field(default_factory=list)
    produced_findings: list[str] = field(default_factory=list)
    produced_recommendations: list[str] = field(default_factory=list)
    produced_fixes: list[str] = field(default_factory=list)
    produced_verifications: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


@dataclass(slots=True)
class DiagnosticSession:
    session_id: str
    started_at: str
    root_dir: str
    target_path: str
    app_kind: str
    execution_mode: str
    enabled_plugin_ids: list[str] = field(default_factory=list)
    environment_summary: dict[str, Any] = field(default_factory=dict)
    artifacts: list[DiagnosticArtifact] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    fix_proposals: list[FixProposal] = field(default_factory=list)
    verification_results: list[VerificationResult] = field(default_factory=list)
    execution_records: list[PluginExecutionRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    options: dict[str, Any] = field(default_factory=dict)
    budgets: DiagnosticBudget = field(default_factory=DiagnosticBudget)
    artifacts_by_phase: dict[str, list[str]] = field(default_factory=dict)
    finished_at: str | None = None

    def add_artifact(self, artifact: DiagnosticArtifact, phase: str | None = None) -> None:
        self.artifacts.append(artifact)
        if phase:
            self.artifacts_by_phase.setdefault(phase, []).append(artifact.artifact_id)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def add_recommendation(self, recommendation: Recommendation) -> None:
        self.recommendations.append(recommendation)

    def add_fix(self, fix: FixProposal) -> None:
        self.fix_proposals.append(fix)

    def add_verification(self, verification: VerificationResult) -> None:
        self.verification_results.append(verification)

    def add_record(self, record: PluginExecutionRecord) -> None:
        self.execution_records.append(record)

    def finish(self) -> None:
        self.finished_at = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        return normalize_jsonable(self)


def make_session_id(prefix: str = "diag") -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}"


def to_jsonable(value: Any) -> Any:
    return normalize_jsonable(value)
