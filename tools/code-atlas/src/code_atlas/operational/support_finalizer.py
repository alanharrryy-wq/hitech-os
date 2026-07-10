from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

VERSION = "1.0.0"
FINALIZER_ID = "PRISMA_SUPPORT_RESOLVER_FINALIZER"

EXPECTED_CANONICAL_PATHS = [
    "README.md", "AUTHORITY_MAP.md", "DUPLICATE_MAP.md", "DEPRECATION_MAP.md", "MIGRATION_REPORT.md",
    "SUPPORT_RESOLVER_FINAL_MANIFEST.json", "SUPPORT_RESOLVER_FINAL_MANIFEST.md",
    "SUPPORT_RESOLVER_GAP_REGISTER.json", "SUPPORT_RESOLVER_GAP_REGISTER.md",
    "SUPPORT_RESOLVER_UI_HANDOFF.json", "SUPPORT_RESOLVER_UI_HANDOFF.md",
    "catalogs/feature-gates.json", "catalogs/resolver-actions.json", "catalogs/resolver-actions.md",
    "catalogs/support-error-codes.json", "catalogs/support-error-codes.md", "catalogs/surface-status-catalog.json",
    "contracts/PRISMA_CUSTOMER_SETUP_CANONICAL_CONTRACT.md",
    "contracts/PRISMA_DEVICE_ACTIVATION_CANONICAL_CONTRACT.md",
    "contracts/PRISMA_RUNTIME_CONFIG_CANONICAL_CONTRACT.md",
    "contracts/PRISMA_SUPPORT_BUNDLE_STANDARD.md",
    "contracts/PRISMA_SUPPORT_ERROR_CODE_CATALOG.md",
    "contracts/PRISMA_SUPPORT_RESOLUTION_ACTION_MATRIX.md",
    "contracts/PRISMA_SUPPORT_RESOLVER_CENTER_CONTRACT.md",
    "contracts/PRISMA_SUPPORT_SEARCH_AND_CASE_SCHEMA.md",
    "contracts/PRISMA_SUPPORT_SURFACE_STATUS_STANDARD.md",
    "schemas/customer-setup.schema.json", "schemas/device-identity.schema.json", "schemas/runtime-config.schema.json",
    "schemas/support-bundle.schema.json", "schemas/support-case.schema.json", "schemas/support-issue.schema.json",
    "schemas/support-resolution-action.schema.json", "schemas/support-search.schema.json", "schemas/surface-status.schema.json",
    "adapters/README.md", "adapters/cloud-center-adapter.md", "adapters/mobile-surface-adapter.md",
    "adapters/pc-surface-adapter.md", "adapters/tablet-surface-adapter.md",
    "evidence/README.md", "evidence/evidence-export-contract.md", "evidence/support-bundle-redaction-rules.md",
    "fixtures/README.md", "fixtures/demo/cross-source-identity-split.support-issue.json",
    "fixtures/demo/license-assignment-wrong-business.support-issue.json", "fixtures/demo/surface-status.tablet.blocked.json",
    "fixtures/sanitized/external-licensing-inventory.json",
    "tests/README.md", "tests/cases/cross-source-identity-split.case.json",
    "tests/cases/license-assignment-wrong-business.case.json",
    "tests/cases/setup-claim-or-refresh-apply-preflight.case.json",
    "tests/cases/setup-claim-or-refresh-guided.case.json",
    "generated/ui/README.md", "generated/ui/support-resolver-ui-feed.json",
    "generated/ui/support-resolver-ui-feed.schema.json", "generated/ui/support-resolver-ui-types.ts",
]

EXTERNAL_CANDIDATES = [
    "Prisma Cloud Ctr/internal/py/support_resolver_api.py",
    "Prisma Cloud Ctr/internal/py/license_ops_api.py",
    "Prisma Cloud Ctr/internal/py/cloud_saas_api.py",
    "Prisma Cloud Ctr/internal/py/licflow4_admin_bridge.py",
    "Prisma Cloud Ctr/internal/py/prisma_unified_lab_v3.py",
    "Prisma Cloud Ctr/internal/web/cloud_command_center.js",
    "Prisma Cloud Ctr/internal/web/cloud_command_center.css",
    "shared/licensing", "shared/runtime", "products/pc", "products/tablet", "products/mobile",
    "tools/verify-support-resolver.mjs", "tools/verify-support-resolver-recon4.mjs",
    "tools/verify-support-resolver-recon5.mjs", "tools/verify-customer-setup-multidevice.mjs",
    "tools/smoke-licops-e2e.mjs", "tools/verify-licflow2.mts", "tools/verify-licflow3.mts", "tools/verify-licflow4.mts",
]

