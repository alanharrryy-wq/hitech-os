#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];

const paths = {
  contract: path.join(root, "shared/contracts/sync-event-contract.v1.json"),
  sharedEvents: path.join(root, "shared/twin-kernel/src/sync/events.ts"),
  twinManifest: path.join(root, "shared/twin-kernel/src/data/twin-capability-manifest.ts"),
  tabletFactory: path.join(root, "products/tablet/app/src/server/pos-engine/event-factory.ts"),
  tabletConstants: path.join(root, "products/tablet/app/src/server/pos-engine/constants.ts"),
  tabletOutbox: path.join(root, "products/tablet/app/src/server/pos-outbox/index.ts"),
  pcContract: path.join(root, "products/pc/app/src/server/validators/sync-event-contract.ts"),
  pcBackofficeContract: path.join(root, "products/pc/app/src/lib/backoffice/event-contract.ts"),
  pcConflicts: path.join(root, "products/pc/app/src/lib/backoffice/conflicts.ts"),
  tabletEvents: path.join(root, "products/tablet/app/src/server/sync/events.ts"),
  pcEvents: path.join(root, "products/pc/app/src/server/sync/events.ts")
};

const docs = [
  path.join(root, "docs/contracts/EVENT_CONTRACT.md"),
  path.join(root, "docs/contracts/SYNC_RECONCILIATION_CONTRACT.md"),
  path.join(root, "shared/contracts/event-contract.md"),
  path.join(root, "shared/contracts/sync-contract.md")
];

const topics = [
  "sale.created","sale.completed","ticket.closed","stock.decremented",
  "inventory.low_stock_detected","sale.cancelled","sale.refunded",
  "cash.session.opened","cash.movement.recorded","shift.opened","shift.closed",
  "stock.adjusted","catalog.product.created","catalog.product.updated",
  "sync.event.sent","sync.event.failed","sync.conflict.detected",
  "sync.conflict.resolved","supplier.created","supplier.updated",
  "supplier.disabled","product.supplier.linked","product.supplier.unlinked",
  "product.supplier.updated"
];

const canonicalOutboxStates = ["pending","sent","failed","acked","conflict","dead_letter"];
const compatibilityOutboxStates = ["pending","sent","failed","acked","conflict"];
const lifecycleStates = [
  "created_local","queued","sent","received","validated","accepted","projected",
  "recognized_not_projected","reconciled","conflict","failed","dead_letter"
];

const compatibilityConflictCodes = [
  "product_discontinued","old_local_price","negative_stock","duplicate_event",
  "terminal_not_registered","sale_outside_shift","inconsistent_sequence",
  "invalid_schema","unknown_topic"
];
const transportConflictCodes = [
  "wrong_scope","payload_hash_mismatch","idempotency_payload_mismatch",
  "unsupported_event_version","unsupported_schema_version","stale_sequence",
  "batch_checksum_mismatch"
];
const canonicalConflictCodes = [...compatibilityConflictCodes, ...transportConflictCodes];

const compatibilityEnvelope = [
  "eventId","eventType","topic","idempotencyKey","businessId","terminalId",
  "actorId","source","occurredAt","payload","schemaVersion","correlationId"
];
const canonicalEnvelope = [
  "eventId","source","subject","eventType","topic","eventVersion","schemaVersion",
  "tenantId","customerId","businessId","storeId","terminalId","deviceId","actorId",
  "aggregateId","originRecordId","idempotencyKey","sequence","correlationId",
  "causationId","traceId","occurredAt","capturedAt","payloadHash","batchId",
  "batchChecksum","payload"
];
const requiredTransport = canonicalEnvelope.filter((field) => field !== "customerId");

const forbiddenCanonicalTopics = [
  "sync.conflict_detected","sync.conflict_resolved","catalog.updated",
  "stock.received","return.created","purchase_order.created",
  "replenishment.requested","audit.completed","sync.started","sync.succeeded",
  "sync.failed","outbox.enqueued","outbox.dispatched"
];

