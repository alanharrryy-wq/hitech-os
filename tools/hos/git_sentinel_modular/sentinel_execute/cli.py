from pathlib import Path
import argparse
import json

from .bundle import build_execution_bundle, execute_manual_promotion

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build or execute a manual promotion bundle from a shadow workspace."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="Build execution bundle only.")
    p_plan.add_argument("--workspace-root", required=True)
    p_plan.add_argument("--target-root", required=True)
    p_plan.add_argument("--policy", required=False)

    p_exec = sub.add_parser("execute", help="Execute manual promotion.")
    p_exec.add_argument("--workspace-root", required=True)
    p_exec.add_argument("--target-root", required=True)
    p_exec.add_argument("--policy", required=False)
    p_exec.add_argument("--confirm-token", required=False)
    p_exec.add_argument("--do-execute", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "plan":
        result = build_execution_bundle(
            workspace_root=Path(args.workspace_root),
            target_root=Path(args.target_root),
            policy_path=Path(args.policy) if args.policy else None,
        )
        print(json.dumps({
            "execution_dir": str(result["execution_dir"]),
            "planned_actions": result["plan_payload"]["counts"]["actions"],
            "blocked": result["plan_payload"]["counts"]["blocked"],
        }, indent=2, sort_keys=True))
        return 0

    if args.cmd == "execute":
        result = execute_manual_promotion(
            workspace_root=Path(args.workspace_root),
            target_root=Path(args.target_root),
            policy_path=Path(args.policy) if args.policy else None,
            do_execute=args.do_execute,
            confirm_token=args.confirm_token,
        )
        print(json.dumps(result["summary"], indent=2, sort_keys=True))
        return 0

    return 1
