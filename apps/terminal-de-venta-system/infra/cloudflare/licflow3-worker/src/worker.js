const SERVICE = "PRISMA LICFLOW3 Cloud Licensing Support Bridge";
const VERSION = "0.2.0-prisma-cloud-semilla-routing";
const TENANT = "prisma-original-customer";
const PLAN = "TABLET_PC_MANAGED";

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
  ["POST", `/api/admin/tenants/${TENANT}/notes`, "tenant_notes", true]
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
  return row || {
    licenseId: "pending-hosted-license",
    license_id: "pending-hosted-license",
    tenantSlug: slug,
    tenant_slug: slug,
    status: "pending_cloud_activation",
    plan: PLAN,
    activationStatus: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
    activation_status: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED"
  };
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
    activationStatus: row.activationStatus || row.activation_status || "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
    validUntil: row.validUntil || row.valid_until || null
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
    hostedCloudEvidence: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED"
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
      hostedCloudEvidence: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED"
    }
  };
}

async function snapshot(env, slug) {
  const [tenantPayload, devices, receipts, notes, events] = await Promise.all([
    tenantStatus(env, slug),
    all(env, "select device_id as deviceId, device_name as name, role, platform, status, created_at as createdAt from devices where tenant_slug = ? order by updated_at desc limit 50", [slug]),
    all(env, "select receipt_id as receiptId, kind, ok, created_at as createdAt from integration_receipts where tenant_slug = ? order by created_at desc limit 50", [slug]),
    all(env, "select note_id as id, text, source, created_at as createdAt from support_notes where tenant_slug = ? order by created_at desc limit 50", [slug]),
    all(env, "select event_id as id, event_type as type, created_at as createdAt from audit_events where tenant_slug = ? order by created_at desc limit 50", [slug])
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
    hostedCloudEvidence: "CLOUDFLARE_LIVE_EVIDENCE_REQUIRED",
    contract: CONTRACT_ENDPOINTS.map(([method, path, capability, mutatesCloud]) => ({ method, path, capability, mutatesCloud }))
  };
}

async function recordAudit(env, slug, eventType, payload) {
  const eventId = `${eventType}-${crypto.randomUUID()}`;
  await run(env, "insert into audit_events (event_id, tenant_slug, event_type, payload_json) values (?, ?, ?, ?)", [eventId, slug, eventType, JSON.stringify(payload || {})]);
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
  const result = await run(env, "insert or replace into licenses (license_id, tenant_slug, status, plan, activation_status, updated_at) values (?, ?, ?, ?, ?, ?)", [licenseId, slug, status, body.plan || PLAN, status, now()]);
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
  const result = await run(env, "insert or replace into devices (device_id, tenant_slug, device_name, role, platform, status, updated_at) values (?, ?, ?, ?, ?, ?, ?)", [deviceId, slug, body.deviceName || deviceId, body.role || "unknown", body.platform || "unknown", "registered", now()]);
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
  const result = await run(env, "insert or replace into integration_receipts (receipt_id, tenant_slug, kind, ok, payload_json) values (?, ?, ?, ?, ?)", [receiptId, slug, body.kind || "integration", body.ok ? 1 : 0, JSON.stringify(body.payload || {})]);
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
  const result = await run(env, "insert into support_notes (note_id, tenant_slug, text, source) values (?, ?, ?, ?)", [noteId, slug, text, body.source || "licflow3-worker"]);
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
