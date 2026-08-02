from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


COMPONENT_UI_ID = "TB-POS-PAY-COBRAR-BTN-01"
RECIPE_ID = "REC.button.primary"
BINDING_ID = "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"
EXPECTED_LAYER_ID = "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE"
EXPECTED_IMPLEMENTATION_LAYER_ID = (
    "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton"
)
APPLICATION_SCHEMA = "PRISMA_ATLASFIN_VISUAL_APPLICATION_RESULT_V1"
EVIDENCE_SCHEMA = "PRISMA_ATLASFIN_VISUAL_APPLICATION_EVIDENCE_BUNDLE_V1"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected an object in {path}")
    return value


def require_one(rows: list[dict[str, Any]], field: str, value: str) -> dict[str, Any]:
    matches = [row for row in rows if isinstance(row, dict) and row.get(field) == value]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {field}={value}; found {len(matches)}")
    return matches[0]


def relative_repo_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def build_projection(
    atlas_root: Path,
    uimap_batch_path: Path,
    mamastrophic_evidence_path: Path | None = None,
) -> dict[str, Any]:
    atlas_root = atlas_root.resolve()
    repo_root = atlas_root.parents[2]
    prisma_root = atlas_root.parents[1]
    code_atlas_src = repo_root / "tools" / "code-atlas" / "src"
    if str(code_atlas_src) not in sys.path:
        sys.path.insert(0, str(code_atlas_src))

    from code_atlas.ui_bridge.planner import build_plan
    from code_atlas.ui_bridge.recipes import RecipeRepository
    from code_atlas.ui_bridge.repository import BridgeRepository

    recipe_path = (
        prisma_root
        / "authority/rifat/identity/recipes/examples"
        / "REC.button.primary.tablet-pos-cobrar.full-stack.json"
    )
    recipe_root = prisma_root / "authority/rifat/identity/recipes"
    portable_v2_root = prisma_root / "authority/rifat/identity/portable/v2"
    coverage_path = (
        prisma_root
        / "authority/rifat/identity/recipes/examples"
        / "REC.button.primary.tablet-pos-cobrar.coverage.json"
    )
    binding_path = (
        prisma_root
        / "authority/rifat/identity/registries/element-bindings.registry.json"
    )

    batch = read_json(uimap_batch_path)
    component = require_one(batch.get("components", []), "componentUiId", COMPONENT_UI_ID)
    recipe = read_json(recipe_path)
    coverage = read_json(coverage_path)
    binding_registry = read_json(binding_path)
    binding = require_one(binding_registry.get("bindings", []), "bindingId", BINDING_ID)

    expected = {
        "surfaceId": "SURF.tb.pos",
        "routeId": "ROUTE.tb.pos",
        "routePath": "/pos",
        "ownerId": "OWN.tb.pos_ticket_panel",
        "regionId": "ZONE.tb.pos.payment",
        "slotId": "SLOT.tb.pos.payment.cobrar",
        "componentUiId": COMPONENT_UI_ID,
        "bindingId": BINDING_ID,
        "layerId": EXPECTED_LAYER_ID,
        "implementationLayerId": EXPECTED_IMPLEMENTATION_LAYER_ID,
    }
    for field, value in expected.items():
        if component.get(field) != value:
            raise ValueError(f"Canonical Cobrar drift: {field}={component.get(field)!r}, expected {value!r}")
    if recipe.get("recipeId") != RECIPE_ID:
        raise ValueError("The certified Cobrar recipe is missing")
    if binding.get("status") != "RESOLVED":
        raise ValueError("The certified Cobrar binding is not RESOLVED")
    binding_target = require_one(binding.get("targets", []), "status", "RESOLVED")
    binding_expected = {
        "layerId": EXPECTED_LAYER_ID,
        "implementationLayerId": EXPECTED_IMPLEMENTATION_LAYER_ID,
        "selector": ".cobrarReferenceButton",
    }
    for field, value in binding_expected.items():
        if binding_target.get(field) != value:
            raise ValueError(f"Certified binding drift: {field}={binding_target.get(field)!r}")

    bridge_repository = BridgeRepository.load([uimap_batch_path])
    # Match the active UI Bridge profile: portable v2 wins over the full-stack
    # evidence object for planning, while both remain part of the trace.
    recipe_repository = RecipeRepository.load([recipe_root, portable_v2_root])
    bridge_recipe_source = Path(recipe_repository.sources[RECIPE_ID])
    plan, semantic_diff = build_plan(
        bridge_repository,
        recipe_repository,
        COMPONENT_UI_ID,
        str(repo_root),
        str(prisma_root),
        RECIPE_ID,
    )
    if plan.get("status") != "PLAN_READY_FOR_REVIEW" or plan.get("blockingReasons"):
        raise ValueError(f"UI Bridge did not produce a clean source plan: {plan.get('blockingReasons')}")
    if plan.get("applicationEnabled") is not False:
        raise ValueError("UI Bridge application guard drifted")

    style_source = next(
        (
            target.get("styleSourceFile")
            for target in component.get("visualTargets", [])
            if isinstance(target, dict) and target.get("styleSourceFile")
        ),
        None,
    )
    if not style_source:
        raise ValueError("Cobrar has no certified style target")
    owner_source = component.get("ownerFile")
    if not owner_source:
        raise ValueError("Cobrar has no canonical owner file")
    style_path = repo_root / str(style_source)
    owner_path = repo_root / str(owner_source)
    current_css_sha = sha256_file(style_path)
    current_owner_sha = sha256_file(owner_path)
    certified_style_hashes = {
        str(target.get("sourceHash", "")).lower()
        for target in component.get("visualTargets", [])
        if isinstance(target, dict) and target.get("styleSourceFile") == style_source
    }
    if certified_style_hashes != {current_css_sha}:
        raise ValueError("Current Cobrar CSS does not match the certified UIMAP target hash")
    certified_owner_hash = str(component.get("sourceHashes", {}).get("ownerFile", "")).lower()
    if certified_owner_hash != current_owner_sha:
        raise ValueError("Current Cobrar owner does not match the certified UIMAP owner hash")
    declared_css_sha = str(coverage.get("sourceCssSha256", "")).lower()
    declared_owner_sha = str(coverage.get("sourceComponentSha256", "")).lower()
    coverage_stale = current_css_sha != declared_css_sha
    owner_stale = current_owner_sha != declared_owner_sha
    coverage_evidence_stale = coverage_stale or owner_stale

    mamastrophic_available = bool(
        mamastrophic_evidence_path and mamastrophic_evidence_path.is_file()
    )
    mamastrophic = {
        "status": (
            "SOURCE_EVIDENCE_AVAILABLE_RUNTIME_REVIEW_REQUIRED"
            if mamastrophic_available
            else "BLOCKED_BY_MISSING_MAMASTROPHIC_EVIDENCE"
        ),
        "requiredFor": ["VISUAL_EVIDENCE_GATE", "RUNTIME_CERTIFICATION_GATE"],
    }
    if mamastrophic_available and mamastrophic_evidence_path:
        mamastrophic["artifactName"] = mamastrophic_evidence_path.name
        mamastrophic["sha256"] = sha256_file(mamastrophic_evidence_path)

    operations: list[dict[str, Any]] = []
    for operation in plan.get("operations", []):
        if not isinstance(operation, dict):
            continue
        property_changes = operation.get("propertyChanges", [])
        property_names = [
            str(change.get("property"))
            for change in property_changes
            if isinstance(change, dict) and change.get("property")
        ]
        searchable = [
            operation.get("unitId"),
            operation.get("kind"),
            operation.get("selector"),
            *operation.get("matchedVisualTargetIds", []),
            *property_names,
        ]
        operations.append(
            {
                "unitId": operation.get("unitId"),
                "kind": operation.get("kind"),
                "selector": operation.get("selector"),
                "targetResolutionStatus": operation.get("targetResolutionStatus"),
                "matchedVisualTargetIds": operation.get("matchedVisualTargetIds", []),
                "applicationPolicy": operation.get("applicationPolicy"),
                "patchPolicy": operation.get("patchPolicy"),
                "propertyCount": len(property_changes),
                "propertyChanges": property_changes,
                "searchText": " ".join(str(value).lower() for value in searchable if value),
            }
        )

    recipe_units = recipe.get("visualStack", {}).get("units", [])
    planned_property_count = sum(
        len(unit.get("properties", {}))
        for unit in recipe_units
        if isinstance(unit, dict) and isinstance(unit.get("properties"), dict)
    )
    missing_property_count = sum(
        len(unit.get("uncoveredKnownProperties", []))
        for unit in coverage.get("units", [])
        if isinstance(unit, dict)
    )

    gates = [
        {"gateId": "CANONICAL_AUTHORITY", "status": "PASS", "blocks": []},
        {"gateId": "UIMAP_EXACT_TARGET", "status": "PASS", "blocks": []},
        {"gateId": "RIFAT_BINDING", "status": "PASS", "blocks": []},
        {"gateId": "UI_BRIDGE_SOURCE_PLAN", "status": "PASS", "blocks": []},
        {
            "gateId": "RECIPE_COVERAGE_FRESHNESS",
            "status": "BLOCKED_BY_STALE_RUNTIME_EVIDENCE" if coverage_evidence_stale else "PASS",
            "blocks": ["RUNTIME_CERTIFICATION", "PRODUCT_APPLICATION"] if coverage_evidence_stale else [],
        },
        {
            "gateId": "MAMASTROPHIC_VISUAL_EVIDENCE",
            "status": mamastrophic["status"],
            "blocks": ["VISUAL_EVIDENCE", "RUNTIME_CERTIFICATION"] if not mamastrophic_available else [],
        },
        {
            "gateId": "PRODUCT_APPLICATION",
            "status": "DISABLED_BY_CONTRACT",
            "blocks": ["SOURCE_MUTATION"],
        },
    ]

    projection: dict[str, Any] = {
        "schema": "PRISMA_ATLASFIN_VISUAL_CONTROL_PILOT_V1",
        "schemaVersion": "1.0.0",
        "controlId": "ATLASFIN.CONTROL.TABLET.POS.COBRAR.V1",
        "projectionRole": "REGENERABLE_READ_ONLY_VIEW_NOT_SOURCE_OF_TRUTH",
        "status": "READY_FOR_SOURCE_ONLY_PLANNING",
        "applicationReadiness": "BLOCKED_PENDING_EVIDENCE_AND_EXPLICIT_AUTHORIZATION",
        "authority": {
            "canonicalCabin": "prisma-html/extras/atlasfin",
            "authorityOrder": [
                "CANONICAL_AUTHORITY",
                "FACTORY_LEDGER",
                "FRESH_AUTHORITY_MESH",
                "ACTIVE_OWNERS_AND_GENERATORS",
                "CONTRACTS_AND_GATES",
                "RUNTIME_EVIDENCE",
                "GIT_HISTORY_CONTEXT_ONLY",
            ],
            "uimap": {
                "batchId": batch.get("batchId"),
                "supersedesBatchId": batch.get("supersedesBatchId"),
                "sourceSnapshotHash": batch.get("sourceSnapshotHash"),
                "contractHash": batch.get("contractHash"),
                "batchArtifactSha256": sha256_file(uimap_batch_path),
                "sourceReference": "EXTERNALLY_SUPPLIED_IMMUTABLE_CERTIFIED_BATCH",
            },
            "rifatBindingRegistry": {
                "path": relative_repo_path(repo_root, binding_path),
                "sha256": sha256_file(binding_path),
            },
            "recipe": {
                "fullStackPath": relative_repo_path(repo_root, recipe_path),
                "fullStackSha256": sha256_file(recipe_path),
                "bridgeSelectedPath": relative_repo_path(repo_root, bridge_recipe_source),
                "bridgeSelectedSha256": sha256_file(bridge_recipe_source),
                "bridgeCanonicalPayloadSha256": plan.get("recipeSha256"),
            },
            "codeAtlasUiBridge": "tools/code-atlas/src/code_atlas/ui_bridge",
        },
        "pilot": {
            "surfaceId": component.get("surfaceId"),
            "interfaceId": component.get("interfaceId"),
            "routeId": component.get("routeId"),
            "routePath": component.get("routePath"),
            "ownerId": component.get("ownerId"),
            "ownerFile": owner_source,
            "regionId": component.get("regionId"),
            "slotId": component.get("slotId"),
            "componentId": component.get("componentId"),
            "componentUiId": component.get("componentUiId"),
            "selector": ".cobrarReferenceButton",
            "layerId": component.get("layerId"),
            "implementationLayerId": component.get("implementationLayerId"),
            "bindingId": component.get("bindingId"),
            "bindingStatus": binding.get("status"),
            "styleSourceFile": style_source,
            "visualTargetIds": [
                target.get("visualTargetId")
                for target in component.get("visualTargets", [])
                if isinstance(target, dict) and target.get("visualTargetId")
            ],
        },
        "recipe": {
            "recipeId": recipe.get("recipeId"),
            "visualStackId": recipe.get("visualStackId"),
            "instructionOnly": recipe.get("instructionOnly"),
            "runtimeMutationAllowed": recipe.get("runtimeMutationAllowed"),
            "productApplicationAllowed": recipe.get("productApplicationAllowed"),
            "coverageStatus": coverage.get("recipeCoverageStatus"),
            "unitCount": len(recipe_units),
            "plannedPropertyCount": planned_property_count,
            "knownDeclarationCount": coverage.get("knownDeclarationCount"),
            "missingKnownDeclarationCount": coverage.get("uncoveredKnownDeclarationCount"),
            "missingPropertyCount": missing_property_count,
            "options": [{"recipeId": RECIPE_ID, "status": "COMPATIBLE_CERTIFIED_SOURCE_ONLY"}],
        },
        "evidence": {
            "source": {
                "ownerSha256": current_owner_sha,
                "styleSha256": current_css_sha,
                "declaredCoverageOwnerSha256": declared_owner_sha,
                "declaredCoverageStyleSha256": declared_css_sha,
                "ownerEvidenceStale": owner_stale,
                "coverageEvidenceStale": coverage_stale,
                "coverageArtifact": relative_repo_path(repo_root, coverage_path),
            },
            "mamastrophic": mamastrophic,
            "runtime": {
                "status": "NOT_CERTIFIED",
                "sourceOnlyEvidenceMustNotBePromoted": True,
            },
        },
        "plan": {
            "planId": plan.get("planId"),
            "schema": plan.get("schema"),
            "mode": plan.get("mode"),
            "status": plan.get("status"),
            "applicationEnabled": plan.get("applicationEnabled"),
            "blockingReasons": plan.get("blockingReasons", []),
            "adapterId": plan.get("adapterId"),
            "operationCount": len(operations),
            "semanticDiffChecksum": semantic_diff.get("checksum"),
            "sourceMutationPerformed": semantic_diff.get("sourceMutationPerformed"),
            "operations": operations,
        },
        "gates": gates,
        "workflow": [
            "SELECT_CERTIFIED_TARGET",
            "SELECT_COMPATIBLE_RECIPE",
            "REVIEW_COVERED_AND_MISSING_PROPERTIES",
            "REVIEW_DETERMINISTIC_SOURCE_PLAN",
            "COLLECT_BEFORE_VISUAL_EVIDENCE",
            "PASS_APPLICATION_AUTHORIZATION_GATE",
            "APPLY_IN_FUTURE_AUTHORIZED_WORKFLOW",
            "COLLECT_AFTER_VISUAL_EVIDENCE",
            "VERIFY_GATES_OR_ROLL_BACK",
        ],
        "history": [
            {
                "event": "UIMAP_BATCH_SELECTED",
                "batchId": batch.get("batchId"),
                "supersedesBatchId": batch.get("supersedesBatchId"),
                "mutationPerformed": False,
            },
            {
                "event": "UI_BRIDGE_SOURCE_PLAN_BUILT",
                "planId": plan.get("planId"),
                "status": plan.get("status"),
                "mutationPerformed": False,
            },
            {
                "event": "PRODUCT_APPLICATION_NOT_EXECUTED",
                "reason": "DISABLED_BY_CONTRACT",
                "mutationPerformed": False,
            },
        ],
        "rollback": {
            "currentPlan": "NO_SOURCE_MUTATION_PERFORMED_NO_ROLLBACK_REQUIRED",
            "futurePolicy": "RESTORE_ONLY_EXACT_AUTHORIZED_PATCH_WITH_BEFORE_HASH_MATCH",
            "protectedFiles": [owner_source, style_source],
            "beforeHashes": {owner_source: current_owner_sha, style_source: current_css_sha},
        },
        "safety": {
            "instructionOnly": True,
            "runtimeMutationAllowed": False,
            "productApplicationAllowed": False,
            "sourceMutationPerformed": False,
            "surfaceExpansionAllowed": False,
        },
        "rescuedPatterns": [
            {
                "pattern": "PROVENANCE_VISIBLE_WITH_EACH_DECISION",
                "origin": "NON_AUTHORITY_PARALLEL_PROTOTYPE_IDEA_ONLY",
                "copiedFiles": [],
            },
            {
                "pattern": "HIERARCHY_RISKS_GATES_HISTORY_ROLLBACK",
                "origin": "NON_AUTHORITY_PARALLEL_PROTOTYPE_IDEA_ONLY",
                "copiedFiles": [],
            },
        ],
        "rendering": {
            "loadPolicy": "LAZY_ON_EXPLICIT_OPEN",
            "operationPageSize": 4,
            "initialOperationRenderCount": 0,
            "searchPolicy": "PRECOMPUTED_SCALAR_SEARCH_TEXT_NO_JSON_STRINGIFY",
        },
    }
    projection["integrity"] = {
        "algorithm": "SHA-256",
        "canonicalPayloadSha256": hashlib.sha256(canonical_bytes(projection)).hexdigest(),
    }
    return projection


