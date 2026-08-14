from __future__ import annotations

import argparse
import json
import sys

from .engine import IntelligenceRequest, run_intelligence

VALID_INTENTS = ("DISCOVER", "AUDIT", "VERIFY", "FIX", "BUILD", "CERTIFY")

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repository-neutral Code Atlas intelligence")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--profile", default="")
    parser.add_argument("--intent", choices=VALID_INTENTS, default="DISCOVER")
    parser.add_argument("--domain", default="")
    parser.add_argument("--required-authority", action="append", default=[])
    parser.add_argument("--required-directory", action="append", default=[])
    parser.add_argument("--excluded-authority", action="append", default=[])
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--query", default="")
    parser.add_argument("--workers", type=int, default=18)
    parser.add_argument("--allow-missing-authority", action="store_true")
    args = parser.parse_args(argv)
    request = IntelligenceRequest(
        intent=args.intent,
        domain=args.domain,
        required_authorities=tuple(args.required_authority),
        required_directories=tuple(args.required_directory),
        excluded_authorities=tuple(args.excluded_authority),
        changed_paths=tuple(args.changed_path),
        semantic_query=args.query,
        fail_on_missing_authority=not args.allow_missing_authority,
        workers=max(1, min(18, args.workers)),
    )
    result = run_intelligence(
        args.repo, args.out, profile_path=args.profile or None, request=request,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
