#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from argparse import Namespace
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capatch_audit.telemetry import enrich_payload, write_telemetry_report
from capatch_diagnostics.runtime import build_session, initialize_plugin_runtime, run_session, run_session_reports
from capatch_contracts.plugin_runtime import summarize_essential_runtime_health


def _write_report(output_dir: Path, stem: str, payload: dict[str, Any]) -> dict[str, str]:
    lines = [
        "## load_summary",
        "",
        f"- discovered: {payload['load_summary']['discovered']}",
        f"- active: {payload['load_summary']['active']}",
        f"- rejected: {payload['load_summary']['rejected']}",
        "",
        "## issues",
        "",
    ]
    if payload["issues"]:
        lines.extend(f"- {issue}" for issue in payload["issues"])
    else:
        lines.append("- none")
    return write_telemetry_report(output_dir, stem, payload, lines)


def run_contract_smoke(base_dir: Path, output_dir: Path | None = None) -> dict[str, Any]:
    started = time.perf_counter()
    state = initialize_plugin_runtime(base_dir)
    issues: list[str] = []
    registry = state.get("registry", {})
    active_plugins = list(state.get("active_plugins", []))
    essential_health = summarize_essential_runtime_health(state.get("runtime_version"), registry)
    for item in active_plugins:
        plugin_id = str(item.get("plugin_id") or "")
        if not plugin_id:
            issues.append("active plugin without plugin_id")
            continue
        entry = registry.get(plugin_id)
        if not isinstance(entry, dict):
            issues.append(f"missing registry entry for {plugin_id}")
            continue
        for required in ("status", "version", "path", "hash"):
            if not entry.get(required):
                issues.append(f"{plugin_id} missing registry field: {required}")
    args = Namespace(
        target_path=".",
        app_kind="auto",
        collect_only=False,
        verify_only=False,
        support_bundle=True,
        fix_plan=False,
        apply_fixes=False,
        dry_diagnose=True,
        include_logs=True,
        include_processes=False,
        include_ports=False,
        include_git=True,
        include_build=False,
        include_tests=False,
        max_log_lines=40,
        max_log_bytes=65536,
        command_timeout_seconds=15,
        bundle_format="md",
    )
    session = build_session(args, base_dir, state)
    session = run_session(session, state)
    written = run_session_reports(base_dir, session)
    duration_ms = round((time.perf_counter() - started) * 1000.0, 3)
    status = "passed"
    if issues or session.errors:
        status = "failed"
    elif essential_health.get("status") != "healthy" or int(state.get("runtime_status", {}).get("rejected_plugins", 0) or 0) > 0:
        status = "degraded"
    if essential_health.get("status") != "healthy":
        issues.append(
            "essential plugin runtime degraded: "
            f"missing={essential_health.get('missing', [])} rejected={essential_health.get('rejected', [])} "
            f"disabled={essential_health.get('disabled', [])} duplicate={essential_health.get('duplicate', [])}"
        )
    payload = enrich_payload(
        {
            "name": "plugin_contract_smoke",
            "status": status,
            "duration_ms": duration_ms,
            "issues": issues + list(session.errors),
            "load_summary": dict(state.get("load_summary", {})),
            "essential_plugin_health": essential_health,
            "runtime_status": dict(state.get("runtime_status", {})),
            "active_plugin_ids": [str(item.get("plugin_id")) for item in active_plugins],
            "session": {
                "session_id": session.session_id,
                "artifacts": len(session.artifacts),
                "findings": len(session.findings),
                "recommendations": len(session.recommendations),
                "execution_records": len(session.execution_records),
            },
            "written": {key: str(value) for key, value in written.items()},
        },
        root_dir=base_dir,
        artifact_kind="telemetry-report",
        artifact_scope="reports/telemetry/plugin_contract_smoke",
    )
    if output_dir is not None:
        payload["report_paths"] = _write_report(output_dir, "plugin_contract_smoke", payload)
    return payload


def main(argv: list[str] | None = None) -> int:
    base_dir = ROOT
    output_dir = base_dir / "reports" / "telemetry"
    payload = run_contract_smoke(base_dir, output_dir)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