def serialized_outputs(projection: dict[str, Any]) -> tuple[str, str]:
    json_text = json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    js_text = "window.PRISMA_ATLASFIN_VISUAL_CONTROL = " + json_text.rstrip() + ";\n"
    return json_text, js_text


def build_application_projection(
    uimap_batch_path: Path,
    application_result_path: Path,
    evidence_bundle_path: Path,
) -> dict[str, Any]:
    batch = read_json(uimap_batch_path)
    component = require_one(batch.get("components", []), "componentUiId", COMPONENT_UI_ID)
    result = read_json(application_result_path)
    evidence = read_json(evidence_bundle_path)
    if result.get("schema") != APPLICATION_SCHEMA:
        raise ValueError("Application result schema mismatch")
    if result.get("controlId") != "ATLASFIN.CONTROL.TABLET.POS.COBRAR.V1":
        raise ValueError("Application result control mismatch")
    if result.get("status") not in {
        "APPLIED_SOURCE_VALIDATION_PENDING_RUNTIME_VISUAL_CERTIFICATION",
        "SOURCE_APPLIED_AND_VERIFIED_PENDING_RUNTIME_VISUAL_CERTIFICATION",
    }:
        raise ValueError("Application result did not verify the source transaction")
    if result.get("productFileCount") != 1 or result.get("productFiles") != [
        "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
    ]:
        raise ValueError("Application result expanded beyond the exact product target")
    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("Application evidence schema mismatch")
    if evidence.get("status") != "APPLIED_AND_RUNTIME_VISUAL_CERTIFIED":
        raise ValueError("Runtime visual evidence is not certified")
    comparison = evidence.get("comparison", {})
    required_comparison = {
        "sameRoute": True,
        "sameViewport": True,
        "sameBrowser": True,
        "sameTarget": True,
        "bboxStable": True,
    }
    for field, expected in required_comparison.items():
        if comparison.get(field) is not expected:
            raise ValueError(f"Runtime comparison gate failed: {field}")
    if comparison.get("pixel", {}).get("visuallyChanged") is not True:
        raise ValueError("Runtime target did not change visually")
    if evidence.get("network", {}).get("status") != "PASS_NO_TARGET_NETWORK_FAILURES":
        raise ValueError("Runtime target has network failures")
    if evidence.get("console", {}).get("newErrorCount") != 0:
        raise ValueError("Runtime target introduced console errors")
    current_css_sha = str(result.get("after", {}).get("productCssSha256", "")).lower()
    certified_hashes = {
        str(target.get("sourceHash", "")).lower()
        for target in component.get("visualTargets", [])
        if isinstance(target, dict) and target.get("styleSourceFile")
        == "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
    }
    if certified_hashes != {current_css_sha}:
        raise ValueError("Application result and corrective UIMAP CSS hashes diverge")
    projection = {
        "schema": APPLICATION_SCHEMA,
        "schemaVersion": "1.0.0",
        "taskId": result.get("taskId"),
        "controlId": result.get("controlId"),
        "transactionId": result.get("transactionId"),
        "requestSha256": result.get("requestSha256"),
        "mode": "verify",
        "status": "APPLIED_AND_RUNTIME_VISUAL_CERTIFIED",
        "sourceMutationPerformed": True,
        "productFileCount": 1,
        "productFiles": list(result.get("productFiles", [])),
        "authorityFiles": list(result.get("authorityFiles", [])),
        "selectors": list(result.get("selectors", [])),
        "policyOnlySelectors": list(result.get("policyOnlySelectors", [])),
        "before": result.get("before"),
        "observedAtExecution": result.get("observedAtExecution"),
        "after": result.get("after"),
        "preview": {
            "changedLineCount": result.get("preview", {}).get("changedLineCount"),
            "patchSha256": result.get("preview", {}).get("sha256"),
            "portableArtifact": "evidence/transaction/COBRAR_EXACT_TARGET.preview.patch",
            "previousAuthorizedPlan": {
                "planId": "BRPLAN.ca4eebf8f3a79d3ec6944488",
                "checksum": "cce8fd8567744602264cf386902ad2e8e1f78042919a4b9365d158c351f83153",
                "operationCount": 11,
                "plannedPropertyCount": 89,
            },
            "evidenceBundle": {
                "artifactName": evidence_bundle_path.name,
                "sha256": sha256_file(evidence_bundle_path),
                "beforeEvidenceSha256": evidence.get("before", {}).get("evidenceSha256"),
                "afterEvidenceSha256": evidence.get("after", {}).get("evidenceSha256"),
                "beforeScreenshotSha256": evidence.get("before", {}).get("screenshotSha256"),
                "afterScreenshotSha256": evidence.get("after", {}).get("screenshotSha256"),
                "comparison": comparison,
                "states": evidence.get("states", []),
                "console": evidence.get("console", {}),
                "network": evidence.get("network", {}),
            },
            "uimap": {
                "batchId": batch.get("batchId"),
                "supersedesBatchId": batch.get("supersedesBatchId"),
                "batchSha256": sha256_file(uimap_batch_path),
                "sourceSnapshotHash": batch.get("sourceSnapshotHash"),
            },
            "postApplicationPlan": {
                "status": "NO_ACTIONABLE_DIFF",
                "idempotencyDisposition": result.get("idempotencyDisposition"),
                "changedLineCount": result.get("preview", {}).get("postApplicationChangedLineCount", 0),
            },
        },
        "rollback": {
            "ready": True,
            "portableManifest": "evidence/rollback/MANIFEST.json",
            "policy": "RESTORE_EXACT_BEFORE_BYTES_AND_REVALIDATE",
        },
        "idempotencyDisposition": result.get("idempotencyDisposition"),
        "createdAt": result.get("createdAt"),
    }
    projection["integrity"] = {
        "algorithm": "SHA-256",
        "canonicalPayloadSha256": hashlib.sha256(canonical_bytes(projection)).hexdigest(),
    }
    serialized = json.dumps(projection, ensure_ascii=False)
    if re.search(r"[A-Za-z]:\\", serialized):
        raise ValueError("Portable application projection contains a local absolute path")
    return projection


