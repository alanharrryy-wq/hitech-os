from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Sequence

from .application import APPLICATION_STATUS, apply_plan
from .canonical import write_json
from .errors import ApplicationDisabledError, BridgeError
from .planner import build_plan, write_plan
from .profile import load_profile
from .projection import build_projection_map, write_projection_map
from .recipes import RecipeRepository
from .repository import BridgeRepository
from .resolver import resolve_component
from .selftest import main as selftest_main
from .cobrar_application import execute_cobrar_transaction


def _recipes(paths: list[str], profile_paths: list[str]) -> RecipeRepository:
    return RecipeRepository.load([*profile_paths, *paths])


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="code-atlas-plus ui-bridge", description="PRISMA UI Bridge v1, source-only")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("inputs", nargs="+")
    p_validate.add_argument("--output")
    p_resolve = sub.add_parser("resolve")
    p_resolve.add_argument("inputs", nargs="+")
    p_resolve.add_argument("--component", required=True)
    p_resolve.add_argument("--profile")
    p_resolve.add_argument("--recipe", action="append", default=[])
    p_resolve.add_argument("--output")
    p_plan = sub.add_parser("plan")
    p_plan.add_argument("inputs", nargs="+")
    p_plan.add_argument("--component", required=True)
    p_plan.add_argument("--recipe-id")
    p_plan.add_argument("--recipe", action="append", default=[])
    p_plan.add_argument("--profile")
    p_plan.add_argument("--output-root")
    p_projection = sub.add_parser(
        "projection-map",
        help="Build deterministic read-only Tablet/PC/Mobile projection coverage from certified UIMAP inputs",
    )
    p_projection.add_argument("inputs", nargs="+")
    p_projection.add_argument(
        "--surface",
        action="append",
        choices=("tablet", "pc", "mobile"),
        default=[],
        help="Surface to include. Repeatable; defaults to tablet, pc and mobile.",
    )
    p_projection.add_argument("--recipe", action="append", default=[])
    p_projection.add_argument("--profile")
    p_projection.add_argument("--output-root")
    sub.add_parser("apply-status")
    p_apply = sub.add_parser("apply")
    p_apply.add_argument("plan")
    p_cobrar = sub.add_parser("apply-cobrar", help="Exact governed Atlasfin Cobrar transaction; not a generic writer")
    p_cobrar.add_argument("request")
    p_cobrar.add_argument("--repo-root", required=True)
    p_cobrar.add_argument("--evidence-root", required=True)
    p_cobrar.add_argument("--mode", choices=("preview", "apply", "verify"), default="preview")
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "selftest": return selftest_main()
        if args.command == "apply-status":
            print(json.dumps(APPLICATION_STATUS, ensure_ascii=False, indent=2, sort_keys=True)); return 0
        if args.command == "apply":
            apply_plan(args.plan); return 0
        if args.command == "apply-cobrar":
            result = execute_cobrar_transaction(args.request, args.repo_root, args.evidence_root, args.mode)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        repo = BridgeRepository.load(args.inputs, require_valid=args.command != "validate")
        if args.command == "validate":
            if args.output: write_json(args.output, repo.validation)
            print(json.dumps(repo.validation, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if repo.validation["ok"] else 2
        profile = load_profile(args.profile)
        recipes = _recipes(args.recipe, profile.recipe_paths)
        if args.command == "resolve":
            result = resolve_component(repo, recipes, args.component, profile.product_root, profile.governor_root)
            if args.output: write_json(args.output, result)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result["status"] != "BLOCKED" else 3
        if args.command == "plan":
            plan, diff = build_plan(repo, recipes, args.component, profile.product_root, profile.governor_root, args.recipe_id)
            output_root = args.output_root or profile.output_root
            paths = write_plan(output_root, plan, diff)
            print(json.dumps({"status":plan["status"],"planId":plan["planId"],"outputs":paths}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if plan["status"] == "PLAN_READY_FOR_REVIEW" else 3
        if args.command == "projection-map":
            surfaces = args.surface or ["tablet", "pc", "mobile"]
            projection, blockers = build_projection_map(
                repo,
                recipes,
                profile.product_root,
                profile.governor_root,
                surfaces,
            )
            output_root = args.output_root or profile.output_root
            paths = write_projection_map(output_root, projection, blockers)
            print(
                json.dumps(
                    {
                        "status": projection["status"],
                        "projectionId": projection["projectionId"],
                        "componentCount": projection["componentCount"],
                        "authorityPreflightReadyCount": projection["authorityPreflightReadyCount"],
                        "blockedComponentCount": projection["blockedComponentCount"],
                        "applicationEnabled": projection["applicationEnabled"],
                        "outputs": paths,
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0 if projection["status"] != "BLOCKED_BY_GLOBAL_AUTHORITY_GAP" else 3
    except ApplicationDisabledError as exc:
        print(json.dumps({"status":exc.code,"error":str(exc)}, ensure_ascii=False, indent=2), flush=True)
        return 4
    except BridgeError as exc:
        print(json.dumps({"status":exc.code,"error":str(exc)}, ensure_ascii=False, indent=2), flush=True)
        return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
