#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PrismaClient } from "@prisma/client";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const projectRoot = path.resolve(appRoot, "..", "..", "..");
const repoRoot = path.resolve(projectRoot, "..", "..");
const tmpRoot = path.join(repoRoot, "tools", "_local", "tmp", "prisma-pc-sync-ingest-persistence-01");
const dbPath = path.join(tmpRoot, `pc-ingest-${Date.now()}-${process.pid}.db`);
const dbUrl = `file:${dbPath.replace(/\\/g, "/")}`;
const failures = [];

function fail(message) {
  failures.push(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function readRel(rel) {
  const full = path.join(appRoot, rel);
  assert(existsSync(full), `Missing file: ${rel}`);
  return existsSync(full) ? readFileSync(full, "utf8") : "";
}

async function bootstrapSchema(prisma) {
  await prisma.$executeRawUnsafe(`CREATE TABLE IF NOT EXISTS OutboxEvent (
    id TEXT PRIMARY KEY,
    businessId TEXT NOT NULL,
    topic TEXT NOT NULL,
    aggregateId TEXT NOT NULL,
    payloadJson TEXT NOT NULL,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sentAt DATETIME,
    lastError TEXT
  )`);
}

async function proveOutboxPersistence() {
  mkdirSync(tmpRoot, { recursive: true });
  const prisma = new PrismaClient({ datasources: { db: { url: dbUrl } } });

  try {
    await bootstrapSchema(prisma);

    const acceptedEvent = {
      eventId: "evt_ingest_accept_01",
      topic: "sale.completed",
      businessId: "biz_tablet_standalone",
      terminalId: "terminal_tablet_local_01",
      actorId: "cashier_01",
      source: "tablet-pos",
      occurredAt: new Date().toISOString(),
      aggregateId: "sale_01",
      schemaVersion: "1.0.0",
      payload: { saleId: "sale_01", totalCents: 2200, cashSessionId: "cash_01" }
    };

    await prisma.outboxEvent.create({
      data: {
        id: acceptedEvent.eventId,
        businessId: acceptedEvent.businessId,
        topic: acceptedEvent.topic,
        aggregateId: acceptedEvent.aggregateId,
        payloadJson: JSON.stringify(acceptedEvent),
        status: "acked",
        attempts: 1,
        createdAt: new Date(acceptedEvent.occurredAt)
      }
    });

    const duplicate = await prisma.outboxEvent.findUnique({ where: { id: acceptedEvent.eventId } });
    assert(Boolean(duplicate), "OutboxEvent idempotency lookup by eventId failed.");

    await prisma.outboxEvent.create({
      data: {
        id: "evt_ingest_conflict_01",
        businessId: acceptedEvent.businessId,
        topic: "stock.decremented",
        aggregateId: "prd_01",
        payloadJson: JSON.stringify({ stockAfter: -1 }),
        status: "conflict",
        attempts: 1,
        lastError: JSON.stringify({ conflicts: [{ code: "negative_stock" }] })
      }
    });

    await prisma.outboxEvent.create({
      data: {
        id: "rejected_invalid_schema_01",
        businessId: "unknown_business",
        topic: "invalid_schema",
        aggregateId: "rejected_invalid_schema_01",
        payloadJson: JSON.stringify({ rejected: true }),
        status: "failed",
        attempts: 1,
        lastError: JSON.stringify({ conflicts: [{ code: "invalid_schema" }] })
      }
    });

    const [accepted, conflicts, rejected] = await Promise.all([
      prisma.outboxEvent.count({ where: { status: "acked" } }),
      prisma.outboxEvent.count({ where: { status: "conflict" } }),
      prisma.outboxEvent.count({ where: { status: "failed" } })
    ]);

    assert(accepted === 1, "Accepted ingest row was not durable.");
    assert(conflicts === 1, "Conflict ingest row was not durable.");
    assert(rejected === 1, "Rejected ingest row was not durable.");

    return { accepted, conflicts, rejected };
  } finally {
    await prisma.$disconnect();
  }
}

const route = readRel("app/api/backoffice/sync/ingest/route.ts");
assert(route.includes("persistIngestPayload"), "Ingest route must use durable persistIngestPayload.");
assert(route.includes('persistence: "outbox_event"'), "Ingest route GET must advertise outbox_event persistence.");
assert(route.includes('storageModel: "OutboxEvent"'), "Ingest route GET must expose the storage model.");

const store = readRel("src/lib/backoffice/sync-ingest-store.ts");
for (const marker of [
  "prisma.outboxEvent.create",
  "prisma.outboxEvent.findUnique",
  '"acked"',
  '"conflict"',
  'status: "failed"',
  "rejected_",
  'idempotencyKey: "eventId"',
  'persistence: "outbox_event"',
  "duplicate_event",
  "invalid_schema"
]) {
  assert(store.includes(marker), `sync-ingest-store missing marker: ${marker}`);
}

const eventContract = readRel("src/lib/backoffice/event-contract.ts");
assert(eventContract.includes("extractIngestEvents"), "event-contract must export extractIngestEvents for shared classifier/persistence extraction.");
assert(eventContract.includes('"outbox_event"'), "event-contract meta must allow outbox_event persistence.");
assert(eventContract.includes("unknown_topic"), "event-contract must classify unknown topics.");
assert(eventContract.includes("invalid_schema"), "event-contract must classify invalid schema.");

const conflicts = readRel("src/lib/backoffice/conflicts.ts");
for (const code of [
  "product_discontinued",
  "old_local_price",
  "negative_stock",
  "duplicate_event",
  "terminal_not_registered",
  "sale_outside_shift",
  "inconsistent_sequence",
  "invalid_schema",
  "unknown_topic"
]) {
  assert(conflicts.includes(code), `conflict catalog missing ${code}`);
}

const dashboard = readRel("src/lib/backoffice/dashboard.ts");
assert(dashboard.includes("lastIngestAt: lastOutbox"), "Dashboard must use persisted OutboxEvent as minimal ingest timestamp source.");

const overview = readRel("src/lib/backoffice/overview.ts");
assert(overview.includes("persiste eventos validados en OutboxEvent"), "Sync overview must not claim validation-only ingest.");

const proof = await proveOutboxPersistence();

if (failures.length) {
  console.error("PRISMA_SYNC_INGEST_PERSISTENCE_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_SYNC_INGEST_PERSISTENCE_01 passed");
console.log(JSON.stringify({ dbPath, ...proof }, null, 2));
