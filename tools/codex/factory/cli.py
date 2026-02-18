from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from factory.common import INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, stable_sha256_text, write_json
    from factory.config import load_factory_config
    from factory.contracts import load_registry, scaffold_all_bundles, validate_run
    from factory.doctor import run_doctor
    from factory.integrator import integrate_run
    from factory.ledger import append_event, query_events, query_runs, replay_ledger, verify_ledger_signature
    from factory.orchestrator import (
        DEFAULT_PHASE,
        DEFAULT_SLEEP_SEC,
        DEFAULT_TIMEOUT_MIN,
        OperatorCollisionError,
        OperatorError,
        generate_phase_prompts,
        resolve_phase_workers,
        run_external_command,
        runboard_path,
        watch_for_worker_statuses,
    )
    from factory.preflight import run_preflight
    from factory.run_id import next_run_identity
    from factory.schemas import contracts_check, validate_payload
    from factory.smoke import run_smoke
    from factory.status_eval import BLOCKED, FAIL, PASS, combine_statuses, evaluate_status, make_check, status_exit_code
    from factory.version import get_version
    from factory.worktrees import create_worktrees, open_worktrees, sync_worktrees, verify_worktrees
else:
    from .common import INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, stable_sha256_text, write_json
    from .config import load_factory_config
    from .contracts import load_registry, scaffold_all_bundles, validate_run
    from .doctor import run_doctor
    from .integrator import integrate_run
    from .ledger import append_event, query_events, query_runs, replay_ledger, verify_ledger_signature
    from .orchestrator import (
        DEFAULT_PHASE,
        DEFAULT_SLEEP_SEC,
        DEFAULT_TIMEOUT_MIN,
        OperatorCollisionError,
        OperatorError,
        generate_phase_prompts,
        resolve_phase_workers,
        run_external_command,
        runboard_path,
        watch_for_worker_statuses,
    )
    from .preflight import run_preflight
    from .run_id import next_run_identity
    from .schemas import contracts_check, validate_payload
    from .smoke import run_smoke
    from .status_eval import BLOCKED, FAIL, PASS, combine_statuses, evaluate_status, make_check, status_exit_code
    from .version import get_version
    from .worktrees import create_worktrees, open_worktrees, sync_worktrees, verify_worktrees


def _parse_workers(raw: str | None) -> list[str]:
    if raw is None or not raw.strip():
        return sorted(set(WORKERS))
    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    return sorted(set(parsed)) or sorted(set(WORKERS))


def _emit(payload: dict[str, Any], json_out: str | None = None) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True)
    print(text)
    if json_out:
        write_json(Path(json_out), payload)


def _status_from_payload(payload: dict[str, Any], *, fallback: str = BLOCKED) -> str:
    value = str(payload.get("status", "")).upper()
    if value in {PASS, BLOCKED, "FAIL", "WARN", "PENDING"}:
        return value
    return fallback


