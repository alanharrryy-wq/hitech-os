import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const mobileOrigin = process.env.SYNC_SENTINEL_MOBILE_ORIGIN;
const tabletOrigin = process.env.SYNC_SENTINEL_TABLET_ORIGIN;
const pcOrigin = process.env.SYNC_SENTINEL_PC_ORIGIN;
const controlToken = process.env.SYNC_SENTINEL_TOKEN;
const sessionSecret = process.env.SYNC_SENTINEL_MOBILE_SESSION_SECRET;
const output = process.env.SYNC_SENTINEL_MOBILE_OUTPUT;

if (!mobileOrigin || !tabletOrigin || !pcOrigin || !controlToken || !sessionSecret || !output) {
  throw new Error("SYNC_SENTINEL_MOBILE_RUNNER_ENV_MISSING");
}

const READ_PATH = "/api/mobile/v1/read-models/sync-source-health";
const PERMISSION = "RM.SYNC.SOURCE_HEALTH";
const ids = {
  tenantId: "tenant_sync_sentinel",
  customerId: "customer_sync_sentinel",
  businessId: "biz_sync_sentinel",
  branchId: "store_sync_sentinel",
  terminalId: "terminal_sync_sentinel",
  deviceId: "mobile_device_sync_sentinel",
  licenseId: "license_sync_sentinel",
  actorId: "sync-sentinel-mobile",
};

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`ASSERT:${message}`);
}

function basePayload(overrides: Record<string, unknown> = {}) {
  const now = Date.now();
  return {
    contractVersion: "PRISMA_MOBILE_SESSION_V1",
    sessionId: `session_mobile_sync_sentinel_${now}`,
    sessionVersion: 1,
    actorId: ids.actorId,
    roleIds: ["ROLE.MOBILE.OWNER"],
    permissionScopes: [PERMISSION],
    tenantId: ids.tenantId,
    businessId: ids.businessId,
    branchId: ids.branchId,
    terminalId: ids.terminalId,
    deviceId: ids.deviceId,
    licenseId: ids.licenseId,
    customerId: ids.customerId,
    businessName: "Sync Sentinel Mobile",
    planLabel: "Sentinel isolated",
    issuedAt: new Date(now - 1_000).toISOString(),
    expiresAt: new Date(now + 15 * 60_000).toISOString(),
    ...overrides,
  };
}

function sign(payload: Record<string, unknown>) {
  const payloadSegment = Buffer.from(JSON.stringify(payload), "utf8").toString("base64url");
  const signature = crypto.createHmac("sha256", sessionSecret).update(payloadSegment).digest("base64url");
  return `${payloadSegment}.${signature}`;
}

async function parseJson(response: Response) {
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch {
    return { __parseError: true, __text: text.slice(0, 500) };
  }
}

async function mobileRead(token: string | null) {
  const headers: Record<string, string> = { Accept: "application/json", "x-request-id": `sync-sentinel-${Date.now()}` };
  if (token) headers.authorization = `Bearer ${token}`;
  const response = await fetch(`${mobileOrigin}${READ_PATH}`, { headers, cache: "no-store" });
  return { status: response.status, body: await parseJson(response) };
}

async function control(origin: string, pathname: string, payload?: Record<string, unknown>) {
  const response = await fetch(`${origin}${pathname}`, {
    method: payload ? "POST" : "GET",
    headers: {
      Accept: "application/json",
      "content-type": "application/json",
      "x-sync-sentinel-token": controlToken,
    },
    body: payload ? JSON.stringify(payload) : undefined,
  });
  const parsed = await parseJson(response);
  assert(response.ok, `control ${pathname} failed ${response.status}: ${JSON.stringify(parsed)}`);
  return parsed;
}

function sources(envelope: any) {
  const rows = Array.isArray(envelope?.data?.sources) ? envelope.data.sources : [];
  return Object.fromEntries(rows.map((row: any) => [String(row.id), row]));
}

function outboxExpected(counts: any) {
  return {
    pending: Number(counts?.pending ?? 0) + Number(counts?.sent ?? 0) + Number(counts?.conflict ?? 0),
    failed: Number(counts?.failed ?? 0),
    acknowledged: Number(counts?.acked ?? 0),
  };
}

