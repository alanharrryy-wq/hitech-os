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
const PLAN_PROVISIONING_CATALOG = {
  TABLET_SOLO: {
    planId: "TABLET_SOLO",
    planName: "Tablet Solo",
    maxTabletDevices: 1,
    maxPcDevices: 0,
    maxMobileDevices: 0,
    maxTotalDevices: 1,
    allowedSurfaces: ["tablet"],
    features: ["pos.local_sale", "catalog.local", "cash.local"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PRO: {
    planId: "TABLET_PRO",
    planName: "Tablet Pro",
    maxTabletDevices: 2,
    maxPcDevices: 0,
    maxMobileDevices: 1,
    maxTotalDevices: 3,
    allowedSurfaces: ["tablet", "mobile"],
    features: ["pos.local_sale", "returns", "outbox.visible", "mobile.supervision"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PC_MANAGED: {
    planId: "TABLET_PC_MANAGED",
    planName: "Tablet + PC Managed",
    maxTabletDevices: 2,
    maxPcDevices: 1,
    maxMobileDevices: 1,
    maxTotalDevices: 4,
    allowedSurfaces: ["tablet", "pc", "mobile"],
    features: ["pos.local_sale", "pc.backoffice", "sync.audit", "mobile.supervision"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  },
  TABLET_PC_MOBILE_MANAGED: {
    planId: DEFAULT_SETUP_PLAN,
    planName: "Tablet + PC + Mobile Managed",
    maxTabletDevices: 1,
    maxPcDevices: 1,
    maxMobileDevices: 1,
    maxTotalDevices: 3,
    allowedSurfaces: ["tablet", "pc", "mobile"],
    features: ["pos.local_sale", "pc.backoffice", "mobile.companion", "customer.setup"],
    setupMode: "setup_link_code_qr",
    claimMode: "auto_generated_claim_slots",
    requiresManualApproval: false,
    expirationPolicy: "setup_bundle_30_days",
    gracePolicy: "offline_grace_policy",
    renewalPolicy: "renew_license_assignment"
  }
};
const ACTIVE_LICENSE_STATES = new Set(["active", "renewed", "expiring", "grace_period", "refreshed"]);
const BLOCKED_LICENSE_STATES = new Set(["suspended", "revoked", "expired"]);
const COMMERCIAL_STATES = new Set(["active", "expiring", "grace_period", "suspended", "revoked", "renewed"]);

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
  ["GET", "/api/customer/portal?setupCode=:setupCode", "customer_portal", false],
  ["GET", "/api/customer/magic-link?setupCode=:setupCode", "customer_magic_link", false],
  ["POST", "/api/customer/devices/claim", "customer_device_claim", true],
  ["POST", "/api/customer/devices/replacement/request", "customer_device_replacement_request", true],
  ["POST", "/api/admin/customer-devices/replacement/approve", "admin_device_replacement_approve", true],
  ["GET", "/api/customer/license/status?setupCode=:setupCode&deviceId=:deviceId", "customer_license_status", false],
  ["POST", "/api/customer/license/refresh", "customer_license_refresh", true],
  ["POST", "/api/licenses/renew", "renew", true],
  ["POST", "/api/licenses/commercial-state", "commercial_state", true]
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

function resolveCustomerSetupPlan(planId) {
  const key = String(planId || DEFAULT_SETUP_PLAN).trim().toUpperCase();
  return PLAN_PROVISIONING_CATALOG[key] || PLAN_PROVISIONING_CATALOG[DEFAULT_SETUP_PLAN];
}

function surfaceLimit(plan, surface) {
  if (surface === "tablet") return Number(plan.maxTabletDevices || 0);
  if (surface === "pc") return Number(plan.maxPcDevices || 0);
  if (surface === "mobile") return Number(plan.maxMobileDevices || 0);
  return 0;
}

function aggregateSlotsForPlan(plan) {
  return ["tablet", "pc", "mobile"]
    .map((surface) => ({
      surface,
      label: SLOT_LABELS[surface],
      allowed: surfaceLimit(plan, surface),
      claimed: 0
    }))
    .filter((slot) => slot.allowed > 0);
}

function claimCodeForSlot(setupCode, surface, index) {
  return `${setupCode}-${surface.toUpperCase()}-${String(index).padStart(2, "0")}`;
}

function buildDeviceClaimSlotsForPlan(pass, plan, expiresAt, auditEventId = null) {
  const slots = [];
  for (const surface of plan.allowedSurfaces) {
    const count = surfaceLimit(plan, surface);
    for (let index = 1; index <= count; index += 1) {
      slots.push({
        slotId: `${pass.setupBundleId}_${surface}_${index}`,
        setupBundleId: pass.setupBundleId,
        setupId: pass.setupId,
        clientId: pass.customerId,
        licenseId: pass.licenseId,
        planId: plan.planId,
        surface,
        status: "AVAILABLE",
        claimCode: claimCodeForSlot(pass.setupCode, surface, index),
        deviceId: null,
        claimedAt: null,
        expiresAt,
        auditEventId
      });
    }
  }
  return slots;
}

function slugify(value, fallback = "prisma-customer") {
  const slug = String(value || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return slug || fallback;
}

function addDays(days) {
  return new Date(Date.now() + days * 24 * 60 * 60 * 1000).toISOString();
}

function isExpired(value) {
  if (!value) return false;
  const time = Date.parse(value);
  return Number.isFinite(time) && time < Date.now();
}

function requestId(prefix = "req") {
  return `${prefix}_${crypto.randomUUID()}`;
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

function sanitizeDiagnosticText(value) {
  return String(value || "unknown")
    .replace(/Bearer\s+[A-Za-z0-9._~+/=-]+/gi, "Bearer [REDACTED]")
    .replace(/prisma_[A-Za-z0-9._~+/=-]+/g, "[REDACTED_PRISMA_TOKEN]")
    .replace(/Authorization:\s*[^\s]+/gi, "Authorization: [REDACTED]")
    .slice(0, 360);
}

function d1ErrorHint(error) {
  const text = sanitizeDiagnosticText(error && error.message ? error.message : error).toLowerCase();
  if (text.includes("new.license_id") || text.includes("no such column: license_id")) return "schema_mismatch_legacy_licenses";
  if (text.includes("no such table") && text.includes("audit")) return "audit_table_missing_or_legacy_named";
  if (text.includes("foreign key")) return "foreign_key_or_replace_conflict";
  if (text.includes("unique constraint")) return "unique_constraint_conflict";
  if (text.includes("trigger")) return "trigger_or_constraint_rejected_write";
  return "inspect_sanitized_d1_error";
}

async function run(env, sql, params = []) {
  const db = d1(env);
  if (!db) return { ok: false, status: "D1_BINDING_REQUIRED" };
  try {
    const result = await db.prepare(sql).bind(...params).run();
    return { ok: true, meta: result?.meta || null, changes: result?.meta?.changes ?? null };
  } catch (error) {
    return {
      ok: false,
      status: "D1_WRITE_FAILED",
      error: sanitizeDiagnosticText(error && error.message ? error.message : error),
      hint: d1ErrorHint(error)
    };
  }
}

async function runBatch(env, statements, context = {}) {
  const db = d1(env);
  if (!db) return { ok: false, status: "D1_BINDING_REQUIRED", operation: context.operation || "unknown" };
  try {
    const prepared = statements.map((statement) => db.prepare(statement.sql).bind(...(statement.params || [])));
    await db.batch(prepared);
    return { ok: true, statements: statements.length };
  } catch (error) {
    return {
      ok: false,
      status: "D1_WRITE_FAILED",
      operation: context.operation || "unknown",
      table: context.table || "unknown",
      error: sanitizeDiagnosticText(error && error.message ? error.message : error),
      hint: d1ErrorHint(error)
    };
  }
}

async function tableColumns(env, tableName) {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(tableName)) return new Set();
  const rows = await all(env, `PRAGMA table_info(${tableName})`);
  return new Set(rows.map((row) => row.name).filter(Boolean));
}

async function licenseSchemaMode(env) {
  const columns = await tableColumns(env, "licenses");
  if (columns.has("license_id") && columns.has("tenant_slug")) return "canonical";
  if (columns.has("id") && columns.has("tenant_id")) return "legacy";
  return "unknown";
}

async function auditSchemaMode(env) {
  const auditEvents = await tableColumns(env, "audit_events");
  if (auditEvents.has("event_id") && auditEvents.has("tenant_slug") && auditEvents.has("event_type")) return "audit_events";
  const auditLog = await tableColumns(env, "audit_log");
  if (auditLog.has("id") && auditLog.has("action") && auditLog.has("payload_json")) return "audit_log";
  return "none";
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

async function licenseById(env, slug, licenseId, schemaMode = null) {
  const mode = schemaMode || await licenseSchemaMode(env);
  if (mode === "canonical") {
    const row = await first(env, "select license_id, tenant_slug, status, plan, activation_status, valid_until, created_at, updated_at from licenses where license_id = ? and tenant_slug = ? limit 1", [licenseId, slug]);
    if (row) return row;
  }
  if (mode === "legacy" || mode === "canonical") {
    const legacyRow = await first(env, "select l.id as license_id, t.slug as tenant_slug, l.status, l.plan, l.status as activation_status, l.expires_at as valid_until, l.created_at, l.updated_at from licenses l join tenants t on l.tenant_id = t.id where l.id = ? and t.slug = ? limit 1", [licenseId, slug]);
    if (legacyRow) return legacyRow;
  }
  return null;
}

function licenseIdentifierFromBody(body) {
  return String(body.licenseId || body.licenseKey || "").trim();
}

function auditInsertStatement(auditMode, eventId, slug, eventType, payload) {
  const payloadJson = JSON.stringify(payload || {});
  if (auditMode === "audit_events") {
    return {
      sql: "insert into audit_events (event_id, tenant_slug, event_type, payload_json) values (?, ?, ?, ?)",
      params: [eventId, slug, eventType, payloadJson]
    };
  }
  if (auditMode === "audit_log") {
    return {
      sql: "insert into audit_log (id, actor, action, entity_type, entity_id, payload_json) values (?, ?, ?, ?, ?, ?)",
      params: [eventId, "licflow3-worker", eventType, "tenant", slug, payloadJson]
    };
  }
  return null;
}

async function auditEventExists(env, auditMode, eventId) {
  if (auditMode === "audit_events") {
    return Boolean(await first(env, "select event_id from audit_events where event_id = ? limit 1", [eventId]));
  }
  if (auditMode === "audit_log") {
    return Boolean(await first(env, "select id from audit_log where id = ? limit 1", [eventId]));
  }
  return false;
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
  const status = row.status || "pending_cloud_activation";
  return {
    licenseId: row.licenseId || row.license_id || "pending-hosted-license",
    tenantSlug: row.tenantSlug || row.tenant_slug || TENANT,
    status,
    plan: row.plan || PLAN,
    activationStatus: row.activationStatus || row.activation_status || LICFLOW3_LIVE_STATUS,
    validUntil: row.validUntil || row.valid_until || null,
    commercialStatus: isExpired(row.validUntil || row.valid_until) && status === "active" ? "expired" : status
  };
}

function defaultSlots(plan = resolveCustomerSetupPlan(DEFAULT_SETUP_PLAN)) {
  return aggregateSlotsForPlan(plan);
}

function buildSetupPass(row = {}, slots = null, deviceClaimSlots = null) {
  const setupCode = normalizeSetupCode(row.setupCode || row.setup_code || DEFAULT_SETUP_CODE);
  const tenantSlug = row.tenantSlug || row.tenant_slug || TENANT;
  const businessName = row.businessName || row.business_name || "Prisma Original Customer";
  const status = row.status || "source_ready";
  const plan = resolveCustomerSetupPlan(row.planId || row.plan_id || row.planCode || row.plan_code || DEFAULT_SETUP_PLAN);
  const setupId = row.setupId || row.setup_id || `setup_${setupCode.toLowerCase().replace(/[^a-z0-9]+/g, "_")}`;
  const setupBundleId = row.setupBundleId || row.setup_bundle_id || `bundle_${setupId.replace(/^setup_/, "")}`;
  const customerId = row.customerId || row.customer_id || "cust_prisma_original_customer";
  const licenseId = row.licenseId || row.license_id || `lic_${setupId}`;
  const licenseAssignmentId = row.licenseAssignmentId || row.license_assignment_id || `assign_${setupId}`;
  const expiresAt = row.expiresAt || row.expires_at || addDays(30);
  const passBase = {
    setupId,
    setupBundleId,
    setupCode,
    customerId,
    licenseId,
    planId: plan.planId
  };
  return {
    ok: true,
    schemaVersion: CUSTOMER_SETUP_SCHEMA_VERSION,
    setupId,
    setupBundleId,
    setupCode,
    setupUrl: row.setupUrl || row.setup_url || `https://app.hitechrts.com/setup/${encodeURIComponent(setupCode)}`,
    qrPayload: row.qrPayload || row.qr_payload || `prisma://setup/${encodeURIComponent(setupCode)}`,
    customerId,
    tenantId: row.tenantId || row.tenant_id || "tenant_prisma_original_customer",
    tenantSlug,
    businessId: row.businessId || row.business_id || "biz_prisma_original_customer",
    businessName,
    packageCode: row.packageCode || row.package_code || DEFAULT_SETUP_PACKAGE,
    planId: plan.planId,
    planCode: plan.planId,
    licenseId,
    licenseAssignmentId,
    status,
    expiresAt,
    slots: slots || defaultSlots(plan),
    deviceClaimSlots: deviceClaimSlots || buildDeviceClaimSlotsForPlan(passBase, plan, expiresAt, row.auditEventId || row.audit_event_id || null),
    plan,
    operatorActionCount: Number(row.operatorActionCount || row.operator_action_count || 1),
    manualDeviceClaimRequired: false,
    auditEventId: row.auditEventId || row.audit_event_id || null,
    customerMessage: status === "active" ? "Prisma Customer Setup esta activo para este cliente." : "Prisma Customer Setup source is ready; live customer use requires authorized Cloud License Gateway deploy and D1 migration.",
    nextStep: status === "active" ? "Usa Setup Link, Setup Code o Setup QR para reclamar dispositivos." : "Use Setup Link, Setup Code, or Setup QR after deployment authorization.",
    secretsExposed: false
  };
}

function customerError(status, resultCode, customerMessage, nextStep, httpStatus = 400) {
  return json({ ok: false, status, resultCode, customerMessage, nextStep, secretsExposed: false }, httpStatus);
}

function licenseCopy(status) {
  const copy = {
    active: ["Licencia activa.", "Continua usando PRISMA."],
    expiring: ["Licencia por vencer.", "Renueva antes del vencimiento para evitar interrupciones."],
    grace_period: ["Licencia en periodo de gracia.", "Renueva o contacta soporte antes de la suspension."],
    suspended: ["Licencia suspendida.", "Contacta soporte para reactivar la cuenta."],
    revoked: ["Licencia revocada.", "Contacta soporte para revisar la cuenta."],
    renewed: ["Licencia renovada.", "Continua usando PRISMA."]
  };
  return copy[status] || ["Estado de licencia pendiente.", "Contacta soporte si necesitas ayuda."];
}

function licenseStateForCustomer(licenseRow) {
  const state = licenseRow.commercialStatus || licenseRow.status || "pending";
  if (isExpired(licenseRow.validUntil) && state === "active") return "expired";
  return state;
}

function licenseBlocksCustomerAction(licenseRow) {
  const state = licenseStateForCustomer(licenseRow);
  if (!BLOCKED_LICENSE_STATES.has(state)) return null;
  const [customerMessage, nextStep] = licenseCopy(state);
  return { state, customerMessage, nextStep };
}

function setupBlocksCustomerAction(pass) {
  if (pass.status === "revoked") return { status: "SETUP_REVOKED", customerMessage: "Este setup fue cancelado.", nextStep: "Contacta soporte para revisar la cuenta.", httpStatus: 403 };
  if (pass.status === "expired" || isExpired(pass.expiresAt)) return { status: "SETUP_EXPIRED", customerMessage: "Este Setup Link expiro.", nextStep: "Pide a soporte reenviar un setup nuevo.", httpStatus: 410 };
  return null;
}

function operatorResult(action, mutationMode, resultCode, options = {}) {
  const confirmed = mutationMode === "confirmed";
  return {
    ok: options.ok !== false,
    service: SERVICE,
    action,
    status: options.status || resultCode,
    resultCode,
    tokenMode: confirmed ? "server_side_admin_secret_required" : "not_required_for_simulation",
    mutationMode,
    lastDryRunAt: confirmed ? null : now(),
    lastSimulationAt: confirmed ? null : now(),
    lastRealActionAt: confirmed ? now() : null,
    lastConfirmedOperationAt: confirmed ? now() : null,
    lastResultCode: resultCode,
    upstreamReachable: true,
    operatorChecklist: options.operatorChecklist || [
      "Admin Token Status: presence-only",
      "Simulation (Dry Run) before confirmed mutation",
      "No secret values returned to frontend or reports"
    ],
    safeToMutate: Boolean(options.safeToMutate),
    safeToMutateReason: options.safeToMutateReason || (confirmed ? "Confirmed operation gates evaluated." : "Simulation does not mutate Cloud License Database."),
    safeToMutateChecks: options.safeToMutateChecks || {
      adminToken: confirmed ? "validated_server_side" : "not_required",
      confirmation: confirmed ? true : "not_required",
      revokePhrase: action === "revoke" ? Boolean(options.revokePhraseAccepted) : "not_required"
    },
    operatorMessage: options.operatorMessage || "License operation evaluated.",
    nextStep: options.nextStep || "Review License Operation Audit.",
    requestId: options.requestId || requestId("licops"),
    latencyMs: options.latencyMs || 0,
    secretsExposed: false,
    ...options.extra
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
      planBasedProvisioning: true,
      autoGenerateClaimSlots: true,
      deviceClaim: true,
      multiDeviceSlots: true,
      deviceReplacement: true,
      customerPortal: true,
      magicLink: true,
      customerLicenseRefresh: true,
      billingRenewal: true,
      gracePeriod: true,
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
  const rows = await all(env, "select surface, label, allowed, claimed from customer_setup_slots where setup_id = ? order by case surface when 'tablet' then 1 when 'pc' then 2 when 'mobile' then 3 else 4 end", [setupId]);
  if (!rows.length) return defaultSlots();
  return rows.map((row) => ({
    surface: row.surface,
    label: row.label || SLOT_LABELS[row.surface] || row.surface,
    allowed: Number(row.allowed || 0),
    claimed: Number(row.claimed || 0)
  }));
}

async function setupBundleForSetup(env, setupId, setupCode) {
  return first(env, "select setup_bundle_id as setupBundleId, setup_id as setupId, setup_code as setupCode, setup_link as setupUrl, setup_qr_payload as qrPayload, customer_id as customerId, tenant_id as tenantId, tenant_slug as tenantSlug, business_id as businessId, business_name as businessName, license_id as licenseId, license_assignment_id as licenseAssignmentId, plan_id as planId, operator_action_count as operatorActionCount, manual_device_claim_required as manualDeviceClaimRequired, audit_event_id as auditEventId, status, expires_at as expiresAt from customer_setup_bundles where setup_id = ? or setup_code = ? order by created_at desc limit 1", [setupId, setupCode]);
}

async function claimSlotsForSetup(env, setupId) {
  const rows = await all(env, "select slot_id as slotId, setup_bundle_id as setupBundleId, setup_id as setupId, customer_id as clientId, license_id as licenseId, plan_id as planId, surface, status, claim_code as claimCode, device_id as deviceId, claimed_at as claimedAt, expires_at as expiresAt, audit_event_id as auditEventId from customer_device_claim_slots where setup_id = ? order by case surface when 'tablet' then 1 when 'pc' then 2 when 'mobile' then 3 else 4 end, slot_index", [setupId]);
  return rows.map((row) => ({
    slotId: row.slotId,
    setupBundleId: row.setupBundleId,
    setupId: row.setupId,
    clientId: row.clientId,
    licenseId: row.licenseId,
    planId: row.planId,
    surface: row.surface,
    status: row.status,
    claimCode: row.claimCode,
    deviceId: row.deviceId || null,
    claimedAt: row.claimedAt || null,
    expiresAt: row.expiresAt,
    auditEventId: row.auditEventId || null
  }));
}

async function setupByCode(env, setupCode) {
  const row = await first(env, "select setup_id, setup_code, setup_url, qr_payload, customer_id, tenant_id, tenant_slug, business_id, business_name, package_code, plan_code, status, expires_at from customer_setups where setup_code = ?", [setupCode]);
  if (!row) return null;
  const bundle = await setupBundleForSetup(env, row.setup_id, row.setup_code);
  const merged = { ...row, ...(bundle || {}) };
  return buildSetupPass(merged, await setupSlots(env, row.setup_id), await claimSlotsForSetup(env, row.setup_id));
}

async function claimsForSetup(env, setupId) {
  return all(env, "select claim_id as claimId, setup_id as setupId, setup_code as setupCode, tenant_slug as tenantSlug, surface, device_id as deviceId, device_name as deviceName, status, claimed_at as claimedAt, replaced_at as replacedAt from customer_device_claims where setup_id = ? order by claimed_at", [setupId]);
}

async function activeClaimForDevice(env, setupId, deviceId) {
  return first(env, "select claim_id as claimId, setup_id as setupId, setup_code as setupCode, tenant_slug as tenantSlug, surface, device_id as deviceId, device_name as deviceName, status, claimed_at as claimedAt, replaced_at as replacedAt from customer_device_claims where setup_id = ? and device_id = ? and status = 'claimed' limit 1", [setupId, deviceId]);
}

async function nextAvailableClaimSlot(env, pass, surface) {
  return first(env, "select slot_id as slotId, setup_bundle_id as setupBundleId, claim_code as claimCode, expires_at as expiresAt, status from customer_device_claim_slots where setup_id = ? and surface = ? and status = 'AVAILABLE' and (expires_at is null or expires_at > ?) order by slot_index asc limit 1", [pass.setupId, surface, now()]);
}

async function consumeClaimSlot(env, claimSlot, deviceId, auditEventId) {
  return run(env, "update customer_device_claim_slots set status = 'CLAIMED', device_id = ?, claimed_at = ?, audit_event_id = ?, updated_at = ? where slot_id = ? and status = 'AVAILABLE'", [deviceId, now(), auditEventId, now(), claimSlot.slotId]);
}

async function upsertTenant(env, slug, displayName, plan) {
  const columns = await tableColumns(env, "tenants");
  const existing = await first(env, "select slug from tenants where slug = ? limit 1", [slug]);
  if (existing) {
    return run(env, "update tenants set display_name = ?, status = ?, plan = ?, updated_at = ? where slug = ?", [displayName, "active", plan, now(), slug]);
  }
  if (columns.has("id")) {
    return run(env, "insert into tenants (id, slug, display_name, status, plan, updated_at) values (?, ?, ?, ?, ?, ?)", [`tenant_${slug}`, slug, displayName, "active", plan, now()]);
  }
  if (columns.has("slug")) {
    return run(env, "insert into tenants (slug, display_name, status, plan, updated_at) values (?, ?, ?, ?, ?)", [slug, displayName, "active", plan, now()]);
  }
  return { ok: false, status: "TENANTS_SCHEMA_UNSUPPORTED", hint: "tenants_table_missing_slug" };
}

async function upsertLicense(env, slug, licenseId, status, plan, validUntil) {
  const schemaMode = await licenseSchemaMode(env);
  const existing = await licenseById(env, slug, licenseId, schemaMode);
  if (schemaMode === "canonical") {
    if (existing) {
      return run(env, "update licenses set tenant_slug = ?, status = ?, plan = ?, activation_status = ?, valid_until = ?, updated_at = ? where license_id = ?", [slug, status, plan, status, validUntil || null, now(), licenseId]);
    }
    return run(env, "insert into licenses (license_id, tenant_slug, status, plan, activation_status, valid_until, updated_at) values (?, ?, ?, ?, ?, ?, ?)", [licenseId, slug, status, plan, status, validUntil || null, now()]);
  }
  if (schemaMode === "legacy") {
    if (existing) {
      return run(env, "update licenses set plan = ?, status = ?, expires_at = ?, updated_at = ? where id = ? and tenant_id = (select id from tenants where slug = ?)", [plan, status, validUntil || null, now(), licenseId, slug]);
    }
    return run(env, "insert into licenses (id, tenant_id, plan, status, expires_at, updated_at) values (?, (select id from tenants where slug = ?), ?, ?, ?, ?)", [licenseId, slug, plan, status, validUntil || null, now()]);
  }
  return { ok: false, status: "LICENSE_SCHEMA_UNSUPPORTED", hint: "licenses_table_missing_canonical_or_legacy_columns" };
}

async function requireLicenseClientContext(env, slug, licenseId, status, mode) {
  if (mode === "revoke" || !ACTIVE_LICENSE_STATES.has(status)) {
    return { ok: true, source: "non_active_or_revoke" };
  }
  const assignment = await first(env, "select license_assignment_id as licenseAssignmentId, customer_id as customerId, business_id as businessId, setup_bundle_id as setupBundleId from license_assignments where license_id = ? and customer_id is not null and business_id is not null order by updated_at desc limit 1", [licenseId]);
  if (assignment?.customerId && assignment?.businessId) return { ok: true, source: "license_assignment", assignment };
  const bundle = await first(env, "select setup_bundle_id as setupBundleId, customer_id as customerId, business_id as businessId, license_assignment_id as licenseAssignmentId from customer_setup_bundles where license_id = ? and customer_id is not null and business_id is not null order by updated_at desc limit 1", [licenseId]);
  if (bundle?.customerId && bundle?.businessId) return { ok: true, source: "setup_bundle", bundle };
  return {
    ok: false,
    status: "LICENSE_CLIENT_CONTEXT_REQUIRED",
    resultCode: "LICENSE_WITHOUT_CLIENT_BLOCKED",
    customerMessage: "No se puede activar una licencia comercial sin cliente, negocio y setup/assignment asociado.",
    operatorMessage: "Use plan-based customer setup first so license, assignment, setup bundle and claim slots are created together.",
    nextStep: "Run /api/admin/customer-setups/create or pass an existing license tied to customer_setup_bundles/license_assignments.",
    tenantSlug: slug,
    licenseId
  };
}

async function upsertLicensePlan(env, plan) {
  return run(env, "insert or replace into license_plans (plan_id, plan_name, max_tablet_devices, max_pc_devices, max_mobile_devices, max_total_devices, allowed_surfaces_json, features_json, setup_mode, claim_mode, requires_manual_approval, expiration_policy, grace_policy, renewal_policy, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    plan.planId,
    plan.planName,
    plan.maxTabletDevices,
    plan.maxPcDevices,
    plan.maxMobileDevices,
    plan.maxTotalDevices,
    JSON.stringify(plan.allowedSurfaces),
    JSON.stringify(plan.features),
    plan.setupMode,
    plan.claimMode,
    plan.requiresManualApproval ? 1 : 0,
    plan.expirationPolicy,
    plan.gracePolicy,
    plan.renewalPolicy,
    now()
  ]);
}

async function upsertLicenseAssignment(env, pass) {
  return run(env, "insert or replace into license_assignments (license_assignment_id, license_id, setup_bundle_id, customer_id, tenant_id, tenant_slug, business_id, plan_id, status, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    pass.licenseAssignmentId,
    pass.licenseId,
    pass.setupBundleId,
    pass.customerId,
    pass.tenantId,
    pass.tenantSlug,
    pass.businessId,
    pass.planId,
    "assigned",
    now()
  ]);
}

async function upsertSetupBundle(env, pass, auditEventId) {
  return run(env, "insert or replace into customer_setup_bundles (setup_bundle_id, setup_id, setup_code, setup_link, setup_qr_payload, customer_id, tenant_id, tenant_slug, business_id, business_name, license_id, license_assignment_id, plan_id, operator_action_count, manual_device_claim_required, audit_event_id, status, expires_at, created_by, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    pass.setupBundleId,
    pass.setupId,
    pass.setupCode,
    pass.setupUrl,
    pass.qrPayload,
    pass.customerId,
    pass.tenantId,
    pass.tenantSlug,
    pass.businessId,
    pass.businessName,
    pass.licenseId,
    pass.licenseAssignmentId,
    pass.planId,
    1,
    0,
    auditEventId,
    pass.status,
    pass.expiresAt,
    "licflow3-worker",
    now()
  ]);
}

async function upsertDeviceClaimSlot(env, pass, slot, index, auditEventId) {
  return run(env, "insert or replace into customer_device_claim_slots (slot_id, setup_bundle_id, setup_id, customer_id, license_id, plan_id, surface, slot_index, claim_code, device_id, claimed_at, expires_at, status, audit_event_id, updated_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    slot.slotId,
    pass.setupBundleId,
    pass.setupId,
    pass.customerId,
    pass.licenseId,
    pass.planId,
    slot.surface,
    index,
    slot.claimCode,
    slot.deviceId,
    slot.claimedAt,
    slot.expiresAt,
    slot.status,
    auditEventId,
    now()
  ]);
}

async function registerClaimedDevice(env, pass, surface, deviceId, deviceName) {
  let result = await run(env, "insert or replace into devices (device_id, tenant_slug, device_name, role, platform, status, updated_at) values (?, ?, ?, ?, ?, ?, ?)", [deviceId, pass.tenantSlug, deviceName || deviceId, surface, surface, "registered", now()]);
  if (!result.ok) {
    result = await run(env, "insert or replace into devices (id, tenant_id, device_code, label, status, updated_at) values (?, (select id from tenants where slug = ?), ?, ?, ?, ?)", [deviceId, pass.tenantSlug, deviceId, deviceName || deviceId, "registered", now()]);
  }
  return result;
}

async function createCustomerSetup(request, env) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  const body = await readJson(request);
  const generatedCode = `PRISMA-${Date.now().toString(36)}-${crypto.randomUUID().slice(0, 8)}`;
  const setupCode = normalizeSetupCode(body.setupCode || generatedCode);
  const setupId = body.setupId || `setup_${crypto.randomUUID()}`;
  const setupBundleId = body.setupBundleId || `bundle_${crypto.randomUUID()}`;
  const tenantSlug = body.tenantSlug || slugify(body.customerPrefix || body.businessName || setupCode, `tenant-${setupCode.toLowerCase()}`);
  const businessName = body.businessName || `PRISMA Customer ${setupCode}`;
  const plan = resolveCustomerSetupPlan(body.planId || body.planCode || DEFAULT_SETUP_PLAN);
  const validUntil = body.validUntil || addDays(365);
  const expiresAt = body.expiresAt || addDays(30);
  const licenseId = body.licenseId || `lic_${setupId}`;
  const licenseAssignmentId = body.licenseAssignmentId || `assign_${setupId}`;
  const pass = buildSetupPass({
    setupId,
    setupBundleId,
    setupCode,
    customerId: body.customerId || `cust_${tenantSlug.replace(/-/g, "_")}`,
    tenantId: body.tenantId || `tenant_${tenantSlug.replace(/-/g, "_")}`,
    tenantSlug,
    businessId: body.businessId || `biz_${tenantSlug.replace(/-/g, "_")}`,
    businessName,
    planId: plan.planId,
    planCode: plan.planId,
    licenseId,
    licenseAssignmentId,
    expiresAt,
    status: "active"
  }, aggregateSlotsForPlan(plan));
  pass.deviceClaimSlots = buildDeviceClaimSlotsForPlan(pass, plan, expiresAt);
  if (!d1(env)) return json({ ...pass, ok: false, status: "D1_BINDING_REQUIRED", sourceReady: true }, 503);
  const planResult = await upsertLicensePlan(env, plan);
  if (!planResult.ok) return json({ ...pass, ok: false, status: planResult.status, resultCode: "PLAN_PROVISIONING_SCHEMA_REQUIRED", nextStep: "Apply migration 0003_plan_based_provisioning.sql before live provisioning.", secretsExposed: false }, 500);
  await upsertTenant(env, pass.tenantSlug, pass.businessName, plan.planId);
  const assignmentResult = await upsertLicenseAssignment(env, pass);
  if (!assignmentResult.ok) return json({ ...pass, ok: false, status: assignmentResult.status, resultCode: "LICENSE_ASSIGNMENT_CREATE_FAILED", secretsExposed: false }, 500);
  await upsertLicense(env, pass.tenantSlug, pass.licenseId, "active", plan.planId, validUntil);
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
  const auditPayload = {
    setupId: pass.setupId,
    setupBundleId: pass.setupBundleId,
    setupCode: pass.setupCode,
    licenseId: pass.licenseId,
    licenseAssignmentId: pass.licenseAssignmentId,
    planId: plan.planId,
    claimSlotsCreated: pass.deviceClaimSlots.length,
    operatorActionCount: 1,
    manualDeviceClaimRequired: false
  };
  const createAuditEventId = await recordAudit(env, pass.tenantSlug, "customer_setup.create", auditPayload);
  const auditEventId = await recordAudit(env, pass.tenantSlug, "customer_setup.plan_based_provision", auditPayload);
  pass.auditEventId = auditEventId;
  pass.auditEventIds = {
    create: createAuditEventId,
    planBasedProvision: auditEventId
  };
  pass.deviceClaimSlots = buildDeviceClaimSlotsForPlan(pass, plan, expiresAt, auditEventId);
  const bundleResult = await upsertSetupBundle(env, pass, auditEventId);
  if (!bundleResult.ok) return json({ ...pass, ok: false, status: bundleResult.status, resultCode: "SETUP_BUNDLE_CREATE_FAILED", secretsExposed: false }, 500);
  const slotIndexBySurface = {};
  for (let index = 0; index < pass.deviceClaimSlots.length; index += 1) {
    const claimSlot = pass.deviceClaimSlots[index];
    slotIndexBySurface[claimSlot.surface] = Number(slotIndexBySurface[claimSlot.surface] || 0) + 1;
    const slotResult = await upsertDeviceClaimSlot(env, pass, claimSlot, slotIndexBySurface[claimSlot.surface], auditEventId);
    if (!slotResult.ok) return json({ ...pass, ok: false, status: slotResult.status, resultCode: "DEVICE_CLAIM_SLOT_CREATE_FAILED", secretsExposed: false }, 500);
  }
  return json({
    ...pass,
    license: { licenseId: pass.licenseId, state: "active", validUntil },
    licenseAssignment: { licenseAssignmentId: pass.licenseAssignmentId, status: "assigned" },
    setupBundle: { setupBundleId: pass.setupBundleId, setupCode: pass.setupCode, setupLink: pass.setupUrl, setupQrPayload: pass.qrPayload },
    plan,
    operatorActionCount: 1,
    manualDeviceClaimRequired: false,
    resultCode: "PLAN_BASED_CUSTOMER_ONBOARDING_READY"
  });
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
  const setupBlock = setupBlocksCustomerAction(pass);
  if (setupBlock) return customerError(setupBlock.status, setupBlock.status, setupBlock.customerMessage, setupBlock.nextStep, setupBlock.httpStatus);
  const licenseRow = normalizeLicense(await license(env, pass.tenantSlug));
  const licenseBlock = licenseBlocksCustomerAction(licenseRow);
  if (licenseBlock) return customerError(`LICENSE_${licenseBlock.state.toUpperCase()}`, `LICENSE_${licenseBlock.state.toUpperCase()}`, licenseBlock.customerMessage, licenseBlock.nextStep, 403);
  const slot = pass.slots.find((item) => item.surface === surface);
  if (!slot) return json({ ok: false, status: "SURFACE_NOT_ALLOWED", resultCode: "SURFACE_NOT_ALLOWED", customerMessage: "Este paquete no incluye esta app.", nextStep: "Revisa tu plan o contacta soporte.", secretsExposed: false }, 422);
  const existing = await first(env, "select claim_id, device_id, surface, status from customer_device_claims where setup_id = ? and device_id = ? and status = 'claimed' limit 1", [pass.setupId, deviceId]);
  if (existing) return json({ ok: false, status: "DEVICE_ALREADY_CLAIMED", resultCode: "DEVICE_ALREADY_CLAIMED", customerMessage: "Este dispositivo ya esta activado.", nextStep: "Continua usando la app o revisa soporte si cambiaste de equipo.", secretsExposed: false }, 409);
  if (slot.claimed >= slot.allowed) return json({ ok: false, status: "DEVICE_SLOT_FULL", resultCode: "DEVICE_SLOT_FULL", customerMessage: "Ya se uso el cupo para este tipo de dispositivo.", nextStep: "Solicita reemplazo autorizado o un cupo adicional.", secretsExposed: false }, 409);
  const claimSlot = await nextAvailableClaimSlot(env, pass, surface);
  if (!claimSlot) return json({ ok: false, status: "DEVICE_SLOT_FULL", resultCode: "DEVICE_SLOT_FULL", customerMessage: "Ya se uso el cupo para este tipo de dispositivo.", nextStep: "Solicita reemplazo autorizado o un cupo adicional.", secretsExposed: false }, 409);
  const claimId = `claim_${crypto.randomUUID()}`;
  const deviceName = String(body.deviceName || deviceId).slice(0, 160);
  const result = await run(env, "insert into customer_device_claims (claim_id, setup_id, setup_code, tenant_slug, surface, device_id, device_name, installation_fingerprint, app_version, operator_label, status, claimed_at) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
    claimId,
    pass.setupId,
    pass.setupCode,
    pass.tenantSlug,
    surface,
    deviceId,
    deviceName,
    String(body.installationFingerprint || "").slice(0, 160),
    String(body.appVersion || "").slice(0, 80),
    String(body.operatorLabel || "").slice(0, 160),
    "claimed",
    now()
  ]);
  if (!result.ok) return json({ ok: false, status: result.status, resultCode: "CUSTOMER_SETUP_UPSTREAM_FAILED", customerMessage: "No pudimos validar el setup.", nextStep: "Reintenta o contacta soporte con evidencia sanitizada.", secretsExposed: false }, 500);
  await registerClaimedDevice(env, pass, surface, deviceId, deviceName);
  const auditEventId = await recordAudit(env, pass.tenantSlug, "customer_device.claim", { setupCode, surface, deviceId, claimSlotId: claimSlot.slotId, licenseId: pass.licenseId, planId: pass.planId });
  const consumeResult = await consumeClaimSlot(env, claimSlot, deviceId, auditEventId);
  if (!consumeResult.ok) return json({ ok: false, status: consumeResult.status, resultCode: "DEVICE_CLAIM_SLOT_CONSUME_FAILED", customerMessage: "No pudimos reservar el cupo preparado.", nextStep: "Reintenta o contacta soporte con evidencia sanitizada.", secretsExposed: false }, 500);
  await run(env, "update customer_setup_slots set claimed = claimed + 1, updated_at = ? where setup_id = ? and surface = ? and claimed < allowed", [now(), pass.setupId, surface]);
  const updatedPass = await setupByCode(env, setupCode) || pass;
  return json({
    ok: true,
    status: "claimed",
    resultCode: "DEVICE_CLAIM_ACCEPTED",
    customerMessage: `Este dispositivo quedo activado para ${SLOT_LABELS[surface]}.`,
    nextStep: "Continua en la app.",
    customer: { customerId: pass.customerId, displayName: pass.businessName },
    business: { businessId: pass.businessId, displayName: pass.businessName },
    license: { licenseId: licenseRow.licenseId, planCode: pass.planCode, state: licenseStateForCustomer(licenseRow), validUntil: licenseRow.validUntil },
    device: { deviceId, surface, slotLabel: SLOT_LABELS[surface], claimId, claimSlotId: claimSlot.slotId, claimCode: claimSlot.claimCode },
    slots: updatedPass.slots,
    deviceClaimSlots: updatedPass.deviceClaimSlots,
    setupBundle: { setupBundleId: pass.setupBundleId, setupCode: pass.setupCode, setupLink: pass.setupUrl, setupQrPayload: pass.qrPayload },
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
  const licenseRow = normalizeLicense(await license(env, pass.tenantSlug));
  const state = licenseStateForCustomer(licenseRow);
  const claim = deviceId && d1(env) ? await activeClaimForDevice(env, pass.setupId, deviceId) : null;
  const [customerMessage, nextStep] = licenseCopy(state);
  return json({
    ok: true,
    status: state,
    resultCode: "LICENSE_STATUS_OK",
    setupCode,
    deviceId: deviceId || null,
    license: { licenseId: licenseRow.licenseId, planCode: pass.planCode, state, status: state, validUntil: licenseRow.validUntil, signed: false },
    device: claim ? { deviceId: claim.deviceId, surface: claim.surface, status: claim.status, claimId: claim.claimId } : null,
    slots: pass.slots,
    customerMessage,
    nextStep,
    secretsExposed: false
  });
}

async function customerLicenseRefresh(request, env) {
  const body = await readJson(request);
  const setupCode = normalizeSetupCode(body.setupCode);
  const deviceId = String(body.deviceId || "").trim();
  if (!setupCode) return customerError("SETUP_CODE_REQUIRED", "SETUP_CODE_REQUIRED", "Falta el codigo de configuracion.", "Pega el Setup Code o abre el Setup Link.", 400);
  if (!deviceId) return customerError("INVALID_LICENSE_REFRESH", "DEVICE_ID_REQUIRED", "Falta identificar este dispositivo.", "Reintenta desde la app para generar el identificador local.", 400);
  const pass = d1(env) ? await setupByCode(env, setupCode) : buildSetupPass({ setupCode, status: "source_ready" });
  if (!pass) return customerError("SETUP_NOT_FOUND", "SETUP_NOT_FOUND", "No encontramos este setup.", "Revisa el Setup Code o pide un link nuevo.", 404);
  const licenseRow = normalizeLicense(await license(env, pass.tenantSlug));
  const licenseBlock = licenseBlocksCustomerAction(licenseRow);
  if (licenseBlock) return customerError(`LICENSE_${licenseBlock.state.toUpperCase()}`, `LICENSE_${licenseBlock.state.toUpperCase()}`, licenseBlock.customerMessage, licenseBlock.nextStep, 403);
  const claim = await activeClaimForDevice(env, pass.setupId, deviceId);
  if (!claim) return customerError("DEVICE_NOT_CLAIMED", "DEVICE_NOT_CLAIMED", "Este dispositivo no esta reclamado en este setup.", "Reclama el dispositivo o contacta soporte.", 404);
  await recordAudit(env, pass.tenantSlug, "customer_license.refresh", { setupCode, deviceId, surface: claim.surface });
  const [customerMessage, nextStep] = licenseCopy(licenseStateForCustomer(licenseRow));
  return json({
    ok: true,
    status: "refreshed",
    resultCode: "LICENSE_REFRESHED",
    setupCode,
    device: { deviceId: claim.deviceId, surface: claim.surface, status: claim.status, claimId: claim.claimId },
    license: { licenseId: licenseRow.licenseId, planCode: pass.planCode, state: licenseStateForCustomer(licenseRow), validUntil: licenseRow.validUntil, signed: false },
    customerMessage,
    nextStep,
    secretsExposed: false
  });
}

async function customerPortal(env, url) {
  const setupCode = normalizeSetupCode(url.searchParams.get("setupCode"));
  if (!setupCode) return customerError("SETUP_CODE_REQUIRED", "SETUP_CODE_REQUIRED", "Falta el codigo de configuracion.", "Pega el Setup Code o abre el Setup Link.", 400);
  const pass = d1(env) ? await setupByCode(env, setupCode) : buildSetupPass({ setupCode, status: "source_ready" });
  if (!pass) return customerError("SETUP_NOT_FOUND", "SETUP_NOT_FOUND", "No encontramos este setup.", "Revisa el Setup Code o pide un link nuevo.", 404);
  const claims = d1(env) ? await claimsForSetup(env, pass.setupId) : [];
  const licenseRow = normalizeLicense(await license(env, pass.tenantSlug));
  return json({
    ok: true,
    status: "CUSTOMER_PORTAL_READY",
    resultCode: "CUSTOMER_PORTAL_READY",
    tenant: { tenantSlug: pass.tenantSlug, businessName: pass.businessName },
    setup: { setupCode: pass.setupCode, setupLink: pass.setupUrl, setupQr: pass.qrPayload, status: pass.status, expiresAt: pass.expiresAt },
    slots: pass.slots,
    devices: claims.map((claim) => ({ deviceId: claim.deviceId, deviceName: claim.deviceName, surface: claim.surface, status: claim.status, claimedAt: claim.claimedAt, replacedAt: claim.replacedAt })),
    license: { licenseId: licenseRow.licenseId, status: licenseStateForCustomer(licenseRow), planCode: pass.planCode, validUntil: licenseRow.validUntil },
    magicLink: { href: pass.setupUrl, scope: "setup-pass-only", admin: false },
    support: { replacementRequestAvailable: true, nextStep: "Solicita soporte/replacement si cambiaste de equipo." },
    secretsExposed: false
  });
}

async function customerMagicLink(env, url) {
  const setupCode = normalizeSetupCode(url.searchParams.get("setupCode"));
  if (!setupCode) return customerError("SETUP_CODE_REQUIRED", "SETUP_CODE_REQUIRED", "Falta el codigo de configuracion.", "Pega el Setup Code o abre el Setup Link.", 400);
  const pass = d1(env) ? await setupByCode(env, setupCode) : buildSetupPass({ setupCode, status: "source_ready" });
  if (!pass) return customerError("SETUP_NOT_FOUND", "SETUP_NOT_FOUND", "No encontramos este setup.", "Revisa el Setup Code o pide un link nuevo.", 404);
  return json({
    ok: true,
    status: "MAGIC_LINK_READY",
    resultCode: "MAGIC_LINK_READY",
    setupCode: pass.setupCode,
    setupLink: pass.setupUrl,
    setupQr: pass.qrPayload,
    scope: "setup-pass-only",
    admin: false,
    secretsExposed: false
  });
}

async function requestDeviceReplacement(request, env) {
  const body = await readJson(request);
  const setupCode = normalizeSetupCode(body.setupCode);
  const surface = normalizeSurface(body.surface);
  const oldDeviceId = String(body.oldDeviceId || body.deviceId || "").trim();
  const newDeviceId = String(body.newDeviceId || "").trim();
  const reason = String(body.reason || "").trim();
  if (!setupCode) return customerError("SETUP_CODE_REQUIRED", "SETUP_CODE_REQUIRED", "Falta el codigo de configuracion.", "Pega el Setup Code o abre el Setup Link.", 400);
  if (!surface) return customerError("SURFACE_NOT_ALLOWED", "SURFACE_NOT_ALLOWED", "Este paquete no incluye esta app.", "Revisa tu plan o contacta soporte.", 422);
  if (!oldDeviceId || !newDeviceId) return customerError("DEVICE_REPLACEMENT_INVALID", "DEVICE_REPLACEMENT_DEVICE_IDS_REQUIRED", "Falta identificar el equipo anterior y el nuevo.", "Reintenta desde la app o contacta soporte.", 400);
  const pass = await setupByCode(env, setupCode);
  if (!pass) return customerError("SETUP_NOT_FOUND", "SETUP_NOT_FOUND", "No encontramos este setup.", "Revisa el Setup Code o pide un link nuevo.", 404);
  const claim = await activeClaimForDevice(env, pass.setupId, oldDeviceId);
  if (!claim || claim.surface !== surface) return customerError("DEVICE_REPLACEMENT_NOT_ALLOWED", "DEVICE_REPLACEMENT_NOT_ALLOWED", "No encontramos un dispositivo activo para reemplazar en ese cupo.", "Verifica el equipo anterior o contacta soporte.", 404);
  const replacementRequestId = requestId("replacement");
  await recordAudit(env, pass.tenantSlug, "customer_device.replacement.request", { replacementRequestId, setupCode, surface, oldDeviceId, newDeviceId, reason });
  return json({
    ok: true,
    status: "REPLACEMENT_REQUESTED",
    resultCode: "REPLACEMENT_REQUESTED",
    replacementRequestId,
    setupCode,
    surface,
    oldDeviceId,
    newDeviceId,
    customerMessage: "Solicitud de reemplazo registrada.",
    nextStep: "Soporte aprobara el reemplazo antes de reclamar el nuevo equipo.",
    secretsExposed: false
  });
}

async function approveDeviceReplacement(request, env) {
  const denied = adminRequired(request, env);
  if (denied) return denied;
  const body = await readJson(request);
  if (body.confirmAdminLicenseAction !== true) return json(operatorResult("replacement.approve", "confirmed", "ADMIN_ACTION_CONFIRMATION_REQUIRED", { ok: false, safeToMutate: false, operatorMessage: "Confirma la accion administrativa antes de mutar slots.", nextStep: "Envia confirmAdminLicenseAction: true." }), 409);
  const setupCode = normalizeSetupCode(body.setupCode);
  const surface = normalizeSurface(body.surface);
  const oldDeviceId = String(body.oldDeviceId || body.deviceId || "").trim();
  const reason = String(body.reason || "").trim();
  if (!setupCode || !surface || !oldDeviceId || !reason) return json(operatorResult("replacement.approve", "confirmed", "INVALID_REPLACEMENT_APPROVAL", { ok: false, safeToMutate: false, operatorMessage: "Faltan datos para aprobar replacement.", nextStep: "Incluye setupCode, surface, oldDeviceId y reason." }), 400);
  const pass = await setupByCode(env, setupCode);
  if (!pass) return customerError("SETUP_NOT_FOUND", "SETUP_NOT_FOUND", "No encontramos este setup.", "Revisa el Setup Code o pide un link nuevo.", 404);
  const claim = await activeClaimForDevice(env, pass.setupId, oldDeviceId);
  if (!claim || claim.surface !== surface) return json(operatorResult("replacement.approve", "confirmed", "DEVICE_REPLACEMENT_NOT_ALLOWED", { ok: false, safeToMutate: false, operatorMessage: "No hay claim activo para liberar.", nextStep: "Verifica setup, surface y oldDeviceId." }), 404);
  await run(env, "update customer_device_claims set status = 'replaced', replaced_at = ? where setup_id = ? and device_id = ? and surface = ? and status = 'claimed'", [now(), pass.setupId, oldDeviceId, surface]);
  await run(env, "update customer_setup_slots set claimed = case when claimed > 0 then claimed - 1 else 0 end, updated_at = ? where setup_id = ? and surface = ?", [now(), pass.setupId, surface]);
  await recordAudit(env, pass.tenantSlug, "customer_device.replacement.approve", { setupCode, surface, oldDeviceId, reason });
  return json(operatorResult("replacement.approve", "confirmed", "DEVICE_REPLACEMENT_APPROVED", {
    safeToMutate: true,
    operatorMessage: "Slot liberado para reclamar el nuevo dispositivo.",
    nextStep: "Ejecuta Device Claim con el nuevo deviceId.",
    extra: { setupCode, surface, oldDeviceId }
  }));
}

async function commercialSummary(env, slug) {
  const payload = await tenantStatus(env, slug);
  const state = licenseStateForCustomer(payload.license);
  const [customerMessage, nextStep] = licenseCopy(state);
  return {
    ok: true,
    service: SERVICE,
    tenant: payload.tenant,
    status: state,
    resultCode: "COMMERCIAL_SUMMARY_READY",
    summary: "Commercial status is available from the Cloud License Database.",
    plan: payload.tenant.plan,
    license: payload.license,
    supportedStates: Array.from(COMMERCIAL_STATES),
    customerMessage,
    nextStep,
    secretsExposed: false
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
    contract: CONTRACT_ENDPOINTS.map(([method, path, capability, mutatesCloud]) => ({ method, path, capability, mutatesCloud })),
    operatorMessage: "License Diagnostics are sanitized for support.",
    nextStep: "Use requestId and resultCode from operation responses for support correlation.",
    resultCode: "LICENSE_DIAGNOSTICS_READY",
    upstreamStatus: db ? "D1_BOUND" : "D1_BINDING_REQUIRED",
    latencyMs: 0,
    secretsExposed: false
  };
}

async function revokeLicenseAtomically(env, slug, licenseId, plan, validUntil, reason, operationRequestId) {
  const schemaMode = await licenseSchemaMode(env);
  if (schemaMode === "unknown") {
    return {
      ok: false,
      status: "LICENSE_SCHEMA_UNSUPPORTED",
      resultCode: "LICENSE_SCHEMA_UNSUPPORTED",
      httpStatus: 500,
      safeToMutateReason: "licenses table does not expose canonical or legacy columns.",
      nextStep: "Inspect remote sqlite_schema and PRAGMA table_info(licenses).",
      d1Hint: "licenses_table_missing_canonical_or_legacy_columns"
    };
  }

  const before = await licenseById(env, slug, licenseId, schemaMode);
  if (!before) {
    return {
      ok: false,
      status: "LICENSE_NOT_FOUND",
      resultCode: "LICENSE_NOT_FOUND",
      httpStatus: 404,
      safeToMutateReason: "No persisted license matched tenantSlug and licenseId.",
      nextStep: "Verify tenantSlug/licenseId before revoke; revoke does not create licenses.",
      d1Hint: "read_before_write_empty"
    };
  }

  const auditMode = await auditSchemaMode(env);
  if (auditMode === "none") {
    return {
      ok: false,
      status: "AUDIT_TABLE_REQUIRED",
      resultCode: "AUDIT_TABLE_REQUIRED",
      httpStatus: 500,
      safeToMutateReason: "Revoke requires an audit/event table before returning green.",
      nextStep: "Inspect remote sqlite_schema for audit_events or audit_log.",
      d1Hint: "audit_table_missing"
    };
  }

  const alreadyRevoked = before.status === "revoked";
  const eventType = alreadyRevoked ? "license.revoke.idempotent" : "license.revoke";
  const eventId = `${eventType}-${crypto.randomUUID()}`;
  const payload = {
    licenseId,
    tenantSlug: slug,
    status: "revoked",
    previousStatus: before.status || null,
    plan: plan || before.plan || PLAN,
    reason: reason || null,
    idempotent: alreadyRevoked,
    requestId: operationRequestId
  };
  const statements = [];
  if (!alreadyRevoked && schemaMode === "canonical") {
    statements.push({
      sql: "update licenses set status = ?, activation_status = ?, plan = ?, valid_until = coalesce(?, valid_until), updated_at = ? where license_id = ? and tenant_slug = ?",
      params: ["revoked", "revoked", plan || before.plan || PLAN, validUntil || null, now(), licenseId, slug]
    });
  }
  if (!alreadyRevoked && schemaMode === "legacy") {
    statements.push({
      sql: "update licenses set status = ?, plan = ?, expires_at = coalesce(?, expires_at), updated_at = ? where id = ? and tenant_id = (select id from tenants where slug = ?)",
      params: ["revoked", plan || before.plan || PLAN, validUntil || null, now(), licenseId, slug]
    });
  }

  const auditStatement = auditInsertStatement(auditMode, eventId, slug, eventType, payload);
  if (!auditStatement) {
    return {
      ok: false,
      status: "AUDIT_TABLE_REQUIRED",
      resultCode: "AUDIT_TABLE_REQUIRED",
      httpStatus: 500,
      safeToMutateReason: "No compatible audit insert statement is available.",
      nextStep: "Inspect audit_events/audit_log schema.",
      d1Hint: "audit_insert_statement_missing"
    };
  }
  statements.push(auditStatement);

  const write = await runBatch(env, statements, { operation: "license_revoke", table: `licenses+${auditMode}` });
  if (!write.ok) {
    return {
      ...write,
      resultCode: write.status,
      httpStatus: 500,
      safeToMutateReason: "Cloud License Database mutation failed before verified persistence.",
      nextStep: "Inspect sanitized D1 hint and remote schema; do not declare revoke green.",
      d1Hint: write.hint
    };
  }

  const after = await licenseById(env, slug, licenseId, schemaMode);
  if (!after || after.status !== "revoked") {
    return {
      ok: false,
      status: "D1_REVOKE_PERSISTENCE_FAILED",
      resultCode: "D1_REVOKE_PERSISTENCE_FAILED",
      httpStatus: 500,
      safeToMutateReason: "D1 write returned OK but read-after-write did not confirm revoked.",
      nextStep: "Inspect license row and audit event before retrying.",
      d1Hint: "read_after_write_not_revoked",
      schemaMode,
      auditTable: auditMode,
      auditEventId: eventId
    };
  }

  const auditVerified = await auditEventExists(env, auditMode, eventId);
  if (!auditVerified) {
    return {
      ok: false,
      status: "D1_REVOKE_AUDIT_VERIFY_FAILED",
      resultCode: "D1_REVOKE_AUDIT_VERIFY_FAILED",
      httpStatus: 500,
      safeToMutateReason: "D1 write returned OK but audit/event read-back did not confirm persistence.",
      nextStep: "Inspect audit table before declaring cleanup revoke PASS.",
      d1Hint: "audit_read_after_write_missing",
      schemaMode,
      auditTable: auditMode,
      auditEventId: eventId
    };
  }

  return {
    ok: true,
    status: "revoked",
    resultCode: "REVOKE_CONFIRMED",
    persisted: true,
    auditVerified: true,
    auditTable: auditMode,
    auditEventId: eventId,
    schemaMode,
    idempotent: alreadyRevoked,
    license: normalizeLicense(after)
  };
}

async function recordAudit(env, slug, eventType, payload) {
  const eventId = `${eventType}-${crypto.randomUUID()}`;
  const auditMode = await auditSchemaMode(env);
  const statement = auditInsertStatement(auditMode, eventId, slug, eventType, payload);
  if (statement) {
    await run(env, statement.sql, statement.params);
  }
  return eventId;
}

async function activateLicense(request, env, mode) {
  const started = Date.now();
  const body = await readJson(request);
  const simulation = body.simulation === true || body.dryRun === true || body.mutationMode === "simulation";
  const mutationMode = simulation ? "simulation" : "confirmed";
  if (!simulation) {
    const denied = adminRequired(request, env);
    if (denied) return denied;
  }
  if (mode === "revoke" && !String(body.reason || "").trim()) {
    return json(operatorResult(mode, mutationMode, "REVOKE_REASON_REQUIRED", {
      ok: false,
      safeToMutate: false,
      operatorMessage: "Revoke requiere reason.",
      nextStep: "Incluye reason antes de ejecutar revoke.",
      latencyMs: Date.now() - started
    }), 400);
  }
  if (!simulation && body.confirmAdminLicenseAction !== true) {
    return json(operatorResult(mode, mutationMode, "ADMIN_ACTION_CONFIRMATION_REQUIRED", {
      ok: false,
      safeToMutate: false,
      operatorMessage: "Confirmed License Operation requiere confirmAdminLicenseAction.",
      nextStep: "Envia confirmAdminLicenseAction: true.",
      latencyMs: Date.now() - started
    }), 409);
  }
  if (!simulation && mode === "revoke" && body.confirmRevoke !== "REVOKE_LICENSE") {
    return json(operatorResult(mode, mutationMode, "REVOKE_CONFIRMATION_REQUIRED", {
      ok: false,
      safeToMutate: false,
      operatorMessage: "Confirmed revoke requiere la frase REVOKE_LICENSE.",
      nextStep: "Envia confirmRevoke: REVOKE_LICENSE y reason.",
      latencyMs: Date.now() - started
    }), 409);
  }
  const db = d1(env);
  if (!db) return json({ ok: false, status: "D1_BINDING_REQUIRED", action: mode, signedLicenseIssued: false }, 503);
  const slug = body.tenantSlug || body.tenant || TENANT;
  const providedLicenseId = licenseIdentifierFromBody(body);
  if (!simulation && !providedLicenseId) {
    return json(operatorResult(mode, mutationMode, "LICENSE_ID_REQUIRED", {
      ok: false,
      safeToMutate: false,
      operatorMessage: "Confirmed License Operation requiere licenseId. licenseKey se acepta solo como alias de compatibilidad.",
      nextStep: "Envia licenseId o licenseKey antes de ejecutar la operacion confirmada.",
      latencyMs: Date.now() - started
    }), 400);
  }
  const licenseId = providedLicenseId || `licflow3-${mode}-${crypto.randomUUID()}`;
  const requestedState = String(body.status || body.commercialStatus || "").trim().toLowerCase();
  const status = mode === "revoke" ? "revoked" : mode === "renew" ? "renewed" : mode === "commercial-state" && COMMERCIAL_STATES.has(requestedState) ? requestedState : mode === "refresh" ? "active" : "active";
  const validUntil = body.validUntil || (mode === "renew" ? addDays(365) : null);
  const resultCode = simulation ? `${mode.toUpperCase().replace(/-/g, "_")}_SIMULATION_READY` : `${mode.toUpperCase().replace(/-/g, "_")}_CONFIRMED`;
  if (simulation) {
    return json(operatorResult(mode, mutationMode, resultCode, {
      safeToMutate: false,
      safeToMutateChecks: {
        adminToken: "not_required",
        confirmation: "not_required",
        revokePhrase: mode === "revoke" ? "not_required_for_simulation" : "not_required",
        reason: mode === "revoke" ? "present" : "not_required"
      },
      operatorMessage: "Simulation (Dry Run) evaluated without mutating Cloud License Database.",
      nextStep: "Review safeToMutateChecks, then run Confirmed License Operation if intended.",
      latencyMs: Date.now() - started,
      extra: { tenantSlug: slug, licenseId, plannedStatus: status }
    }));
  }
  if (mode !== "revoke") {
    await upsertTenant(env, slug, body.businessName || slug, body.plan || PLAN);
  }
  if (mode === "revoke") {
    const operationRequestId = requestId("licops");
    const revokeResult = await revokeLicenseAtomically(env, slug, licenseId, body.plan || PLAN, validUntil, body.reason, operationRequestId);
    return json(operatorResult(mode, mutationMode, revokeResult.resultCode || revokeResult.status, {
      ok: revokeResult.ok,
      status: revokeResult.ok ? "revoked" : revokeResult.status,
      safeToMutate: revokeResult.ok,
      safeToMutateReason: revokeResult.ok ? "Confirmed operation gates passed; revoke status and audit/event persisted." : revokeResult.safeToMutateReason,
      safeToMutateChecks: {
        adminToken: "validated_server_side",
        confirmation: true,
        revokePhrase: true,
        reason: "present",
        readAfterWrite: revokeResult.ok ? "confirmed" : "not_confirmed",
        auditEvent: revokeResult.ok ? "verified" : "not_verified"
      },
      revokePhraseAccepted: true,
      operatorMessage: revokeResult.ok ? "Confirmed License Operation completed and verified." : "Confirmed License Operation failed before verified persistence.",
      nextStep: revokeResult.ok ? "Review License Operation Audit and customer status." : revokeResult.nextStep || "Inspect sanitized diagnostics.",
      requestId: operationRequestId,
      latencyMs: Date.now() - started,
      extra: {
        tenantSlug: slug,
        licenseId,
        license: revokeResult.license ? { ...revokeResult.license, signedLicenseIssued: false } : { licenseId, status: revokeResult.status, plan: body.plan || PLAN, validUntil, signedLicenseIssued: false },
        revokePersistence: {
          persisted: revokeResult.persisted === true,
          readAfterWrite: revokeResult.ok ? "confirmed" : "not_confirmed",
          auditVerified: revokeResult.auditVerified === true,
          auditTable: revokeResult.auditTable || null,
          auditEventId: revokeResult.auditEventId || null,
          schemaMode: revokeResult.schemaMode || null,
          idempotent: revokeResult.idempotent === true
        },
        d1: {
          operation: revokeResult.operation || "license_revoke",
          table: revokeResult.table || "licenses",
          hint: revokeResult.d1Hint || revokeResult.hint || null,
          error: revokeResult.error || null
        }
      }
    }), revokeResult.ok ? 200 : revokeResult.httpStatus || 500);
  }
  const clientContext = await requireLicenseClientContext(env, slug, licenseId, status, mode);
  if (!clientContext.ok) {
    return json(operatorResult(mode, mutationMode, clientContext.resultCode, {
      ok: false,
      status: clientContext.status,
      safeToMutate: false,
      safeToMutateReason: clientContext.operatorMessage,
      safeToMutateChecks: {
        adminToken: "validated_server_side",
        confirmation: true,
        clientContext: "missing",
        licenseAssignmentOrSetupBundle: "missing"
      },
      operatorMessage: clientContext.operatorMessage,
      nextStep: clientContext.nextStep,
      latencyMs: Date.now() - started,
      extra: { tenantSlug: slug, licenseId }
    }), 409);
  }
  const result = await upsertLicense(env, slug, licenseId, status, body.plan || PLAN, validUntil);
  await recordAudit(env, slug, `license.${mode}`, { licenseId, status, reason: body.reason || null });
  return json(operatorResult(mode, mutationMode, result.ok ? resultCode : result.status, {
    ok: result.ok,
    status: result.ok ? status : result.status,
    safeToMutate: result.ok,
    safeToMutateReason: result.ok ? "Confirmed operation gates passed and Cloud License Database mutation completed." : "Cloud License Database mutation failed.",
    safeToMutateChecks: {
      adminToken: "validated_server_side",
      confirmation: true,
      revokePhrase: mode === "revoke" ? true : "not_required",
      reason: mode === "revoke" ? "present" : "not_required"
    },
    revokePhraseAccepted: mode === "revoke",
    operatorMessage: result.ok ? "Confirmed License Operation completed." : "Confirmed License Operation failed.",
    nextStep: result.ok ? "Review License Operation Audit and customer status." : "Inspect sanitized diagnostics.",
    latencyMs: Date.now() - started,
    extra: {
      tenantSlug: slug,
      licenseId,
      license: { licenseId, status, plan: body.plan || PLAN, validUntil, signedLicenseIssued: false }
    }
  }), result.ok ? 200 : 500);
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
  if (method === "GET" && url.pathname === "/api/customer/portal") return customerPortal(env, url);
  if (method === "GET" && url.pathname === "/api/customer/magic-link") return customerMagicLink(env, url);
  if (method === "POST" && url.pathname === "/api/customer/devices/claim") return claimCustomerDevice(request, env);
  if (method === "POST" && url.pathname === "/api/customer/devices/replacement/request") return requestDeviceReplacement(request, env);
  if (method === "POST" && url.pathname === "/api/admin/customer-devices/replacement/approve") return approveDeviceReplacement(request, env);
  if (method === "GET" && url.pathname === "/api/customer/license/status") return customerLicenseStatus(env, url);
  if (method === "POST" && url.pathname === "/api/customer/license/refresh") return customerLicenseRefresh(request, env);
  if (method === "POST" && url.pathname === "/api/licenses/activate") return activateLicense(request, env, "activate");
  if (method === "POST" && url.pathname === "/api/licenses/refresh") return activateLicense(request, env, "refresh");
  if (method === "POST" && url.pathname === "/api/licenses/revoke") return activateLicense(request, env, "revoke");
  if (method === "POST" && url.pathname === "/api/licenses/renew") return activateLicense(request, env, "renew");
  if (method === "POST" && url.pathname === "/api/licenses/commercial-state") return activateLicense(request, env, "commercial-state");
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
