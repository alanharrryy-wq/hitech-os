import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const contractPath = path.join(root, "shared", "contracts", "sync-event-contract.v1.json");
const sharedEventsPath = path.join(root, "shared", "twin-kernel", "src", "sync", "events.ts");
const twinManifestPath = path.join(root, "shared", "twin-kernel", "src", "data", "twin-capability-manifest.ts");
const tabletEventFactoryPath = path.join(root, "products", "tablet", "app", "src", "server", "pos-engine", "event-factory.ts");
const tabletConstantsPath = path.join(root, "products", "tablet", "app", "src", "server", "pos-engine", "constants.ts");
const tabletOutboxPath = path.join(root, "products", "tablet", "app", "src", "server", "pos-outbox", "index.ts");
const pcEventContractPath = path.join(root, "products", "pc", "app", "src", "lib", "backoffice", "event-contract.ts");
const pcConflictsPath = path.join(root, "products", "pc", "app", "src", "lib", "backoffice", "conflicts.ts");
const tabletSyncEventsPath = path.join(root, "products", "tablet", "app", "src", "server", "sync", "events.ts");
const pcSyncEventsPath = path.join(root, "products", "pc", "app", "src", "server", "sync", "events.ts");
const docsContractPaths = [
  path.join(root, "docs", "contracts", "EVENT_CONTRACT.md"),
  path.join(root, "docs", "contracts", "SYNC_RECONCILIATION_CONTRACT.md"),
  path.join(root, "shared", "contracts", "event-contract.md"),
  path.join(root, "shared", "contracts", "sync-contract.md")
];

const expectedTopics = [
  "sale.created",
  "sale.completed",
  "ticket.closed",
  "stock.decremented",
  "inventory.low_stock_detected",
  "sale.cancelled",
  "sale.refunded",
  "shift.opened",
  "shift.closed",
  "stock.adjusted",
  "catalog.product.created",
  "catalog.product.updated",
  "sync.event.sent",
  "sync.event.failed",
  "sync.conflict.detected",
  "sync.conflict.resolved"
];

const expectedOutboxStates = ["pending", "sent", "failed", "acked", "conflict"];
const expectedConflictCodes = [
  "product_discontinued",
  "old_local_price",
  "negative_stock",
  "duplicate_event",
  "terminal_not_registered",
  "sale_outside_shift",
  "inconsistent_sequence",
  "invalid_schema",
  "unknown_topic"
];
const expectedEnvelope = ["eventId", "topic", "businessId", "terminalId", "actorId", "source", "occurredAt", "payload", "schemaVersion"];
const forbiddenCanonicalTopics = [
  "sync.conflict_detected",
  "sync.conflict_resolved",
  "catalog.updated",
  "stock.received",
  "return.created",
  "purchase_order.created",
  "replenishment.requested",
  "audit.completed",
  "sync.started",
  "sync.succeeded",
  "sync.failed",
  "outbox.enqueued",
  "outbox.dispatched"
];

const failures = [];

function read(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function readJson(filePath) {
  return JSON.parse(read(filePath));
}

function pushFailure(message) {
  failures.push(message);
}

function sameSet(actual, expected) {
  return actual.length === expected.length && expected.every((item) => actual.includes(item));
}

function compareExact(label, actual, expected) {
  const missing = expected.filter((item) => !actual.includes(item));
  const extra = actual.filter((item) => !expected.includes(item));
  const orderMatches = actual.join("\n") === expected.join("\n");
  if (missing.length || extra.length || !orderMatches) {
    pushFailure(`${label} drift. missing=${JSON.stringify(missing)} extra=${JSON.stringify(extra)} orderMatches=${orderMatches}`);
  }
}

function stringArrayFromConst(source, constName) {
  const re = new RegExp(`export\\s+const\\s+${constName}\\s*=\\s*\\[([\\s\\S]*?)\\]\\s+as\\s+const`, "m");
  const match = source.match(re);
  if (!match) return null;
  return [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]);
}