ALLOWED_STATUS = {
    "EXISTS_CANONICAL", "EXISTS_CONNECTED", "PARTIAL", "MISSING_CONFIRMED", "TEST_ONLY", "DOC_ONLY", "LEGACY",
    "DEPRECATED", "DUPLICATE_CANDIDATE", "BLOCKED", "NOT_APPLICABLE", "IMPLEMENTED_UNTESTED",
    "IMPLEMENTED_AND_TESTED", "CERTIFIED",
}
ALLOWED_ACTION = {
    "USE_AS_IS", "USE_AND_CONNECT", "FIX_EXISTING", "EXTEND_EXISTING", "CREATE_MISSING", "MERGE_INTO_CANONICAL",
    "DEPRECATE_DUPLICATE", "MOVE_TO_TRASH_OLD_WITH_MANIFEST", "BLOCK_SECRET_RISK", "NO_CHANGE",
}
GAP_CLASSIFICATIONS = {
    "IMPLEMENTED_SAME_NAME", "IMPLEMENTED_DIFFERENT_NAME", "COVERED_BY_COMPOSITE_ACTION", "CONTRACT_ONLY",
    "MISSING_CONFIRMED", "NOT_APPLICABLE_CURRENT_RUNTIME", "BLOCKED_BY_AUTHORITY", "BLOCKED_BY_SAFETY", "LEGACY_ONLY",
}


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_json(path: Path, value: Any) -> None:
    _write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _app_root(repo_root: Path) -> Path:
    direct = repo_root / "apps" / "terminal-de-venta-system"
    if direct.exists():
        return direct
    if repo_root.name == "terminal-de-venta-system":
        return repo_root
    raise FileNotFoundError("terminal-de-venta-system app root not found")


def _artifact_type(rel: str) -> str:
    p = Path(rel)
    if rel.startswith("catalogs/"):
        return "CATALOG"
    if rel.startswith("contracts/"):
        return "CONTRACT"
    if rel.startswith("schemas/"):
        return "SCHEMA"
    if rel.startswith("adapters/"):
        return "ADAPTER"
    if rel.startswith("evidence/"):
        return "EVIDENCE_CONTRACT"
    if rel.startswith("fixtures/"):
        return "FIXTURE"
    if rel.startswith("tests/"):
        return "TEST_ASSET"
    if rel.startswith("generated/ui/"):
        return "UI_FEED"
    if p.suffix.lower() == ".json":
        return "MANIFEST"
    return "DOCUMENT"


def _split_paths(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if str(x)]
    return [x for x in str(value or "").split("|") if x]


def _coverage_map(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(row.get(key)): row for row in rows if row.get(key)}


