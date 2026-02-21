from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

from .attestations import write_all_attestations
from .common import INTEGRATOR, RUNS_DIR, WORKERS, iso_utc, read_json, read_text, stable_sha256_text
from .config import load_factory_config
from .contracts import bundle_dir, scaffold_integrator_bundle, validate_bundle
from .fs_guard import WriteGuard, WritePolicyError
from .ledger import append_event, verify_ledger_signature
from .overlap import detect_file_overlaps, detect_scope_violations
from .schemas import validate_payload
from .status_eval import BLOCKED, FAIL, PASS, evaluate_status, make_check, status_exit_code

try:  # pragma: no cover - import path depends on launcher mode
    from verify.meaningful_gate import BLOCKED as GATE_BLOCKED
    from verify.meaningful_gate import FAIL as GATE_FAIL
    from verify.meaningful_gate import PASS as GATE_PASS
    from verify.meaningful_gate import WARN as GATE_WARN
    from verify.meaningful_gate import run_meaningful_gate
except Exception:  # pragma: no cover - package mode fallback
    from tools.codex.verify.meaningful_gate import BLOCKED as GATE_BLOCKED
    from tools.codex.verify.meaningful_gate import FAIL as GATE_FAIL
    from tools.codex.verify.meaningful_gate import PASS as GATE_PASS
    from tools.codex.verify.meaningful_gate import WARN as GATE_WARN
    from tools.codex.verify.meaningful_gate import run_meaningful_gate


def _collect_worker_inputs(run_id: str, workers: list[str]) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    for worker in workers:
        root = bundle_dir(run_id, worker)
        record = {
            "worker": worker,
            "bundle": root.as_posix(),
            "status": "MISSING",
            "validation": validate_bundle(run_id, worker),
            "files_changed": [],
            "summary": "",
            "diff": "",
            "noop": False,
            "noop_reason": "",
            "noop_ack": "",
        }
        if root.exists():
            record["status"] = "PRESENT"
            files_changed_path = root / "FILES_CHANGED.json"
            summary_path = root / "SUMMARY.md"
            diff_path = root / "DIFF.patch"
            if files_changed_path.exists():
                payload = read_json(files_changed_path)
                record["files_changed"] = list(payload.get("changes", []))
                record["noop"] = bool(payload.get("noop", False))
                record["noop_reason"] = str(payload.get("noop_reason", "")).strip()
                record["noop_ack"] = str(payload.get("noop_ack", "")).strip()
            if summary_path.exists():
                record["summary"] = read_text(summary_path).strip()
            if diff_path.exists():
                record["diff"] = read_text(diff_path)
        collected.append(record)
    return collected


def _merge_files_changed(run_id: str, collected: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    records = list(collected)
    merged: list[dict[str, Any]] = []
    noop_records: list[tuple[str, str, str]] = []
    for item in records:
        owner = str(item.get("worker", ""))
        noop = bool(item.get("noop", False))
        noop_reason = str(item.get("noop_reason", "")).strip()
        noop_ack = str(item.get("noop_ack", "")).strip()
        if noop and noop_reason and noop_ack:
            noop_records.append((owner, noop_reason, noop_ack))
        for change in item.get("files_changed", []) or []:
            if not isinstance(change, Mapping):
                continue
            merged.append(
                {
                    "path": str(change.get("path", "")),
                    "change_type": str(change.get("change_type", "modified")),
                    "owner": owner,
                    "reason": str(change.get("reason", "")),
                    "sha256": str(change.get("sha256", "")),
                }
            )
    merged = sorted(merged, key=lambda entry: (str(entry.get("path", "")), str(entry.get("owner", ""))))
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "owner": INTEGRATOR,
        "changes": merged,
    }
    if not merged and noop_records and len(noop_records) == len(records):
        ordered = sorted(noop_records, key=lambda item: item[0])
        payload["noop"] = True
        payload["noop_reason"] = "; ".join(f"{worker}: {reason}" for worker, reason, _ in ordered)
        payload["noop_ack"] = ",".join(worker for worker, _, _ in ordered)
    else:
        payload["noop"] = False
        payload["noop_reason"] = ""
        payload["noop_ack"] = ""
    return payload


