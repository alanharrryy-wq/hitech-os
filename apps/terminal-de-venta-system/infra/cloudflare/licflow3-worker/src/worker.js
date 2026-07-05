const SERVICE = "PRISMA LICFLOW3 Cloud Licensing Support Bridge";
const VERSION = "0.2.0-prisma-cloud-semilla-routing";
const TENANT = "prisma-original-customer";
const PLAN = "TABLET_PC_MANAGED";
const LICFLOW3_LIVE_STATUS = "LICFLOW3_CLOUDFLARE_ROUTES_LIVE";
const CUSTOMER_SETUP_SCHEMA_VERSION = "1.0.0";
const DEFAULT_SETUP_CODE = "PRISMA-SETUP-STARTER";
const DEFAULT_SETUP_PACKAGE = "PRISMA_TRIPLE_DEVICE_STARTER";
const DEFAULT_SETUP_PLAN = "TABLET_PC_MOBILE_MANAGED";
const SLOT_LABELS = {
  tablet: "Tablet POS Slot",
  pc: "PC Admin Slot",
  mobile: "Mobile Companion Slot"
};

const CONTRACT_ENDPOINTS = [
  ["GET", "/health", "health", false],
  ["GET", "/api/public/capabilities", "capabilities", false],
  ["GET", `/api/public/tenants/${TENANT}/status`, "tenant_status", false],
  ["GET", `/api/client/contract?tenant=${TENANT}`, "contract_fetch", false],
  ["POST", "/api/licenses/activate", "activate", true],
  ["POST", "/api/licenses/refresh", "refresh", true],
  ["POST", "/api/licenses/revoke", "revoke", true],
  ["POST", "/api/devices/register", "register_device", true],
  ["POST", "/api/client/integration-receipt", "integration_receipt", true],
  ["GET", `/api/support/diagnostics?tenant=${TENANT}`, "support_diagnostics", false],
  ["GET", "/api/admin/selftest", "admin_selftest", false],
  ["GET", "/api/admin/commercial-summary", "commercial_summary", false],
  ["GET", `/api/admin/tenants/${TENANT}/snapshot`, "tenant_snapshot", false],
  ["POST", `/api/admin/tenants/${TENANT}/notes`, "tenant_notes", true],
  ["POST", "/api/admin/customer-setups/create", "customer_setup_create", true],
  ["GET", "/api/customer/setup/:setupCode", "customer_setup_resolve", false],
  ["POST", "/api/customer/devices/claim", "customer_device_claim", true],
  ["GET", "/api/customer/license/status?setupCode=:setupCode&deviceId=:deviceId", "customer_license_status", false]
];

function json(payload, status = 200) {
  return new Response(JSON.stringify(payload, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store"
    }
  });
}

function now() {
  return new Date().toISOString();
}

function d1(env) {
  return env && env.PRISMA_LICFLOW3_D1 && typeof env.PRISMA_LICFLOW3_D1.prepare === "function" ? env.PRISMA_LICFLOW3_D1 : null;
}

function tenantSlugFromUrl(url) {
  return url.searchParams.get("tenant") || TENANT;
}

function normalizeSetupCode(value) {
  return String(value || "").trim().toUpperCase();
}

function normalizeSurface(value) {
  const surface = String(value || "").trim().toLowerCase();
  return Object.prototype.hasOwnProperty.call(SLOT_LABELS, surface) ? surface : "";
}

function authorized(request, env) {
  const expected = env && typeof env.PRISMA_ADMIN_TOKEN === "string" ? env.PRISMA_ADMIN_TOKEN : "";
  const provided = request.headers.get("x-prisma-admin-token") || request.headers.get("x-admin-token") || request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") || "";
  return Boolean(expected && provided && provided === expected);
}

function adminRequired(request, env) {
  if (authorized(request, env)) return null;
  return json({
    ok: false,
    service: SERVICE,
    status: "ADMIN_TOKEN_REQUIRED",
    reason: "Configure PRISMA_ADMIN_TOKEN outside the repo and send it in an admin header."
  }, 401);
}

async function readJson(request) {
  if (!request.body) return {};
  try {
    const payload = await request.json();
    return payload && typeof payload === "object" ? payload : {};
  } catch {
    return {};
  }
}