def _load_runtime_config(args: argparse.Namespace, *, cli_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    return load_factory_config(
        config_path=args.config,
        cli_overrides=cli_overrides or {},
        strict=True,
    )


def _init_run(kind: str, explicit_run_id: str | None, *, base_ref: str, config: dict[str, Any]) -> dict[str, Any]:
    identity = None
    run_id = explicit_run_id
    if run_id is None:
        identity = next_run_identity(kind, base_ref=base_ref)
        run_id = identity.run_id
    run_dir = RUNS_DIR / run_id
    ensure_dir(run_dir)

    manifest = {
        "schema_version": 1,
        "contract_version": int(config.get("contract_version", 2)),
        "run_id": run_id,
        "kind": kind,
        "base_ref": base_ref,
        "base_ref_hash": identity.base_ref_hash if identity else "",
        "status": "PENDING",
        "workers": list(WORKERS),
        "integrator": INTEGRATOR,
        "created_at": identity.stamp if identity else "",
        "paths": {
            "run_dir": run_dir.as_posix(),
            "integrator_dir": (run_dir / INTEGRATOR).as_posix(),
            "logs_dir": (run_dir / "logs").as_posix(),
        },
    }
    manifest_errors = validate_payload("run_manifest", manifest)
    manifest_check = make_check(
        "run_manifest_schema",
        rc=0 if not manifest_errors else 2,
        required=True,
        detail=f"errors={len(manifest_errors)}",
        actor=INTEGRATOR,
    )
    evaluation = evaluate_status(
        required_checks=[manifest_check],
        schema_errors=[f"RUN_MANIFEST.json: {item}" for item in manifest_errors],
        blockers=[],
        internal_errors=[],
    )
    if evaluation.status == PASS:
        write_json(run_dir / "RUN_MANIFEST.json", manifest)

    append_event(
        {
            "schema_version": 1,
            "ts_utc": manifest.get("created_at", "") or "",
            "run_id": run_id,
            "event_type": "RUN_START",
            "actor": INTEGRATOR,
            "parent_event_id": "",
            "duration_ms": 0,
            "file_counts": {},
            "hashes": {"manifest_sha256": stable_sha256_text(json.dumps(manifest, sort_keys=True))},
            "rc": status_exit_code(evaluation.status),
            "details": {
                "kind": kind,
                "status": evaluation.status,
                "path": run_dir.as_posix(),
                "manifest": (run_dir / "RUN_MANIFEST.json").as_posix(),
                "schema_errors": list(evaluation.schema_errors),
            },
        }
    )

    return {
        "status": evaluation.status,
        "run_id": run_id,
        "manifest": (run_dir / "RUN_MANIFEST.json").as_posix(),
        "base_ref": base_ref,
        "schema_errors": list(evaluation.schema_errors),
    }


def _launch_run(
    *,
    run_id: str | None,
    workers: list[str],
    base_ref: str,
    dry_run: bool,
    include_preflight: bool,
    config: dict[str, Any],
) -> dict[str, Any]:
    init_result = _init_run("factory", run_id, base_ref=base_ref, config=config)
    chosen_run_id = str(init_result["run_id"])

    preflight = run_preflight(chosen_run_id) if include_preflight else {"status": PASS, "checks": [], "run_id": chosen_run_id}
    worktrees = create_worktrees(
        chosen_run_id,
        workers=workers,
        base_ref=base_ref,
        dry_run=dry_run,
    )
    bundles = scaffold_all_bundles(chosen_run_id, workers=workers)

    required_checks = [
        make_check("init_run", rc=0 if _status_from_payload(init_result) == PASS else 2, required=True, actor=INTEGRATOR),
        make_check("preflight", rc=0 if _status_from_payload(preflight) == PASS else 2, required=True, actor=INTEGRATOR),
        make_check("worktrees_create", rc=0 if _status_from_payload(worktrees) == PASS else 2, required=True, actor=INTEGRATOR),
        make_check("bundle_scaffold", rc=0, required=True, actor=INTEGRATOR),
    ]

    evaluation = evaluate_status(
        required_checks=required_checks,
        blockers=[],
        schema_errors=[],
        internal_errors=[],
    )

    append_event(
        {
            "schema_version": 1,
            "run_id": chosen_run_id,
            "event_type": "WORKTREE_CREATE",
            "actor": INTEGRATOR,
            "parent_event_id": "",
            "duration_ms": 0,
            "file_counts": {"workers": len(workers)},
            "hashes": {},
            "rc": status_exit_code(evaluation.status),
            "details": {
                "kind": "factory",
                "status": evaluation.status,
                "run_id": chosen_run_id,
                "dry_run": bool(dry_run),
                "workers": workers,
                "worktrees_blocked": int(worktrees.get("blocked", 0)),
            },
        }
    )

    return {
        "status": evaluation.status,
        "run_id": chosen_run_id,
        "init": init_result,
        "preflight": preflight,
        "worktrees": worktrees,
        "bundles": bundles,
        "required_checks": [dict(item) for item in evaluation.required_checks],
    }


def cmd_contracts_check(args: argparse.Namespace) -> int:
    registry = load_registry()
    schema_result = contracts_check()
    payload = {
        "status": PASS if schema_result["status"] == PASS else BLOCKED,
        "schemas": schema_result,
        "registry_version": registry.get("schema_version", 0),
        "workers": registry.get("workers", []),
    }
    _emit(payload, args.json_out)
    return status_exit_code(payload["status"])


def cmd_doctor(args: argparse.Namespace) -> int:
    payload = run_doctor(config_path=args.config)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_init_run(args: argparse.Namespace) -> int:
    config = _load_runtime_config(args, cli_overrides={})
    payload = _init_run(args.kind, args.run_id, base_ref=args.base_ref, config=config)
    _emit(payload, args.json_out)
    return status_exit_code(payload["status"])


def cmd_preflight(args: argparse.Namespace) -> int:
    payload = run_preflight(args.run_id)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_worktrees(args: argparse.Namespace) -> int:
    workers = _parse_workers(args.workers)
    if args.action == "create":
        payload = create_worktrees(args.run_id, workers=workers, base_ref=args.base_ref, dry_run=args.dry_run)
    elif args.action == "verify":
        payload = verify_worktrees(args.run_id, workers=workers)
    elif args.action == "sync":
        payload = sync_worktrees(args.run_id, workers=workers, dry_run=args.dry_run)
    elif args.action == "open":
        payload = open_worktrees(
            args.run_id,
            workers=workers,
            dry_run=args.dry_run,
            new_window=bool(getattr(args, "new_window", False)),
            goto=getattr(args, "goto", None),
        )
    else:
        raise ValueError(f"unsupported worktree action: {args.action}")
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_bundle_init(args: argparse.Namespace) -> int:
    workers = _parse_workers(args.workers)
    payload = scaffold_all_bundles(args.run_id, workers=workers)
    payload["status"] = PASS
    _emit(payload, args.json_out)
    return status_exit_code(payload["status"])


def cmd_bundle_validate(args: argparse.Namespace) -> int:
    workers = _parse_workers(args.workers)
    payload = validate_run(args.run_id, workers=workers)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_integrate(args: argparse.Namespace) -> int:
    workers = _parse_workers(args.workers)
    run_overrides: dict[str, Any] = {}
    if args.strict_collision_mode is not None:
        run_overrides["strict_collision_mode"] = bool(args.strict_collision_mode)
    if args.allow_identical_patch_overlap is not None:
        run_overrides["allow_identical_patch_overlap"] = bool(args.allow_identical_patch_overlap)
    config = _load_runtime_config(
        args,
        cli_overrides={"run": run_overrides} if run_overrides else {},
    )
    payload = integrate_run(args.run_id, workers=workers, config=config)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_launch(args: argparse.Namespace) -> int:
    config = _load_runtime_config(args, cli_overrides={"run": {"base_ref": args.base_ref}})
    payload = _launch_run(
        run_id=args.run_id,
        workers=_parse_workers(args.workers),
        base_ref=args.base_ref,
        dry_run=args.dry_run,
        include_preflight=True,
        config=config,
    )
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_oneshot(args: argparse.Namespace) -> int:
    workers = _parse_workers(args.workers)
    run_overrides: dict[str, Any] = {"base_ref": args.base_ref}
    if args.strict_collision_mode is not None:
        run_overrides["strict_collision_mode"] = bool(args.strict_collision_mode)
    if args.allow_identical_patch_overlap is not None:
        run_overrides["allow_identical_patch_overlap"] = bool(args.allow_identical_patch_overlap)
    config = _load_runtime_config(
        args,
        cli_overrides={"run": run_overrides},
    )
    run_id = args.run_id or next_run_identity("factory", base_ref=args.base_ref).run_id

    stage_payloads: dict[str, dict[str, Any]] = {}
    stage_checks: list[dict[str, Any]] = []

    preflight_payload = run_preflight(run_id)
    append_event(
        {
            "schema_version": 1,
            "run_id": run_id,
            "event_type": "PREFLIGHT",
            "actor": INTEGRATOR,
            "parent_event_id": "",
            "duration_ms": 0,
            "file_counts": {"checks": len(preflight_payload.get("checks", []))},
            "hashes": {},
            "rc": status_exit_code(_status_from_payload(preflight_payload)),
            "details": {"status": _status_from_payload(preflight_payload), "kind": "factory"},
        }
    )
    stage_payloads["preflight"] = preflight_payload
    stage_checks.append(make_check("preflight", rc=0 if _status_from_payload(preflight_payload) == PASS else 2, required=True, actor=INTEGRATOR))
    if _status_from_payload(preflight_payload) != PASS:
        evaluation = evaluate_status(required_checks=stage_checks, blockers=["preflight blocked"], schema_errors=[], internal_errors=[])
        payload = {
            "status": evaluation.status,
            "run_id": run_id,
            "stages": stage_payloads,
            "summary": {
                "final_report": "",
                "required_checks": [dict(item) for item in evaluation.required_checks],
            },
        }
        _emit(payload, args.json_out)
        return evaluation.exit_code

    launch_payload = _launch_run(
        run_id=run_id,
        workers=workers,
        base_ref=args.base_ref,
        dry_run=args.dry_run,
        include_preflight=False,
        config=config,
    )
    stage_payloads["launch"] = launch_payload
    stage_checks.append(make_check("launch", rc=0 if _status_from_payload(launch_payload) == PASS else 2, required=True, actor=INTEGRATOR))
    if _status_from_payload(launch_payload) != PASS:
        evaluation = evaluate_status(required_checks=stage_checks, blockers=["launch blocked"], schema_errors=[], internal_errors=[])
        payload = {
            "status": evaluation.status,
            "run_id": run_id,
            "stages": stage_payloads,
            "summary": {
                "final_report": "",
                "required_checks": [dict(item) for item in evaluation.required_checks],
            },
        }
        _emit(payload, args.json_out)
        return evaluation.exit_code

    validate_payload_result = validate_run(run_id, workers=workers)
    append_event(
        {
            "schema_version": 1,
            "run_id": run_id,
            "event_type": "BUNDLE_VALIDATED",
            "actor": INTEGRATOR,
            "parent_event_id": "",
            "duration_ms": 0,
            "file_counts": {"workers": len(workers)},
            "hashes": {},
            "rc": status_exit_code(_status_from_payload(validate_payload_result)),
            "details": {"status": _status_from_payload(validate_payload_result), "kind": "factory"},
        }
    )
    stage_payloads["bundle_validate"] = validate_payload_result
    stage_checks.append(
        make_check(
            "bundle_validate",
            rc=0 if _status_from_payload(validate_payload_result) == PASS else 2,
            required=True,
            actor=INTEGRATOR,
        )
    )
    if _status_from_payload(validate_payload_result) != PASS:
        evaluation = evaluate_status(required_checks=stage_checks, blockers=["bundle validation blocked"], schema_errors=[], internal_errors=[])
        payload = {
            "status": evaluation.status,
            "run_id": run_id,
            "stages": stage_payloads,
            "summary": {
                "final_report": "",
                "required_checks": [dict(item) for item in evaluation.required_checks],
            },
        }
        _emit(payload, args.json_out)
        return evaluation.exit_code

    integrate_payload = integrate_run(run_id, workers=workers, config=config)
    stage_payloads["integrate"] = integrate_payload
    stage_checks.append(make_check("integrate", rc=0 if _status_from_payload(integrate_payload) == PASS else 2, required=True, actor=INTEGRATOR))

    evaluation = evaluate_status(required_checks=stage_checks, blockers=[], schema_errors=[], internal_errors=[])
    final_report = str(integrate_payload.get("report", ""))

    append_event(
        {
            "schema_version": 1,
            "run_id": run_id,
            "event_type": "ONESHOT_SUMMARY",
            "actor": INTEGRATOR,
            "parent_event_id": "",
            "duration_ms": 0,
            "file_counts": {"workers": len(workers)},
            "hashes": {"summary_sha256": stable_sha256_text(json.dumps(stage_payloads, sort_keys=True))},
            "rc": evaluation.exit_code,
            "details": {
                "kind": "factory",
                "status": evaluation.status,
                "run_id": run_id,
                "workers": workers,
                "final_report": final_report,
                "dry_run": bool(args.dry_run),
            },
        }
    )

    payload = {
        "status": evaluation.status,
        "run_id": run_id,
        "stages": stage_payloads,
        "summary": {
            "final_report": final_report,
            "required_checks": [dict(item) for item in evaluation.required_checks],
        },
    }
    _emit(payload, args.json_out)
    return evaluation.exit_code


def cmd_ledger(args: argparse.Namespace) -> int:
    if args.raw_events:
        rows = query_events(
            run_id=args.run_id,
            event_type=args.event_type,
            actor=args.actor,
            rc=args.rc,
            since=args.since,
            status=args.status,
            kind=args.kind,
            limit=args.limit,
        )
    else:
        rows = query_runs(status=args.status, kind=args.kind, limit=args.limit)
    signature = verify_ledger_signature()
    payload = {
        "status": PASS,
        "count": len(rows),
        "entries": rows,
        "signature": signature,
    }
    _emit(payload, args.json_out)
    return 0


def cmd_ledger_replay(args: argparse.Namespace) -> int:
    payload = replay_ledger(run_id=args.run_id)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload, fallback=PASS))


