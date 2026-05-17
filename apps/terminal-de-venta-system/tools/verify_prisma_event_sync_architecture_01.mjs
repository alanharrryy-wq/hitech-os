#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];
const checks = [];

function rel(...parts) {
  return path.join(root, ...parts);
}

function read(...parts) {
  const full = rel(...parts);
  if (!fs.existsSync(full)) {
    failures.push(`Missing file: ${full}`);
    return "";
  }
  return fs.readFileSync(full, "utf8");
}

function readJson(...parts) {
  try {
    return JSON.parse(read(...parts));
  } catch (error) {
    failures.push(`Invalid JSON ${parts.join("/")}: ${error.message}`);
    return {};
  }
}

function check(name, condition, detail = "") {
  checks.push({ name, ok: Boolean(condition), detail });
  if (!condition) failures.push(`${name}${detail ? `: ${detail}` : ""}`);
}

const requiredDocs = [
  "PRISMA_DATA_FLOW_AND_AUTHORITY.md",
  "PRISMA_SYNC_STANDARD.md",
  "PRISMA_EVENT_CONTRACT.md",
  "PRISMA_DATABASE_AUTHORITY.md"
];

for (const doc of requiredDocs) {
  const content = read("docs", "prisma", doc);
  check(`doc exists ${doc}`, content.length > 200);
}

const contract = readJson("shared", "contracts", "sync-event-contract.v1.json");
for (const topic of ["sale.completed", "stock.decremented", "cash.session.opened", "cash.movement.recorded", "inventory.low_stock_detected"]) {
  check(`contract topic ${topic}`, contract.eventTopics?.includes(topic));
}
for (const state of ["created_local", "queued", "received", "validated", "accepted", "projected", "reconciled", "conflict", "failed", "dead_letter"]) {
  check(`contract lifecycle ${state}`, contract.lifecycleStates?.includes(state));
}
for (const field of ["eventId", "eventType", "topic", "idempotencyKey", "businessId", "terminalId", "payload", "occurredAt", "source", "schemaVersion"]) {
  check(`contract envelope ${field}`, contract.envelopeFields?.includes(field));
}

const schema = read("prisma", "schema.prisma");
for (const field of ["idempotencyKey", "lifecycleStatus", "receivedAt", "validatedAt", "acceptedAt", "projectedAt", "reconciledAt", "deadLetterAt", "diagnosticsJson"]) {
  check(`schema OutboxEvent field ${field}`, new RegExp(`model\\s+OutboxEvent[\\s\\S]*${field}`).test(schema));
}
for (const model of ["SyncAttempt", "SyncConflict", "DeviceHeartbeat", "SyncCheckpoint", "SyncOutboxStatusBucket", "DataSourceFreshness"]) {
  check(`schema real model ${model}`, new RegExp(`model\\s+${model}\\s+{`).test(schema));
}
for (const indexMarker of ["@@index([businessId, source", "@@index([businessId, deviceId", "@@index([businessId, status", "@@index([freshnessSeconds])"]) {
  check(`schema observability index marker ${indexMarker}`, schema.includes(indexMarker));
}

const migration = read("prisma", "migrations", "20260511000000_event_ledger_lifecycle", "migration.sql");
check("migration is additive", migration.includes('ALTER TABLE "OutboxEvent" ADD COLUMN') && !/DROP\s+TABLE|DELETE\s+FROM/i.test(migration));
const syncObservabilityMigration = read("prisma", "migrations", "20260512000100_sync_observability_tables", "migration.sql");
for (const table of ["SyncAttempt", "SyncConflict", "DeviceHeartbeat", "SyncCheckpoint", "SyncOutboxStatusBucket", "DataSourceFreshness"]) {
  check(`sync observability migration creates ${table}`, syncObservabilityMigration.includes(`CREATE TABLE IF NOT EXISTS "${table}"`) || syncObservabilityMigration.includes(`CREATE TABLE "${table}"`));
}
check("sync observability migration is additive-only", !/ALTER\s+TABLE\s+"OutboxEvent"|DROP\s+TABLE|DELETE\s+FROM/i.test(syncObservabilityMigration));

const tabletSaleRoute = read("products", "tablet", "app", "app", "api", "pos", "sales", "complete", "route.ts");
check("tablet sale route stays local", tabletSaleRoute.includes("posEngineRepository.completeLocalSale") && !tabletSaleRoute.includes("fetch("));

const tabletSchema = read("products", "tablet", "app", "prisma", "schema.prisma");
check("tablet OutboxEvent has idempotencyKey column", /model\s+OutboxEvent[\s\S]*idempotencyKey\s+String\?/.test(tabletSchema));
check("tablet OutboxEvent has businessId idempotencyKey index", tabletSchema.includes("@@index([businessId, idempotencyKey])"));
const tabletMigration = read("products", "tablet", "app", "prisma", "migrations", "20260512000200_outbox_idempotency_key", "migration.sql");
check("tablet idempotency migration adds column", tabletMigration.includes('ADD COLUMN "idempotencyKey"'));

const tabletEventFactory = read("products", "tablet", "app", "src", "server", "pos-engine", "event-factory.ts");
for (const token of ["idempotencyKey", "eventType", "correlationId", "lines: result.lines.map", "stock.decremented"]) {
  check(`tablet event factory ${token}`, tabletEventFactory.includes(token));
}