async function first(env, sql, params = []) {
  const db = d1(env);
  if (!db) return null;
  try {
    return await db.prepare(sql).bind(...params).first();
  } catch {
    return null;
  }
}

async function all(env, sql, params = []) {
  const db = d1(env);
  if (!db) return [];
  try {
    const result = await db.prepare(sql).bind(...params).all();
    return Array.isArray(result.results) ? result.results : [];
  } catch {
    return [];
  }
}

async function run(env, sql, params = []) {
  const db = d1(env);
  if (!db) return { ok: false, status: "D1_BINDING_REQUIRED" };
  try {
    await db.prepare(sql).bind(...params).run();
    return { ok: true };
  } catch (error) {
    return { ok: false, status: "D1_WRITE_FAILED", error: String(error && error.message ? error.message : error) };
  }
}

async function tenant(env, slug = TENANT) {
  const row = await first(env, "select slug, display_name, status, plan, created_at, updated_at from tenants where slug = ?", [slug]);
  return row || {
    slug,
    displayName: "Prisma Original Customer",
    display_name: "Prisma Original Customer",
    status: "prepared",
    plan: PLAN
  };
}

async function license(env, slug = TENANT) {
  const row = await first(env, "select license_id, tenant_slug, status, plan, activation_status, valid_until, created_at, updated_at from licenses where tenant_slug = ? order by updated_at desc limit 1", [slug]);
  if (row) return row;
  const legacyRow = await first(env, "select l.id as license_id, t.slug as tenant_slug, l.status, l.plan, l.status as activation_status, l.expires_at as valid_until, l.created_at, l.updated_at from licenses l join tenants t on l.tenant_id = t.id where t.slug = ? order by l.updated_at desc limit 1", [slug]);
  if (legacyRow) return legacyRow;
  return {
    licenseId: "pending-hosted-license",
    license_id: "pending-hosted-license",
    tenantSlug: slug,
    tenant_slug: slug,
    status: "pending_cloud_activation",
    plan: PLAN,
    activationStatus: LICFLOW3_LIVE_STATUS,
    activation_status: LICFLOW3_LIVE_STATUS
  };
}

async function devicesForTenant(env, slug) {
  const rows = await all(env, "select device_id as deviceId, device_name as name, role, platform, status, created_at as createdAt from devices where tenant_slug = ? order by updated_at desc limit 50", [slug]);
  if (rows.length) return rows;
  return all(env, "select d.id as deviceId, d.label as name, 'device' as role, d.device_code as platform, d.status, d.created_at as createdAt from devices d join tenants t on d.tenant_id = t.id where t.slug = ? order by d.updated_at desc limit 50", [slug]);
}

async function receiptsForTenant(env, slug) {
  const rows = await all(env, "select receipt_id as receiptId, kind, ok, created_at as createdAt from integration_receipts where tenant_slug = ? order by created_at desc limit 50", [slug]);
  if (rows.length) return rows;
  return all(env, "select r.id as receiptId, r.receipt_type as kind, case when r.status = 'accepted' then 1 else 0 end as ok, r.created_at as createdAt from integration_receipts r join tenants t on r.tenant_id = t.id where t.slug = ? order by r.created_at desc limit 50", [slug]);
}

async function notesForTenant(env, slug) {
  const rows = await all(env, "select note_id as id, text, source, created_at as createdAt from support_notes where tenant_slug = ? order by created_at desc limit 50", [slug]);
  if (rows.length) return rows;
  return all(env, "select n.id, n.body as text, n.created_by as source, n.created_at as createdAt from tenant_notes n join tenants t on n.tenant_id = t.id where t.slug = ? order by n.created_at desc limit 50", [slug]);
}

async function eventsForTenant(env, slug) {
  const rows = await all(env, "select event_id as id, event_type as type, created_at as createdAt from audit_events where tenant_slug = ? order by created_at desc limit 50", [slug]);
  if (rows.length) return rows;
  return all(env, "select e.id, e.event_type as type, e.created_at as createdAt from client_events e join tenants t on e.tenant_id = t.id where t.slug = ? order by e.created_at desc limit 50", [slug]);
}

function normalizeTenant(row) {
  return {
    slug: row.slug || row.tenant_slug || TENANT,
    displayName: row.displayName || row.display_name || "Prisma Original Customer",
    status: row.status || "prepared",
    plan: row.plan || PLAN
  };
}

