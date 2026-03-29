from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ..operations.status import build_combined_status
from ..plugins.registry import list_registered_plugins
from ..sentinel_cutover.bundle import build_cutover_readiness_bundle
from ..sentinel_execute.bundle import build_execution_bundle, execute_manual_promotion
from ..sentinel_promotion.bundle import build_promotion_bundle
from ..sentinel_shadow.runner import prepare_shadow_run
from ..sentinel_shadow_apply.engine import run_shadow_apply_engine
from ..sentinel_shadow_apply.overlay_plan import build_overlay_plan

def run_rollout_pipeline_plan_only(
    *,
    run_id: str,
    source_root: str | Path,
    target_root: str | Path,
    overlay_mutations: dict[str, str] | list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    prepared = prepare_shadow_run(run_id=run_id, source_root=source_root)
    workspace_root = prepared["workspace_root"]
    plan = build_overlay_plan(overlay_mutations or {})
    apply_engine = run_shadow_apply_engine(workspace_root, plan, dry_run=False)
    promotion = build_promotion_bundle(
        workspace_root,
        diff_manifest=apply_engine["diff_manifest"],
        apply_result=apply_engine["apply_result"],
    )
    cutover = build_cutover_readiness_bundle(workspace_root)
    execution = build_execution_bundle(workspace_root, target_root, plan_only=True)
    dry_run_summary = execute_manual_promotion(
        workspace_root,
        target_root,
        do_execute=False,
    )
    return {
        "workspace_root": workspace_root,
        "apply_counts": apply_engine["apply_result"]["manifest"],
        "diff_counts": apply_engine["diff_manifest"]["counts"],
        "gate_allowed": apply_engine["gate"]["allowed"],
        "promotion_status": promotion["status"],
        "cutover_status": cutover["status"],
        "cutover_risk": cutover["overall_risk"],
        "execution_counts": execution["counts"],
        "execute_dry_run_summary": dry_run_summary,
    }

def _print_json(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Canonical CLI for git_sentinel_modular.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    shadow_parser = subparsers.add_parser("shadow-prepare")
    shadow_parser.add_argument("--run-id", required=True)
    shadow_parser.add_argument("--source-root", required=True)

    promotion_parser = subparsers.add_parser("promotion")
    promotion_parser.add_argument("--workspace-root", required=True)

    cutover_parser = subparsers.add_parser("cutover")
    cutover_parser.add_argument("--workspace-root", required=True)

    execute_plan_parser = subparsers.add_parser("execute-plan")
    execute_plan_parser.add_argument("--workspace-root", required=True)
    execute_plan_parser.add_argument("--target-root", required=True)

    execute_run_parser = subparsers.add_parser("execute-run")
    execute_run_parser.add_argument("--workspace-root", required=True)
    execute_run_parser.add_argument("--target-root", required=True)
    execute_run_parser.add_argument("--confirm-token", required=True)

    pipeline_parser = subparsers.add_parser("pipeline-plan-only")
    pipeline_parser.add_argument("--run-id", required=True)
    pipeline_parser.add_argument("--source-root", required=True)
    pipeline_parser.add_argument("--target-root", required=True)

    subparsers.add_parser("status")
    subparsers.add_parser("plugin-list")

    args = parser.parse_args(argv)

    if args.command == "shadow-prepare":
        return _print_json(prepare_shadow_run(run_id=args.run_id, source_root=args.source_root))
    if args.command == "promotion":
        return _print_json(build_promotion_bundle(args.workspace_root))
    if args.command == "cutover":
        return _print_json(build_cutover_readiness_bundle(args.workspace_root))
    if args.command == "execute-plan":
        return _print_json(build_execution_bundle(args.workspace_root, args.target_root, plan_only=True))
    if args.command == "execute-run":
        return _print_json(execute_manual_promotion(
            args.workspace_root,
            args.target_root,
            do_execute=True,
            confirm_token=args.confirm_token,
        ))
    if args.command == "pipeline-plan-only":
        return _print_json(run_rollout_pipeline_plan_only(
            run_id=args.run_id,
            source_root=args.source_root,
            target_root=args.target_root,
        ))
    if args.command == "status":
        return _print_json(build_combined_status().to_dict())
    if args.command == "plugin-list":
        return _print_json({"plugins": list_registered_plugins()})
    return 1