def _merge_patch(collected: Iterable[Mapping[str, Any]]) -> str:
    chunks: list[str] = []
    for item in collected:
        worker = str(item.get("worker", ""))
        patch = str(item.get("diff", ""))
        if not patch.strip():
            continue
        chunks.append(f"# >>> BEGIN {worker}\n{patch.rstrip()}\n# <<< END {worker}\n")
    return "\n".join(chunks).strip() + ("\n" if chunks else "")


def _render_merge_plan(
    run_id: str,
    collected: list[dict[str, Any]],
    overlap_report: dict[str, Any],
    scope_report: dict[str, Any],
    required_checks: list[dict[str, Any]],
) -> str:
    lines = [
        f"# Merge Plan: {run_id}",
        "",
        "## Worker Inputs",
    ]
    for item in collected:
        validation = item.get("validation", {})
        lines.append(f"- {item['worker']}: {validation.get('status', 'UNKNOWN')} ({len(validation.get('errors', []))} errors)")

    lines.extend(["", "## Required Checks"])
    for check in required_checks:
        lines.append(f"- {check['name']}: {check['status']} (rc={check['rc']})")

    lines.extend(["", "## Overlap Report"])
    if overlap_report.get("overlaps"):
        for overlap in overlap_report["overlaps"]:
            workers = ", ".join(overlap.get("workers", []))
            lines.append(f"- {overlap['status']}: {overlap['path']} ({workers})")
    else:
        lines.append("- None")

    lines.extend(["", "## Scope Violations"])
    if scope_report.get("violations"):
        for violation in scope_report["violations"]:
            lines.append(f"- {violation['worker']}: {violation['path']} ({violation['rule']})")
    else:
        lines.append("- None")

    return "\n".join(lines).rstrip() + "\n"


def _render_final_report(
    run_id: str,
    collected: list[dict[str, Any]],
    overlap_report: dict[str, Any],
    scope_report: dict[str, Any],
    final_status: str,
    required_checks: Iterable[Mapping[str, Any]],
    *,
    contract_version: int = 2,
    schema_errors: Iterable[str] | None = None,
    policy_errors: Iterable[str] | None = None,
    internal_errors: Iterable[str] | None = None,
    ledger_signature_status: Mapping[str, Any] | None = None,
    meaningful_gate: Mapping[str, Any] | None = None,
) -> str:
    gate = meaningful_gate or {}
    gate_verdict = str(gate.get("verdict", "N/A"))
    gate_noop = bool(gate.get("noop", False))
    lines = [
        f"# FINAL_REPORT - {run_id}",
        "",
        "## Summary",
        f"- Final status: {final_status}",
        f"- Contract version: {contract_version}",
        f"- Worker bundles processed: {len(collected)}",
        f"- Overlap conflicts: {overlap_report.get('blocked', 0)}",
        f"- Scope violations: {scope_report.get('blocked', 0)}",
        f"- Hidden overlaps: {len(overlap_report.get('hidden_overlaps', []))}",
        f"- Invalid FILES_CHANGED paths: {len(overlap_report.get('invalid_paths', []))}",
        f"- Meaningful gate verdict: {gate_verdict}",
        f"- NOOP declared: {str(gate_noop).lower()}",
        "",
        "## Required Checks",
    ]
    for check in required_checks:
        lines.append(f"- {check['name']}: {check['status']} (rc={check['rc']})")

    lines.extend(["", "## Inputs"])
    for item in collected:
        validation = item.get("validation", {})
        lines.append(f"- {item['worker']}: {validation.get('status', 'UNKNOWN')} | errors={len(validation.get('errors', []))} | bundle={item['bundle']}")

    lines.extend(["", "## Worker Summaries"])
    for item in collected:
        lines.append(f"### {item['worker']}")
        summary = str(item.get("summary", "")).strip()
        lines.append(summary if summary else "- No summary provided")
        lines.append("")

    lines.extend(["## Blocking Conditions"])
    blockers: list[str] = []
    for item in collected:
        for error in item.get("validation", {}).get("errors", []):
            blockers.append(f"{item['worker']}: {error}")
    for overlap in overlap_report.get("overlaps", []):
        if overlap.get("status") == "BLOCKED":
            blockers.append(f"overlap: {overlap['path']} ({', '.join(overlap.get('workers', []))})")
    for hidden in overlap_report.get("hidden_overlaps", []):
        blockers.append(f"hidden_overlap: {hidden['worker']} {hidden['path']}")
    for invalid in overlap_report.get("invalid_paths", []):
        blockers.append(f"invalid_path: {invalid['worker']} {invalid['path']}")
    for violation in scope_report.get("violations", []):
        blockers.append(f"scope: {violation['worker']} {violation['path']}")
    for item in schema_errors or []:
        blockers.append(f"schema: {item}")
    for item in policy_errors or []:
        blockers.append(f"policy: {item}")
    for item in internal_errors or []:
        blockers.append(f"internal: {item}")
    for mode in gate.get("fail_modes", []) if isinstance(gate.get("fail_modes", []), list) else []:
        blockers.append(f"meaningful_gate: {mode}")

    if blockers:
        for blocker in sorted(set(blockers)):
            lines.append(f"- {blocker}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Ledger Signature",
            f"- Status: {ledger_signature_status.get('status', 'UNKNOWN') if ledger_signature_status else 'UNKNOWN'}",
            f"- Signature file: {ledger_signature_status.get('signature', '') if ledger_signature_status else ''}",
            "",
            "## NEXT ACTION",
            "- If BLOCKED: resolve overlap/scope/policy issues and rerun integration.",
            "- If FAIL: inspect logs and fix internal factory errors.",
            "- If PASS: run project-level validation and publish the run report.",
            "- If PASS with NOOP: do not count as phase progress; record explicit noop rationale.",
        ]
    )

    return "\n".join(lines).rstrip() + "\n"