function normalizeLicense(row) {
  return {
    licenseId: row.licenseId || row.license_id || "pending-hosted-license",
    tenantSlug: row.tenantSlug || row.tenant_slug || TENANT,
    status: row.status || "pending_cloud_activation",
    plan: row.plan || PLAN,
    activationStatus: row.activationStatus || row.activation_status || LICFLOW3_LIVE_STATUS,
    validUntil: row.validUntil || row.valid_until || null
  };
}

function defaultSlots() {
  return [
    { surface: "tablet", label: SLOT_LABELS.tablet, allowed: 1, claimed: 0 },
    { surface: "pc", label: SLOT_LABELS.pc, allowed: 1, claimed: 0 },
    { surface: "mobile", label: SLOT_LABELS.mobile, allowed: 1, claimed: 0 }
  ];
}

function buildSetupPass(row = {}, slots = defaultSlots()) {
  const setupCode = normalizeSetupCode(row.setupCode || row.setup_code || DEFAULT_SETUP_CODE);
  const tenantSlug = row.tenantSlug || row.tenant_slug || TENANT;
  const businessName = row.businessName || row.business_name || "Prisma Original Customer";
  return {
    ok: true,
    schemaVersion: CUSTOMER_SETUP_SCHEMA_VERSION,
    setupId: row.setupId || row.setup_id || `setup_${setupCode.toLowerCase().replace(/[^a-z0-9]+/g, "_")}`,
    setupCode,
    setupUrl: row.setupUrl || row.setup_url || `https://app.hitechrts.com/setup/${encodeURIComponent(setupCode)}`,
    qrPayload: row.qrPayload || row.qr_payload || `prisma://setup/${encodeURIComponent(setupCode)}`,
    customerId: row.customerId || row.customer_id || "cust_prisma_original_customer",
    tenantId: row.tenantId || row.tenant_id || "tenant_prisma_original_customer",
    tenantSlug,
    businessId: row.businessId || row.business_id || "biz_prisma_original_customer",
    businessName,
    packageCode: row.packageCode || row.package_code || DEFAULT_SETUP_PACKAGE,
    planCode: row.planCode || row.plan_code || DEFAULT_SETUP_PLAN,
    status: row.status || "source_ready",
    expiresAt: row.expiresAt || row.expires_at || null,
    slots,
    customerMessage: "Prisma Customer Setup source is ready; live customer use requires authorized Cloud License Gateway deploy and D1 migration.",
    nextStep: "Use Setup Link, Setup Code, or Setup QR after deployment authorization.",
    secretsExposed: false
  };
}

async function capabilities(env) {
  return {
    ok: true,
    service: SERVICE,
    version: VERSION,
    mode: env.PRISMA_LICFLOW3_MODE || "scaffold",
    capabilities: {
      activate: true,
      refresh: true,
      revoke: true,
      registerDevice: true,
      integrationReceipt: true,
      tenantStatus: true,
      supportDiagnostics: true,
      commercialSummary: true,
      contractFetch: true,
      customerSetup: true,
      setupLink: true,
      setupQr: true,
      deviceClaim: true,
      multiDeviceSlots: true,
      signedLicenseIssuance: false,
      deployClaim: false
    },
    safety: {
      noDeployByDefault: true,
      noSecretValuesInRepo: true,
      tabletOfflineStillValid: true,
      licflow2LocalActivationStillCanonical: true
    },
    endpoints: CONTRACT_ENDPOINTS.map(([method, path, capability, mutatesCloud]) => ({ method, path, capability, mutatesCloud }))
  };
}

async function health(env) {
  const db = d1(env);
  const tenantCount = db ? await first(env, "select count(*) as count from tenants") : null;
  const deviceCount = db ? await first(env, "select count(*) as count from devices") : null;
  const receiptCount = db ? await first(env, "select count(*) as count from integration_receipts") : null;
  return {
    ok: true,
    service: SERVICE,
    version: VERSION,
    generatedAt: now(),
    dbHealth: db ? "D1_BOUND" : "D1_BINDING_REQUIRED",
    counts: {
      tenants: tenantCount ? tenantCount.count : 0,
      devices: deviceCount ? deviceCount.count : 0,
      receipts: receiptCount ? receiptCount.count : 0
    },
    hostedCloudEvidence: LICFLOW3_LIVE_STATUS
  };
}

