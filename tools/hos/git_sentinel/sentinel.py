#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tools.hos._core.stable_json import write_json

from .artifact_detector import classify_artifacts
from .cleanup_engine import execute_cleanup_plan, plan_cleanup
from .config import SentinelConfig
from .ignore_manager import apply_ignore_rules, generate_ignore_rules
from .learning_engine import read_learned_patterns, update_learning_database, write_security_history
from .prediction_engine import generate_predictions
from .repair_engine import execute_repairs, plan_repairs
from .report_generator import build_report_payload, compute_health_score, write_reports
from .scanner import scan_repository
from .security_scanner import scan_security
from .telemetry import build_telemetry_payload, persist_telemetry_payload, write_telemetry_files
from .visualization import generate_visualization_data


@dataclass(frozen=True)
class SentinelRunOptions:
    apply: bool = False
    update_ignore: bool = True
    enable_cleanup: bool = True
    enable_repair: bool = True
    restore_missing_tracked: bool = False
    allow_revert_unsafe: bool = False
    scan_only: bool = False


def run_sentinel_cycle(config: SentinelConfig, options: SentinelRunOptions) -> dict[str, Any]:
    config.ensure_layout()
    errors: list[str] = []
    commands: list[str] = []

    initial_scan = scan_repository(config)
    initial_artifacts = classify_artifacts(initial_scan, config)
    initial_security = scan_security(config, initial_scan)
    write_security_history(config=config, findings=initial_security.get("findings", []))

    learning_summary = update_learning_database(config=config, artifact_result=initial_artifacts, scan_state=initial_scan)
    learned_patterns = read_learned_patterns(config=config, min_count=2, limit=300)

    ignore_plan = generate_ignore_rules(
        config=config,
        artifact_result=initial_artifacts,
        learned_patterns=learned_patterns,
    )
    repair_plan = plan_repairs(
        config=config,
        scan_state=initial_scan,
        security_result=initial_security,
        restore_missing_tracked=options.restore_missing_tracked,
        allow_revert_unsafe=options.allow_revert_unsafe,
    )

    stop_triggered = options.apply and int(repair_plan.get("summary", {}).get("riskyActions", 0)) > 0
    if stop_triggered:
        errors.append("stop_condition_triggered: repair operations may affect legitimate source files")

    mutation_mode = bool(options.apply and not stop_triggered and not options.scan_only)

    ignore_result = {
        "changed": False,
        "applied": False,
        "ruleCount": int(ignore_plan.get("count", 0)),
    }
    if options.update_ignore and not options.scan_only:
        ignore_result = apply_ignore_rules(
            config=config,
            rules=ignore_plan.get("rules", []),
            apply_changes=mutation_mode,
        )
        if ignore_result.get("applied"):
            commands.append("update .gitignore managed block")

    cleanup_plan = {"actions": [], "summary": {"plannedActions": 0, "blockedActions": 0}, "blockedActions": []}
    cleanup_result = {
        "summary": {
            "plannedActions": 0,
            "blockedActions": 0,
            "deletedFiles": 0,
            "deletedDirs": 0,
            "applyMode": mutation_mode,
        },
        "results": [],
        "commandLog": [],
    }
    if options.enable_cleanup and not options.scan_only:
        cleanup_plan = plan_cleanup(config=config, scan_state=initial_scan, artifact_result=initial_artifacts)
        cleanup_result = execute_cleanup_plan(config=config, plan=cleanup_plan, apply_changes=mutation_mode)
        commands.extend(cleanup_result.get("commandLog", []))

    repair_result = {
        "summary": {
            "applyMode": mutation_mode,
            "executedActions": 0,
            "failedActions": 0,
            "stopTriggered": stop_triggered,
        },
        "results": [],
        "blocked": repair_plan.get("riskyActions", []),
    }
    if options.enable_repair and not options.scan_only:
        repair_result = execute_repairs(config=config, plan=repair_plan, apply_changes=mutation_mode)
        if repair_result.get("summary", {}).get("stopTriggered", False):
            errors.append(str(repair_result.get("stopReason", "stop condition triggered")))

    mutating_effect = (
        ignore_result.get("applied", False)
        or int(cleanup_result.get("summary", {}).get("deletedFiles", 0)) > 0
        or int(repair_result.get("summary", {}).get("executedActions", 0)) > 0
    )

    if mutating_effect:
        final_scan = scan_repository(config)
        final_artifacts = classify_artifacts(final_scan, config)
        final_security = scan_security(config, final_scan)
        write_security_history(config=config, findings=final_security.get("findings", []))
    else:
        final_scan = initial_scan
        final_artifacts = initial_artifacts
        final_security = initial_security

    visualization = generate_visualization_data(config=config, scan_state=final_scan)

    telemetry_payload = build_telemetry_payload(
        config=config,
        scan_state=final_scan,
        artifact_result=final_artifacts,
        cleanup_result=cleanup_result,
        repair_result=repair_result,
        security_result=final_security,
        health_score=0,
        error_count=len(errors),
    )
    prediction_result = generate_predictions(config=config, current_telemetry=telemetry_payload)
    health_score, _health_factors = compute_health_score(
        scan_state=final_scan,
        artifact_result=final_artifacts,
        cleanup_result=cleanup_result,
        repair_result=repair_result,
        security_result=final_security,
        prediction_result=prediction_result,
        telemetry_payload=telemetry_payload,
    )
    telemetry_payload["healthScore"] = int(health_score)
    persist_telemetry_payload(config=config, telemetry_payload=telemetry_payload)
    telemetry_files = write_telemetry_files(config=config, telemetry_payload=telemetry_payload)

    report_payload = build_report_payload(
        config=config,
        scan_state=final_scan,
        artifact_result=final_artifacts,
        ignore_result={
            **ignore_result,
            "plan": ignore_plan,
        },
        cleanup_result={
            **cleanup_result,
            "plan": cleanup_plan,
        },
        repair_result={
            **repair_result,
            "plan": repair_plan,
        },
        security_result=final_security,
        telemetry_payload=telemetry_payload,
        prediction_result=prediction_result,
        visualization_result=visualization,
        errors=errors,
        telemetry_files=telemetry_files,
    )
    report_payload["learning"] = learning_summary
    report_payload["commandsExecuted"] = commands
    report_files = write_reports(config=config, payload=report_payload)
    report_payload["files"].update(report_files)
    # Persist enriched file pointers in latest report payload.
    write_reports(config=config, payload=report_payload)

    cycle_stamp = str(report_payload.get("timestamp", "")).replace(":", "").replace("-", "")
    cycle_log_path = (config.log_dir / f"sentinel_cycle_{cycle_stamp}.json").resolve()
    cycle_log_payload = {
        "timestamp": report_payload.get("timestamp"),
        "applyMode": bool(options.apply),
        "scanOnly": bool(options.scan_only),
        "commandsExecuted": commands,
        "summary": report_payload.get("summary", {}),
        "health": report_payload.get("health", {}),
        "errors": report_payload.get("errors", []),
    }
    write_json(cycle_log_path, cycle_log_payload, indent=2, sort_keys=True)
    report_payload["files"]["cycleLog"] = cycle_log_path.as_posix()
    write_reports(config=config, payload=report_payload)

    return report_payload
