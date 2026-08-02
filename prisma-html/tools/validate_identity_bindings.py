#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from identity_binding_resolver_core import (
    COVERAGE_PATH,
    IDENTITY,
    ROOT,
    coverage_report,
    load_json,
    resolve_artifact,
    validate_registry,
    verify_envelope,
)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    required = [
        IDENTITY / "contract/PRISMA_IDENTITY_BINDING_CONTRACT.md",
        IDENTITY / "registries/element-bindings.registry.json",
        IDENTITY / "schemas/concrete-binding.schema.json",
        IDENTITY / "schemas/element-bindings-registry.schema.json",
        IDENTITY / "schemas/binding-envelope.schema.json",
        IDENTITY / "bindings/reports/BINDING_COVERAGE.json",
        IDENTITY / "portable/examples/preview-component-recipe_iddict-preview-primary-btn-01.tablet.prisma-visual.json",
        ROOT / "tools/identity_binding_resolver_core.py",
        ROOT / "tools/identity_binding_resolver.py",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing: {path.relative_to(ROOT).as_posix()}")

    if not errors:
        registry_errors, registry_warnings = validate_registry()
        errors.extend(registry_errors)
        warnings.extend(registry_warnings)

        expected_coverage = load_json(COVERAGE_PATH)
        actual_coverage = coverage_report()
        if expected_coverage != actual_coverage:
            errors.append("coverage report drift")

        example_path = IDENTITY / "portable/examples/preview-component-recipe_iddict-preview-primary-btn-01.tablet.prisma-visual.json"
        envelope = resolve_artifact(load_json(example_path))
        errors.extend(verify_envelope(envelope))
        if envelope.get("status") != "RESOLVED":
            errors.append(f"unexpected Tablet example status: {envelope.get('status')}")
        matches = envelope.get("matches") or []
        if len(matches) != 1:
            errors.append("Tablet example must match exactly one registry entry")
        else:
            targets = matches[0].get("targets") or []
            if len(targets) != 1 or targets[0].get("layerId") != "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE":
                errors.append("Tablet candidate must resolve the certified Cobrar layerId")
            elif targets[0].get("status") != "RESOLVED" or targets[0].get("missingBindings"):
                errors.append("Tablet candidate must be fully RESOLVED with no missing bindings")

        for path in [ROOT / "tools/identity_binding_resolver_core.py", ROOT / "tools/identity_binding_resolver.py", Path(__file__)]:
            try:
                compile(path.read_text(encoding="utf-8-sig"), str(path), "exec")
            except Exception as exc:
                errors.append(f"syntax {path.name}: {exc}")

    result = {
        "schema": "prisma.identity.binding-validation.v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "runtimeMutationAllowed": False,
        "productApplicationAllowed": False,
        "hardTruth": "PASS validates source binding evidence only; it does not authorize runtime application.",
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