def cmd_self_test(args: argparse.Namespace) -> int:
    payload = run_smoke(args.run_id)
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_open_report(args: argparse.Namespace) -> int:
    run_id = args.run_id
    target = RUNS_DIR / run_id / INTEGRATOR
    if not target.exists():
        payload = {
            "status": BLOCKED,
            "detail": f"report folder does not exist: {target.as_posix()}",
        }
        _emit(payload, args.json_out)
        return status_exit_code(payload["status"])

    if args.dry_run:
        payload = {
            "status": PASS,
            "detail": "dry-run",
            "target": target.as_posix(),
        }
        _emit(payload, args.json_out)
        return 0

    proc = subprocess.run(["explorer", target.as_posix()], capture_output=True, text=True, check=False)
    payload = {
        "status": PASS if proc.returncode == 0 else "WARN",
        "target": target.as_posix(),
        "rc": proc.returncode,
        "stderr": proc.stderr,
    }
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload, fallback=PASS))


def cmd_open_run(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    if not run_dir.exists():
        payload = {"status": BLOCKED, "detail": f"run folder does not exist: {run_dir.as_posix()}"}
        _emit(payload, args.json_out)
        return status_exit_code(payload["status"])
    if args.dry_run:
        payload = {"status": PASS, "target": run_dir.as_posix(), "detail": "dry-run"}
        _emit(payload, args.json_out)
        return 0
    proc = subprocess.run(["explorer", run_dir.as_posix()], capture_output=True, text=True, check=False)
    payload = {
        "status": PASS if proc.returncode == 0 else "WARN",
        "target": run_dir.as_posix(),
        "rc": proc.returncode,
        "stderr": proc.stderr,
    }
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload, fallback=PASS))


