from __future__ import annotations

from typing import Any, Mapping

from .contracts import ContractError


def _bullets(values: list[Any]) -> list[str]:
    return [f"- {value}" for value in values] if values else ["- None"]


def render_change_model_markdown(model: Mapping[str, Any]) -> str:
    if not isinstance(model, Mapping) or model.get("schemaVersion") != "code_atlas_change_model.v1":
        raise ContractError("unsupported change model")
    lines = [
        "# Change Intelligence Report",
        "",
        f"Decision: **{model.get('decision', 'UNKNOWN')}**",
        f"Intent: {model.get('normalizedIntent', '')}",
        "",
        "## Primary targets",
    ]
    for row in model.get("primaryTargets", []):
        lines.append(f"- `{row.get('path')}` [{row.get('supportLevel')}] {row.get('reason', '')}".rstrip())
    lines += ["", "## Protected scope", *_bullets([f"`{p}`" for p in model.get("protectedScope", [])])]
    lines += ["", "## Unknowns", *_bullets(list(model.get("unknowns", [])))]
    lines += ["", "## Contradictions", *_bullets(list(model.get("contradictions", [])))]
    lines += ["", "## Missing required evidence", *_bullets(list(model.get("missingRequiredEvidence", [])))]
    lines += ["", "## Does not prove", *_bullets(list(model.get("doesNotProve", [])))]
    lines += ["", f"Model digest: `{model.get('modelDigest', '')}`", ""]
    return "\n".join(lines)


def render_verification_markdown(report: Mapping[str, Any]) -> str:
    if not isinstance(report, Mapping) or report.get("schemaVersion") != "code_atlas_change_verification.v1":
        raise ContractError("unsupported verification report")
    lines = [
        "# Change Verification Report",
        "",
        f"Decision: **{report.get('decision', 'UNKNOWN')}**",
        f"Authority pack: `{report.get('packId', '')}`",
        "",
        "## Out-of-scope mutations",
        *_bullets([f"`{p}`" for p in report.get("outOfScopeMutations", [])]),
        "",
        "## Protected boundary violations",
        *_bullets([f"`{p}`" for p in report.get("protectedBoundaryViolations", [])]),
        "",
        "## Missing checks",
        *_bullets(list(report.get("missingChecks", []))),
        "",
        "## Missing evidence",
        *_bullets(list(report.get("missingEvidence", []))),
        "",
        "## Findings",
    ]
    findings = report.get("findings", [])
    if findings:
        for finding in findings:
            lines.append(f"- `{finding.get('code', 'UNKNOWN')}`: {finding}")
    else:
        lines.append("- None")
    lines += ["", "## Does not prove", *_bullets(list(report.get("doesNotProve", [])))]
    lines += ["", f"Report digest: `{report.get('reportDigest', '')}`", ""]
    return "\n".join(lines)