def serialized_application_outputs(projection: dict[str, Any]) -> tuple[str, str]:
    json_text = json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    js_text = "window.PRISMA_ATLASFIN_VISUAL_APPLICATION = " + json_text.rstrip() + ";\n"
    return json_text, js_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the Atlasfin canonical Cobrar control view")
    parser.add_argument("atlas_root")
    parser.add_argument("--uimap-batch", required=True)
    parser.add_argument("--mamastrophic-evidence")
    parser.add_argument("--application-result")
    parser.add_argument("--application-evidence")
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    atlas_root = Path(args.atlas_root)
    output_root = Path(args.output) if args.output else atlas_root / "assets" / "data"
    projection = build_projection(
        atlas_root,
        Path(args.uimap_batch),
        Path(args.mamastrophic_evidence) if args.mamastrophic_evidence else None,
    )
    json_text, js_text = serialized_outputs(projection)
    json_path = output_root / "visual-control.cobrar.pilot.json"
    js_path = output_root / "visual-control.cobrar.pilot.js"
    application_pairs: list[tuple[Path, str]] = []
    if bool(args.application_result) != bool(args.application_evidence):
        raise ValueError("--application-result and --application-evidence must be supplied together")
    if args.application_result and args.application_evidence:
        application = build_application_projection(
            Path(args.uimap_batch),
            Path(args.application_result),
            Path(args.application_evidence),
        )
        application_json, application_js = serialized_application_outputs(application)
        application_pairs = [
            (output_root / "visual-application.cobrar.current.json", application_json),
            (output_root / "visual-application.cobrar.current.js", application_js),
        ]
    if args.check:
        mismatches = [
            str(path)
            for path, expected in [
                (json_path, json_text),
                (js_path, js_text),
                *application_pairs,
            ]
            if not path.is_file() or path.read_text(encoding="utf-8") != expected
        ]
        if mismatches:
            print(json.dumps({"status": "FAIL_NON_DETERMINISTIC_OR_STALE", "paths": mismatches}, indent=2))
            return 2
        print(json.dumps({"status": "PASS_DETERMINISTIC", "planId": projection["plan"]["planId"]}, indent=2))
        return 0
    output_root.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json_text, encoding="utf-8", newline="\n")
    js_path.write_text(js_text, encoding="utf-8", newline="\n")
    for path, content in application_pairs:
        path.write_text(content, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "status": projection["status"],
                "planId": projection["plan"]["planId"],
                "outputs": [str(json_path), str(js_path), *[str(path) for path, _ in application_pairs]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