def cmd_print_report(args: argparse.Namespace) -> int:
    report = RUNS_DIR / args.run_id / INTEGRATOR / "FINAL_REPORT.txt"
    if not report.exists():
        payload = {"status": BLOCKED, "detail": f"report missing: {report.as_posix()}", "report": report.as_posix()}
        _emit(payload, args.json_out)
        return status_exit_code(payload["status"])
    lines = report.read_text(encoding="utf-8").splitlines()
    summary = [line for line in lines if line.startswith("- Final status:") or line.startswith("- Worker bundles processed:")]
    payload = {"status": PASS, "report": report.as_posix(), "summary": summary}
    _emit(payload, args.json_out)
    return 0


_PHASE1_AGENT_ACTION = "In each worker VS Code window: Ctrl+Alt+P → New Codex Agent → paste PROMPT_WORKER.txt"


def _as_sorted_unique(values: list[str]) -> list[str]:
    return sorted({str(item).strip() for item in values if str(item).strip()})


def _operator_summary(
    *,
    command: str,
    run_id: str,
    base_ref: str,
    workers: list[str],
    actions_performed: list[str],
    status: str,
    paths_opened: list[str],
    next_steps: list[str],
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "command": command,
        "run_id": run_id,
        "base_ref": base_ref,
        "workers": _as_sorted_unique(workers),
        "actions_performed": _as_sorted_unique(actions_performed),
        "status": status,
        "paths_opened": _as_sorted_unique(paths_opened),
        "next_steps": _as_sorted_unique(next_steps),
    }
    if details:
        payload["details"] = details
    return payload


def _open_in_code(path: Path, *, dry_run: bool, new_window: bool = False, goto: bool = False) -> dict[str, Any]:
    cmd = ["code"]
    if new_window:
        cmd.append("-n")
    if goto:
        cmd.extend(["--goto", path.as_posix()])
    else:
        cmd.append(path.as_posix())
    return run_external_command(cmd, dry_run=dry_run)


def _open_in_explorer(path: Path, *, dry_run: bool) -> dict[str, Any]:
    return run_external_command(["explorer", path.as_posix()], dry_run=dry_run)


def _open_final_report_outputs(
    *,
    run_id: str,
    dry_run: bool,
    open_vscode: bool,
) -> dict[str, Any]:
    report_path = RUNS_DIR / run_id / INTEGRATOR / "FINAL_REPORT.txt"
    run_dir = RUNS_DIR / run_id
    actions: list[dict[str, Any]] = []
    opened_paths: list[str] = []

    if open_vscode:
        report_action = _open_in_code(report_path, dry_run=dry_run, new_window=False, goto=True)
        actions.append(report_action)
        if int(report_action.get("rc", 1)) == 0:
            opened_paths.append(report_path.as_posix())

    explorer_action = _open_in_explorer(run_dir, dry_run=dry_run)
    actions.append(explorer_action)
    if int(explorer_action.get("rc", 1)) == 0:
        opened_paths.append(run_dir.as_posix())

    return {
        "actions": actions,
        "opened_paths": sorted(set(opened_paths)),
        "status": PASS if all(int(item.get("rc", 1)) == 0 for item in actions) else "WARN",
    }


def _bundle_init_with_optional_dry_run(run_id: str, *, workers: list[str], dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "run_id": run_id,
            "workers": [{"worker": worker, "bundle_dir": (RUNS_DIR / run_id / worker).as_posix(), "created": []} for worker in workers],
            "integrator": {"worker": INTEGRATOR, "bundle_dir": (RUNS_DIR / run_id / INTEGRATOR).as_posix(), "created": []},
            "status": PASS,
            "detail": "dry-run planned bundle scaffold",
        }
    payload = scaffold_all_bundles(run_id, workers=workers)
    payload["status"] = PASS
    return payload