async function tenantStatus(env, slug) {
  const tenantRow = normalizeTenant(await tenant(env, slug));
  const licenseRow = normalizeLicense(await license(env, slug));
  return {
    ok: true,
    service: SERVICE,
    tenant: tenantRow,
    license: licenseRow,
    publicContract: {
      tenantSlug: tenantRow.slug,
      status: tenantRow.status,
      plan: tenantRow.plan,
      contractVersion: "licflow3-scaffold-v1",
      hostedCloudEvidence: LICFLOW3_LIVE_STATUS
    }
  };
}

async function snapshot(env, slug) {
  const [tenantPayload, devices, receipts, notes, events] = await Promise.all([
    tenantStatus(env, slug),
    devicesForTenant(env, slug),
    receiptsForTenant(env, slug),
    notesForTenant(env, slug),
    eventsForTenant(env, slug)
  ]);
  return {
    ok: true,
    service: SERVICE,
    tenant: tenantPayload.tenant,
    license: tenantPayload.license,
    publicContract: tenantPayload.publicContract,
    devices,
    integrationReceipts: receipts,
    notes,
    events
  };
}

async function setupSlots(env, setupId) {
  const rows = await all(env, "select surface, label, allowed, claimed from customer_setup_slots where setup_id = ? order by surface", [setupId]);
  if (!rows.length) return defaultSlots();
  return rows.map((row) => ({
    surface: row.surface,
    label: row.label || SLOT_LABELS[row.surface] || row.surface,
    allowed: Number(row.allowed || 0),
    claimed: Number(row.claimed || 0)
  }));
}

async function setupByCode(env, setupCode) {
  const row = await first(env, "select setup_id, setup_code, setup_url, qr_payload, customer_id, tenant_id, tenant_slug, business_id, business_name, package_code, plan_code, status, expires_at from customer_setups where setup_code = ?", [setupCode]);
  if (!row) return null;
  return buildSetupPass(row, await setupSlots(env, row.setup_id));
}

async function createCustomerSetup(request, env) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  const body = await readJson(request);
  const setupCode = normalizeSetupCode(body.setupCode || DEFAULT_SETUP_CODE);
  const setupId = body.setupId || `setup_${crypto.randomUUID()}`;
  const pass = buildSetupPass({
    setupId,
    setupCode,
    customerId: body.customerId,
    tenantId: body.tenantId,
    tenantSlug: body.tenantSlug || TENANT,
    businessId: body.businessId,
    businessName: body.businessName,
    expiresAt: body.expiresAt,
    status: "active"
  });
  if (!d1(env)) return json({ ...pass, ok: false, status: "D1_BINDING_REQUIRED", sourceReady: true }, 503);
  const result = await run(env, "insert or replace into customer_setups (setup_id, setup_code, setup_url, qr_payload, customer_id, tenant_id, tenant_slug, business_id, business_name, package_code, plan_code, status, expires_at, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    pass.setupId,
    pass.setupCode,
    pass.setupUrl,
    pass.qrPayload,
    pass.customerId,
    pass.tenantId,
    pass.tenantSlug,
    pass.businessId,
    pass.businessName,
    pass.packageCode,
    pass.planCode,
    pass.status,
    pass.expiresAt,
    now()
  ]);
  if (!result.ok) return json({ ...pass, ok: false, status: result.status, secretsExposed: false }, 500);
  for (const slot of pass.slots) {
    await run(env, "insert or replace into customer_setup_slots (setup_id, surface, label, allowed, claimed, updated_at) values (?, ?, ?, ?, ?, ?)", [
      pass.setupId,
      slot.surface,
      slot.label,
      slot.allowed,
      slot.claimed,
      now()
    ]);
  }
  await recordAudit(env, pass.tenantSlug, "customer_setup.create", { setupId: pass.setupId, setupCode: pass.setupCode, packageCode: pass.packageCode });
  return json(pass);
}