function assertEnvelopeScope(envelope: any, expected = ids) {
  assert(envelope?.ok === true, `Mobile envelope not ok: ${JSON.stringify(envelope)}`);
  assert(envelope?.meta?.readModelId === PERMISSION, `read model mismatch: ${envelope?.meta?.readModelId}`);
  assert(envelope?.meta?.sourceRuntime === "3140", `canonical Mobile runtime mismatch: ${envelope?.meta?.sourceRuntime}`);
  assert(envelope?.meta?.sourceOwner === "TABLET|PC", `source owner mismatch: ${envelope?.meta?.sourceOwner}`);
  assert(envelope?.meta?.sourceSystem === "PRISMA_GOVERNED_PROJECTION", `source system mismatch: ${envelope?.meta?.sourceSystem}`);
  assert(envelope?.meta?.tenantId === expected.tenantId, `tenant mismatch: ${envelope?.meta?.tenantId}`);
  assert(envelope?.meta?.businessId === expected.businessId, `business mismatch: ${envelope?.meta?.businessId}`);
  assert(envelope?.meta?.branchId === expected.branchId, `branch mismatch: ${envelope?.meta?.branchId}`);
  assert(envelope?.meta?.terminalId === expected.terminalId, `terminal mismatch: ${envelope?.meta?.terminalId}`);
  assert(envelope?.meta?.deviceId === expected.deviceId, `device mismatch: ${envelope?.meta?.deviceId}`);
  assert(envelope?.meta?.licenseId === expected.licenseId, `license mismatch: ${envelope?.meta?.licenseId}`);
  assert(envelope?.meta?.actorId === expected.actorId, `actor mismatch: ${envelope?.meta?.actorId}`);
  assert(envelope?.meta?.authorizationMode === "signed-session", `authorization mode mismatch: ${envelope?.meta?.authorizationMode}`);
  assert(envelope?.meta?.permissionScope === PERMISSION, `permission scope mismatch: ${envelope?.meta?.permissionScope}`);
}

