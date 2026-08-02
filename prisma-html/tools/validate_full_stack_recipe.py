#!/usr/bin/env python3
"""Strict source-only validator for IDRECIPE1 full-stack recipe authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from full_stack_recipe_core import (
    IDENTITY,
    ROOT,
    load_json,
    recipe_units,
    registry_record,
    round_trip,
    verify_integrity,
)

RECIPE_ID = "REC.button.primary"
RECIPE_PATH = IDENTITY / "recipes" / "examples" / "REC.button.primary.tablet-pos-cobrar.full-stack.json"
COVERAGE_PATH = IDENTITY / "recipes" / "examples" / "REC.button.primary.tablet-pos-cobrar.coverage.json"
RECIPE_REGISTRY = IDENTITY / "registries" / "recipe.registry.json"
PROPERTY_REGISTRY = IDENTITY / "registries" / "recipe-properties.registry.json"
STACK_REGISTRY = IDENTITY / "registries" / "visual-stack.registry.json"
ALIAS_REGISTRY = IDENTITY / "registries" / "legacy-aliases.registry.json"
COMPATIBILITY = IDENTITY / "contract" / "REC.button.primary.compatibility.json"
PORTABLE_V2 = IDENTITY / "portable" / "v2" / "examples" / "REC.button.primary.tablet-pos-cobrar.v2.prisma-visual.json"
SCHEMAS = {
    "recipe": IDENTITY / "schemas" / "full-stack-recipe.schema.json",
    "propertyRegistry": IDENTITY / "schemas" / "recipe-property-registry.schema.json",
    "portableV2": IDENTITY / "schemas" / "portable-element-export-v2.schema.json",
}

REQUIRED_UNITS = {
    "base",
    "before",
    "hover",
    "hoverBefore",
    "disabled",
    "icon",
    "copy",
    "copyStrong",
    "copySmall",
    "amount",
    "loading",
}
REQUIRED_EXTENSION_STATES = {
    "focus",
    "focus-visible",
    "pressed",
    "success",
    "warning",
    "error",
    "reduced-motion",
}
ALLOWED_EXTENSION_STATUS = {"DEFINED", "NOT_DEFINED", "NOT_APPLICABLE", "BLOCKED_BY_UNGOVERNED_STATE"}
KNOWN_SELECTOR_UNITS = {
    "base": ".cobrarReferenceButton",
    "before": ".cobrarReferenceButton::before",
    "hover": ".cobrarReferenceButton:hover",
    "hoverBefore": ".cobrarReferenceButton:hover::before",
    "disabled": ".cobrarReferenceButton:disabled",
    "icon": ".cobrarIcon",
    "copy": ".cobrarCopy",
    "copyStrong": ".cobrarCopy strong",
    "copySmall": ".cobrarCopy small",
    "amount": ".cobrarAmount",
}
EXPECTED_AUTHORITY_BASIS = {
    "fieldManual": "apps/terminal-de-venta-system/docs/ops/PRISMA_FIELD_MANUAL_APRENDIZAJE_OPERATIVO.md",
    "factoryLedgerAgentGate": "PRISMA Factory Ledger/PRISMA_FACTORY_LEDGER_AGENT_GATE.md",
}


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_schema(value: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    """Small deterministic validator for the schema keywords used by IDRECIPE1."""
    errors: list[str] = []
    if "$ref" in schema:
        errors.append(f"{path}: external $ref unsupported by local gate")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: value not in enum")
    expected_type = schema.get("type")
    type_map = {
        "object": dict,
        "array": list,
        "string": str,
        "boolean": bool,
        "number": (int, float),
        "integer": int,
        "null": type(None),
    }
    if expected_type:
        allowed = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(isinstance(value, type_map[item]) and not (item in {"number", "integer"} and isinstance(value, bool)) for item in allowed):
            return [f"{path}: type mismatch, expected {allowed}"]
    if isinstance(value, dict):
        required = schema.get("required") or []
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required {key}")
        properties = schema.get("properties") or {}
        for key, subschema in properties.items():
            if key in value:
                errors.extend(validate_schema(value[key], subschema, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            extras = sorted(set(value) - set(properties))
            if extras:
                errors.append(f"{path}: extra properties {extras}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: too few items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, ensure_ascii=False) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: duplicate items")
        if "items" in schema:
            for index, item in enumerate(value):
                errors.extend(validate_schema(item, schema["items"], f"{path}[{index}]"))
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: string too short")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: pattern mismatch")
    return errors


def css_properties(css: str, selector: str) -> set[str]:
    pattern = re.compile(rf"(?ms)^[ \t]*{re.escape(selector)}\s*\{{(?P<body>.*?)^[ \t]*\}}")
    matches = list(pattern.finditer(css))
    if len(matches) != 1:
        raise ValueError(f"Selector cardinality {selector}: {len(matches)}")
    body = re.sub(r"/\*.*?\*/", "", matches[0].group("body"), flags=re.S)
    names = set()
    for match in re.finditer(r"(?m)^[ \t]*([a-zA-Z-]+)\s*:", body):
        names.add(match.group(1))
    return names


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-repo", default=r"F:\repos\hitech-os")
    parser.add_argument(
        "--refresh-coverage",
        action="store_true",
        help="Refresh only the deterministic Cobrar coverage projection before validating it.",
    )
    args = parser.parse_args()
    errors: list[str] = []
    warnings: list[str] = []
    required_files = [
        RECIPE_PATH,
        COVERAGE_PATH,
        RECIPE_REGISTRY,
        PROPERTY_REGISTRY,
        STACK_REGISTRY,
        ALIAS_REGISTRY,
        COMPATIBILITY,
        PORTABLE_V2,
        *SCHEMAS.values(),
        IDENTITY / "contract" / "PRISMA_FULL_STACK_RECIPE_CONTRACT.md",
        IDENTITY / "portable" / "MIGRATION_V1_TO_V2.md",
    ]
    for path in required_files:
        if not path.is_file():
            errors.append(f"missing:{path.relative_to(ROOT).as_posix()}")
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2, ensure_ascii=False))
        return 1

    recipe = load_json(RECIPE_PATH)
    coverage = load_json(COVERAGE_PATH)
    recipe_registry = load_json(RECIPE_REGISTRY)
    properties = load_json(PROPERTY_REGISTRY)
    stacks = load_json(STACK_REGISTRY)
    aliases = load_json(ALIAS_REGISTRY)
    compatibility = load_json(COMPATIBILITY)
    portable = load_json(PORTABLE_V2)

    errors.extend(validate_schema(recipe, load_json(SCHEMAS["recipe"]), "$recipe"))
    errors.extend(validate_schema(properties, load_json(SCHEMAS["propertyRegistry"]), "$propertyRegistry"))
    errors.extend(validate_schema(portable, load_json(SCHEMAS["portableV2"]), "$portableV2"))
    errors.extend(verify_integrity(recipe))
    errors.extend(verify_integrity(portable, excluded=("exportId", "integrity")))

    if recipe.get("recipeId") != RECIPE_ID:
        errors.append("recipeId mismatch")
    status_fields = {
        "compatibilityStatus": "COMPATIBLE_V1_ADDITIVE_EXTENSION",
        "bindingStatus": "RESOLVED",
        "recipeCoverageStatus": "COMPLETE",
        "applicationReadiness": "BLOCKED_PENDING_FUTURE_EXACT_TARGET_APPLICATION_GATE",
        "evidenceStatus": "SOURCE_EVIDENCE_COMPLETE_RUNTIME_NOT_CERTIFIED",
    }
    for key, expected in status_fields.items():
        if recipe.get(key) != expected:
            errors.append(f"{key} mismatch")
    if recipe.get("instructionOnly") is not True:
        errors.append("instructionOnly must be true")
    if recipe.get("runtimeMutationAllowed") is not False:
        errors.append("runtimeMutationAllowed must be false")
    if recipe.get("productApplicationAllowed") is not False:
        errors.append("productApplicationAllowed must be false")
    if recipe.get("authorityBasis", {}).get("fieldManual") != EXPECTED_AUTHORITY_BASIS["fieldManual"]:
        errors.append("Field Manual authority reference must be source-repo-relative")
    if recipe.get("authorityBasis", {}).get("factoryLedgerAgentGate") != EXPECTED_AUTHORITY_BASIS["factoryLedgerAgentGate"]:
        errors.append("Factory Ledger authority reference must be source-repo-relative")
    if re.search(r"[A-Za-z]:\\", json.dumps(recipe.get("authorityBasis", {}), ensure_ascii=False)):
        errors.append("authorityBasis contains a local absolute path")

    units = recipe_units(recipe)
    if set(units) != REQUIRED_UNITS:
        errors.append(f"visual stack units mismatch: {sorted(set(units) ^ REQUIRED_UNITS)}")
    property_ids = [row.get("propertyId") for row in properties.get("properties", [])]
    if len(property_ids) != len(set(property_ids)):
        errors.append("duplicate propertyId")
    property_set = set(property_ids)
    for unit_id, unit in units.items():
        if unit.get("coverageStatus") != "DEFINED":
            errors.append(f"unit not defined:{unit_id}")
        unknown = sorted(set((unit.get("properties") or {})) - property_set)
        if unknown:
            errors.append(f"unknown properties in {unit_id}:{unknown}")
        for name, spec in (unit.get("properties") or {}).items():
            if not isinstance(spec, dict) or spec.get("mode") not in {
                "TOKEN",
                "EXPRESSION",
                "LITERAL",
                "NONE",
                "PRESERVE_STRUCTURAL",
                "INHERIT",
                "POLICY",
            }:
                errors.append(f"invalid value mode:{unit_id}:{name}")

    extension_rows = recipe.get("extensionStates") or []
    extension_names = {row.get("stateId") for row in extension_rows}
    if extension_names != REQUIRED_EXTENSION_STATES:
        errors.append(f"extension state mismatch:{sorted(extension_names ^ REQUIRED_EXTENSION_STATES)}")
    for row in extension_rows:
        if row.get("status") not in ALLOWED_EXTENSION_STATUS:
            errors.append(f"extension state status invalid:{row}")

    stack_records = stacks.get("visualStacks") or []
    if len(stack_records) != 1 or stack_records[0].get("visualStackId") != recipe.get("visualStackId"):
        errors.append("visual stack registry mismatch")
    required_by_unit = stack_records[0].get("requiredPropertiesByUnit") or {}
    for unit_id, required_names in required_by_unit.items():
        missing = sorted(set(required_names) - set((units.get(unit_id) or {}).get("properties", {})))
        if missing:
            errors.append(f"required properties missing:{unit_id}:{missing}")

    record = registry_record(recipe_registry, RECIPE_ID)
    if record.get("path") != "recipes/examples/REC.button.primary.tablet-pos-cobrar.full-stack.json":
        errors.append("recipe registry path mismatch")
    if record.get("canonicalRecipeSha256") != recipe.get("integrity", {}).get("canonicalPayloadSha256"):
        errors.append("recipe registry canonical checksum mismatch")
    if record.get("fileSha256") != file_sha(RECIPE_PATH):
        errors.append("recipe registry file checksum mismatch")

    alias_ids = [row.get("aliasId") for row in aliases.get("aliases", [])]
    if len(alias_ids) != len(set(alias_ids)):
        errors.append("duplicate aliasId")
    if not any(row.get("legacyValue") == "IDDICT-PREVIEW-PRIMARY-BTN-01" for row in aliases.get("aliases", [])):
        errors.append("legacy component alias missing")

    if compatibility.get("compatibilityStatus") != status_fields["compatibilityStatus"]:
        errors.append("compatibility contract mismatch")
    if compatibility.get("v1ArtifactModified") is not False:
        errors.append("V1 artifact must remain untouched")

    if portable.get("recipeId") != RECIPE_ID:
        errors.append("portable V2 recipeId mismatch")
    if portable.get("sourceArtifact", {}).get("exportId") != "PEX.preview-component-recipe-iddict-preview-primary-btn-01.733104ad5ccd":
        errors.append("portable V2 source export mismatch")
    if round_trip(portable) != portable:
        errors.append("portable V2 round trip mismatch")

    source_css = (
        Path(args.source_repo)
        / "apps"
        / "terminal-de-venta-system"
        / "products"
        / "tablet"
        / "app"
        / "components"
        / "pos"
        / "pos.module.css"
    )
    if not source_css.is_file():
        errors.append(f"source CSS missing:{source_css}")
    else:
        css = source_css.read_text(encoding="utf-8-sig")
        if args.refresh_coverage:
            coverage_units = {row["unitId"]: row for row in coverage.get("units", [])}
            refreshed_units: list[dict[str, Any]] = []
            for unit_id in REQUIRED_UNITS:
                matrix_row = dict(coverage_units[unit_id])
                selector = KNOWN_SELECTOR_UNITS.get(unit_id)
                actual = css_properties(css, selector) if selector else set()
                matrix_row.update({
                    "selector": selector or matrix_row.get("selector"),
                    "coverageStatus": "DEFINED",
                    "knownProperties": sorted(actual),
                    "knownDeclarationCount": len(actual),
                    "uncoveredKnownProperties": [],
                })
                refreshed_units.append(matrix_row)
            unit_order = {unit_id: index for index, unit_id in enumerate((
                "base", "before", "hover", "hoverBefore", "disabled", "icon",
                "copy", "copyStrong", "copySmall", "amount", "loading",
            ))}
            refreshed_units.sort(key=lambda row: unit_order[row["unitId"]])
            coverage.update({
                "sourceCssSha256": file_sha(source_css),
                "sourceComponentSha256": file_sha(source_css.with_name("pos-ticket-panel.tsx")),
                "recipeCoverageStatus": "COMPLETE",
                "knownDeclarationCount": sum(row["knownDeclarationCount"] for row in refreshed_units),
                "uncoveredKnownDeclarationCount": 0,
                "units": refreshed_units,
            })
            COVERAGE_PATH.write_text(
                json.dumps(coverage, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        coverage_units = {row["unitId"]: row for row in coverage.get("units", [])}
        known_total = 0
        uncovered_total = 0
        for unit_id, selector in KNOWN_SELECTOR_UNITS.items():
            try:
                actual = css_properties(css, selector)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            matrix_row = coverage_units.get(unit_id)
            if not matrix_row:
                errors.append(f"coverage row missing:{unit_id}")
                continue
            declared = set(matrix_row.get("knownProperties") or [])
            uncovered = sorted(actual - declared)
            stale = sorted(declared - actual)
            known_total += len(actual)
            uncovered_total += len(uncovered)
            if uncovered:
                errors.append(f"BLOCKED_BY_INCOMPLETE_RECIPE_COVERAGE:{unit_id}:{uncovered}")
            if stale:
                errors.append(f"coverage matrix stale:{unit_id}:{stale}")
        if coverage.get("knownDeclarationCount") != known_total:
            errors.append("coverage knownDeclarationCount mismatch")
        if coverage.get("uncoveredKnownDeclarationCount") != uncovered_total:
            errors.append("coverage uncoveredKnownDeclarationCount mismatch")
        if uncovered_total:
            errors.append("recipeCoverageStatus cannot be COMPLETE")

    serialized = "\n".join(
        path.read_text(encoding="utf-8-sig", errors="replace")
        for path in required_files
        if path.suffix.lower() in {".json", ".md"}
    )
    forbidden_priority_token = "!" + "important"
    if forbidden_priority_token in serialized:
        errors.append("priority override token found")

    result = {
        "schema": "prisma.identity.full-stack-recipe-validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "recipeId": RECIPE_ID,
        "recipeCoverageStatus": recipe.get("recipeCoverageStatus"),
        "visualStackUnitCount": len(units),
        "propertyCount": len(property_ids),
        "extensionStateCount": len(extension_rows),
        "portableRoundTrip": "PASS" if round_trip(portable) == portable else "FAIL",
        "instructionOnly": recipe.get("instructionOnly"),
        "runtimeMutationAllowed": recipe.get("runtimeMutationAllowed"),
        "productApplicationAllowed": recipe.get("productApplicationAllowed"),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
