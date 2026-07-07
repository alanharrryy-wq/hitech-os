import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 1) {
  const item = process.argv[index];
  if (item.startsWith("--")) {
    args.set(item.slice(2), process.argv[index + 1] && !process.argv[index + 1].startsWith("--") ? process.argv[++index] : "true");
  }
}

const baseUrl = String(args.get("base") || process.env.PRISMA_LICOPS_BASE_URL || "https://app.hitechrts.com").replace(/\/+$/, "");
const outFile = args.get("out") ? path.resolve(String(args.get("out"))) : "";
const adminToken = process.env.PRISMA_ADMIN_TOKEN || "";
const generatedAt = new Date().toISOString();
const stamp = generatedAt.replace(/[-:.TZ]/g, "").slice(0, 14);
const e2ePrefix = `E2E_LICOPS_${stamp}`;
const tenantSlug = e2ePrefix.toLowerCase().replace(/_/g, "-");
const businessName = `PRISMA LICOPS E2E ${stamp}`;
const results = [];
const testData = {
  prefix: e2ePrefix,
  tenantSlug,
  businessName,
  setupCode: null,
  setupId: null,
  licenseId: null,
  devices: {}
};

function hash(value) {
  return crypto.createHash("sha256").update(String(value)).digest("hex");
}

function safePick(payload) {
  if (!payload || typeof payload !== "object") return payload;
  return {
    ok: payload.ok,
    status: payload.status,
    resultCode: payload.resultCode,
    mutationMode: payload.mutationMode,
    tokenMode: payload.tokenMode,
    safeToMutate: payload.safeToMutate,
    safeToMutateReason: payload.safeToMutateReason,
    secretsExposed: payload.secretsExposed,
    setupCode: payload.setupCode,
    setupId: payload.setupId,
    tenantSlug: payload.tenantSlug,
    requestId: payload.requestId,
    replacementRequestId: payload.replacementRequestId,
    device: payload.device,
    license: payload.license,
    slots: Array.isArray(payload.slots) ? payload.slots : undefined,
    capabilities: payload.capabilities
  };
}

function addResult(entry) {
  results.push({
    generatedAt: new Date().toISOString(),
    ...entry,
    tokenValuePrinted: false,
    secretsExposed: entry.secretsExposed === true
  });
}

function matchesExpectation(response, payload, expected = {}) {
  const statuses = expected.statusCodes || [200];
  if (!statuses.includes(response.status)) return false;
  if (expected.resultCode && payload?.resultCode !== expected.resultCode) return false;
  if (expected.status && payload?.status !== expected.status) return false;
  if (expected.ok !== undefined && payload?.ok !== expected.ok) return false;
  return true;
}

