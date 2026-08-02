#!/usr/bin/env python3
"""Focused gate for PRISMA portable identity element export."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from identity_dictionary_core import COMPILED, IDENTITY, ROOT, load_json, load_model
from portable_identity_export_core import load_artifact, verify_artifact

REQUIRED = [
    IDENTITY / "registries" / "portable-export.registry.json",
    IDENTITY / "schemas" / "portable-element-export.schema.json",
    IDENTITY / "schemas" / "portable-export-registry.schema.json",
    IDENTITY / "contract" / "PRISMA_PORTABLE_ELEMENT_EXPORT_CONTRACT.md",
    IDENTITY / "portable" / "README.md",
    ROOT / "tools" / "portable_identity_export.py",
    ROOT / "tools" / "portable_identity_export_core.py",
    ROOT / "sistema-ui" / "identidad" / "index.html",
    ROOT / "sistema-ui" / "identidad" / "identity.js",
    ROOT / "sistema-ui" / "identidad" / "identity.css",
]


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT).as_posix()}")
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    model = load_model()
    registry = model["exportRegistry"]
    if registry.get("artifactSchema") != "prisma.identity.portable-element-export.v1":
        errors.append("artifact schema mismatch")
    if registry.get("instructionOnly") is not True:
        errors.append("portable export must remain instruction-only")
    if registry.get("runtimeMutationAllowed") is not False:
        errors.append("portable export runtime mutation must remain false")
    if registry.get("bindingPolicy", {}).get("unknownBindingsMustRemainNull") is not True:
        errors.append("unknown bindings must remain null")
    if registry.get("bindingPolicy", {}).get("productApplicationForbidden") is not True:
        errors.append("product application must remain forbidden")

    bundle = load_json(COMPILED / "identity-bundle.json")
    if bundle.get("portableExportRegistry") != registry:
        errors.append("compiled bundle portable export registry drift")
    if set((bundle.get("surfaceAdapters") or {}).keys()) != set(model["adapters"].keys()):
        errors.append("compiled bundle surface adapter set drift")
    manifest = load_json(COMPILED / "manifest.json")
    portable = manifest.get("portableElementExport") or {}
    if portable.get("status") != "SOURCE_READY_INSTRUCTION_ONLY":
        errors.append("compiled manifest portable export status mismatch")
    if portable.get("productApplicationAllowed") is not False:
        errors.append("compiled manifest must forbid product application")

    examples = sorted((IDENTITY / "portable" / "examples").glob("*.prisma-visual.json"))
    if len(examples) < 4:
        errors.append("portable export examples are incomplete")
    kinds = set()
    for path in examples:
        artifact = load_artifact(path)
        item_errors, item_warnings = verify_artifact(artifact)
        kinds.add(artifact.get("kind"))
        errors.extend(f"{path.name}: {error}" for error in item_errors)
        warnings.extend(f"{path.name}: {warning}" for warning in item_warnings)
    expected_kinds = {
        "identity-profile",
        "semantic-token",
        "surface-adapter",
        "preview-component-recipe",
    }
    if kinds != expected_kinds:
        errors.append(f"portable export example kinds mismatch: {sorted(kinds)}")

    html = (ROOT / "sistema-ui" / "identidad" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "sistema-ui" / "identidad" / "identity.js").read_text(encoding="utf-8")
    css = (ROOT / "sistema-ui" / "identidad" / "identity.css").read_text(encoding="utf-8")
    combined = "\n".join([html, js, css])
    required_markers = [
        'id="surfaceSelect"',
        'id="importArtifact"',
        'id="importResult"',
        "portableExportRegistry",
        "buildPortableArtifact",
        "verifyPortableArtifact",
        "element-export-button",
        "BLOCKED_BY_MISSING_BINDING",
    ]
    for marker in required_markers:
        if marker not in combined:
            errors.append(f"viewer marker missing: {marker}")
    if "runtimeMutationAllowed: true" in combined or "productApplicationAllowed: true" in combined:
        errors.append("viewer contains forbidden application permission")
    if "!important" in combined:
        errors.append("priority override found in portable export viewer")

    package = load_json(ROOT / "package.json")
    scripts = package.get("scripts", {})
    expected_scripts = {
        "identity:export:list": "python tools/portable_identity_export.py list",
        "identity:export:validate": "python tools/validate_portable_identity_export.py",
        "identity:export:examples": "python tools/portable_identity_export.py examples",
    }
    for key, value in expected_scripts.items():
        if scripts.get(key) != value:
            errors.append(f"package script mismatch: {key}")

    result = {
        "schema": "prisma.identity.portable-export-validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "supportedKindCount": len(registry.get("supportedKinds", [])),
        "exampleCount": len(examples),
        "instructionOnly": registry.get("instructionOnly"),
        "runtimeMutationAllowed": registry.get("runtimeMutationAllowed"),
        "productApplicationAllowed": False,
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
