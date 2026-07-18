import { prisma } from "../src/server/prisma/client";
import { applyCatalogDeltaEnvelope } from "../src/server/sync/catalog-pull";
import { CATALOG_DELTA_CONTRACT_ID, CATALOG_DELTA_SCHEMA_VERSION, CATALOG_DELTA_STREAM } from "@shared-kernel/sync/catalog-delta";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function bootstrap() {
  const ddl = [
    `CREATE TABLE "Business" ("id" TEXT NOT NULL PRIMARY KEY, "name" TEXT NOT NULL, "taxId" TEXT, "currency" TEXT NOT NULL DEFAULT 'MXN', "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "Product" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "sku" TEXT NOT NULL, "name" TEXT NOT NULL, "category" TEXT NOT NULL, "brandId" TEXT, "priceCents" INTEGER NOT NULL, "costCents" INTEGER NOT NULL, "stockOnHand" INTEGER NOT NULL DEFAULT 0, "taxRateId" TEXT, "mediaRef" TEXT, "isActive" BOOLEAN NOT NULL DEFAULT true, "createdAt" DATETIME NOT NULL, "updatedAt" DATETIME NOT NULL)`,
    `CREATE UNIQUE INDEX "Product_businessId_sku_key" ON "Product"("businessId", "sku")`,
    `CREATE TABLE "Barcode" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "productId" TEXT NOT NULL, "code" TEXT NOT NULL, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE UNIQUE INDEX "Barcode_businessId_code_key" ON "Barcode"("businessId", "code")`,
    `CREATE TABLE "ModifierGroup" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "name" TEXT NOT NULL, "minSelections" INTEGER NOT NULL DEFAULT 0, "maxSelections" INTEGER NOT NULL DEFAULT 1, "status" TEXT NOT NULL DEFAULT 'ACTIVE', "sortOrder" INTEGER NOT NULL DEFAULT 0, "version" INTEGER NOT NULL DEFAULT 1, "createdAt" DATETIME NOT NULL, "updatedAt" DATETIME NOT NULL)`,
    `CREATE TABLE "ModifierOption" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "modifierGroupId" TEXT NOT NULL, "name" TEXT NOT NULL, "priceDeltaCents" INTEGER NOT NULL DEFAULT 0, "isDefault" BOOLEAN NOT NULL DEFAULT false, "status" TEXT NOT NULL DEFAULT 'ACTIVE', "sortOrder" INTEGER NOT NULL DEFAULT 0, "version" INTEGER NOT NULL DEFAULT 1, "createdAt" DATETIME NOT NULL, "updatedAt" DATETIME NOT NULL)`,
    `CREATE TABLE "ProductModifierGroup" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "productId" TEXT NOT NULL, "modifierGroupId" TEXT NOT NULL, "required" BOOLEAN NOT NULL DEFAULT false, "sortOrder" INTEGER NOT NULL DEFAULT 0, "status" TEXT NOT NULL DEFAULT 'ACTIVE', "version" INTEGER NOT NULL DEFAULT 1, "createdAt" DATETIME NOT NULL, "updatedAt" DATETIME NOT NULL)`,
    `CREATE TABLE "SyncCheckpoint" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "source" TEXT NOT NULL, "scopeKey" TEXT NOT NULL, "deviceId" TEXT, "terminalId" TEXT, "stream" TEXT NOT NULL, "cursorValue" TEXT, "lastEventId" TEXT, "lastIdempotencyKey" TEXT, "lastAttemptId" TEXT, "status" TEXT NOT NULL, "lifecycleStatus" TEXT, "checkpointAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "lastAttemptedAt" DATETIME, "lastSuccessfulAt" DATETIME, "metadataJson" TEXT, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE UNIQUE INDEX "SyncCheckpoint_businessId_scopeKey_stream_key" ON "SyncCheckpoint"("businessId", "scopeKey", "stream")`
  ];
  for (const statement of ddl) await prisma.$executeRawUnsafe(statement);
}

