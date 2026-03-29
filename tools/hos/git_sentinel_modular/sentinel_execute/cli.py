from __future__ import annotations

import argparse
import json

from .bundle import build_execution_bundle, execute_manual_promotion

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or execute an execution bundle.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan")
    plan_parser.add_argument("--workspace-root", required=True)
    plan_parser.add_argument("--target-root", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--workspace-root", required=True)
    run_parser.add_argument("--target-root", required=True)
    run_parser.add_argument("--confirm-token", required=True)

    args = parser.parse_args(argv)
    if args.command == "plan":
        payload = build_execution_bundle(args.workspace_root, args.target_root, plan_only=True)
    else:
        payload = execute_manual_promotion(
            args.workspace_root,
            args.target_root,
            do_execute=True,
            confirm_token=args.confirm_token,
        )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0