async function call(name, method, route, body, expected = {}, options = {}) {
  const started = Date.now();
  const headers = { "content-type": "application/json" };
  if (options.admin) headers["x-prisma-admin-token"] = adminToken;
  let response;
  let text = "";
  let payload = null;
  let error = null;
  try {
    response = await fetch(`${baseUrl}${route}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body)
    });
    text = await response.text();
    try {
      payload = text ? JSON.parse(text) : null;
    } catch {
      payload = null;
    }
  } catch (err) {
    error = err instanceof Error ? err.message : String(err);
  }
  const passed = response ? matchesExpectation(response, payload, expected) : false;
  addResult({
    name,
    method,
    path: route,
    statusCode: response?.status ?? 0,
    expected,
    passed,
    okField: payload?.ok,
    resultCode: payload?.resultCode,
    bodyStatus: payload?.status,
    latencyMs: Date.now() - started,
    bodySha256: text ? hash(text) : null,
    body: safePick(payload),
    secretHeaderSent: options.admin ? "x-prisma-admin-token:<redacted>" : false,
    error
  });
  if (!passed && options.required !== false) {
    throw new Error(`${name} failed: HTTP ${response?.status ?? 0} ${payload?.resultCode || payload?.status || error || ""}`.trim());
  }
  return payload;
}

function deviceId(surface, suffix = "primary") {
  return `${e2ePrefix}_${surface}_${suffix}`.toLowerCase();
}

function addDays(days) {
  return new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
}

async function main() {
  if (!adminToken) {
    const failure = {
      generatedAt,
      baseUrl,
      allPassed: false,
      status: "ADMIN_TOKEN_LOCAL_VALUE_REQUIRED",
      resultCode: "ADMIN_TOKEN_LOCAL_VALUE_REQUIRED",
      tokenValuePrinted: false,
      secretsExposed: false,
      results,
      testData
    };
    if (outFile) fs.writeFileSync(outFile, `${JSON.stringify(failure, null, 2)}\n`);
    console.log(JSON.stringify(failure, null, 2));
    process.exit(2);
  }

  await call("health", "GET", "/health", undefined, { statusCodes: [200], ok: true });
  await call("capabilities", "GET", "/api/public/capabilities", undefined, { statusCodes: [200], ok: true });

  const setup = await call("admin_create_setup_live", "POST", "/api/admin/customer-setups/create", {
    customerPrefix: e2ePrefix,
    tenantSlug,
    businessName,
    plan: "TABLET_PC_MOBILE_MANAGED",
    validUntil: addDays(365)
  }, { statusCodes: [200], resultCode: "PLAN_BASED_CUSTOMER_ONBOARDING_READY" }, { admin: true });
  testData.setupCode = setup.setupCode;
  testData.setupId = setup.setupId;
  testData.licenseId = setup.license?.licenseId || `lic_${setup.setupId}`;

  await call("resolve_setup_code_live", "GET", `/api/customer/setup/${encodeURIComponent(testData.setupCode)}`, undefined, { statusCodes: [200], ok: true });
  await call("resolve_missing_setup_negative", "GET", `/api/customer/setup/${encodeURIComponent(`${e2ePrefix}_MISSING`)}`, undefined, { statusCodes: [404], status: "SETUP_NOT_FOUND" });

  const surfaces = [
    ["tablet", "Tablet POS Slot"],
    ["pc", "PC Admin Slot"],
    ["mobile", "Mobile Companion Slot"]
  ];
  for (const [surface] of surfaces) {
    const id = deviceId(surface);
    testData.devices[surface] = id;
    await call(`claim_${surface}_live`, "POST", "/api/customer/devices/claim", {
      setupCode: testData.setupCode,
      surface,
      deviceId: id,
      deviceName: `${e2ePrefix} ${surface}`,
      installationFingerprint: `${e2ePrefix}:${surface}`,
      appVersion: "licops-e2e"
    }, { statusCodes: [200], resultCode: "DEVICE_CLAIM_ACCEPTED" });
  }

  await call("duplicate_claim_negative", "POST", "/api/customer/devices/claim", {
    setupCode: testData.setupCode,
    surface: "tablet",
    deviceId: testData.devices.tablet,
    deviceName: `${e2ePrefix} tablet duplicate`
  }, { statusCodes: [409], resultCode: "DEVICE_ALREADY_CLAIMED" });

  await call("slot_full_negative", "POST", "/api/customer/devices/claim", {
    setupCode: testData.setupCode,
    surface: "pc",
    deviceId: deviceId("pc", "second"),
    deviceName: `${e2ePrefix} pc second`
  }, { statusCodes: [409], resultCode: "DEVICE_SLOT_FULL" });

  await call("wrong_slot_negative", "POST", "/api/customer/devices/claim", {
    setupCode: testData.setupCode,
    surface: "kiosk",
    deviceId: deviceId("kiosk")
  }, { statusCodes: [422], resultCode: "SURFACE_NOT_ALLOWED" });

  await call("missing_claim_fields_negative", "POST", "/api/customer/devices/claim", {}, { statusCodes: [400], resultCode: "SETUP_CODE_REQUIRED" });
  await call("invalid_setup_claim_negative", "POST", "/api/customer/devices/claim", {
    setupCode: `${e2ePrefix}_MISSING`,
    surface: "tablet",
    deviceId: deviceId("tablet", "missing")
  }, { statusCodes: [404], resultCode: "SETUP_NOT_FOUND" });

  for (const [surface] of surfaces) {
    const id = testData.devices[surface];
    await call(`status_${surface}_live`, "GET", `/api/customer/license/status?setupCode=${encodeURIComponent(testData.setupCode)}&deviceId=${encodeURIComponent(id)}`, undefined, { statusCodes: [200], resultCode: "LICENSE_STATUS_OK" });
    await call(`refresh_${surface}_live`, "POST", "/api/customer/license/refresh", {
      setupCode: testData.setupCode,
      deviceId: id
    }, { statusCodes: [200], resultCode: "LICENSE_REFRESHED" });
  }

  await call("simulation_activate", "POST", "/api/licenses/activate", {
    simulation: true,
    tenantSlug,
    licenseId: testData.licenseId,
    plan: "TABLET_PC_MOBILE_MANAGED"
  }, { statusCodes: [200], resultCode: "ACTIVATE_SIMULATION_READY" });
  await call("confirmed_activate", "POST", "/api/licenses/activate", {
    confirmAdminLicenseAction: true,
    tenantSlug,
    licenseId: testData.licenseId,
    plan: "TABLET_PC_MOBILE_MANAGED"
  }, { statusCodes: [200], resultCode: "ACTIVATE_CONFIRMED" }, { admin: true });
  await call("simulation_refresh", "POST", "/api/licenses/refresh", {
    simulation: true,
    tenantSlug,
    licenseId: testData.licenseId
  }, { statusCodes: [200], resultCode: "REFRESH_SIMULATION_READY" });
  await call("confirmed_refresh", "POST", "/api/licenses/refresh", {
    confirmAdminLicenseAction: true,
    tenantSlug,
    licenseId: testData.licenseId
  }, { statusCodes: [200], resultCode: "REFRESH_CONFIRMED" }, { admin: true });

  const newTablet = deviceId("tablet", "replacement");
  testData.devices.tabletReplacement = newTablet;
  await call("replacement_request", "POST", "/api/customer/devices/replacement/request", {
    setupCode: testData.setupCode,
    surface: "tablet",
    oldDeviceId: testData.devices.tablet,
    newDeviceId: newTablet,
    reason: "controlled licops e2e replacement"
  }, { statusCodes: [200], resultCode: "REPLACEMENT_REQUESTED" });
  await call("replacement_approve", "POST", "/api/admin/customer-devices/replacement/approve", {
    confirmAdminLicenseAction: true,
    setupCode: testData.setupCode,
    surface: "tablet",
    oldDeviceId: testData.devices.tablet,
    reason: "controlled licops e2e replacement"
  }, { statusCodes: [200], resultCode: "DEVICE_REPLACEMENT_APPROVED" }, { admin: true });
  await call("replacement_claim_new_tablet", "POST", "/api/customer/devices/claim", {
    setupCode: testData.setupCode,
    surface: "tablet",
    deviceId: newTablet,
    deviceName: `${e2ePrefix} tablet replacement`,
    installationFingerprint: `${e2ePrefix}:tablet:replacement`,
    appVersion: "licops-e2e"
  }, { statusCodes: [200], resultCode: "DEVICE_CLAIM_ACCEPTED" });

  await call("customer_portal_magic_context", "GET", `/api/customer/portal?setupCode=${encodeURIComponent(testData.setupCode)}`, undefined, { statusCodes: [200], resultCode: "CUSTOMER_PORTAL_READY" });
  await call("customer_magic_link", "GET", `/api/customer/magic-link?setupCode=${encodeURIComponent(testData.setupCode)}`, undefined, { statusCodes: [200], resultCode: "MAGIC_LINK_READY" });

  await call("billing_expiring_simulation", "POST", "/api/licenses/commercial-state", {
    simulation: true,
    tenantSlug,
    licenseId: testData.licenseId,
    status: "expiring",
    validUntil: addDays(7)
  }, { statusCodes: [200], resultCode: "COMMERCIAL_STATE_SIMULATION_READY" });
  await call("billing_expiring_confirmed", "POST", "/api/licenses/commercial-state", {
    confirmAdminLicenseAction: true,
    tenantSlug,
    licenseId: testData.licenseId,
    status: "expiring",
    validUntil: addDays(7)
  }, { statusCodes: [200], resultCode: "COMMERCIAL_STATE_CONFIRMED" }, { admin: true });
  await call("billing_suspended_confirmed", "POST", "/api/licenses/commercial-state", {
    confirmAdminLicenseAction: true,
    tenantSlug,
    licenseId: testData.licenseId,
    status: "suspended",
    reason: "controlled licops e2e suspension"
  }, { statusCodes: [200], resultCode: "COMMERCIAL_STATE_CONFIRMED" }, { admin: true });
  await call("suspended_refresh_blocked", "POST", "/api/customer/license/refresh", {
    setupCode: testData.setupCode,
    deviceId: newTablet
  }, { statusCodes: [403], resultCode: "LICENSE_SUSPENDED" });
  await call("renewal_simulation", "POST", "/api/licenses/renew", {
    simulation: true,
    tenantSlug,
    licenseId: testData.licenseId,
    validUntil: addDays(365)
  }, { statusCodes: [200], resultCode: "RENEW_SIMULATION_READY" });
  await call("renewal_confirmed", "POST", "/api/licenses/renew", {
    confirmAdminLicenseAction: true,
    tenantSlug,
    licenseId: testData.licenseId,
    validUntil: addDays(365)
  }, { statusCodes: [200], resultCode: "RENEW_CONFIRMED" }, { admin: true });
  await call("renewed_refresh_live", "POST", "/api/customer/license/refresh", {
    setupCode: testData.setupCode,
    deviceId: newTablet
  }, { statusCodes: [200], resultCode: "LICENSE_REFRESHED" });

  await call("simulation_revoke_with_reason", "POST", "/api/licenses/revoke", {
    simulation: true,
    tenantSlug,
    licenseId: testData.licenseId,
    reason: "controlled licops e2e revoke simulation"
  }, { statusCodes: [200], resultCode: "REVOKE_SIMULATION_READY" });
  await call("confirmed_revoke", "POST", "/api/licenses/revoke", {
    confirmAdminLicenseAction: true,
    confirmRevoke: "REVOKE_LICENSE",
    tenantSlug,
    licenseId: testData.licenseId,
    reason: "controlled licops e2e final deactivation"
  }, { statusCodes: [200], resultCode: "REVOKE_CONFIRMED" }, { admin: true });
  await call("revoked_refresh_blocked", "POST", "/api/customer/license/refresh", {
    setupCode: testData.setupCode,
    deviceId: newTablet
  }, { statusCodes: [403], resultCode: "LICENSE_REVOKED" });

  await call("support_diagnostics_auth", "GET", `/api/support/diagnostics?tenant=${encodeURIComponent(tenantSlug)}`, undefined, { statusCodes: [200], resultCode: "LICENSE_DIAGNOSTICS_READY" }, { admin: true });
  await call("commercial_summary_auth", "GET", "/api/admin/commercial-summary", undefined, { statusCodes: [200], resultCode: "COMMERCIAL_SUMMARY_READY" }, { admin: true });

  const allPassed = results.every((result) => result.passed);
  const output = {
    generatedAt,
    baseUrl,
    allPassed,
    status: allPassed ? "PASS" : "FAIL",
    tokenFingerprint: hash(adminToken).slice(0, 16),
    tokenValuePrinted: false,
    secretsExposed: false,
    testData,
    results
  };
  if (outFile) {
    fs.mkdirSync(path.dirname(outFile), { recursive: true });
    fs.writeFileSync(outFile, `${JSON.stringify(output, null, 2)}\n`);
  }
  console.log(JSON.stringify(output, null, 2));
  if (!allPassed) process.exit(1);
}

main().catch((error) => {
  const output = {
    generatedAt,
    baseUrl,
    allPassed: false,
    status: "FAIL",
    error: error instanceof Error ? error.message : String(error),
    tokenFingerprint: adminToken ? hash(adminToken).slice(0, 16) : null,
    tokenValuePrinted: false,
    secretsExposed: false,
    testData,
    results
  };
  if (outFile) {
    fs.mkdirSync(path.dirname(outFile), { recursive: true });
    fs.writeFileSync(outFile, `${JSON.stringify(output, null, 2)}\n`);
  }
  console.log(JSON.stringify(output, null, 2));
  process.exit(1);
});