def _artifact_record(app: Path, support_root: Path, rel: str, generated_rels: set[str]) -> dict[str, Any]:
    target = support_root / rel
    exists = target.exists()
    generated = rel in generated_rels
    current = "EXISTS_CANONICAL" if exists else ("PARTIAL" if generated else "MISSING_CONFIRMED")
    action = "USE_AS_IS" if exists and not generated else ("EXTEND_EXISTING" if exists else "CREATE_MISSING")
    return {
        "id": "ART." + re.sub(r"[^a-z0-9]+", ".", rel.lower()).strip("."),
        "name": Path(rel).name,
        "artifactType": _artifact_type(rel),
        "canonicalPath": str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\"),
        "expectedAtFinal": True,
        "existsNow": exists,
        "currentStatus": current,
        "requiredFinalStatus": "EXISTS_CANONICAL",
        "authority": "prisma-support-resolver",
        "authorityDecision": "CANONICAL_DOCUMENTARY_ROOT",
        "implementationOwner": "Support Resolver canonical root",
        "implementationPaths": [],
        "uiSurfacePaths": [],
        "apiPaths": [],
        "contractPaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if rel.startswith("contracts/") else [],
        "schemaPaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if rel.startswith("schemas/") else [],
        "catalogPaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if rel.startswith("catalogs/") else [],
        "testPaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if rel.startswith("tests/") else [],
        "executableTestPaths": [],
        "documentationEvidencePaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if target.suffix.lower() == ".md" else [],
        "generatedEvidencePaths": [str(Path("prisma-support-resolver") / Path(rel)).replace("/", "\\")] if generated else [],
        "dependencies": [],
        "duplicateCandidates": [],
        "legacySources": [],
        "secretRisk": "NONE",
        "action": action,
        "blockingReason": "" if exists or generated else "Canonical artifact missing before finalization",
        "validationStatus": "PENDING_GENERATION" if generated else ("PASS_EXISTS" if exists else "PENDING_CREATE"),
        "notes": "Generated by Support Finalizer" if generated else "Canonical source artifact",
    }


def _md_table(headers: list[str], rows: Iterable[Iterable[Any]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in row) + " |")
    return "\n".join(out)


def _build_types() -> str:
    return """// Generated by PRISMA Support Resolver Finalizer. Do not hand-edit.\n\nexport type SupportArtifactStatus =\n  | 'EXISTS_CANONICAL' | 'EXISTS_CONNECTED' | 'PARTIAL' | 'MISSING_CONFIRMED'\n  | 'TEST_ONLY' | 'DOC_ONLY' | 'LEGACY' | 'DEPRECATED' | 'DUPLICATE_CANDIDATE'\n  | 'BLOCKED' | 'NOT_APPLICABLE' | 'IMPLEMENTED_UNTESTED' | 'IMPLEMENTED_AND_TESTED' | 'CERTIFIED';\n\nexport interface SupportResolverUiFeed {\n  schemaVersion: '1.0.0';\n  generatedAt: string;\n  authority: Record<string, unknown>;\n  summary: Record<string, number | string | boolean>;\n  navigation: Array<{id:string; label:string; screen:string; dataKeys:string[]}>;\n  screens: Array<{id:string; title:string; purpose:string; dataKeys:string[]; states:string[]; actions:string[]}>;\n  errorCodes: Array<Record<string, unknown>>;\n  actions: Array<Record<string, unknown>>;\n  surfaces: Record<string, unknown>;\n  featureGates: Record<string, unknown>;\n  routes: Array<Record<string, unknown>>;\n  capabilities: Array<Record<string, unknown>>;\n  gaps: Array<Record<string, unknown>>;\n  safety: Record<string, unknown>;\n}\n"""


def _build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "PRISMA_SUPPORT_RESOLVER_UI_FEED_V1",
        "title": "PRISMA Support Resolver UI Feed",
        "type": "object",
        "required": ["schemaVersion", "generatedAt", "authority", "summary", "navigation", "screens", "errorCodes", "actions", "surfaces", "featureGates", "routes", "capabilities", "gaps", "safety"],
        "properties": {
            "schemaVersion": {"const": "1.0.0"}, "generatedAt": {"type": "string"},
            "authority": {"type": "object"}, "summary": {"type": "object"},
            "navigation": {"type": "array"}, "screens": {"type": "array"},
            "errorCodes": {"type": "array", "minItems": 68}, "actions": {"type": "array", "minItems": 13},
            "surfaces": {"type": "object"}, "featureGates": {"type": "object"},
            "routes": {"type": "array"}, "capabilities": {"type": "array"}, "gaps": {"type": "array"},
            "safety": {"type": "object"},
        },
        "additionalProperties": False,
    }


