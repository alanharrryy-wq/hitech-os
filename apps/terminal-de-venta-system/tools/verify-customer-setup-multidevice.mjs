import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const terminalRoot = path.resolve(scriptDir, "..");
const mode = String(process.argv[2] || "multidevice");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function read(relativePath) {
  return fs.readFileSync(path.join(terminalRoot, relativePath), "utf8");
}

function exists(relativePath) {
  return fs.existsSync(path.join(terminalRoot, relativePath));
}

function walk(root, extensions) {
  const absoluteRoot = path.join(terminalRoot, root);
  if (!fs.existsSync(absoluteRoot)) return [];
  const out = [];
  for (const entry of fs.readdirSync(absoluteRoot, { withFileTypes: true })) {
    const filePath = path.join(absoluteRoot, entry.name);
    if (entry.isDirectory()) out.push(...walk(path.relative(terminalRoot, filePath), extensions));
    else if (extensions.includes(path.extname(entry.name))) out.push(filePath);
  }
  return out;
}

function rel(file) {
  return path.relative(terminalRoot, file).replace(/\\/g, "/");
}

function pass(name, evidence) {
  console.log(JSON.stringify({ ok: true, verifier: name, generatedAt: new Date().toISOString(), ...evidence }, null, 2));
}

function assertSharedContract() {
  const contract = read("shared/licensing/customer-setup-contract.ts");
  const index = read("shared/licensing/index.ts");
  for (const token of [
    "CustomerSetupSurface",
    "CustomerSetupPass",
    "CustomerSetupSlot",
    "DeviceClaimRequest",
    "DeviceClaimResponse",
    "CustomerSetupErrorCode",
    "PRISMA_TRIPLE_DEVICE_STARTER",
    "Tablet POS Slot",
    "PC Admin Slot",
    "Mobile Companion Slot",
    "customerMessage",
    "nextStep",
    "secretsExposed: false"
  ]) {
    assert(contract.includes(token), `Shared customer setup contract missing ${token}`);
  }
  assert(index.includes("./customer-setup-contract"), "Shared licensing barrel does not export customer setup contract.");
}

function assertCloudCenter() {
  const ui = read("Prisma Cloud Ctr/internal/web/cloud_command_center.js");
  const html = read("Prisma Cloud Ctr/internal/web/cloud_command_center.html");
  for (const token of ["Prisma Customer Setup", "Setup Link", "Setup Code", "Setup QR", "Device Slots", "Tablet POS Slot", "PC Admin Slot", "Mobile Companion Slot"]) {
    assert(ui.includes(token) || html.includes(token), `Cloud Center missing visible customer setup token ${token}`);
  }
  assert(ui.includes("License Admin Bridge"), "Cloud Center must keep License Admin Bridge visible.");
  assert(!fs.existsSync(path.join(terminalRoot, "Prisma Cloud Center")), "Duplicate Prisma Cloud Center folder detected.");
}

function assertCloudSource() {
  const worker = read("infra/cloudflare/licflow3-worker/src/worker.js");
  const migration = read("infra/cloudflare/licflow3-worker/migrations/0002_customer_setup.sql");
  const contract = read("shared/licensing/licflow3-cloud-contract.ts");
  for (const token of [
    "/api/admin/customer-setups/create",
    "/api/customer/setup/:setupCode",
    "/api/customer/devices/claim",
    "/api/customer/license/status?setupCode=:setupCode&deviceId=:deviceId",
    "customerSetup",
    "deviceClaim",
    "setupQr",
    "setupLink",
    "multiDeviceSlots"
  ]) {
    assert(worker.includes(token) || contract.includes(token), `Cloud source missing ${token}`);
  }
  for (const table of ["customer_setups", "customer_setup_slots", "customer_device_claims"]) {
    assert(migration.includes(table), `Customer setup migration missing ${table}`);
  }
  for (const forbidden of ["wrangler deploy", "d1 execute", "d1 export", "cloudflared tunnel"]) {
    assert(!worker.toLowerCase().includes(forbidden), `Cloud source contains forbidden autorun token ${forbidden}`);
  }
}

