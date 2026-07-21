from __future__ import annotations

import argparse
import json
import sys

from .authority import validate_authority_chain
from .contracts import LegalPipelineConfig
from .pipeline import run_pipeline
from .registry import build_legal_stage_registry


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Code Atlas Legal / Investor Readiness backend")
    parser.add_argument("--profile", choices=["plan", "static", "full", "runtime-only"], default="plan")
    parser.add_argument("--include-runtime", action="store_true")
    parser.add_argument("--surface", choices=["all", "chart-lab", "web", "tablet", "pc", "mobile", "control-center"], default="all")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--shards", type=int, default=1)
    parser.add_argument("--strict", action="store_true", help="Treat optional runtime failure as blocker")
    parser.add_argument("--output-root", default=r"F:\descargasf")
    parser.add_argument("--repo-root", default=r"F:\repos\hitech-os")
    parser.add_argument("--code-atlas-root", default=r"F:\repos\hitech-os\tools\code-atlas")
    parser.add_argument("--motors-root", default=r"F:\PRISMA_CTX\MOTORES")
    parser.add_argument("--ndc-root", default=r"F:\PRISMA_CTX\NDC")
    parser.add_argument("--mamastrophic-root", default=r"F:\repos\hitech-os\tools\Plawright Mamastrophic")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--cancel-file", default="", help="Cooperative stop marker checked between stages")
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--print-plan", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = LegalPipelineConfig(
        profile=args.profile,
        workers=args.workers,
        shards=args.shards,
        surface=args.surface,
        include_runtime=args.include_runtime,
        allow_partial=not args.strict,
        output_root=args.output_root,
        repo_root=args.repo_root,
        code_atlas_root=args.code_atlas_root,
        motors_root=args.motors_root,
        ndc_root=args.ndc_root,
        mamastrophic_root=args.mamastrophic_root,
        run_id=args.run_id,
        cancel_file=args.cancel_file,
    ).normalized()
    authority = validate_authority_chain(
        config.output_root,
        require_mamastrophic=config.include_runtime or config.profile == "runtime-only",
    )
    if args.authority_only:
        print(json.dumps(authority, ensure_ascii=False, indent=2))
        return 0 if authority["status"] == "PASS" else 2

    if args.print_plan:
        plan = [stage.to_dict() for stage in build_legal_stage_registry(config)]
        print(json.dumps({"authority": authority, "plan": plan}, ensure_ascii=False, indent=2))
        return 0 if authority["status"] == "PASS" else 2

    result = run_pipeline(config)
    return 0 if result["status"] != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