async function resolveCustomerSetup(env, setupCode) {
  const code = normalizeSetupCode(setupCode);
  if (!code) return json({ ok: false, status: "SETUP_CODE_REQUIRED", customerMessage: "Falta el codigo de configuracion.", nextStep: "Pega el Setup Code o abre el Setup Link.", secretsExposed: false }, 400);
  if (!d1(env)) return json(buildSetupPass({ setupCode: code, status: "source_ready" }));
  const pass = await setupByCode(env, code);
  if (!pass) return json({ ok: false, status: "SETUP_NOT_FOUND", customerMessage: "No encontramos este setup.", nextStep: "Revisa el Setup Code o pide un link nuevo.", secretsExposed: false }, 404);
  return json(pass);
}

async function claimCustomerDevice(request, env) {
  const body = await readJson(request);
  const setupCode = normalizeSetupCode(body.setupCode);
  const surface = normalizeSurface(body.surface);
  const deviceId = String(body.deviceId || "").trim();
  if (!setupCode) return json({ ok: false, status: "SETUP_CODE_REQUIRED", resultCode: "SETUP_CODE_REQUIRED", customerMessage: "Falta el codigo de configuracion.", nextStep: "Pega el Setup Code o abre el Setup Link.", secretsExposed: false }, 400);
  if (!surface) return json({ ok: false, status: "SURFACE_NOT_ALLOWED", resultCode: "SURFACE_NOT_ALLOWED", customerMessage: "Este paquete no incluye esta app.", nextStep: "Revisa tu plan o contacta soporte.", secretsExposed: false }, 422);
  if (!deviceId) return json({ ok: false, status: "INVALID_DEVICE_CLAIM", resultCode: "DEVICE_ID_REQUIRED", customerMessage: "Falta identificar este dispositivo.", nextStep: "Reintenta desde la app para generar el identificador local.", secretsExposed: false }, 400);
  if (!d1(env)) {
    const pass = buildSetupPass({ setupCode, status: "source_ready" });
    return json({
      ok: true,
      status: "source_ready",
      resultCode: "CUSTOMER_SETUP_SOURCE_READY",
      customerMessage: `Este dispositivo esta listo para reclamar ${SLOT_LABELS[surface]} cuando Prisma Customer Setup este desplegado.`,
      nextStep: "Conserva el Setup Code y reintenta cuando soporte confirme el deploy del Cloud License Gateway.",
      customer: { customerId: pass.customerId, displayName: pass.businessName },
      business: { businessId: pass.businessId, displayName: pass.businessName },
      license: { licenseId: "lic_prisma_customer_setup_pending", planCode: pass.planCode, state: "source_ready" },
      device: { deviceId, surface, slotLabel: SLOT_LABELS[surface] },
      slots: pass.slots,
      localLicensePayload: { signed: false, source: "customer-setup-source-ready" },
      secretsExposed: false
    });
  }
  const pass = await setupByCode(env, setupCode);
  if (!pass) return json({ ok: false, status: "SETUP_NOT_FOUND", resultCode: "SETUP_NOT_FOUND", customerMessage: "No encontramos este setup.", nextStep: "Revisa el Setup Code o pide un link nuevo.", secretsExposed: false }, 404);
  const slot = pass.slots.find((item) => item.surface === surface);
  if (!slot) return json({ ok: false, status: "SURFACE_NOT_ALLOWED", resultCode: "SURFACE_NOT_ALLOWED", customerMessage: "Este paquete no incluye esta app.", nextStep: "Revisa tu plan o contacta soporte.", secretsExposed: false }, 422);
  const existing = await first(env, "select claim_id, device_id, surface from customer_device_claims where setup_id = ? and device_id = ? limit 1", [pass.setupId, deviceId]);
  if (existing) return json({ ok: false, status: "DEVICE_ALREADY_CLAIMED", resultCode: "DEVICE_ALREADY_CLAIMED", customerMessage: "Este dispositivo ya esta activado.", nextStep: "Continua usando la app o revisa soporte si cambiaste de equipo.", secretsExposed: false }, 409);
  if (slot.claimed >= slot.allowed) return json({ ok: false, status: "DEVICE_SLOT_FULL", resultCode: "DEVICE_SLOT_FULL", customerMessage: "Ya se uso el cupo para este tipo de dispositivo.", nextStep: "Solicita reemplazo autorizado o un cupo adicional.", secretsExposed: false }, 409);
  const claimId = `claim_${crypto.randomUUID()}`;
  const result = await run(env, "insert into customer_device_claims (claim_id, setup_id, setup_code, tenant_slug, surface, device_id, device_name, installation_fingerprint, app_version, operator_label, status, claimed_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    claimId,
    pass.setupId,
    pass.setupCode,
    pass.tenantSlug,
    surface,
    deviceId,
    String(body.deviceName || deviceId).slice(0, 160),
    String(body.installationFingerprint || "").slice(0, 160),
    String(body.appVersion || "").slice(0, 80),
    String(body.operatorLabel || "").slice(0, 160),
    "claimed",
    now()
  ]);
  if (!result.ok) return json({ ok: false, status: result.status, resultCode: "CUSTOMER_SETUP_UPSTREAM_FAILED", customerMessage: "No pudimos validar el setup.", nextStep: "Reintenta o contacta soporte con evidencia sanitizada.", secretsExposed: false }, 500);
  await run(env, "update customer_setup_slots set claimed = claimed + 1, updated_at = ? where setup_id = ? and surface = ?", [now(), pass.setupId, surface]);
  await recordAudit(env, pass.tenantSlug, "customer_device.claim", { setupCode, surface, deviceId });
  const updatedPass = await setupByCode(env, setupCode) || pass;
  return json({
    ok: true,
    status: "claimed",
    resultCode: "DEVICE_CLAIM_ACCEPTED",
    customerMessage: `Este dispositivo quedo activado para ${SLOT_LABELS[surface]}.`,
    nextStep: "Continua en la app.",
    customer: { customerId: pass.customerId, displayName: pass.businessName },
    business: { businessId: pass.businessId, displayName: pass.businessName },
    license: { licenseId: "lic_prisma_customer_setup_claimed", planCode: pass.planCode, state: "active" },
    device: { deviceId, surface, slotLabel: SLOT_LABELS[surface] },
    slots: updatedPass.slots,
    localLicensePayload: { signed: false, source: "customer-setup-scaffold" },
    secretsExposed: false
  });
}