def _build_log_index(run_id: str, rc: int) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "run_id": run_id,
        "owner": INTEGRATOR,
        "logs": [
            {
                "name": "integration",
                "path": "LOGS/integration.log.txt",
                "rc": int(rc),
            }
        ],
    }


def _build_status_payload(
    run_id: str,
    *,
    final_status: str,
    started_at: str,
    ended_at: str,
    required_checks: list[dict[str, Any]],
    optional_checks: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    noop: bool = False,
    noop_reason: str = "",
    noop_ack: str = "",
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "contract_version": 2,
        "run_id": run_id,
        "worker_id": INTEGRATOR,
        "status": final_status,
        "noop": bool(noop),
        "noop_reason": str(noop_reason),
        "noop_ack": str(noop_ack),
        "started_at": started_at,
        "ended_at": ended_at,
        "required_checks": required_checks,
        "optional_checks": optional_checks,
        "errors": errors,
        "warnings": warnings,
        "artifacts": [
            "FINAL_REPORT.txt",
            "MERGE_PLAN.md",
            "FILES_CHANGED.json",
            "DIFF.patch",
            "LOGS/integration.log.txt",
            "LOGS/INDEX.json",
        ],
    }


def _write_standard_outputs(
    *,
    guard: WriteGuard,
    z_dir: Path,
    merged_files: dict[str, Any],
    merged_patch: str,
    merge_plan: str,
    final_report: str,
    status_payload: dict[str, Any],
    log_index_payload: dict[str, Any],
    extra_writes: Iterable[Mapping[str, Any]] | None = None,
) -> None:
    guard.write_json(z_dir / "FILES_CHANGED.json", merged_files)
    guard.write_text(z_dir / "DIFF.patch", merged_patch)
    guard.write_text(z_dir / "MERGE_PLAN.md", merge_plan)
    guard.write_text(z_dir / "FINAL_REPORT.txt", final_report)
    guard.write_json(z_dir / "STATUS.json", status_payload)
    guard.write_json(z_dir / "LOGS" / "INDEX.json", log_index_payload)

    for extra in extra_writes or []:
        payload = dict(extra)
        target_raw = payload.get("path")
        if target_raw is None:
            continue
        target = Path(str(target_raw))
        if payload.get("is_json"):
            guard.write_json(target, payload.get("payload", {}))
        else:
            guard.write_text(target, str(payload.get("text", "")))