def _verify_worktrees_with_optional_dry_run(run_id: str, *, workers: list[str], dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {
            "run_id": run_id,
            "operation": "verify",
            "status": PASS,
            "steps": [
                {
                    "worker": worker,
                    "status": PASS,
                    "path": (Path("tools") / "codex" / "worktrees" / run_id / worker).as_posix(),
                    "detail": "dry-run planned verification",
                }
                for worker in workers
            ],
            "blocked": 0,
            "detail": "dry-run planned worktree verification",
        }
    return verify_worktrees(run_id, workers=workers)


def _init_run_if_needed(
    *,
    run_id: str | None,
    base_ref: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    if run_id:
        manifest_path = RUNS_DIR / run_id / "RUN_MANIFEST.json"
        if manifest_path.exists():
            return {
                "status": PASS,
                "run_id": run_id,
                "manifest": manifest_path.as_posix(),
                "base_ref": base_ref,
                "schema_errors": [],
                "detail": "existing run manifest reused",
            }
    return _init_run("factory", run_id, base_ref=base_ref, config=config)


def _collect_opened_worktree_targets(payload: dict[str, Any]) -> list[str]:
    opened: list[str] = []
    for step in payload.get("steps", []):
        if str(step.get("status", "")).upper() == BLOCKED:
            continue
        goto = str(step.get("goto", "")).strip()
        target = goto or str(step.get("path", "")).strip()
        if target:
            opened.append(target)
    return sorted(set(opened))


def _operator_bootstrap_payload(
    *,
    run_id: str | None,
    base_ref: str,
    workers_raw: str | None,
    phase: str,
    open_vscode: bool,
    goto_prompt: bool,
    open_runboard: bool,
    dry_run: bool,
    config_path: str | None,
) -> dict[str, Any]:
    actions: list[str] = []
    paths_opened: list[str] = []
    next_steps: list[str] = []
    stage_details: dict[str, Any] = {}

    workers = resolve_phase_workers(phase, workers_raw)
    preflight_payload = run_preflight(run_id)
    actions.append("preflight")
    stage_details["preflight"] = preflight_payload
    if _status_from_payload(preflight_payload) != PASS:
        return _operator_summary(
            command="operator bootstrap",
            run_id=run_id or "",
            base_ref=base_ref,
            workers=workers,
            actions_performed=actions,
            status=BLOCKED,
            paths_opened=paths_opened,
            next_steps=[
                "Resolve preflight blockers before bootstrap.",
            ],
            details=stage_details,
        )

    config = load_factory_config(
        config_path=config_path,
        cli_overrides={"run": {"base_ref": base_ref}},
        strict=True,
    )
    init_payload = _init_run_if_needed(run_id=run_id, base_ref=base_ref, config=config)
    actions.append("init-run")
    stage_details["init_run"] = init_payload
    chosen_run_id = str(init_payload.get("run_id", run_id or ""))
    if _status_from_payload(init_payload) != PASS:
        return _operator_summary(
            command="operator bootstrap",
            run_id=chosen_run_id,
            base_ref=base_ref,
            workers=workers,
            actions_performed=actions,
            status=BLOCKED,
            paths_opened=paths_opened,
            next_steps=[
                "Resolve run initialization blockers before bootstrap.",
            ],
            details=stage_details,
        )

    create_payload = create_worktrees(chosen_run_id, workers=workers, base_ref=base_ref, dry_run=dry_run)
    actions.append("worktrees create")
    stage_details["worktrees_create"] = create_payload

    bundles_payload = _bundle_init_with_optional_dry_run(chosen_run_id, workers=workers, dry_run=dry_run)
    actions.append("bundle-init")
    stage_details["bundle_init"] = bundles_payload

    verify_payload = _verify_worktrees_with_optional_dry_run(chosen_run_id, workers=workers, dry_run=dry_run)
    actions.append("worktrees verify")
    stage_details["worktrees_verify"] = verify_payload

    prompts_payload = generate_phase_prompts(
        run_id=chosen_run_id,
        base_ref=base_ref,
        phase=phase,
        workers=workers,
        dry_run=dry_run,
    )
    actions.append("prompts generate")
    stage_details["prompts"] = prompts_payload

    if open_vscode:
        worktree_open_payload = open_worktrees(
            chosen_run_id,
            workers=workers,
            dry_run=dry_run,
            new_window=True,
            goto="PROMPT_WORKER.txt" if goto_prompt else None,
        )
        actions.append("worktrees open")
        stage_details["worktrees_open"] = worktree_open_payload
        paths_opened.extend(_collect_opened_worktree_targets(worktree_open_payload))

    if open_runboard:
        board_path = runboard_path(chosen_run_id)
        runboard_open_payload = _open_in_code(
            board_path,
            dry_run=dry_run,
            new_window=False,
            goto=False,
        )
        actions.append("open runboard")
        stage_details["runboard_open"] = runboard_open_payload
        if int(runboard_open_payload.get("rc", 1)) == 0:
            paths_opened.append(board_path.as_posix())

    stage_statuses = [
        _status_from_payload(create_payload),
        _status_from_payload(bundles_payload),
        _status_from_payload(verify_payload),
        _status_from_payload(prompts_payload),
    ]
    final_status = combine_statuses(stage_statuses)
    if final_status not in {PASS, BLOCKED, FAIL}:
        final_status = BLOCKED

    if final_status == PASS:
        next_steps.append(f"Run: python -m tools.codex.factory operator watch --run-id {chosen_run_id}")
        if open_vscode:
            next_steps.append(_PHASE1_AGENT_ACTION)
    else:
        next_steps.append("Review bootstrap stage details and resolve blockers before rerunning.")

    return _operator_summary(
        command="operator bootstrap",
        run_id=chosen_run_id,
        base_ref=base_ref,
        workers=workers,
        actions_performed=actions,
        status=final_status,
        paths_opened=paths_opened,
        next_steps=next_steps,
        details=stage_details,
    )


def _operator_watch_payload(
    *,
    run_id: str,
    base_ref: str,
    workers_raw: str | None,
    phase: str,
    sleep_sec: int,
    timeout_min: int,
    open_vscode: bool,
    open_final_report: bool,
    dry_run: bool,
    config_path: str | None,
) -> dict[str, Any]:
    actions: list[str] = []
    paths_opened: list[str] = []
    next_steps: list[str] = []
    stage_details: dict[str, Any] = {}

    workers = resolve_phase_workers(phase, workers_raw)

    def _progress(progress_payload: dict[str, Any]) -> None:
        missing = ",".join(progress_payload.get("missing", []))
        present = ",".join(progress_payload.get("present", []))
        print(
            f"[operator.watch] iteration={progress_payload.get('iteration', 0)} present=[{present}] missing=[{missing}]",
            file=sys.stderr,
            flush=True,
        )

    watch_payload = watch_for_worker_statuses(
        run_id=run_id,
        workers=workers,
        sleep_sec=sleep_sec,
        timeout_min=timeout_min,
        dry_run=dry_run,
        on_progress=None if dry_run else _progress,
    )
    actions.append("watch worker statuses")
    stage_details["watch"] = watch_payload

    if dry_run:
        actions.append("bundle-validate (planned)")
        actions.append("integrate (planned)")
        next_steps.append("Run operator watch without --dry-run after workers complete.")
        return _operator_summary(
            command="operator watch",
            run_id=run_id,
            base_ref=base_ref,
            workers=workers,
            actions_performed=actions,
            status=PASS,
            paths_opened=paths_opened,
            next_steps=next_steps,
            details=stage_details,
        )

    if _status_from_payload(watch_payload) != PASS or not bool(watch_payload.get("ready", False)):
        next_steps.append("Ensure all worker STATUS.json files exist, then rerun operator watch.")
        return _operator_summary(
            command="operator watch",
            run_id=run_id,
            base_ref=base_ref,
            workers=workers,
            actions_performed=actions,
            status=BLOCKED,
            paths_opened=paths_opened,
            next_steps=next_steps,
            details=stage_details,
        )

    validate_payload = validate_run(run_id, workers=workers)
    actions.append("bundle-validate")
    stage_details["bundle_validate"] = validate_payload
    if _status_from_payload(validate_payload) != PASS:
        next_steps.append("Fix bundle validation blockers, then rerun operator watch.")
        return _operator_summary(
            command="operator watch",
            run_id=run_id,
            base_ref=base_ref,
            workers=workers,
            actions_performed=actions,
            status=BLOCKED,
            paths_opened=paths_opened,
            next_steps=next_steps,
            details=stage_details,
        )

    config = load_factory_config(
        config_path=config_path,
        cli_overrides={"run": {"base_ref": base_ref}},
        strict=True,
    )
    integrate_payload = integrate_run(run_id, workers=workers, config=config)
    actions.append("integrate")
    stage_details["integrate"] = integrate_payload

    final_status = _status_from_payload(integrate_payload, fallback=BLOCKED)
    if final_status == PASS:
        next_steps.append("Review tools/codex/runs/<RUN_ID>/Z_integrator/FINAL_REPORT.txt.")
    else:
        next_steps.append("Inspect integration logs and resolve blockers.")

    if open_final_report:
        final_open_payload = _open_final_report_outputs(run_id=run_id, dry_run=False, open_vscode=open_vscode)
        actions.append("open final report outputs")
        stage_details["open_final_report"] = final_open_payload
        paths_opened.extend(final_open_payload.get("opened_paths", []))

    return _operator_summary(
        command="operator watch",
        run_id=run_id,
        base_ref=base_ref,
        workers=workers,
        actions_performed=actions,
        status=final_status if final_status in {PASS, BLOCKED, FAIL} else BLOCKED,
        paths_opened=paths_opened,
        next_steps=next_steps,
        details=stage_details,
    )


def cmd_operator_bootstrap(args: argparse.Namespace) -> int:
    try:
        payload = _operator_bootstrap_payload(
            run_id=args.run_id,
            base_ref=args.base_ref,
            workers_raw=args.workers,
            phase=args.phase,
            open_vscode=bool(args.open_vscode),
            goto_prompt=bool(args.goto_prompt),
            open_runboard=bool(args.open_runboard),
            dry_run=bool(args.dry_run),
            config_path=args.config,
        )
    except (OperatorError, OperatorCollisionError) as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator bootstrap",
            run_id=args.run_id or "",
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=BLOCKED,
            paths_opened=[],
            next_steps=["Resolve collision/policy issues and rerun bootstrap."],
            details={"error": str(exc)},
        )
    except Exception as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator bootstrap",
            run_id=args.run_id or "",
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=FAIL,
            paths_opened=[],
            next_steps=["Inspect internal errors and rerun bootstrap."],
            details={"error": str(exc)},
        )
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_operator_watch(args: argparse.Namespace) -> int:
    try:
        payload = _operator_watch_payload(
            run_id=args.run_id,
            base_ref=args.base_ref,
            workers_raw=args.workers,
            phase=args.phase,
            sleep_sec=args.sleep_sec,
            timeout_min=args.timeout_min,
            open_vscode=bool(args.open_vscode),
            open_final_report=bool(args.open_final_report),
            dry_run=bool(args.dry_run),
            config_path=args.config,
        )
    except (OperatorError, OperatorCollisionError) as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator watch",
            run_id=args.run_id,
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=BLOCKED,
            paths_opened=[],
            next_steps=["Resolve collision/policy issues and rerun watch."],
            details={"error": str(exc)},
        )
    except Exception as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator watch",
            run_id=args.run_id,
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=FAIL,
            paths_opened=[],
            next_steps=["Inspect internal errors and rerun watch."],
            details={"error": str(exc)},
        )
    _emit(payload, args.json_out)
    return status_exit_code(_status_from_payload(payload))