async function main() {
  if (!process.env.TABLET_DATABASE_URL && !process.env.DATABASE_URL) throw new Error("PRODUCT_MODIFIERS_TABLET_DATABASE_URL_REQUIRED");
  await bootstrap();
  const businessId = "biz-modifier-tablet";
  const terminalId = "terminal-modifier-tablet";
  const at = "2026-07-17T14:00:00.000Z";
  const changes = [
    { entityType: "Product", entityId: "product-modifier", payload: { id: "product-modifier", businessId, sku: "MOD-001", name: "Bebida configurable", category: "Bebidas", priceCents: 4200, costCents: 1200, stockOnHand: 6, isActive: true, barcodes: [], createdAt: at, updatedAt: at } },
    { entityType: "ModifierGroup", entityId: "group-milk", payload: { id: "group-milk", businessId, name: "Tipo de leche", minSelections: 1, maxSelections: 1, status: "ACTIVE", sortOrder: 1, version: 1, createdAt: at, updatedAt: at } },
    { entityType: "ModifierOption", entityId: "option-oat", payload: { id: "option-oat", businessId, modifierGroupId: "group-milk", name: "Avena", priceDeltaCents: 800, isDefault: false, status: "ACTIVE", sortOrder: 1, version: 1, createdAt: at, updatedAt: at } },
    { entityType: "ProductModifierGroup", entityId: "link-product-milk", payload: { id: "link-product-milk", businessId, productId: "product-modifier", modifierGroupId: "group-milk", required: true, status: "ACTIVE", sortOrder: 1, version: 1, createdAt: at, updatedAt: at } }
  ].map((change, index) => ({
    ...change,
    changeId: `${CATALOG_DELTA_STREAM}:${change.entityType}:${change.entityId}:${at}`,
    businessId,
    operation: "upsert" as const,
    occurredAt: at,
    cursor: `${at}~${String(index + 4).padStart(2, "0")}~${change.entityId}`
  }));
  const envelope = {
    contractId: CATALOG_DELTA_CONTRACT_ID,
    schemaVersion: CATALOG_DELTA_SCHEMA_VERSION,
    stream: CATALOG_DELTA_STREAM,
    mode: "bootstrap" as const,
    businessId,
    generatedAt: at,
    scope: { businessId, terminalId, storeId: null, target: "tablet" },
    cursor: { requested: null, from: null, to: changes.at(-1)?.cursor ?? null, hasMore: false, checkpointStrategy: "updatedAt_entityRank_id" as const },
    changes,
    counts: { total: changes.length, byEntity: Object.fromEntries(changes.map((change) => [change.entityType, 1])) },
    diagnostics: { source: "pc-canonical-db" as const, validator: CATALOG_DELTA_CONTRACT_ID, ordering: "updatedAt_entityRank_id" as const, notes: ["modifier catalog projection fixture"] }
  };
  const result = await applyCatalogDeltaEnvelope(envelope, { mode: "bootstrap", targetBusinessId: businessId, terminalId, pcBusinessId: businessId });
  assert(result.ok && result.counts.applied === 4, "MODIFIER_CATALOG_DELTA_APPLY_FAILED");
  const rows = await prisma.$queryRawUnsafe<Array<{ groupName: string; optionName: string; priceDeltaCents: number; required: number }>>(
    `SELECT g."name" AS "groupName", o."name" AS "optionName", o."priceDeltaCents", l."required" FROM "ProductModifierGroup" l JOIN "ModifierGroup" g ON g."id" = l."modifierGroupId" JOIN "ModifierOption" o ON o."modifierGroupId" = g."id" WHERE l."businessId" = ? AND l."productId" = ?`,
    businessId,
    "product-modifier"
  );
  assert(rows[0]?.groupName === "Tipo de leche" && rows[0]?.optionName === "Avena" && rows[0]?.priceDeltaCents === 800 && Number(rows[0]?.required) === 1, "MODIFIER_CATALOG_PROJECTION_CONTENT_INVALID");
  console.log("product_modifiers_catalog_projection=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}).then(async () => {
  await prisma.$disconnect();
});
