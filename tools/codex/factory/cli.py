from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from factory.common import INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, stable_sha256_text, write_json
    from factory.config import load_factory_config
    from factory.contracts import load_registry, scaffold_all_bundles, validate_run
    from factory.doctor import run_doctor
    from factory.integrator import integrate_run
    from factory.ledger import append_event, query_events, query_runs, replay_ledger, verify_ledger_signature
    from factory.preflight import run_preflight
    from factory.run_id import next_run_identity
    from factory.schemas import contracts_check, validate_payload
    from factory.smoke import run_smoke
    from factory.status_eval import BLOCKED, PASS, evaluate_status, make_check, status_exit_code
    from factory.version import get_version
    from factory.worktrees import create_worktrees, open_worktrees, sync_worktrees, verify_worktrees
else:
    from .common import INTEGRATOR, RUNS_DIR, WORKERS, ensure_dir, stable_sha256_text, write_json
    from .config import load_factory_config
    from .contracts import load_registry, scaffold_all_bundles, validate_run
    from .doctor import run_doctor
    from .integrator import integrate_run
    from .ledger import append_event, query_events, query_runs, replay_ledger, verify_ledger_signature
    from .preflight import run_preflight
    from .run_id import next_run_identity
    from .schemas import contracts_check, validate_payload
    from .smoke import run_smoke
    from .status_eval import BLOCKED, PASS, evaluate_status, make_check, status_exit_code
    from .version import get_version
    from .worktrees import create_worktrees, open_worktrees, sync_worktrees, verify_worktrees


def _parse_workers(raw: str | None) -> list[str]:
    if raw is None or not raw.strip():
        return list(WORKERS)
    parsed = [item.strip() for item in raw.split(",") if item.strip()]
    return parsed or list(WORKERS)


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
        payload = open_worktrees(args.run_id, workers=workers, dry_run=args.dry_run)
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


def cmd_watch(args: argparse.Namespace) -> int:
    run_dir = RUNS_DIR / args.run_id
    if not run_dir.exists():
        payload = {
            "status": BLOCKED,
            "run_id": args.run_id,
            "detail": f"run folder does not exist: {run_dir.as_posix()}",
        }
        _emit(payload, args.json_out)
        return status_exit_code(payload["status"])

    z_status_path = run_dir / INTEGRATOR / "STATUS.json"
    gate_path = run_dir / "VERIFY_MEANINGFUL_GATE.json"
    integrator_status = BLOCKED
    integrator_payload: dict[str, Any] = {}
    gate_payload: dict[str, Any] = {}
    gate_verdict = BLOCKED

    if z_status_path.exists():
        try:
            integrator_payload = json.loads(z_status_path.read_text(encoding="utf-8"))
            integrator_status = _status_from_payload(integrator_payload)
        except Exception as exc:
            integrator_status = BLOCKED
            integrator_payload = {"status": BLOCKED, "error": str(exc)}

    if gate_path.exists():
        try:
            gate_payload = json.loads(gate_path.read_text(encoding="utf-8"))
            gate_verdict = str(gate_payload.get("verdict", BLOCKED)).upper()
        except Exception as exc:
            gate_payload = {"verdict": BLOCKED, "error": str(exc), "fail_modes": ["UNREADABLE_REPORT"]}
            gate_verdict = BLOCKED

    if integrator_status == "FAIL":
        final_status = "FAIL"
    elif integrator_status != PASS:
        final_status = BLOCKED
    elif gate_verdict in {PASS, "WARN"}:
        final_status = PASS
    else:
        final_status = BLOCKED

    summary = {
        "run_id": args.run_id,
        "integrator_status": integrator_status,
        "meaningful_gate_verdict": gate_verdict if gate_path.exists() else "MISSING",
        "meaningful_gate_fail_modes": list(gate_payload.get("fail_modes", [])) if gate_payload else [],
        "noop": bool(gate_payload.get("noop", False)),
        "phase_progress": bool(final_status == PASS and not gate_payload.get("noop", False)),
    }
    payload = {
        "status": final_status,
        "run_id": args.run_id,
        "run_dir": run_dir.as_posix(),
        "summary": summary,
        "integrator": {
            "status_path": z_status_path.as_posix(),
            "payload": integrator_payload,
        },
        "meaningful_gate": {
            "path": gate_path.as_posix(),
            "exists": gate_path.exists(),
            "payload": gate_payload,
        },
    }
    _emit(payload, args.json_out)
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

    watch = sub.add_parser("watch", help="Summarize run status including meaningful gate verdict")
    watch.add_argument("--run-id", required=True)
    watch.set_defaults(func=cmd_watch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