function matrixSection(documentText, matrixName) {
  const marker = `## ${matrixName}`;
  const start = documentText.indexOf(marker);
  assert(start >= 0, `Missing matrix ${matrixName}`);
  const rest = documentText.slice(start + marker.length);
  const nextHeading = rest.search(/\n##\s+/);
  return nextHeading >= 0 ? rest.slice(0, nextHeading) : rest;
}

function assertMatrixColumns(documentText, matrixName, columns, docName) {
  const section = matrixSection(documentText, matrixName);
  for (const column of columns) {
    assert(section.includes(column), `${docName} ${matrixName} missing required column ${column}`);
  }
}

function assertPlanBasedProvisioningReadonly() {
  const contract = read("shared/licensing/customer-setup-contract.ts");
  const worker = read("infra/cloudflare/licflow3-worker/src/worker.js");
  const migration0002 = read("infra/cloudflare/licflow3-worker/migrations/0002_customer_setup.sql");
  const migration0003 = read("infra/cloudflare/licflow3-worker/migrations/0003_plan_based_provisioning.sql");
  const opsMap = read("docs/ops/PRISMA_SUPREME_OPERATIONS_MAP.md");
  const productization = read("docs/productization/PRISMA_PLAN_BASED_CLIENT_ONBOARDING_MATRICES.md");
  const e2e012 = read("docs/productization/E2E_012_PLAN_BASED_CLIENT_ONBOARDING.md");

  for (const token of [
    "PlanProvisioningDefinition",
    "PlanBasedProvisioningResult",
    "DeviceClaimSlot",
    "PLAN_BASED_PROVISIONING_CATALOG",
    "resolvePlanProvisioningDefinition",
    "aggregateSlotsForPlan",
    "buildDeviceClaimSlotsForPlan",
    "maxTabletDevices",
    "maxPcDevices",
    "maxMobileDevices",
    "maxTotalDevices",
    "allowedSurfaces",
    "setupMode",
    "claimMode",
    "requiresManualApproval",
    "expirationPolicy",
    "gracePolicy",
    "renewalPolicy",
    "manualDeviceClaimRequired: false",
    "operatorActionCount: 1"
  ]) {
    assert(contract.includes(token), `Shared plan provisioning contract missing ${token}`);
  }
  for (const planId of ["TABLET_SOLO", "TABLET_PRO", "TABLET_PC_MANAGED", "TABLET_PC_MOBILE_MANAGED"]) {
    assert(contract.includes(planId), `Shared plan catalog missing ${planId}`);
    assert(worker.includes(planId), `Worker plan catalog missing ${planId}`);
    assert(opsMap.includes(planId), `Ops matrix missing ${planId}`);
    assert(productization.includes(planId), `Productization matrix missing ${planId}`);
  }
  for (const token of [
    "PLAN_PROVISIONING_CATALOG",
    "resolveCustomerSetupPlan",
    "buildDeviceClaimSlotsForPlan",
    "upsertLicensePlan",
    "upsertLicenseAssignment",
    "upsertSetupBundle",
    "upsertDeviceClaimSlot",
    "nextAvailableClaimSlot",
    "consumeClaimSlot",
    "PLAN_BASED_CUSTOMER_ONBOARDING_READY",
    "PLAN_PROVISIONING_SCHEMA_REQUIRED",
    "customer_setup.create",
    "customer_setup.plan_based_provision",
    "claimSlotsCreated",
    "manualDeviceClaimRequired: false",
    "operatorActionCount: 1",
    "claimed < allowed",
    "status = 'AVAILABLE'",
    "status = 'CLAIMED'",
    "claimSlotId",
    "setupBundle",
    "deviceClaimSlots"
  ]) {
    assert(worker.includes(token), `Worker plan provisioning path missing ${token}`);
  }
  for (const token of [
    "CREATE TABLE IF NOT EXISTS license_plans",
    "CREATE TABLE IF NOT EXISTS license_assignments",
    "CREATE TABLE IF NOT EXISTS customer_setup_bundles",
    "CREATE TABLE IF NOT EXISTS customer_device_claim_slots",
    "claim_code TEXT NOT NULL UNIQUE",
    "expires_at TEXT NOT NULL",
    "status TEXT NOT NULL DEFAULT 'AVAILABLE'",
    "audit_event_id TEXT",
    "UNIQUE (setup_bundle_id, surface, slot_index)"
  ]) {
    assert(migration0003.includes(token), `Plan provisioning migration missing ${token}`);
  }
  for (const legacyToken of ["customer_setup_bundles", "customer_device_claim_slots", "license_assignments"]) {
    assert(!migration0002.includes(legacyToken), `Historical 0002 migration was mutated with ${legacyToken}`);
  }
  for (const matrix of [
    "PLAN_PROVISIONING_MATRIX",
    "SETUP_BUNDLE_MATRIX",
    "DEVICE_CLAIM_SLOT_MATRIX",
    "CLIENT_ONBOARDING_FLOW_MATRIX"
  ]) {
    assert(opsMap.includes(matrix), `Ops map missing ${matrix}`);
    assert(productization.includes(matrix), `Productization doc missing ${matrix}`);
  }
  const matrixRequirements = {
    PLAN_PROVISIONING_MATRIX: ["planId", "planName", "maxTabletDevices", "maxPcDevices", "maxMobileDevices", "maxTotalDevices", "allowedSurfaces", "features", "claimMode", "autoGenerateSlots", "requiresManualApproval", "status", "evidence"],
    SETUP_BUNDLE_MATRIX: ["setupBundleId", "clientId", "tenantId", "businessId", "licenseId", "planId", "setupCode", "setupLink", "setupQrPresent", "claimSlotsGenerated", "tabletSlots", "pcSlots", "mobileSlots", "expiresAt", "createdBy", "createdAt", "status", "evidence"],
    DEVICE_CLAIM_SLOT_MATRIX: ["slotId", "setupBundleId", "clientId", "licenseId", "planId", "surface", "claimCodePresent", "deviceId", "claimedAt", "expiresAt", "status", "risk", "evidence"],
    CLIENT_ONBOARDING_FLOW_MATRIX: ["clientId", "planId", "licenseCreated", "assignmentCreated", "setupBundleCreated", "claimSlotsCreated", "qrCreated", "auditCreated", "operatorActionCount", "manualDeviceClaimRequired", "status", "evidence"]
  };
  for (const [matrix, columns] of Object.entries(matrixRequirements)) {
    assertMatrixColumns(opsMap, matrix, columns, "PRISMA_SUPREME_OPERATIONS_MAP.md");
    assertMatrixColumns(productization, matrix, columns, "PRISMA_PLAN_BASED_CLIENT_ONBOARDING_MATRICES.md");
  }
  for (const token of [
    "manualDeviceClaimRequired = false",
    "operator chooses customer + plan once",
    "plan -> slots",
    "setup bundle",
    "audit",
    "customer_setup.create",
    "customer_setup.plan_based_provision",
    "VERIFY_PLAN_BASED_PROVISIONING_READONLY"
  ]) {
    assert(`${opsMap}\n${productization}\n${e2e012}`.includes(token), `Plan onboarding docs missing ${token}`);
  }
  const smoke = read("tools/smoke-licops-e2e.mjs");
  const legacyCreatedResultCode = ["CUSTOMER_SETUP", "CREATED"].join("_");
  assert(smoke.includes('resultCode: "PLAN_BASED_CUSTOMER_ONBOARDING_READY"'), "Live Customer Setup smoke must expect the canonical plan-based resultCode.");
  assert(!smoke.includes(`resultCode: "${legacyCreatedResultCode}"`), `Live Customer Setup smoke still expects legacy ${legacyCreatedResultCode}.`);
  assert(e2e012.includes("E2E_012_PLAN_BASED_CLIENT_ONBOARDING"), "Missing E2E_012 plan onboarding spec/result.");
}

function assertSurfaceEntrypoints() {
  const files = [
    "products/tablet/app/app/setup/page.tsx",
    "products/tablet/app/app/api/customer-setup/resolve/route.ts",
    "products/tablet/app/app/api/customer-setup/claim/route.ts",
    "products/tablet/app/src/server/licensing/tablet-customer-setup.ts",
    "products/pc/app/app/setup/page.tsx",
    "products/pc/app/app/api/customer-setup/resolve/route.ts",
    "products/pc/app/app/api/customer-setup/claim/route.ts",
    "products/pc/app/src/server/licensing/pc-customer-setup.ts",
    "products/mobile/app/app/prisma-app/setup/page.tsx",
    "products/mobile/app/app/api/customer-setup/resolve/route.ts",
    "products/mobile/app/app/api/customer-setup/claim/route.ts",
    "products/mobile/app/src/lib/prisma-app/prisma-mobile-customer-setup.ts"
  ];
  for (const file of files) assert(exists(file), `Missing customer setup surface file ${file}`);
  assert(read("products/tablet/app/src/server/licensing/tablet-customer-setup.ts").includes('TABLET_CUSTOMER_SETUP_SURFACE = "tablet"'), "Tablet helper does not lock surface tablet.");
  assert(read("products/pc/app/src/server/licensing/pc-customer-setup.ts").includes('PC_CUSTOMER_SETUP_SURFACE = "pc"'), "PC helper does not lock surface pc.");
  assert(read("products/mobile/app/src/lib/prisma-app/prisma-mobile-customer-setup.ts").includes('MOBILE_CUSTOMER_SETUP_SURFACE = "mobile"'), "Mobile helper does not lock surface mobile.");
}

function assertNoSecrets() {
  const roots = [
    "products/tablet/app/app/setup",
    "products/tablet/app/app/api/customer-setup",
    "products/tablet/app/src/server/licensing",
    "products/pc/app/app/setup",
    "products/pc/app/app/api/customer-setup",
    "products/pc/app/src/server/licensing",
    "products/mobile/app/app/prisma-app/setup",
    "products/mobile/app/app/api/customer-setup",
    "products/mobile/app/src/lib/prisma-app"
  ];
  const files = roots.flatMap((root) => walk(root, [".ts", ".tsx"]));
  const forbidden = ["ADMIN_TOKEN", "PRISMA_ADMIN_TOKEN", "x-prisma-admin-token", "X-Prisma-Admin-Token", "Authorization: Bearer"];
  const hits = [];
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    for (const token of forbidden) {
      if (text.includes(token)) hits.push({ file: rel(file), token });
    }
  }
  assert(hits.length === 0, `Customer setup frontend/helper files expose token material: ${JSON.stringify(hits)}`);
}