const tabletShiftRepo = read("products", "tablet", "app", "src", "server", "pos-shift", "repository.prisma.ts");
check("tablet emits cash session event", tabletShiftRepo.includes("POS_EVENT_CASH_SESSION_OPENED"));
check("tablet emits cash movement event", tabletShiftRepo.includes("POS_EVENT_CASH_MOVEMENT_RECORDED"));

const pcIngest = read("products", "pc", "app", "src", "server", "services", "sync-ingest.service.ts");
for (const token of ["$transaction", "projectAcceptedSyncEvent", "recordSyncObservability", "lifecycleStatus", "idempotencyKey", "ALREADY_PROCESSED", "reconciledAt", "deadLetterAt", "diagnosticsJson"]) {
  check(`pc ingest ${token}`, pcIngest.includes(token));
}

const pcProjectors = read("products", "pc", "app", "src", "server", "services", "sync-projectors.service.ts");
for (const token of ["projectSaleCompleted", "projectStockDecremented", "projectCashSessionOpened", "projectCashMovementRecorded", "projectLowStockDetected"]) {
  check(`pc projector ${token}`, pcProjectors.includes(token));
}
for (const token of ["tx.sale.create", "tx.stockMovement.create", "tx.cashSession.create", "tx.cashMovement.create", "tx.replenishmentSignal.create"]) {
  check(`pc projector uses Prisma ${token}`, pcProjectors.includes(token));
}
const projectorRawSqlMatch = pcProjectors.match(/\$(?:queryRaw|executeRaw)|\bON\s+CONFLICT\b/i);
check("pc projectors avoid raw SQL", !projectorRawSqlMatch, projectorRawSqlMatch?.[0] ?? "");
check("pc projectors conflict duplicate sale", pcProjectors.includes("SALE_DUPLICATE_MISMATCH"));
check("pc projectors conflict negative stock", pcProjectors.includes("STOCK_NEGATIVE_TRANSITION"));
check("pc projectors conflict cash overlap", pcProjectors.includes("CASH_SESSION_OVERLAP"));

const pcBackofficeStore = read("products", "pc", "app", "src", "lib", "backoffice", "sync-ingest-store.ts");
check("backoffice ingest wraps server pipeline", pcBackofficeStore.includes("persistSyncIngestPayload"));
const pcObservabilityService = read("products", "pc", "app", "src", "server", "services", "sync-observability.service.ts");
check("pc observability records conflicts", pcObservabilityService.includes("recordSyncConflicts"));
for (const token of ["syncAttempt", "syncConflict", "syncCheckpoint", "syncOutboxStatusBucket", "dataSourceFreshness"]) {
  check(`pc observability writes ${token}`, pcObservabilityService.includes(token));
}

const bridge = read("tools", "prisma", "tri_db_bridge.py");
for (const token of ["rescue/backfill/diagnostic", "not the primary PRISMA sync path", "compat-acked", "governance_reconciled"]) {
  check(`bridge secondary wording ${token}`, bridge.includes(token));
}
check("bridge filters partial unique indexes", bridge.includes("is_partial") && bridge.includes("not is_partial"));

const mobileRoute = read("products", "mobile", "app", "app", "api", "mobile", "snapshot", "route.ts");
check("mobile snapshot king endpoint", mobileRoute.includes("mobileDataPlaneSnapshotJson"));

const mobileTypes = read("products", "mobile", "app", "src", "lib", "prisma-app", "mobile-data-plane", "types.ts");
for (const mode of ["live", "partial", "offline", "stale", "unknown", "demo-disabled"]) {
  check(`mobile runtime mode ${mode}`, mobileTypes.includes(`"${mode}"`));
}

const mobileNavigator = read("products", "mobile", "app", "src", "components", "prisma-app", "PrismaMobilePremiumNavigator.tsx");
check("mobile sales chart consumes chart view model", mobileNavigator.includes('chartKey === "sales-rhythm-hourly"') && mobileNavigator.includes("PrismaMobileSalesChart chart="));

const mobileAlertEngine = read("products", "mobile", "app", "src", "lib", "prisma-app", "mobile-intelligence", "alert-engine.ts");
check("mobile critical/high require evidence", mobileAlertEngine.includes('draft.severity === "critical"') && mobileAlertEngine.includes("hasEvidence"));
check("mobile alerts dedupe", mobileAlertEngine.includes("dedupeAlerts"));

const dbDoc = read("docs", "prisma", "PRISMA_DATABASE_AUTHORITY.md");
check("spreadsheet/access classified child only", /Excel, CSV, XLSX, Access/.test(dbDoc) && dbDoc.includes("child/support artifacts only"));
check("raw SQL exceptions documented", dbDoc.includes("Raw SQL Exceptions"));

if (failures.length) {
  console.error("PRISMA_EVENT_SYNC_ARCHITECTURE_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  console.error(JSON.stringify({ checks }, null, 2));
  process.exit(1);
}

console.log("PRISMA_EVENT_SYNC_ARCHITECTURE_01 passed");
console.log(JSON.stringify({ root, checks: checks.length, checkedAt: new Date().toISOString() }, null, 2));
