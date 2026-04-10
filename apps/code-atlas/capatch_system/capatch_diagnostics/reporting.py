from __future__ import annotations

"""Reporting y persistencia del runtime diagnóstico."""

import json
from pathlib import Path
from typing import Any

from plugin_lib.fs_utils import atomic_write_text, ensure_dir
from plugin_lib.redaction_utils import redact_text

from ._contracts import MANDATORY_OUTPUT_FILES, REPORT_DIRS
from .session import DiagnosticSession, to_jsonable


CANONICAL_DIR_KEYS = {
    "reports/diagnostics": "diagnostics_dir",
    "reports/findings": "findings_dir",
    "reports/verification": "verification_dir",
    "reports/bundles": "bundles_dir",
    "reports/telemetry": "telemetry_dir",
    "reports/confidence": "confidence_dir",
    "reports/decision_ledger": "decision_ledger_dir",
    "reports/patch_history": "patch_history_dir",
    "reports/patch_runs": "patch_runs_dir",
    "reports/checkpoints": "checkpoints_dir",
    "reports/rollback": "rollback_dir",
    "reports/baselines": "baselines_dir",
    "reports/cache": "cache_dir",
}


def ensure_report_dirs(base_dir: Path) -> dict[str, Path]:
    reports_root = ensure_dir(base_dir / "reports")
    mapping: dict[str, Path] = {"reports_root": reports_root}
    for relative in REPORT_DIRS:
        path_value = ensure_dir(base_dir / relative)
        mapping[CANONICAL_DIR_KEYS.get(relative, relative.replace("/", "_") + "_dir")] = path_value
    mapping["tmp_dir"] = ensure_dir(base_dir / "tmp")
    return mapping


def write_json(path_value: Path, payload: Any) -> None:
    text = json.dumps(to_jsonable(payload), indent=2, ensure_ascii=False)
    atomic_write_text(path_value, text + "\n")


def render_session_markdown(session: DiagnosticSession) -> str:
    lines: list[str] = []
    lines.append(f"# Diagnostic Session {session.session_id}")
    lines.append("")
    lines.append(f"- started_at: `{session.started_at}`")
    lines.append(f"- finished_at: `{session.finished_at or 'pending'}`")
    lines.append(f"- execution_mode: `{session.execution_mode}`")
    lines.append(f"- target_path: `{session.target_path}`")
    lines.append(f"- app_kind: `{session.app_kind}`")
    lines.append(f"- enabled_plugins: `{len(session.enabled_plugin_ids)}`")
    lines.append("")
    lines.append("## Environment summary")
    lines.append("")
    for key, value in sorted(session.environment_summary.items()):
        rendered = json.dumps(to_jsonable(value), ensure_ascii=False)
        lines.append(f"- **{key}**: `{rendered}`")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    if not session.artifacts:
        lines.append("- No artifacts yet.")
    else:
        for artifact in session.artifacts:
            lines.append(
                f"- `{artifact.artifact_id}` [{artifact.category}] via `{artifact.source_plugin}`"
                + (f" -> `{artifact.path}`" if artifact.path else "")
                + (f" | {artifact.summary}" if artifact.summary else "")
            )
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    if not session.findings:
        lines.append("- No findings.")
    else:
        for finding in session.findings:
            score = finding.confidence_score if finding.confidence_score is not None else finding.confidence
            lines.append(
                f"- **{finding.severity.upper()}** `{finding.finding_id}` {finding.title}"
                f" | confidence={float(score or 0.0):.2f} | via `{finding.source_plugin}`"
            )
            if finding.detail:
                lines.append(f"  - {finding.detail}")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    if not session.recommendations:
        lines.append("- No recommendations.")
    else:
        for recommendation in session.recommendations:
            lines.append(f"- `{recommendation.recommendation_id}` {recommendation.title}")
            if recommendation.actions:
                for action in recommendation.actions:
                    lines.append(f"  - action: {action}")
    lines.append("")
    lines.append("## Fix proposals")
    lines.append("")
    if not session.fix_proposals:
        lines.append("- No fix proposals.")
    else:
        for proposal in session.fix_proposals:
            lines.append(
                f"- `{proposal.proposal_id}` {proposal.title} | risk={proposal.risk_level} | reversible={proposal.reversible}"
            )
    lines.append("")
    lines.append("## Verification")
    lines.append("")
    if not session.verification_results:
        lines.append("- No verification results.")
    else:
        for verification in session.verification_results:
            status = "PASS" if verification.ok else "FAIL"
            lines.append(f"- **{status}** `{verification.verifier_id}` {verification.title}")
            if verification.detail:
                lines.append(f"  - {verification.detail}")
    lines.append("")
    lines.append("## Execution records")
    lines.append("")
    if not session.execution_records:
        lines.append("- No plugin execution records.")
    else:
        for record in session.execution_records:
            status = "ok" if record.ok else "error"
            lines.append(
                f"- `{record.phase}` / `{record.plugin_id}` -> {status} in {record.duration_ms} ms"
                + (f" | {record.summary}" if record.summary else "")
            )
    lines.append("")
    if session.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in session.warnings:
            lines.append(f"- {warning}")
        lines.append("")
    if session.errors:
        lines.append("## Errors")
        lines.append("")
        for error in session.errors:
            lines.append(f"- {error}")
        lines.append("")
    return redact_text("\n".join(lines).rstrip() + "\n")


