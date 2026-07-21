#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];
const checks = [];

function read(rel) {
  const full = path.join(root, rel);
  const exists = fs.existsSync(full);
  checks.push({ name: `exists:${rel}`, ok: exists });
  if (!exists) failures.push(`missing ${rel}`);
  return exists ? fs.readFileSync(full, "utf8") : "";
}
function check(name, condition, detail = "") {
  checks.push({ name, ok: Boolean(condition), detail });
  if (!condition) failures.push(`${name}${detail ? `: ${detail}` : ""}`);
}

const contractText = read("shared/contracts/sync-event-contract.v1.json");
let contract = {};
try { contract = JSON.parse(contractText); }
catch (error) { failures.push(`invalid sync-event-contract.v1.json: ${error.message}`); }

const requiredEnvelope = [
  "eventId","source","subject","eventType","topic","eventVersion","schemaVersion",
  "tenantId","businessId","storeId","terminalId","deviceId","actorId","aggregateId",
  "originRecordId","idempotencyKey","sequence","correlationId","causationId","traceId",
  "occurredAt","capturedAt","payloadHash","batchId","batchChecksum","payload"
];
for (const field of requiredEnvelope) {
  check(`contract envelope ${field}`, contract.envelopeFields?.includes(field));
}

const validator = read("products/pc/app/src/server/validators/sync-event-contract.ts");
for (const token of [
  "SUPPORTED_SYNC_EVENT_VERSIONS","normalizeSyncTimestamp","payload_hash_mismatch",
  "idempotency_payload_mismatch","wrong_scope","batch_checksum_mismatch"
]) {
  check(`validator token ${token}`, validator.includes(token));
}
check(
  "validator materializes normalized sequence",
  /sequence\s*:\s*sequence\s*\?\?\s*0/.test(validator)
);
check(
  "validator materializes device identity",
  /const\s+deviceId\s*=\s*asString\(input\.deviceId\)/.test(validator) &&
  /(?:^|\n)\s*deviceId,\s*(?:\n|$)/m.test(validator)
);

const dispatcher = read("products/tablet/app/src/server/sync/dispatcher.ts");
for (const token of [
  "batchChecksum","payloadHash","tenantId","storeId","deviceId","sequenceFor",
  "SyncScopeError",'const cleanDispatch = response.status === 200',
  'reason: cleanDispatch ? "dispatched" : response.ok ? "partial"'
]) {
  check(`dispatcher token ${token}`, dispatcher.includes(token));
}

const route = read("products/pc/app/app/api/backoffice/sync/ingest/route.ts");
check("route uses persistIngestPayload", route.includes("persistIngestPayload"));
check("route does not bypass store wrapper", !route.includes("persistSyncIngestPayload"));

const ingest = read("products/pc/app/src/server/services/sync-ingest.service.ts");
for (const token of [
  "batchValidationErrors","batch_checksum_mismatch","storedPayloadHash",
  "IDEMPOTENCY_PAYLOAD_MISMATCH","sequenceConflict","stale_sequence",
  "canonicalProjectionSource"
]) {
  check(`ingest token ${token}`, ingest.includes(token));
}

const observability = read("products/pc/app/src/server/services/sync-observability.service.ts");
for (const token of [
  "shouldAdvanceCheckpoint","cursorValue: String(event.sequence)","event.deviceId",
  "recordDeviceHeartbeat","deviceHeartbeat"
]) {
  check(`observability token ${token}`, observability.includes(token));
}

const projectors = read("products/pc/app/src/server/services/sync-projectors.service.ts");
check("projector validates event.storeId", projectors.includes("terminal.storeId !== event.storeId"));

const eventFactory = read("products/tablet/app/src/server/pos-engine/event-factory.ts");
for (const token of [
  "eventVersion","tenantId","storeId","deviceId","originRecordId","sequenceFor",
  "payloadHash","capturedAt"
]) {
  check(`event factory token ${token}`, eventFactory.includes(token));
}

const shift = read("products/tablet/app/src/server/pos-shift/repository.prisma.ts");
check("cash session event emitted", shift.includes("POS_EVENT_CASH_SESSION_OPENED"));
check("cash movement event emitted", shift.includes("POS_EVENT_CASH_MOVEMENT_RECORDED"));

const returns = read("products/tablet/app/src/server/pos-api/returns.prisma.ts");
check("return eventType canonical token", returns.includes("eventType: topic"));
check("return topic canonical", returns.includes('const topic = "sale.refunded"'));

const closure = read("docs/prisma/PRISMA_SYNC_CLOSURE_PATCH_20260518.md");
check("closure does not fake production", closure.includes("BLOCKED_REAL_MULTI_DEVICE_EVIDENCE_NOT_AVAILABLE"));
check("closure preserves Support Resolver exclusion", closure.includes("Support Resolver remains excluded"));

const sourceOnly = [
  validator, dispatcher, route, ingest, observability, projectors, eventFactory, shift, returns
].join("\n");
check(
  "no CSS important declaration in target source",
  !/!\s*important\s*;?/i.test(sourceOnly)
);
check(
  "no Support Resolver source ownership",
  !/Prisma Cloud Ctr|support_resolver_api|support_resolver_core/.test(sourceOnly)
);

const result = {
  ok: failures.length === 0,
  status: failures.length ? "FAIL" : "PASS",
  checks,
  failures,
  checkedAt: new Date().toISOString()
};
console.log(JSON.stringify(result, null, 2));
if (failures.length) process.exit(1);
console.log("PRISMA_SYNC_DEFINITIVE_FIX_1607 passed");
