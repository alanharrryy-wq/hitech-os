#!/usr/bin/env python3
"""CLI for portable, instruction-only PRISMA identity element exports."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from identity_dictionary_core import IDENTITY, SURFACES, load_model
from portable_identity_export_core import (
    EXTENSION,
    export_preview_component,
    export_profile,
    export_surface_adapter,
    export_token,
    load_artifact,
    verify_artifact,
    write_artifact,
)


def safe_filename(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in value).strip("-").lower()


def build_artifact(args: argparse.Namespace):
    model = load_model()
    profile_id = args.profile or model["activation"]["selectedProfileId"]
    if args.kind == "identity-profile":
        return export_profile(args.object_id, surface=args.surface, model=model)
    if args.kind == "semantic-token":
        return export_token(
            args.object_id,
            profile_id=profile_id,
            surface=args.surface,
            model=model,
        )
    if args.kind == "surface-adapter":
        return export_surface_adapter(
            args.object_id,
            profile_id=profile_id,
            model=model,
        )
    if args.kind == "preview-component-recipe":
        return export_preview_component(
            args.object_id,
            profile_id=profile_id,
            surface=args.surface,
            model=model,
        )
    raise ValueError(f"Unsupported kind: {args.kind}")


def print_summary(artifact: dict) -> None:
    summary = {
        "schema": artifact["schema"],
        "exportId": artifact["exportId"],
        "kind": artifact["kind"],
        "objectId": artifact["element"]["objectId"],
        "neutralMeaningId": artifact["element"]["neutralMeaningId"],
        "identityProfileId": artifact["identity"]["identityProfileId"],
        "surfaceId": artifact["target"]["surfaceId"],
        "bindingStatus": artifact["target"]["bindingStatus"],
        "missingBindings": artifact["target"]["missingBindings"],
        "instructionOnly": artifact["instructionOnly"],
        "runtimeMutationAllowed": artifact["runtimeMutationAllowed"],
        "checksum": artifact["integrity"]["canonicalPayloadSha256"],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def cmd_list() -> int:
    model = load_model()
    payload = {
        "profiles": [
            {"id": item["id"], "name": model["profiles"][item["id"]]["name"]}
            for item in model["profileRegistry"]["profiles"]
        ],
        "tokens": [item["id"] for item in model["tokens"]["tokens"]],
        "surfaces": list(SURFACES),
        "surfaceAdapters": [model["adapters"][surface]["id"] for surface in SURFACES],
        "previewComponents": [
            item["id"] for item in model["exportRegistry"]["viewerComponents"]
        ],
        "artifactExtension": EXTENSION,
        "applicationMode": "INSTRUCTION_ONLY",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    artifact = build_artifact(args)
    output = Path(args.out) if args.out else Path(
        f"{safe_filename(artifact['kind'])}_{safe_filename(artifact['element']['objectId'])}{EXTENSION}"
    )
    write_artifact(output, artifact)
    print_summary(artifact)
    print(f"OUTPUT={output.resolve()}")
    return 0


def cmd_verify(path: Path, *, inspect: bool) -> int:
    artifact = load_artifact(path)
    errors, warnings = verify_artifact(artifact)
    payload = {
        "status": "PASS" if not errors else "FAIL",
        "path": str(path.resolve()),
        "errors": errors,
        "warnings": warnings,
        "instructionOnly": artifact.get("instructionOnly"),
        "runtimeMutationAllowed": artifact.get("runtimeMutationAllowed"),
        "bindingStatus": (artifact.get("target") or {}).get("bindingStatus"),
        "exportId": artifact.get("exportId"),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    if inspect and not errors:
        print_summary(artifact)
    return 0 if not errors else 1


def cmd_examples(output: Path) -> int:
    model = load_model()
    selected = model["activation"]["selectedProfileId"]
    examples = [
        export_profile(selected, surface="shared-ui", model=model),
        export_token("color.accent", profile_id=selected, surface="tablet", model=model),
        export_surface_adapter("tablet", profile_id=selected, model=model),
        export_preview_component(
            "IDDICT-PREVIEW-PRIMARY-BTN-01",
            profile_id=selected,
            surface="shared-ui",
            model=model,
        ),
    ]
    output.mkdir(parents=True, exist_ok=True)
    written = []
    for artifact in examples:
        filename = (
            f"{safe_filename(artifact['kind'])}_"
            f"{safe_filename(artifact['element']['objectId'])}{EXTENSION}"
        )
        path = output / filename
        write_artifact(path, artifact)
        written.append(str(path))
    print(json.dumps({"status": "PASS", "written": written}, indent=2, ensure_ascii=False))
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Create and inspect portable PRISMA visual instructions."
    )
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("list")

    export = sub.add_parser("export")
    export.add_argument(
        "--kind",
        required=True,
        choices=[
            "identity-profile",
            "semantic-token",
            "surface-adapter",
            "preview-component-recipe",
        ],
    )
    export.add_argument("--id", dest="object_id", required=True)
    export.add_argument("--profile")
    export.add_argument("--surface", default="shared-ui", choices=SURFACES)
    export.add_argument("--out")

    verify = sub.add_parser("verify")
    verify.add_argument("path")

    inspect = sub.add_parser("inspect")
    inspect.add_argument("path")

    examples = sub.add_parser("examples")
    examples.add_argument(
        "--out",
        default=str(IDENTITY / "portable" / "examples"),
    )
    return ap


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "list":
            return cmd_list()
        if args.command == "export":
            return cmd_export(args)
        if args.command == "verify":
            return cmd_verify(Path(args.path), inspect=False)
        if args.command == "inspect":
            return cmd_verify(Path(args.path), inspect=True)
        if args.command == "examples":
            return cmd_examples(Path(args.out))
        raise RuntimeError("Unknown command")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
