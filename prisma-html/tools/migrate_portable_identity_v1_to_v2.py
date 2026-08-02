#!/usr/bin/env python3
"""Compatibility gate for the additive IDRECIPE1 V1 -> V2 portable artifact."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from full_stack_recipe_core import IDENTITY, load_json, round_trip, verify_integrity

V1 = (
    IDENTITY
    / "portable"
    / "examples"
    / "preview-component-recipe_iddict-preview-primary-btn-01.tablet.prisma-visual.json"
)
V2 = (
    IDENTITY
    / "portable"
    / "v2"
    / "examples"
    / "REC.button.primary.tablet-pos-cobrar.v2.prisma-visual.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    if not args.check_only:
        errors.append("This migration tool is intentionally check-only in IDRECIPE1.")
    if not V1.is_file() or not V2.is_file():
        errors.append("V1 or V2 artifact missing.")
    else:
        v1 = load_json(V1)
        v2 = load_json(V2)
        if v1.get("schema") != "prisma.identity.portable-element-export.v1":
            errors.append("V1 schema drift.")
        if v2.get("schema") != "prisma.identity.portable-element-export.v2":
            errors.append("V2 schema mismatch.")
        if v2.get("sourceArtifact", {}).get("exportId") != v1.get("exportId"):
            errors.append("V2 does not reference the canonical V1 exportId.")
        if v2.get("compatibilityStatus") != "COMPATIBLE_V1_ADDITIVE_EXTENSION":
            errors.append("Compatibility status mismatch.")
        if v2.get("instructionOnly") is not True:
            errors.append("V2 must remain instructionOnly.")
        if v2.get("runtimeMutationAllowed") is not False:
            errors.append("V2 runtime mutation must remain false.")
        if v2.get("productApplicationAllowed") is not False:
            errors.append("V2 product application must remain false.")
        errors.extend(verify_integrity(v2, excluded=("exportId", "integrity")))
        if round_trip(v2) != v2:
            errors.append("V2 export/import round trip drift.")
    result = {
        "schema": "prisma.identity.portable-migration-check.v1",
        "status": "PASS" if not errors else "FAIL",
        "mode": "CHECK_ONLY_ADDITIVE_EXTENSION",
        "v1Modified": False,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
