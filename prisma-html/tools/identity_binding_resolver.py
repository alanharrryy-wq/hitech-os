#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from identity_binding_resolver_core import (
    COVERAGE_PATH,
    IDENTITY,
    ROOT,
    coverage_report,
    current_authority_snapshot,
    load_json,
    load_registry,
    resolve_artifact,
    verify_envelope,
)


def dump(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="PRISMA IDBIND1 read-only binding resolver")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("artifact")
    resolve = sub.add_parser("resolve")
    resolve.add_argument("artifact")
    resolve.add_argument("--out")
    sub.add_parser("coverage")
    sub.add_parser("sources")
    sub.add_parser("registry")
    example = sub.add_parser("example")
    example.add_argument("--out")
    args = parser.parse_args()

    if args.command == "sources":
        dump(current_authority_snapshot(load_registry()))
        return 0
    if args.command == "coverage":
        dump(coverage_report())
        return 0
    if args.command == "registry":
        dump(load_registry())
        return 0

    if args.command == "example":
        artifact_path = IDENTITY / "portable/examples/preview-component-recipe_iddict-preview-primary-btn-01.tablet.prisma-visual.json"
        out = args.out
    else:
        artifact_path = Path(args.artifact).resolve()
        out = getattr(args, "out", None)
    artifact = load_json(artifact_path)
    envelope = resolve_artifact(artifact)
    errors = verify_envelope(envelope)
    if errors:
        dump({"status": "FAIL", "errors": errors})
        return 1
    if out:
        destination = Path(out).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"OUTPUT={destination}")
    if args.command == "inspect":
        dump({
            "status": envelope["status"],
            "sourceArtifact": envelope["sourceArtifact"],
            "matchCount": len(envelope["matches"]),
            "missing": sorted({missing for match in envelope["matches"] for target in match.get("targets", []) for missing in target.get("missingBindings", [])}),
            "runtimeMutationAllowed": envelope["runtimeMutationAllowed"],
            "productApplicationAllowed": envelope["productApplicationAllowed"],
        })
    else:
        dump(envelope)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