async function customerLicenseStatus(env, url) {
  const setupCode = normalizeSetupCode(url.searchParams.get("setupCode"));
  const deviceId = String(url.searchParams.get("deviceId") || "").trim();
  if (!setupCode) return json({ ok: false, status: "SETUP_CODE_REQUIRED", customerMessage: "Falta el codigo de configuracion.", nextStep: "Pega el Setup Code o abre el Setup Link.", secretsExposed: false }, 400);
  const pass = d1(env) ? await setupByCode(env, setupCode) : buildSetupPass({ setupCode, status: "source_ready" });
  if (!pass) return json({ ok: false, status: "SETUP_NOT_FOUND", customerMessage: "No encontramos este setup.", nextStep: "Revisa el Setup Code o pide un link nuevo.", secretsExposed: false }, 404);
  return json({
    ok: true,
    status: pass.status,
    setupCode,
    deviceId: deviceId || null,
    license: { planCode: pass.planCode, state: pass.status === "active" ? "active" : "source_ready", signed: false },
    slots: pass.slots,
    customerMessage: pass.customerMessage,
    nextStep: pass.nextStep,
    secretsExposed: false
  });
}

async function commercialSummary(env, slug) {
  const payload = await tenantStatus(env, slug);
  return {
    ok: true,
    service: SERVICE,
    tenant: payload.tenant,
    status: "scaffold_only",
    summary: "Commercial data requires live D1 data and authorized Cloudflare evidence.",
    plan: payload.tenant.plan
  };
}

async function diagnostics(env, slug) {
  const db = d1(env);
  return {
    ok: true,
    service: SERVICE,
    generatedAt: now(),
    tenantSlug: slug,
    dbBinding: db ? "present" : "missing",
    mode: env.PRISMA_LICFLOW3_MODE || "scaffold",
    hostedCloudEvidence: LICFLOW3_LIVE_STATUS,
    contract: CONTRACT_ENDPOINTS.map(([method, path, capability, mutatesCloud]) => ({ method, path, capability, mutatesCloud }))
  };
}

async function recordAudit(env, slug, eventType, payload) {
  const eventId = `${eventType}-${crypto.randomUUID()}`;
  const result = await run(env, "insert into audit_events (event_id, tenant_slug, event_type, payload_json) values (?, ?, ?, ?)", [eventId, slug, eventType, JSON.stringify(payload || {})]);
  if (!result.ok) {
    await run(env, "insert into audit_log (id, actor, action, entity_type, entity_id, payload_json) values (?, ?, ?, ?, ?, ?)", [eventId, "licflow3-worker", eventType, "tenant", slug, JSON.stringify(payload || {})]);
  }
  return eventId;
}