def cmd_operator_phase1_extract(args: argparse.Namespace) -> int:
    try:
        bootstrap_payload = _operator_bootstrap_payload(
            run_id=args.run_id,
            base_ref=args.base_ref,
            workers_raw=args.workers,
            phase=DEFAULT_PHASE,
            open_vscode=bool(args.open_vscode),
            goto_prompt=bool(args.goto_prompt),
            open_runboard=bool(args.open_runboard),
            dry_run=bool(args.dry_run),
            config_path=args.config,
        )
        chosen_run_id = str(bootstrap_payload.get("run_id", args.run_id or ""))
        if _status_from_payload(bootstrap_payload) != PASS:
            payload = _operator_summary(
                command="operator phase1-extract",
                run_id=chosen_run_id,
                base_ref=args.base_ref,
                workers=list(bootstrap_payload.get("workers", [])),
                actions_performed=list(bootstrap_payload.get("actions_performed", [])),
                status=_status_from_payload(bootstrap_payload),
                paths_opened=list(bootstrap_payload.get("paths_opened", [])),
                next_steps=["Resolve bootstrap blockers before phase1 watch/integrate."],
                details={"bootstrap": bootstrap_payload},
            )
            _emit(payload, args.json_out)
            print(_PHASE1_AGENT_ACTION, file=sys.stderr, flush=True)
            return status_exit_code(_status_from_payload(payload))

        watch_payload = _operator_watch_payload(
            run_id=chosen_run_id,
            base_ref=args.base_ref,
            workers_raw=args.workers,
            phase=DEFAULT_PHASE,
            sleep_sec=args.sleep_sec,
            timeout_min=args.timeout_min,
            open_vscode=bool(args.open_vscode),
            open_final_report=bool(args.open_final_report),
            dry_run=bool(args.dry_run),
            config_path=args.config,
        )

        merged_actions = list(bootstrap_payload.get("actions_performed", [])) + list(watch_payload.get("actions_performed", []))
        merged_paths = list(bootstrap_payload.get("paths_opened", [])) + list(watch_payload.get("paths_opened", []))
        merged_next_steps = list(bootstrap_payload.get("next_steps", [])) + list(watch_payload.get("next_steps", []))
        merged_next_steps.append(_PHASE1_AGENT_ACTION)

        statuses = [_status_from_payload(bootstrap_payload), _status_from_payload(watch_payload)]
        final_status = combine_statuses(statuses)
        if final_status not in {PASS, BLOCKED, FAIL}:
            final_status = BLOCKED

        payload = _operator_summary(
            command="operator phase1-extract",
            run_id=chosen_run_id,
            base_ref=args.base_ref,
            workers=list(bootstrap_payload.get("workers", [])),
            actions_performed=merged_actions,
            status=final_status,
            paths_opened=merged_paths,
            next_steps=merged_next_steps,
            details={
                "bootstrap": bootstrap_payload,
                "watch": watch_payload,
            },
        )
    except (OperatorError, OperatorCollisionError) as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator phase1-extract",
            run_id=args.run_id or "",
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=BLOCKED,
            paths_opened=[],
            next_steps=["Resolve collision/policy issues and rerun phase1-extract."],
            details={"error": str(exc)},
        )
    except Exception as exc:
        workers = _parse_workers(args.workers)
        payload = _operator_summary(
            command="operator phase1-extract",
            run_id=args.run_id or "",
            base_ref=args.base_ref,
            workers=workers,
            actions_performed=[],
            status=FAIL,
            paths_opened=[],
            next_steps=["Inspect internal errors and rerun phase1-extract."],
            details={"error": str(exc)},
        )
    _emit(payload, args.json_out)
    print(_PHASE1_AGENT_ACTION, file=sys.stderr, flush=True)
    return status_exit_code(_status_from_payload(payload))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m tools.codex.factory",
        description=f"HITECH OS multi-codex factory tooling (v{get_version()})",
        epilog="Example: python -m tools.codex.factory oneshot --base-ref HEAD --dry-run",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")
    parser.add_argument("--json-out", help="Optional path to write machine-readable output JSON")
    parser.add_argument("--config", help="Optional factory config file path")
    sub = parser.add_subparsers(dest="command", required=True)

    contracts = sub.add_parser("contracts-check", help="Validate factory contracts and schema registry")
    contracts.set_defaults(func=cmd_contracts_check)

    doctor = sub.add_parser("doctor", help="Check local factory setup and contracts")
    doctor.set_defaults(func=cmd_doctor)

    init_run = sub.add_parser("init-run", help="Create deterministic run folder and manifest")
    init_run.add_argument("--run-id", help="Optional explicit run id")
    init_run.add_argument("--kind", default="factory", help="Run type prefix")
    init_run.add_argument("--base-ref", default="HEAD")
    init_run.set_defaults(func=cmd_init_run)

    preflight = sub.add_parser("preflight", help="Run factory preflight checks")
    preflight.add_argument("--run-id", help="Optional run id for log emission")
    preflight.set_defaults(func=cmd_preflight)

    worktrees = sub.add_parser("worktrees", help="Manage worker worktrees")
    worktrees.add_argument("action", choices=["create", "verify", "sync", "open"])
    worktrees.add_argument("--run-id", required=True)
    worktrees.add_argument("--workers", help="Comma-separated worker IDs")
    worktrees.add_argument("--base-ref", default="HEAD")
    worktrees.add_argument("--dry-run", action="store_true")
    worktrees.add_argument("--new-window", action="store_true", help="Open each worktree in a new VS Code window")
    worktrees.add_argument("--goto", help="Optional relative/absolute file path to open with --goto in each worktree")
    worktrees.set_defaults(func=cmd_worktrees)

    bundle_init = sub.add_parser("bundle-init", help="Scaffold worker bundles for a run")
    bundle_init.add_argument("--run-id", required=True)
    bundle_init.add_argument("--workers", help="Comma-separated worker IDs")
    bundle_init.set_defaults(func=cmd_bundle_init)

    bundle_validate = sub.add_parser("bundle-validate", help="Validate bundle structure and schemas")
    bundle_validate.add_argument("--run-id", required=True)
    bundle_validate.add_argument("--workers", help="Comma-separated worker IDs")
    bundle_validate.set_defaults(func=cmd_bundle_validate)

    integrate = sub.add_parser("integrate", help="Run Z integrator pipeline")
    integrate.add_argument("--run-id", required=True)
    integrate.add_argument("--workers", help="Comma-separated worker IDs")
    integrate.add_argument("--strict-collision-mode", action="store_true", default=None)
    integrate.add_argument("--allow-identical-patch-overlap", action="store_true", default=None)
    integrate.set_defaults(func=cmd_integrate)

    launch = sub.add_parser("launch", help="One-command preflight + run init + worktree + bundle scaffold")
    launch.add_argument("--run-id", help="Optional run id")
    launch.add_argument("--workers", help="Comma-separated worker IDs")
    launch.add_argument("--base-ref", default="HEAD")
    launch.add_argument("--dry-run", action="store_true")
    launch.set_defaults(func=cmd_launch)

    oneshot = sub.add_parser("oneshot", help="Run preflight -> launch -> bundle-validate -> integrate -> summary")
    oneshot.add_argument("--run-id", help="Optional explicit run id")
    oneshot.add_argument("--workers", help="Comma-separated worker IDs")
    oneshot.add_argument("--base-ref", default="HEAD")
    oneshot.add_argument("--dry-run", action="store_true")
    oneshot.add_argument("--strict-collision-mode", action="store_true", default=None)
    oneshot.add_argument("--allow-identical-patch-overlap", action="store_true", default=None)
    oneshot.set_defaults(func=cmd_oneshot)

    ledger = sub.add_parser("ledger", help="Query run ledger")
    ledger.add_argument("--status")
    ledger.add_argument("--kind")
    ledger.add_argument("--run-id")
    ledger.add_argument("--actor")
    ledger.add_argument("--event-type")
    ledger.add_argument("--rc", type=int)
    ledger.add_argument("--since", help="ISO8601 lower bound for ts_utc")
    ledger.add_argument("--raw-events", action="store_true")
    ledger.add_argument("--limit", type=int, default=50)
    ledger.set_defaults(func=cmd_ledger)

    ledger_replay = sub.add_parser("ledger-replay", help="Replay ledger events and reconstruct run states")
    ledger_replay.add_argument("--run-id")
    ledger_replay.set_defaults(func=cmd_ledger_replay)

    self_test = sub.add_parser("self-test", help="Run deterministic factory smoke test")
    self_test.add_argument("--run-id", help="Optional run id")
    self_test.set_defaults(func=cmd_self_test)

    open_report = sub.add_parser("open-report", help="Open integrator report folder in Explorer")
    open_report.add_argument("--run-id", required=True)
    open_report.add_argument("--dry-run", action="store_true")
    open_report.set_defaults(func=cmd_open_report)

    open_run = sub.add_parser("open-run", help="Open full run folder in Explorer")
    open_run.add_argument("--run-id", required=True)
    open_run.add_argument("--dry-run", action="store_true")
    open_run.set_defaults(func=cmd_open_run)

    print_report = sub.add_parser("print-report", help="Print FINAL_REPORT path and summary")
    print_report.add_argument("--run-id", required=True)
    print_report.set_defaults(func=cmd_print_report)

    operator = sub.add_parser("operator", help="Operator orchestrator commands")
    operator_sub = operator.add_subparsers(dest="operator_command", required=True)

    operator_bootstrap = operator_sub.add_parser(
        "bootstrap",
        help="Preflight -> init-run -> worktrees create -> bundle-init -> worktrees verify -> prompt/runboard generation",
    )
    operator_bootstrap.add_argument("--run-id", help="Optional explicit run id")
    operator_bootstrap.add_argument("--base-ref", default="HEAD")
    operator_bootstrap.add_argument("--workers", default=",".join(sorted(WORKERS)), help="Comma-separated worker IDs")
    operator_bootstrap.add_argument("--phase", default=DEFAULT_PHASE)
    operator_bootstrap.add_argument("--open-vscode", action=argparse.BooleanOptionalAction, default=False)
    operator_bootstrap.add_argument("--goto-prompt", action=argparse.BooleanOptionalAction, default=True)
    operator_bootstrap.add_argument("--open-runboard", action=argparse.BooleanOptionalAction, default=True)
    operator_bootstrap.add_argument("--dry-run", action="store_true")
    operator_bootstrap.set_defaults(func=cmd_operator_bootstrap)

    operator_watch = operator_sub.add_parser(
        "watch",
        help="Watch worker STATUS.json files, then run bundle-validate + integrate",
    )
    operator_watch.add_argument("--run-id", required=True)
    operator_watch.add_argument("--base-ref", default="HEAD")
    operator_watch.add_argument("--workers", default=",".join(sorted(WORKERS)), help="Comma-separated worker IDs")
    operator_watch.add_argument("--phase", default=DEFAULT_PHASE)
    operator_watch.add_argument("--sleep-sec", type=int, default=DEFAULT_SLEEP_SEC)
    operator_watch.add_argument("--timeout-min", type=int, default=DEFAULT_TIMEOUT_MIN)
    operator_watch.add_argument("--open-vscode", action=argparse.BooleanOptionalAction, default=False)
    operator_watch.add_argument("--open-final-report", action=argparse.BooleanOptionalAction, default=True)
    operator_watch.add_argument("--dry-run", action="store_true")
    operator_watch.set_defaults(func=cmd_operator_watch)

    operator_phase1 = operator_sub.add_parser(
        "phase1-extract",
        help="Bootstrap + worker watch + bundle-validate + integrate flow for phase1 extraction",
    )
    operator_phase1.add_argument("--run-id", help="Optional explicit run id")
    operator_phase1.add_argument("--base-ref", default="HEAD")
    operator_phase1.add_argument("--workers", default=",".join(sorted(WORKERS)), help="Comma-separated worker IDs")
    operator_phase1.add_argument("--sleep-sec", type=int, default=DEFAULT_SLEEP_SEC)
    operator_phase1.add_argument("--timeout-min", type=int, default=DEFAULT_TIMEOUT_MIN)
    operator_phase1.add_argument("--open-vscode", action=argparse.BooleanOptionalAction, default=True)
    operator_phase1.add_argument("--goto-prompt", action=argparse.BooleanOptionalAction, default=True)
    operator_phase1.add_argument("--open-runboard", action=argparse.BooleanOptionalAction, default=True)
    operator_phase1.add_argument("--open-final-report", action=argparse.BooleanOptionalAction, default=True)
    operator_phase1.add_argument("--dry-run", action="store_true")
    operator_phase1.set_defaults(func=cmd_operator_phase1_extract)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