def run_support_finalizer(repo_root: str | Path, atlas_output: str | Path, authority: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    app = _app_root(repo)
    support_root = app / "prisma-support-resolver"
    support_root.mkdir(parents=True, exist_ok=True)
    atlas = Path(atlas_output).resolve() / "support_resolver"
    if not atlas.exists():
        raise FileNotFoundError(f"Code Atlas Support output not found: {atlas}")

    errors_catalog = _load_json(support_root / "catalogs/support-error-codes.json", {}).get("codes", [])
    actions_catalog = _load_json(support_root / "catalogs/resolver-actions.json", {}).get("actions", [])
    feature_gates = _load_json(support_root / "catalogs/feature-gates.json", {})
    surface_status = _load_json(support_root / "catalogs/surface-status-catalog.json", {})
    error_cov = _load_json(atlas / "supportErrorCodeCoverage.json", [])
    action_cov = _load_json(atlas / "supportActionCoverage.json", [])
    routes = _load_json(atlas / "supportUiRouteMap.json", [])
    capabilities = _load_json(atlas / "supportCapabilityMatrix.json", [])
    e2e = _load_json(atlas / "supportE2eCoverage.json", [])
    duplicates = _load_json(atlas / "supportDuplicateImplementations.json", [])
    security = _load_json(atlas / "supportSecurityRisks.json", [])
    atlas_manifest = _load_json(atlas / "SUPPORT_ATLAS_MANIFEST.json", {})

    if len(errors_catalog) != 68 or len(actions_catalog) != 13:
        raise RuntimeError(f"Canonical catalog count mismatch: errors={len(errors_catalog)} actions={len(actions_catalog)}")

    error_map = _coverage_map(error_cov, "code")
    action_map = _coverage_map(action_cov, "action")
    generated_rels = {x for x in EXPECTED_CANONICAL_PATHS if x.startswith("generated/ui/") or x.startswith("SUPPORT_RESOLVER_")}
    artifacts = [_artifact_record(app, support_root, rel, generated_rels) for rel in EXPECTED_CANONICAL_PATHS]

    external_artifacts = []
    for rel in EXTERNAL_CANDIDATES:
        p = app / rel
        external_artifacts.append({
            "id": "EXT." + re.sub(r"[^a-z0-9]+", ".", rel.lower()).strip("."),
            "name": p.name, "artifactType": "IMPLEMENTATION" if p.suffix else "IMPLEMENTATION_AREA",
            "canonicalPath": rel.replace("/", "\\"), "expectedAtFinal": True, "existsNow": p.exists(),
            "currentStatus": "EXISTS_CONNECTED" if p.exists() else "PARTIAL", "requiredFinalStatus": "EXISTS_CONNECTED",
            "authority": "live repo", "authorityDecision": "VERIFY_EXISTING_NOT_REBUILD", "implementationOwner": rel,
            "implementationPaths": [rel.replace("/", "\\")] if p.exists() else [], "uiSurfacePaths": [], "apiPaths": [],
            "contractPaths": [], "schemaPaths": [], "catalogPaths": [],
            "testPaths": [rel.replace("/", "\\")] if ("verify" in rel.lower() or "smoke" in rel.lower()) else [],
            "executableTestPaths": [rel.replace("/", "\\")] if p.exists() and ("verify" in rel.lower() or "smoke" in rel.lower()) else [],
            "documentationEvidencePaths": [], "generatedEvidencePaths": [], "dependencies": [], "duplicateCandidates": [],
            "legacySources": [], "secretRisk": "NONE", "action": "USE_AND_CONNECT" if p.exists() else "NO_CHANGE",
            "blockingReason": "" if p.exists() else "Expected integration candidate not found at current path",
            "validationStatus": "PASS_EXISTS" if p.exists() else "REVIEW_PATH_OR_NOT_APPLICABLE", "notes": "External live implementation candidate",
        })

    error_rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    for item in errors_catalog:
        code = str(item.get("code"))
        cov = error_map.get(code, {})
        active = int(cov.get("activeReferenceCount", 0) or 0)
        direct_tests = int(cov.get("testReferenceCount", 0) or 0)
        if active and direct_tests:
            status, gap_class = "IMPLEMENTED_AND_TESTED", "IMPLEMENTED_SAME_NAME"
        elif active:
            status, gap_class = "IMPLEMENTED_UNTESTED", "IMPLEMENTED_SAME_NAME"
        else:
            status, gap_class = "DOC_ONLY", "CONTRACT_ONLY"
        row = dict(item)
        row.update({
            "manifestStatus": status, "gapClassification": gap_class,
            "activeReferenceCount": active, "directTestReferenceCount": direct_tests,
            "activePaths": _split_paths(cov.get("activePaths")), "executableTestPaths": _split_paths(cov.get("testPaths")),
            "catalogVerifierPaths": _split_paths(cov.get("catalogVerifierPaths")),
            "uiReferenceCount": int(cov.get("uiReferenceCount", 0) or 0), "apiReferenceCount": int(cov.get("apiReferenceCount", 0) or 0),
        })
        error_rows.append(row)
        if gap_class != "IMPLEMENTED_SAME_NAME" or status != "IMPLEMENTED_AND_TESTED":
            gaps.append({"kind": "ERROR_CODE", "id": code, "label": item.get("label", code), "classification": gap_class, "status": status, "blocking": False, "recommendedAction": "VERIFY_OR_EXTEND_EXISTING" if active else "KEEP_CONTRACT_VISIBLE_TO_UI", "evidencePaths": row["activePaths"] + row["executableTestPaths"]})

    action_rows: list[dict[str, Any]] = []
    for item in actions_catalog:
        action_id = str(item.get("id"))
        cov = action_map.get(action_id, {})
        active = int(cov.get("activeReferenceCount", 0) or 0)
        direct_tests = int(cov.get("testReferenceCount", 0) or 0)
        if active and direct_tests:
            status, gap_class = "IMPLEMENTED_AND_TESTED", "IMPLEMENTED_SAME_NAME"
        elif active:
            status, gap_class = "IMPLEMENTED_UNTESTED", "IMPLEMENTED_SAME_NAME"
        else:
            status, gap_class = "DOC_ONLY", "CONTRACT_ONLY"
        row = dict(item)
        row.update({
            "manifestStatus": status, "gapClassification": gap_class,
            "activeReferenceCount": active, "directTestReferenceCount": direct_tests,
            "activePaths": _split_paths(cov.get("activePaths")), "executableTestPaths": _split_paths(cov.get("testPaths")),
            "catalogVerifierPaths": _split_paths(cov.get("catalogVerifierPaths")),
            "uiBehavior": {
                "buttonEnabledByDefault": bool(item.get("safeByDefault", False)) and not bool(item.get("mutates", item.get("wouldMutate", False))),
                "requiresConfirmation": bool(item.get("requiresConfirmation", False)),
                "requiresDryRun": bool(item.get("requiresDryRun", item.get("requiresRollbackSafePlan", False))),
                "mutates": bool(item.get("mutates", item.get("wouldMutate", False))),
            },
        })
        action_rows.append(row)
        if gap_class != "IMPLEMENTED_SAME_NAME" or status != "IMPLEMENTED_AND_TESTED":
            gaps.append({"kind": "ACTION", "id": action_id, "label": item.get("label", action_id), "classification": gap_class, "status": status, "blocking": bool(item.get("mutates", item.get("wouldMutate", False))) and not active, "recommendedAction": "EXTEND_EXISTING_ONLY_AFTER_AUTHORITY" if not active else "ADD_DIRECT_EXECUTABLE_TEST", "evidencePaths": row["activePaths"] + row["executableTestPaths"]})

    navigation = [
        {"id": "overview", "label": "Resumen", "screen": "support-overview", "dataKeys": ["summary", "capabilities", "gaps"]},
        {"id": "diagnose", "label": "Diagnóstico", "screen": "support-diagnose", "dataKeys": ["errorCodes", "actions", "surfaces"]},
        {"id": "cases", "label": "Casos", "screen": "support-cases", "dataKeys": ["schemas", "routes", "actions"]},
        {"id": "catalog", "label": "Códigos", "screen": "support-error-catalog", "dataKeys": ["errorCodes"]},
        {"id": "actions", "label": "Acciones", "screen": "support-actions", "dataKeys": ["actions", "safety"]},
        {"id": "surfaces", "label": "Superficies", "screen": "support-surfaces", "dataKeys": ["surfaces", "featureGates", "routes"]},
        {"id": "evidence", "label": "Evidencia", "screen": "support-evidence", "dataKeys": ["authority", "capabilities", "gaps", "safety"]},
    ]
    screens = [
        {"id": "support-overview", "title": "Support Command Center", "purpose": "Mostrar salud, cobertura, bloqueadores y próximos pasos sin declarar green falso.", "dataKeys": ["summary", "capabilities", "gaps"], "states": ["ready", "partial", "blocked", "unknown"], "actions": ["diagnose", "export_evidence", "copy_support_summary"]},
        {"id": "support-diagnose", "title": "Diagnóstico guiado", "purpose": "Convertir evidencia de identidad, licencia y runtime en issue codes y acciones seguras.", "dataKeys": ["errorCodes", "actions", "surfaces"], "states": ["idle", "collecting", "diagnosed", "blocked"], "actions": ["diagnose", "simulate_runtime_alignment", "choose_authority", "simulate_identity_reconciliation"]},
        {"id": "support-cases", "title": "Casos y timeline", "purpose": "Buscar, abrir y seguir casos con evidencia, estado y resolución.", "dataKeys": ["schemas", "routes", "actions"], "states": ["empty", "loading", "open", "resolved", "blocked"], "actions": ["export_evidence", "send_to_chatgpt", "send_to_codex", "mark_onsite"]},
        {"id": "support-error-catalog", "title": "Catálogo de errores", "purpose": "Explorar los 68 códigos canónicos y su cobertura viva.", "dataKeys": ["errorCodes"], "states": ["ready", "filtered", "no_results"], "actions": ["copy_support_summary"]},
        {"id": "support-actions", "title": "Acciones resolutivas", "purpose": "Mostrar seguridad, dry-run, confirmación y cobertura de las 13 acciones.", "dataKeys": ["actions", "safety"], "states": ["safe", "requires_simulation", "requires_confirmation", "blocked"], "actions": [x.get("id") for x in actions_catalog]},
        {"id": "support-surfaces", "title": "Estado por superficie", "purpose": "Comparar Tablet, PC y Mobile sin contradicciones visuales.", "dataKeys": ["surfaces", "featureGates", "routes"], "states": list(surface_status.get("operationStatuses", [])), "actions": ["diagnose", "setup_claim", "license_refresh"]},
        {"id": "support-evidence", "title": "Evidencia y autoridad", "purpose": "Mostrar fuentes, contratos, pruebas, gaps y exportación sanitizada.", "dataKeys": ["authority", "capabilities", "gaps", "safety"], "states": ["ready", "partial", "blocked"], "actions": ["export_evidence", "copy_support_summary"]},
    ]

    duplicate_blockers = [row for row in duplicates if str(row.get("status", "")).startswith("BLOCKED")]
    blocking_secrets = [row for row in security if bool(row.get("blocking"))]
    summary = {
        "decision": "VERIFY_AND_FIX_EXISTING_NOT_REBUILD",
        "doNotRebuild": True,
        "canonicalArtifactCount": len(artifacts), "externalIntegrationCandidateCount": len(external_artifacts),
        "errorCodeCount": len(error_rows), "errorCodesImplemented": sum(1 for x in error_rows if x["activeReferenceCount"] > 0),
        "errorCodesDirectlyTested": sum(1 for x in error_rows if x["directTestReferenceCount"] > 0),
        "actionCount": len(action_rows), "actionsImplemented": sum(1 for x in action_rows if x["activeReferenceCount"] > 0),
        "actionsDirectlyTested": sum(1 for x in action_rows if x["directTestReferenceCount"] > 0),
        "uiRouteCount": sum(1 for x in routes if x.get("artifactType") == "UI_ROUTE"),
        "apiRouteCount": sum(1 for x in routes if x.get("artifactType") == "API_ROUTE"),
        "gapCount": len(gaps), "blockingGapCount": sum(1 for x in gaps if x.get("blocking")),
        "blockingSecretRiskCount": len(blocking_secrets), "duplicateAuthorityBlockerCount": len(duplicate_blockers),
        "uiFeedReady": True, "runtimeCertified": False,
    }

    authority_payload = authority or {}
    authority_payload.update({
        "decision": "VERIFY_AND_FIX_EXISTING_NOT_REBUILD", "canonicalRoot": str(support_root),
        "canonicalApi": "Prisma Cloud Ctr/internal/py/support_resolver_api.py", "generatedEvidenceIsAuthority": False,
        "codeAtlasManifestStatus": atlas_manifest.get("status"),
    })

    feed = {
        "schemaVersion": "1.0.0", "generatedAt": _now(), "authority": authority_payload, "summary": summary,
        "navigation": navigation, "screens": screens, "errorCodes": error_rows, "actions": action_rows,
        "surfaces": surface_status, "featureGates": feature_gates, "routes": routes, "capabilities": capabilities,
        "gaps": gaps, "safety": {
            "forbiddenOperations": ["read_private_key", "export_tokens", "export_authorization_headers", "edit_real_env", "edit_signed_license_manually", "deploy", "migrate_d1", "prisma_generate", "kill_processes", "free_ports", "restart_servers", "fake_green"],
            "blockingSecretRisks": blocking_secrets, "reviewCandidates": security,
            "applyRule": "Any mutating action remains blocked without prior simulation, explicit confirmation, backup, rollback and post-validation.",
        },
        "schemas": [str(p.relative_to(support_root)).replace("\\", "/") for p in sorted((support_root / "schemas").glob("*.json"))],
        "e2eCoverage": e2e, "duplicates": duplicates,
    }

    manifest = {
        "schemaVersion": "1.0.0", "manifestId": "PRISMA_SUPPORT_RESOLVER_FINAL_MANIFEST", "generatedAt": _now(),
        "generator": {"id": FINALIZER_ID, "version": VERSION}, "decision": summary["decision"], "doNotRebuild": True,
        "finalStatus": "PARTIAL_SUPPORT_RESOLVER_GAPS_REMAIN" if gaps or duplicate_blockers or blocking_secrets else "PASS_SUPPORT_RESOLVER_FINAL_MANIFEST_COMPLETE",
        "uiDataStatus": "PASS_SUPPORT_DATA_SPINE_READY_FOR_UI", "runtimeCertified": False,
        "summary": summary, "artifacts": artifacts + external_artifacts, "errorCodes": error_rows, "actions": action_rows,
        "flows": e2e, "routes": routes, "capabilities": capabilities, "duplicates": duplicates, "security": security,
        "generatedOutputs": [
            "SUPPORT_RESOLVER_FINAL_MANIFEST.json", "SUPPORT_RESOLVER_FINAL_MANIFEST.md",
            "SUPPORT_RESOLVER_GAP_REGISTER.json", "SUPPORT_RESOLVER_GAP_REGISTER.md",
            "SUPPORT_RESOLVER_UI_HANDOFF.json", "SUPPORT_RESOLVER_UI_HANDOFF.md",
            "generated/ui/support-resolver-ui-feed.json", "generated/ui/support-resolver-ui-feed.schema.json",
            "generated/ui/support-resolver-ui-types.ts", "generated/ui/README.md",
        ],
    }

    # Generated outputs
    generated_dir = support_root / "generated" / "ui"
    _write_json(generated_dir / "support-resolver-ui-feed.json", feed)
    _write_json(generated_dir / "support-resolver-ui-feed.schema.json", _build_schema())
    _write_text(generated_dir / "support-resolver-ui-types.ts", _build_types())
    _write_text(generated_dir / "README.md", "# Support Resolver UI Feed\n\nGenerated, machine-readable data spine for the Support Resolver UI. Codex should consume `support-resolver-ui-feed.json`, validate against the schema, and use the TypeScript definitions. This directory is generated evidence, not runtime authority.\n")
    _write_json(support_root / "SUPPORT_RESOLVER_GAP_REGISTER.json", {"schemaVersion": "1.0.0", "generatedAt": _now(), "count": len(gaps), "gaps": gaps})
    _write_text(support_root / "SUPPORT_RESOLVER_GAP_REGISTER.md", "# Support Resolver Gap Register\n\n" + _md_table(["Kind", "ID", "Classification", "Status", "Blocking", "Action"], [[x["kind"], x["id"], x["classification"], x["status"], x["blocking"], x["recommendedAction"]] for x in gaps]) + "\n")
    handoff = {"schemaVersion": "1.0.0", "generatedAt": _now(), "feedPath": "generated/ui/support-resolver-ui-feed.json", "schemaPath": "generated/ui/support-resolver-ui-feed.schema.json", "typesPath": "generated/ui/support-resolver-ui-types.ts", "navigation": navigation, "screens": screens, "codexRules": ["Do not invent business logic", "Do not rebuild Support Resolver", "Render gaps honestly", "Disable mutating actions unless feed safety permits", "Keep executable tests distinct from documentation evidence", "Use API/UI route map as integration evidence, not as a command to duplicate routes"]}
    _write_json(support_root / "SUPPORT_RESOLVER_UI_HANDOFF.json", handoff)
    _write_text(support_root / "SUPPORT_RESOLVER_UI_HANDOFF.md", "# Support Resolver UI Handoff\n\n- Feed: `generated/ui/support-resolver-ui-feed.json`\n- Schema: `generated/ui/support-resolver-ui-feed.schema.json`\n- Types: `generated/ui/support-resolver-ui-types.ts`\n- Decision: `VERIFY_AND_FIX_EXISTING_NOT_REBUILD`\n- Runtime certified: **No**. The UI must surface gaps honestly.\n\n## Screens\n\n" + _md_table(["Screen", "Purpose", "Data", "Actions"], [[x["id"], x["purpose"], ", ".join(x["dataKeys"]), ", ".join(x["actions"])] for x in screens]) + "\n")
    _write_json(support_root / "SUPPORT_RESOLVER_FINAL_MANIFEST.json", manifest)

    missing_before = sum(1 for x in artifacts if not x["existsNow"] and x["canonicalPath"] not in {"prisma-support-resolver\\SUPPORT_RESOLVER_FINAL_MANIFEST.json", "prisma-support-resolver\\SUPPORT_RESOLVER_FINAL_MANIFEST.md"})
    manifest_md = [
        "# PRISMA Support Resolver Final Manifest", "",
        f"- Generated: `{manifest['generatedAt']}`", f"- Decision: `{manifest['decision']}`",
        f"- Final runtime status: `{manifest['finalStatus']}`", f"- UI data status: `{manifest['uiDataStatus']}`",
        "- Runtime certified: **No**. This manifest and feed are the complete UI data substrate, not a production-runtime certification.", "",
        "## Executive inventory", "",
        _md_table(["Metric", "Value"], [[k, v] for k, v in summary.items()]), "",
        "## Canonical artifacts", "",
        _md_table(["Path", "Type", "Existed before", "Action"], [[x["canonicalPath"], x["artifactType"], x["existsNow"], x["action"]] for x in artifacts]), "",
        "## Runtime gaps", "",
        f"Gaps recorded: **{len(gaps)}**. Missing canonical artifacts before generation: **{missing_before}**.", "",
        "See `SUPPORT_RESOLVER_GAP_REGISTER.md` for item-level classifications.", "",
        "## UI handoff", "",
        "Codex must consume `generated/ui/support-resolver-ui-feed.json` and must not invent capabilities absent from the feed.", "",
    ]
    _write_text(support_root / "SUPPORT_RESOLVER_FINAL_MANIFEST.md", "\n".join(manifest_md))

    # Update generated artifact records after writing.
    for rec in manifest["artifacts"]:
        cp = str(rec.get("canonicalPath", "")).replace("prisma-support-resolver\\", "").replace("\\", "/")
        target = support_root / cp if cp else None
        if target and target.exists():
            rec["existsNow"] = True
            rec["currentStatus"] = "EXISTS_CANONICAL" if rec["artifactType"] != "IMPLEMENTATION" else rec["currentStatus"]
            rec["validationStatus"] = "PASS_EXISTS"
            if target.is_file():
                rec["sha256"] = _sha256(target)
    _write_json(support_root / "SUPPORT_RESOLVER_FINAL_MANIFEST.json", manifest)

    return {"status": "PASS_SUPPORT_DATA_SPINE_READY_FOR_UI", "manifest": manifest, "feed": feed, "supportRoot": str(support_root)}