def write_session_reports(base_dir: Path, session: DiagnosticSession) -> dict[str, Path]:
    ensure_report_dirs(base_dir)
    session_json = (base_dir / MANDATORY_OUTPUT_FILES["diagnostic_session_json"]).resolve()
    session_md = (base_dir / MANDATORY_OUTPUT_FILES["diagnostic_session_md"]).resolve()
    write_json(session_json, session.to_dict())
    atomic_write_text(session_md, render_session_markdown(session))
    return {"session_json": session_json, "session_md": session_md}


def _render_artifact_excerpts(session: DiagnosticSession, *, max_artifacts: int = 12) -> list[str]:
    lines: list[str] = []
    shown = 0
    for artifact in session.artifacts:
        excerpt = str(getattr(artifact, "excerpt", "") or "").strip()
        if not excerpt:
            continue
        lines.append(f"### {artifact.artifact_id}")
        lines.append("")
        lines.append(f"- category: `{artifact.category}`")
        lines.append(f"- source_plugin: `{artifact.source_plugin}`")
        if artifact.path:
            lines.append(f"- path: `{artifact.path}`")
        lines.append("")
        lines.append("```")
        lines.append(excerpt[:1800])
        lines.append("```")
        lines.append("")
        shown += 1
        if shown >= max_artifacts:
            break
    if not lines:
        lines.append("- No hay excerpts inline todavía.")
        lines.append("")
    return lines


def render_support_bundle_markdown(session: DiagnosticSession) -> str:
    lines: list[str] = []
    lines.append("# Support Bundle")
    lines.append("")
    lines.append(f"- session_id: `{session.session_id}`")
    lines.append(f"- target_path: `{session.target_path}`")
    lines.append(f"- app_kind: `{session.app_kind}`")
    lines.append(f"- execution_mode: `{session.execution_mode}`")
    lines.append("")
    lines.append("## Priority findings")
    lines.append("")
    if session.findings:
        ordered = sorted(
            session.findings,
            key=lambda item: (
                {"critical": 4, "error": 3, "warn": 2, "info": 1}.get(str(item.severity).lower(), 0),
                float(item.confidence_score if item.confidence_score is not None else item.confidence or 0.0),
                item.title,
            ),
            reverse=True,
        )
        for finding in ordered[:10]:
            lines.append(f"- **{finding.severity.upper()}** {finding.title} | {finding.detail}")
    else:
        lines.append("- No findings collected yet.")
    lines.append("")
    lines.append("## Recommended next steps")
    lines.append("")
    if session.recommendations:
        for recommendation in session.recommendations[:10]:
            lines.append(f"- {recommendation.title}")
            for action in recommendation.actions[:5]:
                lines.append(f"  - {action}")
    else:
        lines.append("- Run collectors/analyzers in later iterations to enrich this bundle.")
    lines.append("")
    lines.append("## Artifact index")
    lines.append("")
    if session.artifacts:
        for artifact in session.artifacts[:48]:
            lines.append(f"- `{artifact.artifact_id}` | {artifact.category} | {artifact.path or 'inline'}")
    else:
        lines.append("- No artifacts.")
    lines.append("")
    lines.append("## Evidence excerpts")
    lines.append("")
    lines.extend(_render_artifact_excerpts(session, max_artifacts=10))
    return redact_text("\n".join(lines).rstrip() + "\n")


def write_support_bundle(base_dir: Path, session: DiagnosticSession, bundle_format: str = "md") -> dict[str, Path]:
    ensure_report_dirs(base_dir)
    bundle_json = (base_dir / MANDATORY_OUTPUT_FILES["support_bundle_json"]).resolve()
    bundle_md = (base_dir / MANDATORY_OUTPUT_FILES["support_bundle_md"]).resolve()
    write_json(bundle_json, session.to_dict())
    atomic_write_text(bundle_md, render_support_bundle_markdown(session))
    written = {"bundle_json": bundle_json, "bundle_md": bundle_md}
    if bundle_format == "json":
        return {"bundle_json": bundle_json}
    if bundle_format == "md":
        return {"bundle_md": bundle_md}
    return written
