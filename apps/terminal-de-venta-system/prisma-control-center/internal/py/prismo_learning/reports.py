# PRISMO Learning Core V1
# Generated package: prismo learn1 3005 1033
# Operation model: local, read-only runtime. Installer writes only the package files and guarded panel route markers with rollback.
# This file intentionally uses only Python standard library modules.

"""Composite report writers."""
from __future__ import annotations
from typing import Any
from .report_json import write_json_report
from .report_markdown import write_markdown_report


def write_ingestion_reports(report: dict[str, Any], base=None) -> dict[str, str]:
    report.setdefault("read_only", True)
    report.setdefault("mutation_allowed", False)
    jp = write_json_report("ingestion_report", report, base)
    mp = write_markdown_report("ingestion_report", "PRISMO Learning Ingestion Report", report, base)
    return {"json": str(jp), "md": str(mp)}


def write_diagnostic_report(report: dict[str, Any], base=None) -> dict[str, str]:
    jp = write_json_report("diagnostic_report", report, base)
    mp = write_markdown_report("diagnostic_report", "PRISMO Learning Diagnostic Report", report, base)
    return {"json": str(jp), "md": str(mp)}