def integrate_run(
    run_id: str,
    workers: list[str] | None = None,
    *,
    config: Mapping[str, Any] | None = None,
    extra_writes: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    chosen = list(workers or WORKERS)
    cfg = dict(config or load_factory_config(strict=False))
    run_cfg = dict(cfg.get("run", {})) if isinstance(cfg.get("run"), Mapping) else {}
    strict_mode = bool(run_cfg.get("strict_collision_mode", True))
    allow_identical_patch_overlap = bool(run_cfg.get("allow_identical_patch_overlap", False))
    started_at = iso_utc()
    scaffold_integrator_bundle(run_id)

    run_root = RUNS_DIR / run_id
    z_dir = bundle_dir(run_id, INTEGRATOR)
    guard = WriteGuard(run_root)
    run_log = z_dir / "LOGS" / "integration.log.txt"

    try:
        append_event(
            {
                "schema_version": 1,
                "ts_utc": started_at,
                "run_id": run_id,
                "event_type": "INTEGRATE_START",
                "actor": INTEGRATOR,
                "parent_event_id": "",
                "duration_ms": 0,
                "file_counts": {},
                "hashes": {},
                "rc": 0,
                "details": {"status": "PASS", "kind": "factory", "workers": chosen},
            }
        )
        guard.append_line(run_log, f"[start] run_id={run_id}")
        collected = _collect_worker_inputs(run_id, chosen)
        overlap_report = detect_file_overlaps(
            run_id,
            workers=chosen,
            strict_mode=strict_mode,
            allow_identical_patch_overlap=allow_identical_patch_overlap,
        )
        scope_report = detect_scope_violations(run_id, workers=chosen)
        merged_files = _merge_files_changed(run_id, collected)
        merged_patch = _merge_patch(collected)

        worker_blockers = [item for item in collected if item.get("validation", {}).get("status") != PASS]
        overlap_blockers = [item for item in overlap_report.get("overlaps", []) if item.get("status") == BLOCKED]
        hidden_overlap_blockers = list(overlap_report.get("hidden_overlaps", []))
        invalid_path_blockers = list(overlap_report.get("invalid_paths", []))
        scope_blockers = list(scope_report.get("violations", []))

        blockers = [
            f"worker bundle blockers={len(worker_blockers)}",
            f"overlap blockers={len(overlap_blockers)}",
            f"hidden overlap blockers={len(hidden_overlap_blockers)}",
            f"invalid path blockers={len(invalid_path_blockers)}",
            f"scope blockers={len(scope_blockers)}",
        ]
        blockers = [item for item in blockers if not item.endswith("=0")]

        required_checks = [
            make_check(
                "worker_bundle_validation",
                rc=0 if not worker_blockers else 2,
                required=True,
                detail=f"workers={len(chosen)} blockers={len(worker_blockers)}",
                actor=INTEGRATOR,
            ),
            make_check(
                "overlap_detection",
                rc=0 if not overlap_blockers and not hidden_overlap_blockers and not invalid_path_blockers else 2,
                required=True,
                detail=(
                    f"blocked={len(overlap_blockers)} hidden={len(hidden_overlap_blockers)} "
                    f"invalid_paths={len(invalid_path_blockers)} strict={strict_mode}"
                ),
                actor=INTEGRATOR,
            ),
            make_check(
                "scope_detection",
                rc=0 if not scope_blockers else 2,
                required=True,
                detail=f"blocked={len(scope_blockers)}",
                actor=INTEGRATOR,
            ),
        ]

        schema_errors: list[str] = []
        merged_schema_errors = validate_payload("files_changed", merged_files)
        if merged_schema_errors:
            schema_errors.extend([f"FILES_CHANGED.json: {item}" for item in merged_schema_errors])
            required_checks.append(
                make_check(
                    "schema_files_changed",
                    rc=2,
                    required=True,
                    detail=f"errors={len(merged_schema_errors)}",
                    actor=INTEGRATOR,
                )
            )
        else:
            required_checks.append(make_check("schema_files_changed", rc=0, required=True, actor=INTEGRATOR))

        evaluation = evaluate_status(
            required_checks=required_checks,
            optional_checks=[],
            schema_errors=schema_errors,
            blockers=blockers,
            internal_errors=[],
        )

        ended_at = iso_utc()
        final_status = evaluation.status
        merge_plan = _render_merge_plan(run_id, collected, overlap_report, scope_report, list(evaluation.required_checks))

        errors = [
            {
                "kind": "bundle",
                "detail": item,
            }
            for item in worker_blockers
        ]
        warnings = [
            {
                "kind": "overlap",
                "detail": overlap,
            }
            for overlap in overlap_report.get("overlaps", [])
            if overlap.get("status") == "WARN"
        ]

        status_payload = _build_status_payload(
            run_id,
            final_status=final_status,
            started_at=started_at,
            ended_at=ended_at,
            required_checks=[dict(item) for item in evaluation.required_checks],
            optional_checks=[dict(item) for item in evaluation.optional_checks],
            errors=errors,
            warnings=warnings,
            noop=bool(merged_files.get("noop", False)),
            noop_reason=str(merged_files.get("noop_reason", "")),
            noop_ack=str(merged_files.get("noop_ack", "")),
        )

        status_schema_errors = validate_payload("integrator_status", status_payload)
        if status_schema_errors:
            schema_errors.extend([f"STATUS.json: {item}" for item in status_schema_errors])
            required_checks.append(make_check("schema_integrator_status", rc=2, required=True, actor=INTEGRATOR))
        else:
            required_checks.append(make_check("schema_integrator_status", rc=0, required=True, actor=INTEGRATOR))

        log_index_payload = _build_log_index(run_id, status_exit_code(final_status))
        log_schema_errors = validate_payload("log_index", log_index_payload)
        if log_schema_errors:
            schema_errors.extend([f"LOGS/INDEX.json: {item}" for item in log_schema_errors])
            required_checks.append(make_check("schema_log_index", rc=2, required=True, actor=INTEGRATOR))
        else:
            required_checks.append(make_check("schema_log_index", rc=0, required=True, actor=INTEGRATOR))

        # Re-evaluate after schema checks.
        evaluation = evaluate_status(
            required_checks=required_checks,
            optional_checks=[],
            schema_errors=schema_errors,
            blockers=blockers,
            internal_errors=[],
        )
        final_status = evaluation.status
        status_payload["status"] = final_status
        status_payload["required_checks"] = [dict(item) for item in evaluation.required_checks]
        status_payload["optional_checks"] = [dict(item) for item in evaluation.optional_checks]
        log_index_payload = _build_log_index(run_id, status_exit_code(final_status))

        final_report = _render_final_report(
            run_id,
            collected,
            overlap_report,
            scope_report,
            final_status,
            evaluation.required_checks,
            contract_version=int(cfg.get("contract_version", 2)),
            schema_errors=schema_errors,
            policy_errors=[],
            internal_errors=[],
            ledger_signature_status={},
            meaningful_gate={},
        )

        policy_errors: list[str] = []
        try:
            _write_standard_outputs(
                guard=guard,
                z_dir=z_dir,
                merged_files=merged_files,
                merged_patch=merged_patch,
                merge_plan=merge_plan,
                final_report=final_report,
                status_payload=status_payload,
                log_index_payload=log_index_payload,
                extra_writes=extra_writes,
            )
        except WritePolicyError as exc:
            policy_errors.append(str(exc))

        if policy_errors:
            required_checks.append(
                make_check(
                    "z_write_policy",
                    rc=2,
                    required=True,
                    detail=policy_errors[0],
                    actor=INTEGRATOR,
                )
            )
            evaluation = evaluate_status(
                required_checks=required_checks,
                optional_checks=[],
                schema_errors=schema_errors,
                blockers=blockers + policy_errors,
                internal_errors=[],
            )
            final_status = evaluation.status
            status_payload["status"] = final_status
            status_payload["required_checks"] = [dict(item) for item in evaluation.required_checks]
            final_report = _render_final_report(
                run_id,
                collected,
                overlap_report,
                scope_report,
                final_status,
                evaluation.required_checks,
                contract_version=int(cfg.get("contract_version", 2)),
                schema_errors=schema_errors,
                policy_errors=policy_errors,
                internal_errors=[],
                ledger_signature_status={},
                meaningful_gate={},
            )
            _write_standard_outputs(
                guard=guard,
                z_dir=z_dir,
                merged_files=merged_files,
                merged_patch=merged_patch,
                merge_plan=merge_plan,
                final_report=final_report,
                status_payload=status_payload,
                log_index_payload=_build_log_index(run_id, status_exit_code(final_status)),
                extra_writes=None,
            )

        repo_root_candidate = Path(str(cfg.get("paths", {}).get("repo_root", Path.cwd().as_posix()))).resolve(strict=False)
        gate_payload = run_meaningful_gate(
            run_id,
            repo_root=repo_root_candidate,
            runs_dir=RUNS_DIR,
            write_outputs=True,
        )
        gate_verdict = str(gate_payload.get("verdict", GATE_BLOCKED)).upper()
        gate_fail_modes = [str(item) for item in gate_payload.get("fail_modes", [])]
        gate_rc = 0 if gate_verdict in {GATE_PASS, GATE_WARN} else 2
        required_checks.append(
            make_check(
                "meaningful_execution_gate",
                rc=gate_rc,
                required=True,
                detail=(
                    f"verdict={gate_verdict} "
                    f"fail_modes={','.join(sorted(gate_fail_modes)) if gate_fail_modes else '<none>'}"
                ),
                actor=INTEGRATOR,
            )
        )
        gate_blockers = [f"meaningful_gate:{item}" for item in sorted(set(gate_fail_modes))]
        if gate_verdict in {GATE_BLOCKED, GATE_FAIL} and not gate_blockers:
            gate_blockers.append(f"meaningful_gate:{gate_verdict}")
        evaluation = evaluate_status(
            required_checks=required_checks,
            optional_checks=[],
            schema_errors=schema_errors,
            blockers=blockers + policy_errors + gate_blockers,
            internal_errors=[],
        )
        final_status = evaluation.status
        status_payload["status"] = final_status
        status_payload["required_checks"] = [dict(item) for item in evaluation.required_checks]
        status_payload["optional_checks"] = [dict(item) for item in evaluation.optional_checks]
        status_payload["noop"] = bool(gate_payload.get("noop", False))
        status_payload["noop_reason"] = str(gate_payload.get("noop_reason", ""))
        status_payload["noop_ack"] = str(gate_payload.get("noop_ack", ""))

        final_report = _render_final_report(
            run_id,
            collected,
            overlap_report,
            scope_report,
            final_status,
            evaluation.required_checks,
            contract_version=int(cfg.get("contract_version", 2)),
            schema_errors=schema_errors,
            policy_errors=policy_errors,
            internal_errors=[],
            ledger_signature_status={},
            meaningful_gate=gate_payload,
        )
        guard.write_json(z_dir / "STATUS.json", status_payload)
        guard.write_json(z_dir / "LOGS" / "INDEX.json", _build_log_index(run_id, status_exit_code(final_status)))
        guard.write_text(z_dir / "FINAL_REPORT.txt", final_report)

        guard.append_line(run_log, f"[done] final_status={final_status}")

        attestations = write_all_attestations(run_id, report_path=z_dir / "FINAL_REPORT.txt")
        ledger_sig = verify_ledger_signature()
        final_report = _render_final_report(
            run_id,
            collected,
            overlap_report,
            scope_report,
            final_status,
            evaluation.required_checks,
            contract_version=int(cfg.get("contract_version", 2)),
            schema_errors=schema_errors,
            policy_errors=policy_errors,
            internal_errors=[],
            ledger_signature_status=ledger_sig,
            meaningful_gate=gate_payload,
        )
        guard.write_text(z_dir / "FINAL_REPORT.txt", final_report)
        report_hash = stable_sha256_text(final_report)
        attestations = write_all_attestations(run_id, report_path=z_dir / "FINAL_REPORT.txt")

        report_hash = stable_sha256_text(final_report)
        append_event(
            {
                "schema_version": 1,
                "ts_utc": ended_at,
                "run_id": run_id,
                "event_type": "REPORT_WRITTEN",
                "actor": INTEGRATOR,
                "parent_event_id": "",
                "duration_ms": 0,
                "file_counts": {"workers": len(chosen), "merged_files": len(merged_files.get("changes", []))},
                "hashes": {"final_report_sha256": report_hash},
                "rc": status_exit_code(final_status),
                "details": {
                    "kind": "factory",
                    "status": final_status,
                    "workers": chosen,
                    "worker_blockers": len(worker_blockers),
                    "overlap_blockers": len(overlap_blockers),
                    "scope_blockers": len(scope_blockers),
                    "report": (z_dir / "FINAL_REPORT.txt").as_posix(),
                    "path": (RUNS_DIR / run_id).as_posix(),
                    "attestations": attestations,
                    "meaningful_gate": gate_payload.get("outputs", {}),
                    "meaningful_gate_verdict": gate_payload.get("verdict", GATE_BLOCKED),
                },
            }
        )
        append_event(
            {
                "schema_version": 1,
                "ts_utc": ended_at,
                "run_id": run_id,
                "event_type": "RUN_END",
                "actor": INTEGRATOR,
                "parent_event_id": "",
                "duration_ms": 0,
                "file_counts": {"workers": len(chosen)},
                "hashes": {"final_report_sha256": report_hash},
                "rc": status_exit_code(final_status),
                "details": {"status": final_status, "kind": "factory"},
            }
        )

        return {
            "run_id": run_id,
            "status": final_status,
            "z_dir": z_dir.as_posix(),
            "worker_blockers": len(worker_blockers),
            "overlap_blockers": len(overlap_blockers),
            "hidden_overlap_blockers": len(hidden_overlap_blockers),
            "invalid_path_blockers": len(invalid_path_blockers),
            "scope_blockers": len(scope_blockers),
            "report": (z_dir / "FINAL_REPORT.txt").as_posix(),
            "attestations": attestations,
            "meaningful_gate": gate_payload,
        }
    except Exception as exc:  # pragma: no cover - integration fallback path
        ended_at = iso_utc()
        fallback_error = str(exc)
        failure_checks = [make_check("integrator_internal_error", rc=1, required=True, detail=fallback_error, actor=INTEGRATOR)]
        evaluation = evaluate_status(
            required_checks=failure_checks,
            optional_checks=[],
            schema_errors=[],
            blockers=[],
            internal_errors=[fallback_error],
        )
        status_payload = _build_status_payload(
            run_id,
            final_status=evaluation.status,
            started_at=started_at,
            ended_at=ended_at,
            required_checks=[dict(item) for item in evaluation.required_checks],
            optional_checks=[],
            errors=[{"kind": "internal", "detail": fallback_error}],
            warnings=[],
            noop=False,
            noop_reason="",
            noop_ack="",
        )
        fallback_report = _render_final_report(
            run_id,
            [],
            {"overlaps": [], "blocked": 0},
            {"violations": [], "blocked": 0},
            FAIL,
            failure_checks,
            contract_version=int(cfg.get("contract_version", 2)),
            schema_errors=[],
            policy_errors=[],
            internal_errors=[fallback_error],
            ledger_signature_status={},
            meaningful_gate={},
        )
        try:
            guard.write_text(z_dir / "FINAL_REPORT.txt", fallback_report)
            guard.write_json(z_dir / "STATUS.json", status_payload)
            guard.write_json(z_dir / "LOGS" / "INDEX.json", _build_log_index(run_id, evaluation.exit_code))
            guard.append_line(run_log, f"[error] {fallback_error}")
        except Exception:
            pass

        append_event(
            {
                "schema_version": 1,
                "ts_utc": ended_at,
                "run_id": run_id,
                "event_type": "RUN_END",
                "actor": INTEGRATOR,
                "parent_event_id": "",
                "duration_ms": 0,
                "file_counts": {},
                "hashes": {},
                "rc": evaluation.exit_code,
                "details": {
                    "kind": "factory",
                    "status": evaluation.status,
                    "error": fallback_error,
                    "path": (RUNS_DIR / run_id).as_posix(),
                },
            }
        )
        return {
            "run_id": run_id,
            "status": evaluation.status,
            "z_dir": z_dir.as_posix(),
            "worker_blockers": 0,
            "overlap_blockers": 0,
            "scope_blockers": 0,
            "error": fallback_error,
            "report": (z_dir / "FINAL_REPORT.txt").as_posix(),
        }
