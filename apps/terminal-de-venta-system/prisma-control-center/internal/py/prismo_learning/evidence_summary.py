# PRISMO Learning Core V1.1 F2
# Generated package: prismo learn2 3005 1100 fix1
# Operation model: evidence-intake-real, local store writes only, read-only against repo/DB/secrets.
# This file intentionally uses only Python standard library modules.

"""Evidence summarization utilities for F2 intake reports."""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import Any


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_type = Counter(str(r.get("type") or "unknown") for r in records)
    by_status = Counter(str(r.get("status") or "UNKNOWN") for r in records)
    by_surface: Counter[str] = Counter()
    warnings = 0
    metadata_only = 0
    secret_like = 0
    for r in records:
        for s in r.get("surface") or []:
            by_surface[str(s)] += 1
        if r.get("warnings"):
            warnings += len(r.get("warnings") or [])
        if r.get("metadata_only"):
            metadata_only += 1
        ss = r.get("secret_scan") or {}
        if ss.get("has_secret_like_pattern"):
            secret_like += 1
    return {
        "total": len(records),
        "by_type": dict(by_type.most_common()),
        "by_status": dict(by_status.most_common()),
        "by_surface": dict(by_surface.most_common()),
        "metadata_only": metadata_only,
        "warning_count": warnings,
        "secret_like_records": secret_like,
    }


def summarize_intake_report(report: dict[str, Any]) -> str:
    lines = ["# PRISMO Learning F2 Evidence Intake Report", ""]
    lines.append(f"Status: **{report.get('status', 'UNKNOWN')}**")
    lines.append(f"Inserted/updated: **{report.get('inserted', 0)}**")
    lines.append(f"Candidates scanned: **{report.get('candidates_scanned', 0)}**")
    lines.append(f"Errors: **{len(report.get('errors') or [])}**")
    summary = report.get("summary") or {}
    if summary:
        lines.extend(["", "## Summary", ""])
        for key in ("by_type", "by_status", "by_surface"):
            val = summary.get(key) or {}
            lines.append(f"### {key}")
            if not val:
                lines.append("- none")
            else:
                for k, v in val.items():
                    lines.append(f"- {k}: {v}")
            lines.append("")
    if report.get("warnings"):
        lines.extend(["## Warnings", ""])
        for w in report.get("warnings")[:50]:
            lines.append(f"- {w}")
    if report.get("errors"):
        lines.extend(["", "## Errors preview", ""])
        for e in report.get("errors")[:40]:
            lines.append(f"- `{e.get('path','')}`: {e.get('error','')}")
    lines.extend(["", "## Safety", "", "- No ZIP entries were executed.", "- Secret-like previews are redacted.", "- DB-like files remain metadata-only.", "- Runtime mutation_allowed remains false."])
    return "\n".join(lines) + "\n"
