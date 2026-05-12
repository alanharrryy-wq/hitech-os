#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const projectRoot = path.resolve(appRoot, "..", "..", "..");
const failures = [];
const checks = [];
const requiredModels = ["SyncAttempt", "SyncConflict", "DeviceHeartbeat", "SyncCheckpoint", "SyncOutboxStatusBucket", "DataSourceFreshness"];

function check(name, condition, detail = "") {
  checks.push({ name, ok: Boolean(condition), detail });
  if (!condition) failures.push(`${name}${detail ? `: ${detail}` : ""}`);
}

function readRel(root, rel) {
  const full = path.join(root, rel);
  check(`file exists ${rel}`, existsSync(full), full);
  return existsSync(full) ? readFileSync(full, "utf8") : "";
}

const rootSchema = readRel(projectRoot, "prisma/schema.prisma");
const migration = readRel(projectRoot, "prisma/migrations/20260512000100_sync_observability_tables/migration.sql");
const ingest = readRel(appRoot, "src/server/services/sync-ingest.service.ts");
const observability = readRel(appRoot, "src/server/services/sync-observability.service.ts");
const backofficeStore = readRel(appRoot, "src/lib/backoffice/sync-ingest-store.ts");
const route = readRel(appRoot, "app/api/backoffice/sync/ingest/route.ts");

check("route uses durable persistIngestPayload", route.includes("persistIngestPayload"));
check("backoffice ingest wraps server pipeline", backofficeStore.includes("persistSyncIngestPayload"));
for (const marker of ["findExistingEvent", "idempotencyKey", "ALREADY_PROCESSED", "recordSyncObservability", "duplicateResult"]) {
  check(`ingest marker ${marker}`, ingest.includes(marker));
}
for (const model of requiredModels) {
  check(`root schema model ${model}`, rootSchema.includes(`model ${model}`));
  check(`migration creates ${model}`, migration.includes(`"${model}"`));
}
for (const delegate of ["syncAttempt", "syncConflict", "syncCheckpoint", "syncOutboxStatusBucket", "dataSourceFreshness"]) {
  check(`observability writes ${delegate}`, observability.includes(delegate));
}
check("no future-table marker shortcut", !/futureTables|missingFutureTables/.test(observability + ingest));
check("OutboxEvent idempotency remains logical index", rootSchema.includes("@@index([businessId, idempotencyKey])") && !rootSchema.includes("@@unique([businessId, idempotencyKey])"));

if (failures.length) {
  console.error("PRISMA_SYNC_INGEST_PERSISTENCE_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  console.error(JSON.stringify({ checks }, null, 2));
  process.exit(1);
}

console.log("PRISMA_SYNC_INGEST_PERSISTENCE_01 passed");
console.log(JSON.stringify({ appRoot, projectRoot, checks: checks.length, checkedAt: new Date().toISOString() }, null, 2));
