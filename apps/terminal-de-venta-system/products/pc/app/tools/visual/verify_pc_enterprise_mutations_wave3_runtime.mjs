#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

function parseArgs(argv) {
  const out = {};
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith("--")) continue;
    out[key.slice(2)] = argv[i + 1];
    i += 1;
  }
  return out;
}

const args = parseArgs(process.argv);
const baseUrl = String(args["base-url"] || "http://127.0.0.1:3130").replace(/\/$/, "");
const outDir = path.resolve(args.out || "artifacts/pc-wave3");
const retryEventId = String(process.env.PRISMA_WAVE3_RETRY_EVENT_ID || "").trim();
fs.mkdirSync(outDir, { recursive: true });

const assertions = [];
const journeys = [];

function assert(name, condition, detail = null) {
  const row = { name, pass: Boolean(condition), detail };
  assertions.push(row);
  if (!condition) {
    const error = new Error(`ASSERTION_FAILED: ${name}${detail ? ` :: ${JSON.stringify(detail)}` : ""}`);
    error.assertion = row;
    throw error;
  }
}

async function requestJson(urlPath, options = {}, expectedStatus = 200) {
  const started = Date.now();
  const response = await fetch(`${baseUrl}${urlPath}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      ...(options.headers || {})
    }
  });
  const text = await response.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text.slice(0, 600) }; }
  journeys.push({ method: options.method || "GET", path: urlPath, status: response.status, elapsedMs: Date.now() - started });
  assert(`${options.method || "GET"} ${urlPath} status ${expectedStatus}`, response.status === expectedStatus, { status: response.status, body: json });
  if (expectedStatus >= 200 && expectedStatus < 300) assert(`${options.method || "GET"} ${urlPath} ok`, json?.ok === true, json);
  return json;
}

function body(value) {
  return JSON.stringify(value);
}

const ids = {};
const expected = {};
let settingsBefore = null;
let failure = null;

try {
  assert("retry event id injected by isolated runner", retryEventId.length > 0, { retryEventId });

  const catalogCreate = await requestJson("/api/backoffice/catalog/products", {
    method: "POST",
    body: body({ sku: "W3-CI-CRUD-001", name: "Wave 3 CRUD product", category: "CI", priceCents: 12500, costCents: 6100, stockOnHand: 0 })
  }, 201);
  ids.catalogProductId = catalogCreate.data.product.id;
  assert("catalog create returned id", Boolean(ids.catalogProductId));

  const catalogRead = await requestJson(`/api/backoffice/catalog/products/${encodeURIComponent(ids.catalogProductId)}`);
  assert("catalog read matches sku", catalogRead.data.product.sku === "W3-CI-CRUD-001", catalogRead.data.product);

  const catalogPatch = await requestJson(`/api/backoffice/catalog/products/${encodeURIComponent(ids.catalogProductId)}`, {
    method: "PATCH",
    body: body({ name: "Wave 3 CRUD product updated", priceCents: 13700 })
  });
  assert("catalog update durable response", catalogPatch.data.product.name === "Wave 3 CRUD product updated" && catalogPatch.data.product.priceCents === 13700, catalogPatch.data.product);

  const catalogReread = await requestJson(`/api/backoffice/catalog/products/${encodeURIComponent(ids.catalogProductId)}`);
  assert("catalog reread sees update", catalogReread.data.product.name === "Wave 3 CRUD product updated" && catalogReread.data.product.priceCents === 13700, catalogReread.data.product);

  const catalogDelete = await requestJson(`/api/backoffice/catalog/products/${encodeURIComponent(ids.catalogProductId)}`, { method: "DELETE" });
  assert("catalog delete acknowledged", catalogDelete.data.deleted === true, catalogDelete.data);
  await requestJson(`/api/backoffice/catalog/products/${encodeURIComponent(ids.catalogProductId)}`, {}, 404);

  const stockProduct = await requestJson("/api/backoffice/catalog/products", {
    method: "POST",
    body: body({ sku: "W3-CI-STOCK-001", name: "Wave 3 stock product", category: "CI", priceCents: 9900, costCents: 4200, stockOnHand: 10 })
  }, 201);
  ids.stockProductId = stockProduct.data.product.id;

  const adjustment = await requestJson("/api/backoffice/inventory/adjustments", {
    method: "POST",
    body: body({ productId: ids.stockProductId, delta: 5, reason: "Wave 3 isolated certification adjustment", location: "W3-CI" })
  }, 201);
  ids.stockMovementId = adjustment.data.adjustment.movement.id;
  ids.stockSnapshotId = adjustment.data.adjustment.snapshot.id;
  expected.stockOnHand = 15;
  expected.stockLocationOnHand = 15;
  assert("stock adjustment total", adjustment.data.adjustment.product.stockOnHand === 15, adjustment.data.adjustment);
  assert("stock adjustment location", adjustment.data.adjustment.snapshot.onHand === 15, adjustment.data.adjustment);
  assert("stock movement delta semantics", adjustment.data.adjustment.movement.movement === "adjust_up" && adjustment.data.adjustment.movement.qty === 5, adjustment.data.adjustment.movement);

  const supplierCreate = await requestJson("/api/backoffice/suppliers/records", {
    method: "POST",
    body: body({ name: "Wave 3 CI Supplier", status: "ACTIVE" })
  }, 201);
  ids.supplierId = supplierCreate.data.supplier.id;

  const supplierRead = await requestJson(`/api/backoffice/suppliers/records/${encodeURIComponent(ids.supplierId)}`);
  assert("supplier read matches name", supplierRead.data.supplier.name === "Wave 3 CI Supplier", supplierRead.data.supplier);

  const supplierPatch = await requestJson(`/api/backoffice/suppliers/records/${encodeURIComponent(ids.supplierId)}`, {
    method: "PATCH",
    body: body({ name: "Wave 3 CI Supplier Updated", status: "PAUSED" })
  });
  assert("supplier update response", supplierPatch.data.supplier.name === "Wave 3 CI Supplier Updated" && supplierPatch.data.supplier.status === "PAUSED", supplierPatch.data.supplier);

  const supplierReread = await requestJson(`/api/backoffice/suppliers/records/${encodeURIComponent(ids.supplierId)}`);
  assert("supplier reread sees update", supplierReread.data.supplier.name === "Wave 3 CI Supplier Updated" && supplierReread.data.supplier.status === "PAUSED", supplierReread.data.supplier);

  const supplierDelete = await requestJson(`/api/backoffice/suppliers/records/${encodeURIComponent(ids.supplierId)}`, { method: "DELETE" });
  assert("supplier delete acknowledged", supplierDelete.data.deleted === true, supplierDelete.data);
  await requestJson(`/api/backoffice/suppliers/records/${encodeURIComponent(ids.supplierId)}`, {}, 404);

  const countCreate = await requestJson("/api/backoffice/counts/records", {
    method: "POST",
    body: body({ location: "W3-CI", countedBy: "operator:wave3-ci", variance: 3, status: "open" })
  }, 201);
  ids.countId = countCreate.data.count.id;
  assert("count opens", countCreate.data.count.status === "open", countCreate.data.count);

  const countOpen = await requestJson(`/api/backoffice/counts/records/${encodeURIComponent(ids.countId)}`);
  assert("count reread open", countOpen.data.count.status === "open", countOpen.data.count);

  const countReview = await requestJson(`/api/backoffice/counts/records/${encodeURIComponent(ids.countId)}`, {
    method: "PATCH",
    body: body({ status: "review", variance: 1, countedBy: "operator:wave3-review" })
  });
  assert("count review transition", countReview.data.count.status === "review" && countReview.data.count.variance === 1, countReview.data.count);

  const countClose = await requestJson(`/api/backoffice/counts/records/${encodeURIComponent(ids.countId)}`, {
    method: "PATCH",
    body: body({ status: "closed", variance: 0 })
  });
  expected.countStatus = "closed";
  expected.countVariance = 0;
  assert("count close transition", countClose.data.count.status === "closed" && countClose.data.count.variance === 0, countClose.data.count);

  const countClosed = await requestJson(`/api/backoffice/counts/records/${encodeURIComponent(ids.countId)}`);
  assert("count reread closed", countClosed.data.count.status === "closed" && countClosed.data.count.variance === 0, countClosed.data.count);
  await requestJson(`/api/backoffice/counts/records/${encodeURIComponent(ids.countId)}`, {
    method: "PATCH",
    body: body({ variance: 2 })
  }, 409);

  const dispatch = await requestJson("/api/backoffice/sync/export-pc-to-tablet", {
    method: "POST",
    body: body({ mode: "delta", target: "tablet", limit: 250, requestedBy: "operator:wave3-ci" })
  });
  ids.syncDispatchAuditEventId = dispatch.data.auditEventId;
  assert("sync dispatch returns canonical audit id", Boolean(ids.syncDispatchAuditEventId), dispatch.data);
  assert("sync dispatch no fake ack metadata", dispatch.meta?.fakeAck === false && dispatch.meta?.owner === "catalog-delta-export.service", dispatch.meta);

  const replay = await requestJson("/api/backoffice/sync/retry", {
    method: "POST",
    body: body({ eventId: retryEventId, operatorNote: "Wave 3 isolated replay certification" })
  });
  ids.retryEventId = retryEventId;
  expected.retryStatus = "pending";
  expected.retryLifecycleStatus = "received";
  expected.retryAttempts = 2;
  assert("sync replay becomes pending", replay.data.status === "pending", replay.data);
  assert("sync replay lifecycle becomes received", replay.data.lifecycleStatus === "received", replay.data);
  assert("sync replay increments attempts", replay.data.attempts === 2, replay.data);

  ids.deviceId = "pc-wave3-ci-device";
  const deviceClaim = await requestJson("/api/backoffice/devices/claims", {
    method: "POST",
    body: body({ deviceId: ids.deviceId, deviceName: "PC Wave 3 CI", appVersion: "wave3-ci", runtimeMode: "managed", operatorLabel: "operator:wave3-ci" })
  }, 201);
  ids.deviceHeartbeatId = deviceClaim.data.device.id;
  assert("device claim status", deviceClaim.data.device.status === "claimed", deviceClaim.data.device);

  const deviceRead = await requestJson(`/api/backoffice/devices/claims?deviceId=${encodeURIComponent(ids.deviceId)}`);
  assert("device claim reread", deviceRead.data.device.status === "claimed" && deviceRead.data.device.id === ids.deviceHeartbeatId, deviceRead.data.device);

  const deviceRevoke = await requestJson("/api/backoffice/devices/claims", {
    method: "DELETE",
    body: body({ deviceId: ids.deviceId, reason: "Wave 3 isolated revoke certification" })
  });
  expected.deviceStatus = "revoked";
  assert("device revoke status", deviceRevoke.data.device.status === "revoked", deviceRevoke.data.device);

  const deviceRevokedRead = await requestJson(`/api/backoffice/devices/claims?deviceId=${encodeURIComponent(ids.deviceId)}`);
  assert("device revoke durable reread", deviceRevokedRead.data.device.status === "revoked" && deviceRevokedRead.data.device.health === "revoked", deviceRevokedRead.data.device);

  const settingsGet = await requestJson("/api/backoffice/settings/business");
  settingsBefore = settingsGet.data.settings;
  ids.businessId = settingsBefore.id;
  const settingsPatch = await requestJson("/api/backoffice/settings/business", {
    method: "PATCH",
    body: body({ name: "Hitech Wave 3 CI", taxId: "W3CI010101XX1", currency: "USD" })
  });
  expected.settings = { name: "Hitech Wave 3 CI", taxId: "W3CI010101XX1", currency: "USD" };
  assert("settings update response", settingsPatch.data.settings.name === expected.settings.name && settingsPatch.data.settings.taxId === expected.settings.taxId && settingsPatch.data.settings.currency === expected.settings.currency, settingsPatch.data.settings);

  const settingsReread = await requestJson("/api/backoffice/settings/business");
  assert("settings durable reread", settingsReread.data.settings.name === expected.settings.name && settingsReread.data.settings.taxId === expected.settings.taxId && settingsReread.data.settings.currency === expected.settings.currency, settingsReread.data.settings);
} catch (error) {
  failure = {
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : null,
    assertion: error?.assertion || null
  };
}

const passed = !failure && assertions.length > 0 && assertions.every((row) => row.pass);
const result = {
  schemaVersion: "prisma.pc-wave3.runtime-certification.v1",
  result: passed ? "PASS_PC_ENTERPRISE_MUTATIONS_WAVE3_RUNTIME" : "FAIL_PC_ENTERPRISE_MUTATIONS_WAVE3_RUNTIME",
  baseUrl,
  assertions: {
    total: assertions.length,
    passed: assertions.filter((row) => row.pass).length,
    failed: assertions.filter((row) => !row.pass).length,
    rows: assertions
  },
  journeys,
  ids,
  expected,
  settingsBefore,
  failure,
  noLiveDatabaseMutationClaimedByVerifier: true,
  productionCertified: false
};

const resultPath = path.join(outDir, "PC_WAVE3_RUNTIME_RESULT.json");
fs.writeFileSync(resultPath, `${JSON.stringify(result, null, 2)}\n`, "utf8");
console.log(JSON.stringify({ result: result.result, assertions: result.assertions, resultPath }, null, 2));
if (!passed) process.exit(1);