async function activateLicense(request, env, mode) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  const db = d1(env);
  if (!db) return json({ ok: false, status: "D1_BINDING_REQUIRED", action: mode, signedLicenseIssued: false }, 503);
  const body = await readJson(request);
  const slug = body.tenantSlug || body.tenant || TENANT;
  const licenseId = body.licenseId || `licflow3-${mode}-${crypto.randomUUID()}`;
  const status = mode === "revoke" ? "revoked" : mode === "refresh" ? "refreshed" : "pending_signed_license";
  let result = await run(env, "insert or replace into licenses (license_id, tenant_slug, status, plan, activation_status, updated_at) values (?, ?, ?, ?, ?, ?)", [licenseId, slug, status, body.plan || PLAN, status, now()]);
  if (!result.ok) {
    result = await run(env, "insert or replace into licenses (id, tenant_id, plan, status, updated_at) values (?, (select id from tenants where slug = ?), ?, ?, ?)", [licenseId, slug, body.plan || PLAN, status, now()]);
  }
  await recordAudit(env, slug, `license.${mode}`, { licenseId, status });
  return json({
    ok: result.ok,
    status: result.ok ? status : result.status,
    action: mode,
    tenantSlug: slug,
    licenseId,
    signedLicenseIssued: false,
    note: "This scaffold records hosted intent. Real signed issuance must be wired to approved key management outside the repo."
  }, result.ok ? 200 : 500);
}

async function registerDevice(request, env) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  if (!d1(env)) return json({ ok: false, status: "D1_BINDING_REQUIRED", action: "register_device" }, 503);
  const body = await readJson(request);
  const slug = body.tenantSlug || TENANT;
  const deviceId = body.deviceId || `device-${crypto.randomUUID()}`;
  let result = await run(env, "insert or replace into devices (device_id, tenant_slug, device_name, role, platform, status, updated_at) values (?, ?, ?, ?, ?, ?, ?)", [deviceId, slug, body.deviceName || deviceId, body.role || "unknown", body.platform || "unknown", "registered", now()]);
  if (!result.ok) {
    result = await run(env, "insert or replace into devices (id, tenant_id, device_code, label, status, updated_at) values (?, (select id from tenants where slug = ?), ?, ?, ?, ?)", [deviceId, slug, deviceId, body.deviceName || deviceId, "registered", now()]);
  }
  await recordAudit(env, slug, "device.register", { deviceId });
  return json({ ok: result.ok, status: result.ok ? "registered" : result.status, tenantSlug: slug, deviceId }, result.ok ? 200 : 500);
}

async function integrationReceipt(request, env) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  if (!d1(env)) return json({ ok: false, status: "D1_BINDING_REQUIRED", action: "integration_receipt" }, 503);
  const body = await readJson(request);
  const slug = body.tenantSlug || TENANT;
  const receiptId = body.receiptId || `receipt-${crypto.randomUUID()}`;
  let result = await run(env, "insert or replace into integration_receipts (receipt_id, tenant_slug, kind, ok, payload_json) values (?, ?, ?, ?, ?)", [receiptId, slug, body.kind || "integration", body.ok ? 1 : 0, JSON.stringify(body.payload || {})]);
  if (!result.ok) {
    result = await run(env, "insert or replace into integration_receipts (id, tenant_id, receipt_type, payload_json, status, created_at) values (?, (select id from tenants where slug = ?), ?, ?, ?, ?)", [receiptId, slug, body.kind || "integration", JSON.stringify(body.payload || {}), body.ok ? "accepted" : "rejected", now()]);
  }
  await recordAudit(env, slug, "integration.receipt", { receiptId });
  return json({ ok: result.ok, status: result.ok ? "recorded" : result.status, tenantSlug: slug, receiptId }, result.ok ? 200 : 500);
}