async function waitForMobile(token: string) {
  const deadline = Date.now() + 120_000;
  let last: unknown = null;
  while (Date.now() < deadline) {
    try {
      const result = await mobileRead(token);
      last = result;
      if (result.status === 200 && result.body?.ok === true) return result;
    } catch (error) {
      last = error instanceof Error ? error.message : String(error);
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`MOBILE_RUNTIME_READINESS_TIMEOUT:${JSON.stringify(last)}`);
}

const result: any = {
  schemaVersion: "prisma.sync-sentinel.mobile-runtime.v1",
  startedAt: new Date().toISOString(),
  canonicalMobileRuntime: "3140",
  productionCertified: false,
  journeys: {},
  negativeFixtures: {},
  dispositions: {},
  timeline: [],
};

const cleanupEventIds = new Set<string>();
const validToken = sign(basePayload());

function passNegative(id: string, faultZone: string, evidence: Record<string, unknown>) {
  result.negativeFixtures[id] = { status: "PASS", faultZone, evidence };
}

try {
  await control(tabletOrigin, "/__sentinel/fault", { mode: "online" });
  await control(pcOrigin, "/__sentinel/fault", { mode: "online" });
  const ready = await waitForMobile(validToken);
  result.timeline.push({ stage: "MOBILE_RUNTIME_READY", status: "PASS", observedAt: new Date().toISOString() });

  // M1: real Mobile runtime read-side projection from the real Tablet/PC owners behind Sentinel loopback transports.
  const tabletBefore = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  const m1 = ready.status === 200 ? ready : await mobileRead(validToken);
  assert(m1.status === 200, `M1 HTTP status ${m1.status}`);
  assertEnvelopeScope(m1.body);
  const m1Sources = sources(m1.body);
  assert(m1Sources.tablet?.status === "ok", `M1 Tablet source not ok: ${JSON.stringify(m1Sources.tablet)}`);
  assert(m1Sources.pc?.status === "ok", `M1 PC source not ok: ${JSON.stringify(m1Sources.pc)}`);
  const expectedBefore = outboxExpected(tabletBefore.counts);
  assert(m1.body?.data?.outbox?.pending === expectedBefore.pending, `M1 pending mismatch ${m1.body?.data?.outbox?.pending} != ${expectedBefore.pending}`);
  assert(m1.body?.data?.outbox?.failed === expectedBefore.failed, `M1 failed mismatch`);
  assert(m1.body?.data?.outbox?.acknowledged === expectedBefore.acknowledged, `M1 ack mismatch`);
  result.journeys.M1 = {
    status: "PASS",
    path: "Tablet/PC owners -> Mobile data plane -> secure projection gateway -> Mobile runtime :3140 -> RM.SYNC.SOURCE_HEALTH",
    scope: {
      tenantId: m1.body.meta.tenantId,
      businessId: m1.body.meta.businessId,
      branchId: m1.body.meta.branchId,
      terminalId: m1.body.meta.terminalId,
      deviceId: m1.body.meta.deviceId,
      licenseId: m1.body.meta.licenseId,
      actorId: m1.body.meta.actorId,
    },
    sourceRuntime: m1.body.meta.sourceRuntime,
    sourceOwner: m1.body.meta.sourceOwner,
    outbox: m1.body.data.outbox,
    sources: m1.body.data.sources,
  };
  console.log("PASS_MOBILE_JOURNEY_M1");

  // M2: a canonical owner change must be observable later through Mobile, not simulated in Python.
  const m2Event = "event_mobile_sentinel_m2";
  cleanupEventIds.add(m2Event);
  await control(tabletOrigin, "/__sentinel/outbox-delete", { eventId: m2Event });
  const beforeM2 = await mobileRead(validToken);
  assert(beforeM2.status === 200, `M2 baseline HTTP ${beforeM2.status}`);
  await control(tabletOrigin, "/__sentinel/outbox-mutation", { eventId: m2Event, status: "pending", ageSeconds: 0 });
  const directAfter = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  const afterM2 = await mobileRead(validToken);
  assert(afterM2.status === 200, `M2 observed HTTP ${afterM2.status}`);
  assertEnvelopeScope(afterM2.body);
  const expectedAfter = outboxExpected(directAfter.counts);
  assert(afterM2.body?.data?.outbox?.pending === expectedAfter.pending, `M2 pending did not converge to owner state`);
  assert(afterM2.body?.data?.outbox?.pending > beforeM2.body?.data?.outbox?.pending, `M2 Mobile state did not change after owner mutation`);
  result.journeys.M2 = {
    status: "PASS",
    ownerChange: { eventId: m2Event, status: "pending" },
    beforePending: beforeM2.body.data.outbox.pending,
    directOwnerPending: expectedAfter.pending,
    observedMobilePending: afterM2.body.data.outbox.pending,
    sourceRuntime: afterM2.body.meta.sourceRuntime,
  };
  console.log("PASS_MOBILE_JOURNEY_M2");

  // M3 is intentionally not manufactured: current governed Phase 1 Mobile is read-only.
  result.journeys.M3 = {
    status: "NOT_APPLICABLE",
    reason: "mobile.secure_projection_gateway_phase1 is governed read-only; current source verifier reports commandPathsEnabled=false and no Mobile mutation owner is authorized",
    requiredFutureGate: "fresh Mobile mutation capability authority + separate owner contract before any mutating Sentinel journey",
  };
  result.dispositions.mobileMutation = "NOT_APPLICABLE";
  console.log("NOT_APPLICABLE_MOBILE_JOURNEY_M3");

  // N1: missing signed session.
  const n1 = await mobileRead(null);
  assert(n1.status === 401 && n1.body?.error?.code === "ERR.AUTH.REQUIRED", `N1 expected 401: ${JSON.stringify(n1)}`);
  passNegative("N1_MISSING_SESSION", "MOBILE_SESSION", { httpStatus: n1.status, code: n1.body?.error?.code });

  // N2: invalid signature/token.
  const n2 = await mobileRead("not-a-valid-mobile-session");
  assert(n2.status === 401 && n2.body?.error?.code === "ERR.AUTH.REQUIRED", `N2 expected 401`);
  passNegative("N2_INVALID_SESSION", "MOBILE_SESSION", { httpStatus: n2.status, code: n2.body?.error?.code });

  // N3: expired but correctly signed session.
  const expiredNow = Date.now();
  const n3 = await mobileRead(sign(basePayload({ issuedAt: new Date(expiredNow - 120_000).toISOString(), expiresAt: new Date(expiredNow - 60_000).toISOString() })));
  assert(n3.status === 401 && n3.body?.error?.code === "ERR.AUTH.REQUIRED", `N3 expected expired 401`);
  passNegative("N3_EXPIRED_SESSION", "MOBILE_SESSION", { httpStatus: n3.status, code: n3.body?.error?.code });

  // N4: signed session without read-model permission.
  const n4 = await mobileRead(sign(basePayload({ permissionScopes: ["RM.SYSTEM.SUMMARY"] })));
  assert(n4.status === 403 && n4.body?.error?.code === "ERR.PERMISSION.DENIED", `N4 expected permission 403`);
  passNegative("N4_UNAUTHORIZED_MODULE", "MOBILE_AUTHORIZATION", { httpStatus: n4.status, code: n4.body?.error?.code });

  // N5: malformed signed-session contract with the license field missing.
  const missingLicense = basePayload();
  delete (missingLicense as any).licenseId;
  const n5 = await mobileRead(sign(missingLicense));
  assert(n5.status === 401 && n5.body?.error?.code === "ERR.AUTH.REQUIRED", `N5 expected contract rejection`);
  passNegative("N5_MISSING_LICENSE_CONTRACT", "MOBILE_SESSION", { httpStatus: n5.status, code: n5.body?.error?.code });

  // N6: wrong tenant/business scope must not reveal the Sentinel business projection.
  const wrongScope = {
    ...ids,
    tenantId: "tenant_sync_sentinel_wrong",
    businessId: "biz_sync_sentinel_wrong",
  };
  const n6 = await mobileRead(sign(basePayload({ tenantId: wrongScope.tenantId, businessId: wrongScope.businessId })));
  assert(n6.status === 200, `N6 wrong-scope projection should remain a bounded empty read: ${n6.status}`);
  assertEnvelopeScope(n6.body, wrongScope);
  assert(Number(n6.body?.data?.outbox?.pending ?? -1) === 0, `N6 cross-business pending leakage`);
  assert(Number(n6.body?.data?.outbox?.failed ?? -1) === 0, `N6 cross-business failed leakage`);
  assert(Number(n6.body?.data?.outbox?.acknowledged ?? -1) === 0, `N6 cross-business ack leakage`);
  passNegative("N6_WRONG_TENANT_BUSINESS_SCOPE", "MOBILE_SCOPE", {
    httpStatus: n6.status,
    envelopeTenantId: n6.body.meta.tenantId,
    envelopeBusinessId: n6.body.meta.businessId,
    outbox: n6.body.data.outbox,
    boundary: "business isolation proven; tenant/business relationship validity remains issuer authority",
  });

  // N7: Tablet unavailable. Real Mobile HTTP retry must occur for the outbox role and no fake healthy Tablet source may appear.
  const beforeN7 = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  await control(tabletOrigin, "/__sentinel/fault", { mode: "unavailable" });
  const n7 = await mobileRead(validToken);
  const afterN7 = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  assert(n7.status === 200, `N7 Mobile response unavailable: ${n7.status}`);
  const n7Sources = sources(n7.body);
  assert(n7Sources.tablet?.status !== "ok", `N7 Tablet falsely healthy`);
  const beforeOutboxRequests = Number(beforeN7.requestCounts?.["/api/pos/events/outbox"] ?? 0);
  const afterOutboxRequests = Number(afterN7.requestCounts?.["/api/pos/events/outbox"] ?? 0);
  assert(afterOutboxRequests - beforeOutboxRequests >= 2, `N7 retry not observed: ${beforeOutboxRequests}->${afterOutboxRequests}`);
  passNegative("N7_TABLET_NETWORK_UNAVAILABLE_RETRY", "MOBILE_UPSTREAM_TABLET", {
    tabletStatus: n7Sources.tablet?.status,
    outboxAttempts: afterOutboxRequests - beforeOutboxRequests,
    freshnessState: n7.body?.meta?.freshnessState,
  });
  await control(tabletOrigin, "/__sentinel/fault", { mode: "online" });

  // N8: PC projection source unavailable.
  await control(pcOrigin, "/__sentinel/fault", { mode: "mobile_read_unavailable" });
  const n8 = await mobileRead(validToken);
  assert(n8.status === 200, `N8 Mobile response unavailable: ${n8.status}`);
  const n8Sources = sources(n8.body);
  assert(n8Sources.pc?.status !== "ok", `N8 PC falsely healthy`);
  passNegative("N8_PC_NETWORK_UNAVAILABLE", "MOBILE_UPSTREAM_PC", {
    pcStatus: n8Sources.pc?.status,
    freshnessState: n8.body?.meta?.freshnessState,
  });
  await control(pcOrigin, "/__sentinel/fault", { mode: "online" });

  // N9: both operational upstreams unavailable must never produce healthy/fresh evidence.
  await control(tabletOrigin, "/__sentinel/fault", { mode: "unavailable" });
  await control(pcOrigin, "/__sentinel/fault", { mode: "mobile_read_unavailable" });
  const n9 = await mobileRead(validToken);
  assert(n9.status === 200, `N9 Mobile envelope unavailable`);
  const n9Sources = sources(n9.body);
  assert(n9Sources.tablet?.status !== "ok" && n9Sources.pc?.status !== "ok", `N9 upstream false-green`);
  assert(n9.body?.meta?.freshnessState !== "STA.FRESH", `N9 false fresh projection`);
  assert(n9.body?.meta?.dataQuality !== "COMPLETE", `N9 false complete projection`);
  passNegative("N9_ALL_UPSTREAMS_UNAVAILABLE_FAIL_CLOSED", "MOBILE_DATA_PLANE", {
    tabletStatus: n9Sources.tablet?.status,
    pcStatus: n9Sources.pc?.status,
    freshnessState: n9.body?.meta?.freshnessState,
    dataQuality: n9.body?.meta?.dataQuality,
  });

  // N10: recovery after network failure.
  await control(tabletOrigin, "/__sentinel/fault", { mode: "online" });
  await control(pcOrigin, "/__sentinel/fault", { mode: "online" });
  const n10 = await mobileRead(validToken);
  const n10Sources = sources(n10.body);
  assert(n10.status === 200 && n10Sources.tablet?.status === "ok" && n10Sources.pc?.status === "ok", `N10 recovery not observed`);
  passNegative("N10_NETWORK_RECOVERY", "MOBILE_RECONCILIATION", {
    tabletStatus: n10Sources.tablet?.status,
    pcStatus: n10Sources.pc?.status,
    freshnessState: n10.body?.meta?.freshnessState,
  });

  // N11: stale projection is explicit, never healthy.
  const staleEvent = "event_mobile_sentinel_stale";
  cleanupEventIds.add(staleEvent);
  await control(tabletOrigin, "/__sentinel/outbox-mutation", { eventId: staleEvent, status: "pending", ageSeconds: 180 });
  const n11 = await mobileRead(validToken);
  assert(n11.status === 200, `N11 Mobile response unavailable`);
  assert(n11.body?.meta?.freshnessState === "STA.STALE", `N11 stale projection not classified: ${n11.body?.meta?.freshnessState}`);
  assert(n11.body?.meta?.dataQuality === "STALE", `N11 stale dataQuality missing: ${n11.body?.meta?.dataQuality}`);
  passNegative("N11_STALE_PROJECTION", "MOBILE_FRESHNESS", {
    freshnessState: n11.body.meta.freshnessState,
    dataQuality: n11.body.meta.dataQuality,
    oldestPendingAt: n11.body?.data?.outbox?.oldestPendingAt,
  });
  await control(tabletOrigin, "/__sentinel/outbox-delete", { eventId: staleEvent });
  cleanupEventIds.delete(staleEvent);

  // N12: malformed upstream payload passes through real fetch/parse path and must degrade quality rather than fake green.
  const beforeN12 = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  await control(tabletOrigin, "/__sentinel/fault", { mode: "malformed_outbox" });
  const n12 = await mobileRead(validToken);
  const afterN12 = await control(tabletOrigin, `/__sentinel/state?businessId=${encodeURIComponent(ids.businessId)}`);
  assert(n12.status === 200, `N12 Mobile response unavailable`);
  assert(Array.isArray(n12.body?.meta?.warnings) && n12.body.meta.warnings.length > 0, `N12 parse warning missing`);
  assert(n12.body?.meta?.dataQuality !== "COMPLETE", `N12 malformed upstream falsely complete`);
  const n12Attempts = Number(afterN12.requestCounts?.["/api/pos/events/outbox"] ?? 0) - Number(beforeN12.requestCounts?.["/api/pos/events/outbox"] ?? 0);
  assert(n12Attempts >= 2, `N12 malformed payload retry not observed`);
  passNegative("N12_MALFORMED_UPSTREAM_PAYLOAD", "MOBILE_PROJECTION", {
    dataQuality: n12.body.meta.dataQuality,
    freshnessState: n12.body.meta.freshnessState,
    warningCount: n12.body.meta.warnings.length,
    outboxAttempts: n12Attempts,
  });
  await control(tabletOrigin, "/__sentinel/fault", { mode: "online" });

  result.dispositions = {
    ...result.dispositions,
    wrongRoleDirectEnforcement: {
      status: "NOT_APPLICABLE",
      reason: "current Mobile gateway authorizes read models with permissionScopes; roleIds are signed context but are not a direct route authorization predicate",
    },
    arbitraryLicenseEntitlementLookup: {
      status: "EXTERNAL_REQUIRED",
      reason: "current Phase 1 gateway trusts the signed-session issuer for entitlement identity; malformed/missing license contract is verified here without inventing a live entitlement service",
    },
    mobileDuplicateAction: { status: "NOT_APPLICABLE", reason: "no governed Mobile command path" },
    mobileServerConflict: { status: "NOT_APPLICABLE", reason: "no governed Mobile command path" },
  };

  const failedNegatives = Object.entries(result.negativeFixtures).filter(([, value]: any) => value?.status !== "PASS");
  assert(failedNegatives.length === 0, `Mobile negatives incomplete: ${JSON.stringify(failedNegatives)}`);
  result.faultZones = [
    "MOBILE_RUNTIME",
    "MOBILE_SESSION",
    "MOBILE_AUTHORIZATION",
    "MOBILE_SCOPE",
    "MOBILE_UPSTREAM_TABLET",
    "MOBILE_UPSTREAM_PC",
    "MOBILE_DATA_PLANE",
    "MOBILE_PROJECTION",
    "MOBILE_FRESHNESS",
    "MOBILE_RECONCILIATION",
  ];
  result.ok = true;
  console.log("PASS_MOBILE_NEGATIVES");
} catch (error) {
  result.ok = false;
  result.error = error instanceof Error ? error.message : String(error);
  console.error(result.error);
  process.exitCode = 1;
} finally {
  try { await control(tabletOrigin, "/__sentinel/fault", { mode: "online" }); } catch {}
  try { await control(pcOrigin, "/__sentinel/fault", { mode: "online" }); } catch {}
  for (const eventId of cleanupEventIds) {
    try { await control(tabletOrigin, "/__sentinel/outbox-delete", { eventId }); } catch {}
  }
  result.finishedAt = new Date().toISOString();
  result.durationMs = Date.parse(result.finishedAt) - Date.parse(result.startedAt);
  result.truthMap = {
    M1: "TABLET|PC source owners -> Mobile data plane -> secure projection gateway -> Mobile canonical runtime 3140 -> RM.SYNC.SOURCE_HEALTH -> Mobile state",
    M2: "Tablet canonical outbox change -> Tablet owner read API -> Mobile data plane refresh -> Mobile canonical runtime 3140 -> changed RM.SYNC.SOURCE_HEALTH",
    M3: "NOT_APPLICABLE: governed Phase 1 is read-only",
  };
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.writeFileSync(output, JSON.stringify(result, null, 2), "utf8");
}