function stringArrayAssignment(source, constName) {
  const re = new RegExp(`export\\s+const\\s+${constName}[^=]*=\\s*\\[([\\s\\S]*?)\\]\\s*;`, "m");
  const match = source.match(re);
  if (!match) return null;
  return [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]);
}

function constantsByPrefix(source, prefix) {
  return [...source.matchAll(new RegExp(`export\\s+const\\s+${prefix}[A-Z0-9_]+\\s*=\\s*"([^"]+)"`, "g"))].map((item) => item[1]);
}

function objectKeys(source, objectName) {
  const re = new RegExp(`export\\s+const\\s+${objectName}[^=]*=\\s*\\{([\\s\\S]*?)\\n\\};`, "m");
  const match = source.match(re);
  if (!match) return null;
  return [...match[1].matchAll(/^\s{2}([a-z0-9_]+):\s*\{/gm)].map((item) => item[1]);
}

function unique(values) {
  return [...new Set(values)];
}

function assertCanonicalOnly(label, values) {
  const extra = unique(values).filter((item) => !expectedTopics.includes(item));
  if (extra.length) {
    pushFailure(`${label} contains non-canonical event topics: ${JSON.stringify(extra)}`);
  }
}

function assertNoForbidden(label, values) {
  const forbidden = unique(values).filter((item) => forbiddenCanonicalTopics.includes(item));
  if (forbidden.length) {
    pushFailure(`${label} returned deprecated aliases as canonical: ${JSON.stringify(forbidden)}`);
  }
}

const contract = readJson(contractPath);
compareExact("contract.eventTopics", contract.eventTopics ?? [], expectedTopics);
compareExact("contract.outboxStates", contract.outboxStates ?? [], expectedOutboxStates);
compareExact("contract.conflictCodes", contract.conflictCodes ?? [], expectedConflictCodes);
compareExact("contract.envelopeFields", contract.envelopeFields ?? [], expectedEnvelope);
assertNoForbidden("contract.eventTopics", contract.eventTopics ?? []);

const aliases = contract.deprecatedAliases ?? [];
for (const alias of aliases) {
  if (!forbiddenCanonicalTopics.includes(alias.alias)) {
    pushFailure(`deprecated alias ${alias.alias} is not in the known drift list.`);
  }
  if (!expectedTopics.includes(alias.canonical)) {
    pushFailure(`deprecated alias ${alias.alias} maps to non-canonical ${alias.canonical}.`);
  }
}

const sharedSource = read(sharedEventsPath);
compareExact("shared/twin-kernel SHARED_SYNC_EVENTS", stringArrayFromConst(sharedSource, "SHARED_SYNC_EVENTS") ?? [], expectedTopics);
compareExact("shared/twin-kernel SHARED_OUTBOX_STATES", stringArrayFromConst(sharedSource, "SHARED_OUTBOX_STATES") ?? [], expectedOutboxStates);
compareExact("shared/twin-kernel SHARED_CONFLICT_CODES", stringArrayFromConst(sharedSource, "SHARED_CONFLICT_CODES") ?? [], expectedConflictCodes);
compareExact("shared/twin-kernel SHARED_EVENT_ENVELOPE_FIELDS", stringArrayFromConst(sharedSource, "SHARED_EVENT_ENVELOPE_FIELDS") ?? [], expectedEnvelope);

const tabletFactorySource = read(tabletEventFactoryPath);
const tabletFactoryTopics = stringArrayFromConst(tabletFactorySource, "POS_ENGINE_EVENT_FACTORY_TOPICS") ?? [];
assertCanonicalOnly("Tablet POS event factory", tabletFactoryTopics);
assertNoForbidden("Tablet POS event factory", tabletFactoryTopics);
for (const required of ["sale.created", "sale.completed", "ticket.closed", "stock.decremented", "inventory.low_stock_detected"]) {
  if (!tabletFactoryTopics.includes(required)) pushFailure(`Tablet POS event factory missing required emitted topic: ${required}`);
}

const tabletConstantsSource = read(tabletConstantsPath);
const tabletEventConstants = constantsByPrefix(tabletConstantsSource, "POS_EVENT_").filter((item) => expectedTopics.includes(item));
assertCanonicalOnly("Tablet POS event constants", tabletEventConstants);
assertNoForbidden("Tablet POS event constants", tabletEventConstants);

const tabletOutboxSource = read(tabletOutboxPath);
const outboxConstants = constantsByPrefix(tabletConstantsSource, "OUTBOX_STATUS_");
compareExact("Tablet outbox state constants", outboxConstants, expectedOutboxStates);
const outboxArray = stringArrayFromConst(tabletOutboxSource, "OUTBOX_STATUSES") ?? [];
if (outboxArray.length === 0 || outboxArray.some((item) => item.startsWith("OUTBOX_STATUS_"))) {
  for (const state of expectedOutboxStates) {
    if (!outboxConstants.includes(state)) pushFailure(`OUTBOX_STATUSES references constants but constants are missing state ${state}`);
  }
} else {
  compareExact("Tablet OUTBOX_STATUSES", outboxArray, expectedOutboxStates);
}

const pcEventSource = read(pcEventContractPath);
compareExact("PC RECOGNIZED_EVENT_TOPICS", stringArrayFromConst(pcEventSource, "RECOGNIZED_EVENT_TOPICS") ?? [], expectedTopics);
compareExact("PC REQUIRED_EVENT_FIELDS", stringArrayFromConst(pcEventSource, "REQUIRED_EVENT_FIELDS") ?? [], expectedEnvelope);

const pcConflictSource = read(pcConflictsPath);
compareExact("PC CONFLICT_CATALOG", objectKeys(pcConflictSource, "CONFLICT_CATALOG") ?? [], expectedConflictCodes);

const tabletSyncEvents = stringArrayAssignment(read(tabletSyncEventsPath), "TABLET_SYNC_EVENTS") ?? [];
assertCanonicalOnly("Tablet sync event list", tabletSyncEvents);
assertNoForbidden("Tablet sync event list", tabletSyncEvents);

const pcSyncEvents = stringArrayAssignment(read(pcSyncEventsPath), "PC_SYNC_EVENTS") ?? [];
compareExact("PC sync event list", pcSyncEvents, expectedTopics);

const twinManifestSource = read(twinManifestPath);
const manifestNamedEvents = [...twinManifestSource.matchAll(/"name":\s*"([^"]+)"/g)].map((item) => item[1]);
const manifestAllowedEvents = [...twinManifestSource.matchAll(/"allowedEvents":\s*\[([\s\S]*?)\]/g)]
  .flatMap((match) => [...match[1].matchAll(/"([^"]+)"/g)].map((item) => item[1]));
const manifestEventNames = [...manifestNamedEvents, ...manifestAllowedEvents];
assertCanonicalOnly("shared/twin-kernel capability manifest", manifestEventNames);
assertNoForbidden("shared/twin-kernel capability manifest", manifestEventNames);

for (const docPath of docsContractPaths) {
  const doc = read(docPath);
  if (!doc.includes("shared/contracts/sync-event-contract.v1.json")) {
    pushFailure(`${path.relative(root, docPath)} does not point at the canonical machine-readable source.`);
  }
  for (const code of expectedConflictCodes) {
    if (!doc.includes(code)) pushFailure(`${path.relative(root, docPath)} missing canonical conflict code ${code}.`);
  }
}

if (!sameSet(contract.eventTopics ?? [], expectedTopics)) {
  pushFailure("Contract topic set mismatch.");
}

if (failures.length) {
  console.error("PRISMA_SYNC_CONTRACT_GATE_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_SYNC_CONTRACT_GATE_01 passed");
console.log(JSON.stringify({
  sourceOfTruth: path.relative(root, contractPath),
  eventTopics: expectedTopics.length,
  outboxStates: expectedOutboxStates.length,
  conflictCodes: expectedConflictCodes.length,
  envelopeFields: expectedEnvelope.length
}, null, 2));