async function createNote(request, env, slug) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  if (!d1(env)) return json({ ok: false, status: "D1_BINDING_REQUIRED", action: "tenant_note" }, 503);
  const body = await readJson(request);
  const noteId = `note-${crypto.randomUUID()}`;
  const text = String(body.text || "").slice(0, 2000) || "Operator note";
  let result = await run(env, "insert into support_notes (note_id, tenant_slug, text, source) values (?, ?, ?, ?)", [noteId, slug, text, body.source || "licflow3-worker"]);
  if (!result.ok) {
    result = await run(env, "insert into tenant_notes (id, tenant_id, note_type, body, created_by, created_at) values (?, (select id from tenants where slug = ?), ?, ?, ?, ?)", [noteId, slug, "general", text, body.source || "licflow3-worker", now()]);
  }
  await recordAudit(env, slug, "tenant.note", { noteId });
  return json({ ok: result.ok, status: result.ok ? "created" : result.status, tenantSlug: slug, noteId }, result.ok ? 200 : 500);
}

async function route(request, env) {
  const url = new URL(request.url);
  const method = request.method.toUpperCase();
  if (method === "OPTIONS") return json({ ok: true });
  if (method === "GET" && url.pathname === "/health") return json(await health(env));
  if (method === "GET" && url.pathname === "/api/public/capabilities") return json(await capabilities(env));
  const tenantStatusMatch = url.pathname.match(/^\/api\/public\/tenants\/([^/]+)\/status$/);
  if (method === "GET" && tenantStatusMatch) return json(await tenantStatus(env, tenantStatusMatch[1]));
  if (method === "GET" && url.pathname === "/api/client/contract") return json((await tenantStatus(env, tenantSlugFromUrl(url))).publicContract);
  if (method === "GET" && url.pathname === "/api/support/diagnostics") {
    const denied = adminRequired(request, env);
    if (denied) return denied;
    return json(await diagnostics(env, tenantSlugFromUrl(url)));
  }
  if (method === "GET" && url.pathname === "/api/admin/selftest") {
    const denied = adminRequired(request, env);
    if (denied) return denied;
    return json({ ok: true, service: SERVICE, generatedAt: now(), dbBinding: d1(env) ? "present" : "missing" });
  }
  if (method === "GET" && url.pathname === "/api/admin/commercial-summary") {
    const denied = adminRequired(request, env);
    if (denied) return denied;
    return json(await commercialSummary(env, TENANT));
  }
  const adminSnapshotMatch = url.pathname.match(/^\/api\/admin\/tenants\/([^/]+)\/snapshot$/);
  if (method === "GET" && adminSnapshotMatch) {
    const denied = adminRequired(request, env);
    if (denied) return denied;
    return json(await snapshot(env, adminSnapshotMatch[1]));
  }
  const adminNotesMatch = url.pathname.match(/^\/api\/admin\/tenants\/([^/]+)\/notes$/);
  if (method === "POST" && adminNotesMatch) return createNote(request, env, adminNotesMatch[1]);
  if (method === "POST" && url.pathname === "/api/admin/customer-setups/create") return createCustomerSetup(request, env);
  const customerSetupMatch = url.pathname.match(/^\/api\/customer\/setup\/([^/]+)$/);
  if (method === "GET" && customerSetupMatch) return resolveCustomerSetup(env, decodeURIComponent(customerSetupMatch[1]));
  if (method === "POST" && url.pathname === "/api/customer/devices/claim") return claimCustomerDevice(request, env);
  if (method === "GET" && url.pathname === "/api/customer/license/status") return customerLicenseStatus(env, url);
  if (method === "POST" && url.pathname === "/api/licenses/activate") return activateLicense(request, env, "activate");
  if (method === "POST" && url.pathname === "/api/licenses/refresh") return activateLicense(request, env, "refresh");
  if (method === "POST" && url.pathname === "/api/licenses/revoke") return activateLicense(request, env, "revoke");
  if (method === "POST" && url.pathname === "/api/devices/register") return registerDevice(request, env);
  if (method === "POST" && url.pathname === "/api/client/integration-receipt") return integrationReceipt(request, env);
  return json({ ok: false, service: SERVICE, status: "NOT_FOUND", method, path: url.pathname }, 404);
}

export default {
  async fetch(request, env) {
    try {
      return await route(request, env || {});
    } catch (error) {
      return json({
        ok: false,
        service: SERVICE,
        status: "INTERNAL_ERROR",
        error: String(error && error.message ? error.message : error)
      }, 500);
    }
  }
};