function assertPreservedRoutes() {
  const bridge = read("Prisma Cloud Ctr/internal/py/licflow4_admin_bridge.py");
  const worker = read("infra/cloudflare/licflow3-worker/src/worker.js");
  const cloudConfig = read("Prisma Cloud Ctr/internal/config/cloud_saas.json");
  const wrangler = read("infra/cloudflare/licflow3-worker/wrangler.jsonc");
  const readme = read("infra/cloudflare/licflow3-worker/README.md");
  for (const route of ["/api/licflow4/bridge/status", "/api/licflow4/bridge/activate", "/api/licflow4/bridge/refresh", "/api/licflow4/bridge/revoke"]) {
    assert(bridge.includes(route), `Preserved bridge route missing ${route}`);
  }
  for (const route of ["/api/licenses/activate", "/api/licenses/refresh", "/api/licenses/revoke"]) {
    assert(worker.includes(route), `Preserved Cloud License Gateway route missing ${route}`);
  }
  const namingSource = `${cloudConfig}\n${wrangler}\n${readme}`;
  assert(namingSource.includes("prisma-cloud-semilla") && namingSource.includes("prisma_cloud_semilla"), "Worker/D1 real names are not preserved in config/docs.");
}

function assertErrorCopy() {
  const contract = read("shared/licensing/customer-setup-contract.ts");
  for (const code of ["SETUP_CODE_REQUIRED", "SETUP_NOT_FOUND", "DEVICE_SLOT_FULL", "DEVICE_ALREADY_CLAIMED", "DEVICE_REPLACEMENT_REQUIRED", "SURFACE_NOT_ALLOWED", "CUSTOMER_SETUP_UPSTREAM_FAILED"]) {
    assert(contract.includes(code), `Missing customer setup error code ${code}`);
  }
  assert(contract.includes("CUSTOMER_SETUP_ERROR_COPY"), "Customer setup error copy map missing.");
  assert(contract.includes("customerMessage") && contract.includes("nextStep"), "Customer setup errors must include customerMessage and nextStep.");
}

