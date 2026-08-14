from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Sequence

from .application import APPLICATION_STATUS, apply_plan
from .binding_promotion import build_binding_promotion_report, write_binding_promotion_report
from .canonical import write_json
from .closure import refresh_three_app_mapping
from .consistency import audit_visual_authority, write_visual_authority_audit
from .errors import ApplicationDisabledError, BridgeError
from .multisurface import build_multisurface_plan, write_multisurface_plan
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

    p_multi = sub.add_parser("plan-multisurface", help="Plan one exact neutral visual meaning across Tablet, PC and Mobile.")
    p_multi.add_argument("inputs", nargs="+")
    source_group = p_multi.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--source-component")
    source_group.add_argument("--neutral-meaning-id")
    p_multi.add_argument("--recipe-id")
    p_multi.add_argument("--recipe", action="append", default=[])
    p_multi.add_argument("--profile")
    p_multi.add_argument("--surface", action="append", choices=("tb", "pc", "mb"), default=[])
    p_multi.add_argument("--allow-missing-surface", action="store_true")
    p_multi.add_argument("--output-root")

    p_projection = sub.add_parser(
        "projection-map",
        help="Build deterministic read-only Tablet/PC/Mobile projection coverage from certified UIMAP inputs.",
    )
    p_projection.add_argument("inputs", nargs="+")
    p_projection.add_argument("--surface", action="append", choices=("tablet", "pc", "mobile"), default=[])
    p_projection.add_argument("--recipe", action="append", default=[])
    p_projection.add_argument("--profile")
    p_projection.add_argument("--output-root")

    p_promote = sub.add_parser("binding-promotion", help="Analyze exact UIMAP records for safe central binding promotion.")
    p_promote.add_argument("inputs", nargs="+")
    p_promote.add_argument("--profile")
    p_promote.add_argument("--binding-registry")
    p_promote.add_argument("--pilot-contract", action="append", default=[])
    p_promote.add_argument("--surface", action="append", choices=("tb", "pc", "mb"), default=[])
    p_promote.add_argument("--output-root")

    p_audit = sub.add_parser("audit-visual-authority", help="Fail-closed consistency audit for RIFAT, VISREC2 and UIMAP adapters.")
    p_audit.add_argument("--profile")
    p_audit.add_argument("--governor-root")
    p_audit.add_argument("--output-root")

    p_refresh = sub.add_parser("refresh-three-app-map", help="Regenerate read-only UIMAP and three-app visual mapping readiness.")
    p_refresh.add_argument("--profile")
    p_refresh.add_argument("--product-root")
    p_refresh.add_argument("--governor-root")
    p_refresh.add_argument("--output-root")
    p_refresh.add_argument("--binding-registry")
    p_refresh.add_argument("--pilot-contract", action="append", default=[])
    p_refresh.add_argument("--previous-batches-source")
    p_refresh.add_argument("--workers", type=int, default=18)

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
        if args.command == "selftest":
            return selftest_main()
        if args.command == "apply-status":
            print(json.dumps(APPLICATION_STATUS, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "apply":
            apply_plan(args.plan)
            return 0
        if args.command == "apply-cobrar":
            result = execute_cobrar_transaction(args.request, args.repo_root, args.evidence_root, args.mode)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "audit-visual-authority":
            profile = load_profile(args.profile)
            governor_root = args.governor_root or profile.governor_root
            output_root = args.output_root or profile.output_root
            report = audit_visual_authority(governor_root)
            output = write_visual_authority_audit(output_root, report)
            print(json.dumps({"status": report["status"], "blockingIssueCount": report.get("blockingIssueCount", 0), "output": output}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if report["status"] == "PASS" else 3
        if args.command == "refresh-three-app-map":
            profile = load_profile(args.profile)
            result = refresh_three_app_mapping(
                product_root=args.product_root or profile.product_root,
                governor_root=args.governor_root or profile.governor_root,
                output_root=args.output_root or profile.output_root,
                binding_registry_path=args.binding_registry,
                pilot_contract_paths=args.pilot_contract,
                recipe_paths=profile.recipe_paths,
                previous_batches_source=args.previous_batches_source,
                workers=max(1, min(18, args.workers)),
            )
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result.get("status") != "BLOCKED_BY_UIMAP" else 3

        repo = BridgeRepository.load(args.inputs, require_valid=args.command != "validate")
        if args.command == "validate":
            if args.output:
                write_json(args.output, repo.validation)
            print(json.dumps(repo.validation, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if repo.validation["ok"] else 2

        profile = load_profile(args.profile)
        recipes = _recipes(getattr(args, "recipe", []), profile.recipe_paths)

        if args.command == "resolve":
            result = resolve_component(repo, recipes, args.component, profile.product_root, profile.governor_root)
            if args.output:
                write_json(args.output, result)
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if result["status"] != "BLOCKED" else 3

        if args.command == "plan":
            plan, diff = build_plan(repo, recipes, args.component, profile.product_root, profile.governor_root, args.recipe_id)
            paths = write_plan(args.output_root or profile.output_root, plan, diff)
            print(json.dumps({"status": plan["status"], "planId": plan["planId"], "outputs": paths}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if plan["status"] == "PLAN_READY_FOR_REVIEW" else 3

        if args.command == "plan-multisurface":
            plan, diff = build_multisurface_plan(
                repo,
                recipes,
                profile.product_root,
                profile.governor_root,
                source_component=args.source_component,
                neutral_meaning_id=args.neutral_meaning_id,
                recipe_id=args.recipe_id,
                runtime_aliases=args.surface or ["tb", "pc", "mb"],
                require_all_surfaces=not args.allow_missing_surface,
            )
            paths = write_multisurface_plan(args.output_root or profile.output_root, plan, diff)
            print(json.dumps({"status": plan["status"], "planId": plan["planId"], "outputs": paths}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if plan["status"] == "PLAN_READY_FOR_REVIEW" else 3

        if args.command == "projection-map":
            projection, blockers = build_projection_map(
                repo,
                recipes,
                profile.product_root,
                profile.governor_root,
                args.surface or ["tablet", "pc", "mobile"],
            )
            paths = write_projection_map(args.output_root or profile.output_root, projection, blockers)
            print(json.dumps({
                "status": projection["status"],
                "projectionId": projection["projectionId"],
                "componentCount": projection["componentCount"],
                "authorityPreflightReadyCount": projection["authorityPreflightReadyCount"],
                "blockedComponentCount": projection["blockedComponentCount"],
                "applicationEnabled": projection["applicationEnabled"],
                "outputs": paths,
            }, ensure_ascii=False, indent=2, sort_keys=True))
            return 0 if projection["status"] != "BLOCKED_BY_GLOBAL_AUTHORITY_GAP" else 3

        if args.command == "binding-promotion":
            registry = args.binding_registry or str(Path(profile.governor_root) / "authority/rifat/identity/registries/element-bindings.registry.json")
            report, gaps = build_binding_promotion_report(
                repo,
                binding_registry_path=registry,
                pilot_contract_paths=args.pilot_contract,
                runtime_aliases=args.surface or ["tb", "pc", "mb"],
            )
            paths = write_binding_promotion_report(args.output_root or profile.output_root, report, gaps)
            print(json.dumps({"status": report["status"], "newPromotionCandidateCount": report["newPromotionCandidateCount"], "blockedCount": report["blockedCount"], "outputs": paths}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

    except ApplicationDisabledError as exc:
        print(json.dumps({"status": exc.code, "error": str(exc)}, ensure_ascii=False, indent=2), flush=True)
        return 4
    except (BridgeError, ValueError) as exc:
        code = getattr(exc, "code", "UI_BRIDGE_INVALID_REQUEST")
        print(json.dumps({"status": code, "error": str(exc)}, ensure_ascii=False, indent=2), flush=True)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