function fail(message) { failures.push(message); }
function read(file) {
  if (!fs.existsSync(file)) {
    fail(`missing file: ${path.relative(root, file)}`);
    return "";
  }
  return fs.readFileSync(file, "utf8");
}
function readJson(file) {
  try { return JSON.parse(read(file)); }
  catch (error) { fail(`invalid JSON ${path.relative(root, file)}: ${error.message}`); return {}; }
}
function compareExact(label, actual, expected) {
  const safe = Array.isArray(actual) ? actual : [];
  const missing = expected.filter((item) => !safe.includes(item));
  const extra = safe.filter((item) => !expected.includes(item));
  const orderMatches = safe.join("\n") === expected.join("\n");
  if (missing.length || extra.length || !orderMatches) {
    fail(`${label} drift. missing=${JSON.stringify(missing)} extra=${JSON.stringify(extra)} orderMatches=${orderMatches}`);
  }
}
function containsAll(label, actual, expected) {
  const safe = Array.isArray(actual) ? actual : [];
  const missing = expected.filter((item) => !safe.includes(item));
  if (missing.length) fail(`${label} missing=${JSON.stringify(missing)}`);
}
function stringArrayFromConst(source, constName) {
  const pattern = new RegExp(`export\\s+const\\s+${constName}\\s*=\\s*\\[([\\s\\S]*?)\\]\\s+as\\s+const`, "m");
  const match = source.match(pattern);
  return match ? [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]) : null;
}
function stringArrayAssignment(source, constName) {
  const pattern = new RegExp(`export\\s+const\\s+${constName}[^=]*=\\s*\\[([\\s\\S]*?)\\]\\s*;`, "m");
  const match = source.match(pattern);
  return match ? [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]) : null;
}
function constantsByPrefix(source, prefix) {
  return [...source.matchAll(new RegExp(`export\\s+const\\s+${prefix}[A-Z0-9_]+\\s*=\\s*"([^"]+)"`, "g"))].map((item) => item[1]);
}
function objectKeys(source, objectName) {
  const pattern = new RegExp(`export\\s+const\\s+${objectName}[^=]*=\\s*\\{([\\s\\S]*?)\\n\\};`, "m");
  const match = source.match(pattern);
  return match ? [...match[1].matchAll(/^\s{2}([a-z0-9_]+):\s*\{/gm)].map((item) => item[1]) : null;
}
function assertCanonicalTopics(label, values) {
  const extra = [...new Set(values)].filter((item) => !topics.includes(item));
  if (extra.length) fail(`${label} contains non-canonical topics: ${JSON.stringify(extra)}`);
  const forbidden = [...new Set(values)].filter((item) => forbiddenCanonicalTopics.includes(item));
  if (forbidden.length) fail(`${label} exposes deprecated aliases: ${JSON.stringify(forbidden)}`);
}

const contract = readJson(paths.contract);
if (contract.schemaVersion !== "1.1.0") fail(`contract schemaVersion must be 1.1.0, received ${contract.schemaVersion}`);
compareExact("contract.eventTopics", contract.eventTopics, topics);
compareExact("contract.outboxStates", contract.outboxStates, canonicalOutboxStates);
compareExact("contract.lifecycleStates", contract.lifecycleStates, lifecycleStates);
compareExact("contract.conflictCodes", contract.conflictCodes, canonicalConflictCodes);
compareExact("contract.envelopeFields", contract.envelopeFields, canonicalEnvelope);
compareExact("contract.requiredTransportFields", contract.requiredTransportFields, requiredTransport);
assertCanonicalTopics("contract.eventTopics", contract.eventTopics ?? []);

for (const alias of contract.deprecatedAliases ?? []) {
  if (!forbiddenCanonicalTopics.includes(alias.alias)) fail(`unknown deprecated alias: ${alias.alias}`);
  if (!topics.includes(alias.canonical)) fail(`deprecated alias ${alias.alias} maps to non-canonical ${alias.canonical}`);
}

const shared = read(paths.sharedEvents);
compareExact("shared SHARED_SYNC_EVENTS", stringArrayFromConst(shared, "SHARED_SYNC_EVENTS"), topics);
compareExact("shared SHARED_OUTBOX_STATES compatibility layer", stringArrayFromConst(shared, "SHARED_OUTBOX_STATES"), compatibilityOutboxStates);
compareExact("shared SHARED_SYNC_LIFECYCLE_STATES", stringArrayFromConst(shared, "SHARED_SYNC_LIFECYCLE_STATES"), lifecycleStates);
compareExact("shared SHARED_CONFLICT_CODES compatibility layer", stringArrayFromConst(shared, "SHARED_CONFLICT_CODES"), compatibilityConflictCodes);
compareExact("shared SHARED_EVENT_ENVELOPE_FIELDS compatibility layer", stringArrayFromConst(shared, "SHARED_EVENT_ENVELOPE_FIELDS"), compatibilityEnvelope);

const factory = read(paths.tabletFactory);
const factoryTopics = stringArrayFromConst(factory, "POS_ENGINE_EVENT_FACTORY_TOPICS") ?? [];
assertCanonicalTopics("Tablet event factory", factoryTopics);
for (const required of ["sale.created","sale.completed","ticket.closed","stock.decremented","inventory.low_stock_detected"]) {
  if (!factoryTopics.includes(required)) fail(`Tablet event factory missing ${required}`);
}

const constants = read(paths.tabletConstants);
assertCanonicalTopics("Tablet event constants", constantsByPrefix(constants, "POS_EVENT_").filter((item) => topics.includes(item)));
compareExact("Tablet outbox state constants", constantsByPrefix(constants, "OUTBOX_STATUS_"), compatibilityOutboxStates);

const outboxSource = read(paths.tabletOutbox);
const outboxArray = stringArrayFromConst(outboxSource, "OUTBOX_STATUSES") ?? [];
if (outboxArray.length && !outboxArray.some((item) => item.startsWith("OUTBOX_STATUS_"))) {
  compareExact("Tablet OUTBOX_STATUSES", outboxArray, compatibilityOutboxStates);
}

const pcContract = read(paths.pcContract);
compareExact("PC RECOGNIZED_SYNC_TOPICS", stringArrayFromConst(pcContract, "RECOGNIZED_SYNC_TOPICS"), topics);
compareExact("PC REQUIRED_SYNC_EVENT_FIELDS", stringArrayFromConst(pcContract, "REQUIRED_SYNC_EVENT_FIELDS"), requiredTransport);
containsAll("PC SYNC_CONFLICT_CATALOG transport extensions", objectKeys(pcContract, "SYNC_CONFLICT_CATALOG"), canonicalConflictCodes);
if (!read(paths.pcBackofficeContract).includes("REQUIRED_SYNC_EVENT_FIELDS")) {
  fail("PC backoffice event contract must wrap the server contract.");
}

compareExact("PC UI conflict compatibility catalog", objectKeys(read(paths.pcConflicts), "CONFLICT_CATALOG"), compatibilityConflictCodes);

const tabletEvents = stringArrayAssignment(read(paths.tabletEvents), "TABLET_SYNC_EVENTS") ?? [];
assertCanonicalTopics("Tablet sync event list", tabletEvents);
compareExact("PC sync event list", stringArrayAssignment(read(paths.pcEvents), "PC_SYNC_EVENTS"), topics);

const manifest = read(paths.twinManifest);
const manifestEvents = [
  ...[...manifest.matchAll(/"name":\s*"([^"]+)"/g)].map((item) => item[1]),
  ...[...manifest.matchAll(/"allowedEvents":\s*\[([\s\S]*?)\]/g)]
    .flatMap((match) => [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]))
];
assertCanonicalTopics("Twin capability manifest", manifestEvents);

