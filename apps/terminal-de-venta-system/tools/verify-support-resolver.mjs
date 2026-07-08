import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const resolverRoot = path.join(terminalRoot, "prisma-support-resolver");

const mandatoryCodes = [
  "CROSS_SOURCE_IDENTITY_SPLIT",
  "LICENSE_ASSIGNMENT_WRONG_BUSINESS",
  "LICENSE_ASSIGNMENT_WRONG_CUSTOMER",
  "LICENSE_ASSIGNMENT_WRONG_STORE",
  "LICENSE_ASSIGNMENT_WRONG_TERMINAL",
  "LICENSE_LOCAL_MISSING",
  "LICENSE_LOCAL_INVALID",
  "LICENSE_SIGNATURE_UNVERIFIABLE",
  "LICENSE_EXPIRED",
  "LICENSE_PLAN_SURFACE_NOT_ALLOWED",
  "LICENSE_FEATURE_BLOCKED",
  "LICENSE_REFRESH_DISABLED",
  "LICENSE_REFRESH_FAILED",
  "SETUP_CODE_REQUIRED",
  "SETUP_CODE_INVALID",
  "SETUP_NOT_FOUND",
  "SETUP_EXPIRED",
  "DEVICE_SLOT_FULL",
  "DEVICE_ALREADY_CLAIMED",
  "DEVICE_CLAIM_SURFACE_MISMATCH",
  "SURFACE_NOT_ALLOWED",
  "CUSTOMER_SETUP_INCOMPLETE",
  "DEVICE_REPLACEMENT_REQUIRED",
  "RUNTIME_IDENTITY_DEMO_MODE",
  "RUNTIME_IDENTITY_MISSING",
  "RUNTIME_BUSINESS_ID_MISMATCH",
  "RUNTIME_STORE_ID_MISMATCH",
  "RUNTIME_TERMINAL_ID_MISMATCH",
  "RUNTIME_TERMINAL_ID_NOT_IN_DB",
  "RUNTIME_DEVICE_ID_MISMATCH",
  "RUNTIME_CONFIG_FILE_MISSING",
  "RUNTIME_CONFIG_SCHEMA_INVALID",
  "TERMINAL_NOT_FOUND",
  "TERMINAL_INACTIVE",
  "TERMINAL_NOT_ASSIGNED_TO_DEVICE",
  "CASH_SESSION_NOT_OPEN",
  "CASH_SESSION_TERMINAL_MISMATCH",
  "POS_LOCAL_DB_NOT_FOUND",
  "POS_LOCAL_DB_SCHEMA_DRIFT",
  "POS_OPERATION_BLOCKED_BY_LICENSE",
  "PC_LICENSE_SURFACE_MISSING",
  "PC_ADMIN_SLOT_NOT_CLAIMED",
  "PC_DEVICE_ASSIGNMENT_MISMATCH",
  "PC_FEATURES_BLOCKED_BY_LICENSE",
  "PC_SUPPORT_STATUS_CONTRADICTION",
  "MOBILE_LICENSE_SURFACE_MISSING",
  "MOBILE_COMPANION_SLOT_NOT_CLAIMED",
  "MOBILE_DEVICE_ASSIGNMENT_MISMATCH",
  "MOBILE_SUPPORT_SURFACE_MISSING",
  "MOBILE_FEATURES_BLOCKED_BY_LICENSE",
  "CLOUD_HEALTH_UNREACHABLE",
  "CLOUD_HEALTH_MARKERS_MISSING",
  "CLOUD_ROUTE_404",
  "CLOUD_GATEWAY_UNCERTIFIED",
  "OAUTH_WRANGLER_BLOCKED",
  "D1_SCHEMA_DRIFT",
  "D1_REQUIRED_AUDIT_MISSING",
  "ADMIN_TOKEN_MISSING_FOR_ADMIN_OP",
  "SECRET_EXPOSURE_RISK",
  "SUPPORT_BUNDLE_UNSANITIZED",
  "PRIVATE_KEY_PRESENT_IN_SUPPORT_CONTEXT",
  "TOKEN_VALUE_EXPOSED",
  "RAW_ENV_EXPOSED",
  "NEEDS_CODEX_FIX",
  "NEEDS_CHATGPT_REVIEW",
  "NEEDS_ONSITE_ACTION",
  "NEEDS_HUMAN_APPROVAL",
  "RESOLUTION_NOT_SAFE_REMOTE"
];