function runAll() {
  assertSharedContract();
  assertCloudCenter();
  assertCloudSource();
  assertPlanBasedProvisioningReadonly();
  assertSurfaceEntrypoints();
  assertNoSecrets();
  assertPreservedRoutes();
  assertErrorCopy();
  pass("verify:customer-setup:multidevice", {
    mode,
    sharedContract: "shared/licensing/customer-setup-contract.ts",
    sourceOnly: true,
    deployPerformed: false,
    d1OperationPerformed: false
  });
}

try {
  if (mode === "no-secrets") {
    assertNoSecrets();
    pass("verify:customer-setup:no-secrets", { mode });
  } else if (mode === "plan-provisioning") {
    assertSharedContract();
    assertCloudSource();
    assertPlanBasedProvisioningReadonly();
    pass("VERIFY_PLAN_BASED_PROVISIONING_READONLY", {
      mode,
      sourceOnly: true,
      deployPerformed: false,
      d1OperationPerformed: false,
      migration: "infra/cloudflare/licflow3-worker/migrations/0003_plan_based_provisioning.sql",
      e2e: "E2E_012_PLAN_BASED_CLIENT_ONBOARDING"
    });
  } else if (mode === "e2e-012-plan-based-client-onboarding") {
    assertSharedContract();
    assertCloudSource();
    assertPlanBasedProvisioningReadonly();
    pass("E2E_012_PLAN_BASED_CLIENT_ONBOARDING", {
      mode,
      sourceVerifier: "VERIFY_PLAN_BASED_PROVISIONING_READONLY",
      sourceOnly: true,
      deployPerformed: false,
      d1OperationPerformed: false,
      manualDeviceClaimRequired: false
    });
  } else if (mode === "surface-entrypoints") {
    assertSurfaceEntrypoints();
    pass("verify:customer-setup:surface-entrypoints", { mode });
  } else if (mode === "cloud-source") {
    assertCloudSource();
    assertPreservedRoutes();
    pass("verify:customer-setup:cloud-source", { mode });
  } else {
    runAll();
  }
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
}