for (const docPath of docs) {
  const doc = read(docPath);
  if (!doc.includes("shared/contracts/sync-event-contract.v1.json")) {
    fail(`${path.relative(root, docPath)} does not point to the machine-readable source.`);
  }
  for (const code of compatibilityConflictCodes) {
    if (!doc.includes(code)) fail(`${path.relative(root, docPath)} missing compatibility conflict code ${code}.`);
  }
}

if (failures.length) {
  console.error("PRISMA_SYNC_CONTRACT_GATE_01 failed");
  for (const message of failures) console.error(`- ${message}`);
  process.exit(1);
}

console.log("PRISMA_SYNC_CONTRACT_GATE_01 passed");
console.log(JSON.stringify({
  sourceOfTruth: path.relative(root, paths.contract),
  schemaVersion: contract.schemaVersion,
  eventTopics: topics.length,
  canonicalOutboxStates: canonicalOutboxStates.length,
  compatibilityOutboxStates: compatibilityOutboxStates.length,
  lifecycleStates: lifecycleStates.length,
  canonicalConflictCodes: canonicalConflictCodes.length,
  compatibilityConflictCodes: compatibilityConflictCodes.length,
  canonicalEnvelopeFields: canonicalEnvelope.length,
  requiredTransportFields: requiredTransport.length,
  compatibilityEnvelopeFields: compatibilityEnvelope.length
}, null, 2));
