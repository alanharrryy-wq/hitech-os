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
    `CREATE TABLE "SyncCheckpoint" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "source" TEXT NOT NULL, "scopeKey" TEXT NOT NULL, "deviceId" TEXT, "terminalId" TEXT, "stream" TEXT NOT NULL, "cursorValue" TEXT, "lastEventId" TEXT, "lastIdempotencyKey" TEXT, "lastAttemptId" TEXT, "status" TEXT NOT NULL, "lifecycleStatus" TEXT, "checkpointAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "lastAttemptedAt" DATETIME, "lastSuccessfulAt" DATETIME, "metadataJson" TEXT, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE UNIQUE INDEX "SyncCheckpoint_businessId_scopeKey_stream_key" ON "SyncCheckpoint"("businessId", "scopeKey", "stream")`
  ];
  for (const statement of ddl) await prisma.$executeRawUnsafe(statement);
}

async function main() {
  if (!process.env.TABLET_DATABASE_URL && !process.env.DATABASE_URL) throw new Error("PRODUCT_MEDIA_TABLET_DATABASE_URL_REQUIRED");
  await bootstrap();
  const businessId = "biz-media-tablet";
  const terminalId = "terminal-media-tablet";
  const at = "2026-07-17T12:30:00.000Z";
  const cursor = `${at}~03~product-media-tablet`;
  const envelope = {
    contractId: CATALOG_DELTA_CONTRACT_ID,
    schemaVersion: CATALOG_DELTA_SCHEMA_VERSION,
    stream: CATALOG_DELTA_STREAM,
    mode: "bootstrap" as const,
    businessId,
    generatedAt: at,
    scope: { businessId, terminalId, storeId: null, target: "tablet" },
    cursor: { requested: null, from: null, to: cursor, hasMore: false, checkpointStrategy: "updatedAt_entityRank_id" as const },
    changes: [{
      changeId: `${CATALOG_DELTA_STREAM}:Product:product-media-tablet:${at}`,
      entityType: "Product" as const,
      entityId: "product-media-tablet",
      businessId,
      operation: "upsert" as const,
      occurredAt: at,
      cursor,
      payload: { id: "product-media-tablet", businessId, sku: "MEDIA-TAB-1", name: "Producto con media", category: "General", priceCents: 2500, costCents: 1000, stockOnHand: 9, isActive: true, mediaRef: "https://cdn.example.test/products/media-tab-1.webp", barcodes: [], createdAt: at, updatedAt: at }
    }],
    counts: { total: 1, byEntity: { Product: 1 } },
    diagnostics: { source: "pc-canonical-db" as const, validator: CATALOG_DELTA_CONTRACT_ID, ordering: "updatedAt_entityRank_id" as const, notes: ["product media projection fixture"] }
  };
  const result = await applyCatalogDeltaEnvelope(envelope, { mode: "bootstrap", targetBusinessId: businessId, terminalId, pcBusinessId: businessId });
  assert(result.ok && result.counts.applied === 1 && result.checkpoint?.status === "applied", "PRODUCT_MEDIA_CATALOG_DELTA_APPLY_FAILED");
  const rows = await prisma.$queryRaw<Array<{ mediaRef: string | null }>>`SELECT "mediaRef" FROM "Product" WHERE "id" = 'product-media-tablet' AND "businessId" = ${businessId}`;
  assert(rows[0]?.mediaRef === "https://cdn.example.test/products/media-tab-1.webp", "PRODUCT_MEDIA_TABLET_REFERENCE_NOT_PROJECTED");
  console.log("product_media_catalog_projection=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}).then(async () => {
  await prisma.$disconnect();
});