const requiredFiles = [
  "README.md",
  "AUTHORITY_MAP.md",
  "DUPLICATE_MAP.md",
  "DEPRECATION_MAP.md",
  "MIGRATION_REPORT.md",
  "contracts/PRISMA_SUPPORT_RESOLVER_CENTER_CONTRACT.md",
  "contracts/PRISMA_SUPPORT_SURFACE_STATUS_STANDARD.md",
  "contracts/PRISMA_SUPPORT_ERROR_CODE_CATALOG.md",
  "contracts/PRISMA_SUPPORT_SEARCH_AND_CASE_SCHEMA.md",
  "contracts/PRISMA_SUPPORT_RESOLUTION_ACTION_MATRIX.md",
  "contracts/PRISMA_SUPPORT_BUNDLE_STANDARD.md",
  "contracts/PRISMA_DEVICE_ACTIVATION_CANONICAL_CONTRACT.md",
  "contracts/PRISMA_CUSTOMER_SETUP_CANONICAL_CONTRACT.md",
  "contracts/PRISMA_RUNTIME_CONFIG_CANONICAL_CONTRACT.md",
  "schemas/support-issue.schema.json",
  "schemas/support-search.schema.json",
  "schemas/support-case.schema.json",
  "schemas/support-resolution-action.schema.json",
  "schemas/support-bundle.schema.json",
  "schemas/surface-status.schema.json",
  "schemas/device-identity.schema.json",
  "schemas/runtime-config.schema.json",
  "schemas/customer-setup.schema.json",
  "catalogs/support-error-codes.json",
  "catalogs/support-error-codes.md",
  "catalogs/resolver-actions.json",
  "catalogs/resolver-actions.md",
  "catalogs/feature-gates.json",
  "catalogs/surface-status-catalog.json",
  "fixtures/demo/license-assignment-wrong-business.support-issue.json",
  "fixtures/demo/surface-status.tablet.blocked.json",
  "fixtures/sanitized/external-licensing-inventory.json",
  "adapters/cloud-center-adapter.md",
  "adapters/tablet-surface-adapter.md",
  "adapters/pc-surface-adapter.md",
  "adapters/mobile-surface-adapter.md",
  "evidence/support-bundle-redaction-rules.md",
  "evidence/evidence-export-contract.md",
  "tests/cases/license-assignment-wrong-business.case.json",
  "fixtures/demo/cross-source-identity-split.support-issue.json",
  "tests/cases/cross-source-identity-split.case.json"
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function read(relativePath) {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function readResolver(relativePath) {
  return fs.readFileSync(path.join(resolverRoot, relativePath), "utf8");
}

function parseResolverJson(relativePath) {
  return JSON.parse(readResolver(relativePath));
}

function walk(root) {
  const out = [];
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else out.push(full);
  }
  return out;
}

function rel(file) {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

for (const file of requiredFiles) {
  assert(fs.existsSync(path.join(resolverRoot, file)), `Missing resolver file ${file}`);
}

for (const file of walk(resolverRoot).filter((item) => item.endsWith(".json"))) {
  JSON.parse(fs.readFileSync(file, "utf8"));
}

const catalog = parseResolverJson("catalogs/support-error-codes.json");
assert(Array.isArray(catalog.codes), "support-error-codes.json must expose codes array");
const codes = catalog.codes.map((item) => item.code);
assert(new Set(codes).size === codes.length, "Duplicate support error codes detected");
for (const code of mandatoryCodes) {
  assert(codes.includes(code), `Missing mandatory support code ${code}`);
}

const requiredCodeFields = [
  "category",
  "severity",
  "label",
  "customerExplanation",
  "technicalExplanation",
  "detectionCriteria",
  "requiredEvidence",
  "suggestedResolution",
  "remoteResolvable",
  "autoResolvable",
  "requiresDryRun",
  "requiresAdminToken",
  "requiresSetupCode",
  "requiresCodex",
  "requiresOnsite",
  "safeActions",
  "blockedActions",
  "validationAfterAction"
];
for (const item of catalog.codes) {
  for (const field of requiredCodeFields) {
    assert(Object.prototype.hasOwnProperty.call(item, field), `Code ${item.code} missing ${field}`);
  }
  assert(item.severity === "info" || item.severity === "warning" || item.severity === "blocked" || item.severity === "critical", `Code ${item.code} has invalid severity`);
  assert(Array.isArray(item.safeActions), `Code ${item.code} safeActions must be array`);
}

const wrongBusiness = parseResolverJson("fixtures/demo/license-assignment-wrong-business.support-issue.json");
assert(wrongBusiness.code === "LICENSE_ASSIGNMENT_WRONG_BUSINESS", "Wrong-business fixture must use canonical code");
assert(wrongBusiness.technicalExplanation.includes("license.businessId != runtime.businessId"), "Wrong-business fixture must include technical mismatch");
assert(wrongBusiness.secretsExposed === false, "Wrong-business fixture must be sanitized");

const identitySplit = parseResolverJson("fixtures/demo/cross-source-identity-split.support-issue.json");
assert(identitySplit.code === "CROSS_SOURCE_IDENTITY_SPLIT", "Identity split fixture must use canonical code");
assert(identitySplit.secretsExposed === false, "Identity split fixture must be sanitized");

const identitySplitCase = parseResolverJson("tests/cases/cross-source-identity-split.case.json");
assert(identitySplitCase.expectedPrimaryIssueCode === "CROSS_SOURCE_IDENTITY_SPLIT", "Identity split case must expect CROSS_SOURCE_IDENTITY_SPLIT");
assert(identitySplitCase.mustNotMutate === true, "Identity split case must remain non-mutating");

const surfaceStatus = parseResolverJson("fixtures/demo/surface-status.tablet.blocked.json");
assert(surfaceStatus.operationStatus === "blocked", "SurfaceStatus fixture must be blocked");
assert(surfaceStatus.primaryIssueCode === "LICENSE_ASSIGNMENT_WRONG_BUSINESS", "SurfaceStatus fixture must point to wrong-business code");
assert(!/lista para operar/i.test(surfaceStatus.visibleStatus), "Blocked SurfaceStatus cannot say ready to operate");

const actions = parseResolverJson("catalogs/resolver-actions.json").actions;
assert(actions.some((item) => item.id === "diagnose"), "Resolver actions missing diagnose");
assert(actions.some((item) => item.id === "apply_runtime_alignment" && item.requiresConfirmation && item.requiresDryRun), "Resolver apply must require dry-run and confirmation");

const supportApi = read("Prisma Cloud Ctr/internal/py/support_resolver_api.py");
for (const route of [
  "/api/support/catalog",
  "/api/support/codes",
  "/api/support/search",
  "/api/support/customer/",
  "/api/support/device/",
  "/api/support/diagnose",
  "/api/support/resolve/simulate",
  "/api/support/resolve/apply",
  "/api/support/export-case"
]) {
  assert(supportApi.includes(route), `Support API missing route ${route}`);
}
assert(supportApi.includes('"wouldMutate": False'), "simulate must report no mutation");
assert(supportApi.includes("confirmResolutionAction"), "apply must require explicit confirmation");
assert(supportApi.includes("_identity_reconciliation"), "Support API must reconcile cross-source identity");
assert(supportApi.includes("CROSS_SOURCE_IDENTITY_SPLIT"), "Support API must detect identity split");

assert(supportApi.includes('"primaryIssueCode": "CROSS_SOURCE_IDENTITY_SPLIT"'), "simulate response must expose CROSS_SOURCE_IDENTITY_SPLIT at top-level");
assert(supportApi.includes('"identityReconciliation": reconciliation'), "simulate response must expose identityReconciliation alias");
assert(supportApi.includes('body.get("identityReconciliationRequested")'), "simulate must honor identityReconciliationRequested from UI");

const server = read("Prisma Cloud Ctr/internal/py/prisma_unified_lab_v3.py");
assert(server.includes("import support_resolver_api"), "Cloud Ctr server must import support resolver API");
assert(server.includes('path.startswith("/api/support")'), "Cloud Ctr server must route /api/support");

assert(server.includes("import importlib"), "Cloud Ctr server must support support_resolver_api reload");
assert(server.includes("support_resolver_payload("), "Cloud Ctr server must route support through reload helper");

const ui = read("Prisma Cloud Ctr/internal/web/cloud_command_center.js");
for (const token of ["Prisma Support Resolver Center", "Reconciliación de identidad", "support-search", "support-diagnose", "support-simulate", "support-apply", "support-export-case", "/api/support/catalog", "/api/support/search"]) {
  assert(ui.includes(token), `Cloud Ctr support UI missing ${token}`);
}

for (const token of ["SUPPORT_IDENTITY_CONTEXT", "supportRequestPayload", "identityReconciliationRequested", "normalizeSupportSimulation", "IDENTITY_RECONCILIATION_REQUIRED"]) {
  assert(ui.includes(token), `Cloud Ctr support UI missing recon3b token ${token}`);
}

const pc = read("products/pc/app/components/license/license-status-card.tsx");
assert(pc.includes("LICENSE_ASSIGNMENT_WRONG_BUSINESS"), "PC license card must expose canonical wrong-business code");
assert(pc.includes("Issue principal"), "PC license card must show primary support issue");

const tablet = read("products/tablet/app/components/license/license-status-card.tsx");
assert(tablet.includes("LICENSE_ASSIGNMENT_WRONG_BUSINESS"), "Tablet license card must expose canonical wrong-business code");
assert(tablet.includes("operación bloqueada por asignación de negocio"), "Tablet license card must avoid ready/blocked contradiction");

const mobile = read("products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
assert(mobile.includes("Licencias y dispositivos"), "Mobile must expose Licencias y dispositivos surface");
assert(mobile.includes("mobile-license-devices"), "Mobile license/devices zone missing");

const text = walk(resolverRoot).map((file) => fs.readFileSync(file, "utf8")).join("\n");
const forbiddenSecretMarkers = [
  "BEGIN " + "PRIVATE KEY",
  "Authorization: " + "Bearer",
  "x-prisma-admin-" + "token:",
  "sk-" + "proj-",
  "s" + "k-"
];
for (const forbidden of forbiddenSecretMarkers) {
  assert(!text.includes(forbidden), `Forbidden secret-like material detected in resolver root: ${forbidden}`);
}

console.log(JSON.stringify({
  ok: true,
  verifier: "verify:support-resolver",
  resolverRoot: rel(resolverRoot),
  filesChecked: requiredFiles.length,
  codesChecked: catalog.codes.length,
  identityReconciliation: true,
  uiSimulateWiredToReconciliation: true,
  supportApiHotReload: true,
  routesChecked: 9,
  noDuplicateCodes: true,
  noBlockedReadyContradiction: true,
  simulateDoesNotMutate: true,
  applyRequiresConfirmation: true,
  secretsExposed: false
}, null, 2));
