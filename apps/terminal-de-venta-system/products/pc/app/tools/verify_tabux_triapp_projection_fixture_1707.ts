import fs from "node:fs";
import path from "node:path";
import { PrismaClient } from "../.generated/prisma-client";
import { projectAcceptedSyncEvent } from "../src/server/services/sync-projectors.service";

function requiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Required fixture environment variable is missing: ${name}`);
  return value;
}

const databaseUrl = requiredEnv("DATABASE_URL");
const envelopesPath = requiredEnv("TRIAPP_FIXTURE_ENVELOPES_PATH");
const reportPath = requiredEnv("TRIAPP_PC_FIXTURE_REPORT_PATH");

const BUSINESS_ID = "fixture-business";
const STORE_ID = "fixture-store";
const TERMINAL_ID = "fixture-terminal";
const ACTOR_ID = "fixture-operator";
const PRODUCT_A = "fixture-product-a";
const PRODUCT_B = "fixture-product-b";
const db = new PrismaClient({ datasources: { db: { url: databaseUrl } } });

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(`ASSERTION_FAILED: ${message}`);
}

async function run() {
  await db.business.create({ data: { id: BUSINESS_ID, name: "Fixture Business", currency: "MXN" } });
  await db.store.create({ data: { id: STORE_ID, businessId: BUSINESS_ID, code: "FIX", name: "Fixture Store" } });
  await db.terminal.create({ data: { id: TERMINAL_ID, businessId: BUSINESS_ID, storeId: STORE_ID, code: "PC-FIX", name: "Fixture PC Target" } });
  await db.product.createMany({
    data: [
      { id: PRODUCT_A, businessId: BUSINESS_ID, sku: "FIX-A", name: "Fixture A", category: "Fixture", priceCents: 1000, costCents: 200, stockOnHand: 10 },
      { id: PRODUCT_B, businessId: BUSINESS_ID, sku: "FIX-B", name: "Fixture B", category: "Fixture", priceCents: 800, costCents: 150, stockOnHand: 4 }
    ]
  });
  await db.user.create({ data: { id: ACTOR_ID, businessId: BUSINESS_ID, displayName: "Fixture Operator", status: "ACTIVE" } });

  const payload = JSON.parse(fs.readFileSync(envelopesPath, "utf8")) as { envelopes: Array<Record<string, any>> };
  const envelopes = payload.envelopes;
  const firstProjection = [] as Array<{ topic: string; status: string; diagnostics: string[] }>;
  for (const envelope of envelopes) {
    const result = await db.$transaction((tx) => projectAcceptedSyncEvent(tx, envelope as any));
    assert(result.status !== "conflict" && result.status !== "dead_letter", `${envelope.topic} first projection failed: ${result.diagnostics.join(",")}`);
    firstProjection.push({ topic: String(envelope.topic), status: result.status, diagnostics: result.diagnostics });
  }

  const replayProjection = [] as Array<{ topic: string; status: string; diagnostics: string[] }>;
  for (const envelope of envelopes) {
    const result = await db.$transaction((tx) => projectAcceptedSyncEvent(tx, envelope as any));
    assert(result.status === "reconciled", `${envelope.topic} replay must reconcile, got ${result.status}`);
    replayProjection.push({ topic: String(envelope.topic), status: result.status, diagnostics: result.diagnostics });
  }

  const productA = await db.product.findUniqueOrThrow({ where: { id: PRODUCT_A } });
  const counts = {
    cashSessions: await db.cashSession.count(),
    cashMovements: await db.cashMovement.count(),
    stockMovements: await db.stockMovement.count(),
    auditEvents: await db.auditEvent.count()
  };
  assert(productA.stockOnHand === 14, `PC projected stock must end at 14, got ${productA.stockOnHand}`);
  assert(counts.cashSessions === 1 && counts.cashMovements === 2, "PC cash projection counts must be exact");
  assert(counts.stockMovements === 3 && counts.auditEvents === 3, "PC inventory projection counts must be exact");

  const integrity = await db.$queryRawUnsafe<Array<Record<string, unknown>>>("PRAGMA integrity_check");
  const foreignKeys = await db.$queryRawUnsafe<Array<Record<string, unknown>>>("PRAGMA foreign_key_check");
  assert(String(Object.values(integrity[0] ?? {})[0]).toLowerCase() === "ok", "PC fixture integrity_check must be ok");
  assert(foreignKeys.length === 0, "PC fixture foreign_key_check must be empty");

  const report = {
    schemaVersion: "tabux.triapp-pc-projection-fixture.v1",
    generatedAt: new Date().toISOString(),
    status: "PASS",
    liveDataTouched: false,
    databaseUrl: "isolated-fixture-redacted",
    productAStockOnHand: productA.stockOnHand,
    counts,
    firstProjection,
    replayProjection,
    integrityCheck: integrity,
    foreignKeyViolations: foreignKeys
  };
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`, "utf8");
  console.log(`TABUX_TRIAPP_PC_PROJECTION_PASS events=${envelopes.length} stock=${productA.stockOnHand}`);
}

run()
  .finally(async () => {
    await db.$disconnect();
  })
  .catch((error) => {
    console.error(error);
    throw error;
  });
