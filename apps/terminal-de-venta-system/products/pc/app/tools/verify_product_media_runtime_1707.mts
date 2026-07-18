import { prisma } from "../src/server/prisma/client";
import { ProductMediaRepository } from "../src/server/repositories/product-media.repository";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function bootstrap() {
  const ddl = [
    `CREATE TABLE "Business" ("id" TEXT NOT NULL PRIMARY KEY, "name" TEXT NOT NULL, "taxId" TEXT, "currency" TEXT NOT NULL DEFAULT 'MXN', "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "Product" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "sku" TEXT NOT NULL, "name" TEXT NOT NULL, "category" TEXT NOT NULL, "brandId" TEXT, "priceCents" INTEGER NOT NULL, "costCents" INTEGER NOT NULL, "stockOnHand" INTEGER NOT NULL DEFAULT 0, "taxRateId" TEXT, "mediaRef" TEXT, "isActive" BOOLEAN NOT NULL DEFAULT true, "createdAt" DATETIME NOT NULL, "updatedAt" DATETIME NOT NULL)`,
    `CREATE TABLE "AuditEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "actorId" TEXT, "topic" TEXT NOT NULL, "entityType" TEXT NOT NULL, "entityId" TEXT, "summary" TEXT NOT NULL, "beforeJson" TEXT, "afterJson" TEXT, "metadataJson" TEXT, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "OutboxEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "terminalId" TEXT, "topic" TEXT NOT NULL, "eventType" TEXT, "aggregateId" TEXT NOT NULL, "idempotencyKey" TEXT, "correlationId" TEXT, "payloadJson" TEXT NOT NULL, "source" TEXT, "schemaVersion" TEXT, "status" TEXT NOT NULL, "lifecycleStatus" TEXT, "attempts" INTEGER NOT NULL DEFAULT 0, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "sentAt" DATETIME, "receivedAt" DATETIME, "validatedAt" DATETIME, "acceptedAt" DATETIME, "projectedAt" DATETIME, "reconciledAt" DATETIME, "failedAt" DATETIME, "deadLetterAt" DATETIME, "conflictCode" TEXT, "diagnosticsJson" TEXT, "lastError" TEXT)`
  ];
  for (const statement of ddl) await prisma.$executeRawUnsafe(statement);
  const at = new Date("2026-07-17T12:00:00.000Z");
  await prisma.$executeRaw`INSERT INTO "Business" ("id", "name", "currency") VALUES ('biz-media-a', 'Media A', 'MXN')`;
  await prisma.$executeRaw`INSERT INTO "Product" ("id", "businessId", "sku", "name", "category", "priceCents", "costCents", "stockOnHand", "isActive", "createdAt", "updatedAt") VALUES ('p-media-a', 'biz-media-a', 'MEDIA-1', 'Producto media', 'General', 1000, 500, 5, true, ${at}, ${at})`;
}

async function main() {
  if (!process.env.DATABASE_URL) throw new Error("PRODUCT_MEDIA_RUNTIME_DATABASE_URL_REQUIRED");
  await bootstrap();
  const repository = new ProductMediaRepository();
  const [current] = await repository.list("biz-media-a");
  assert(current?.mediaRef === null, "PRODUCT_MEDIA_INITIAL_READ_FAILED");
  const updated = await repository.update({ businessId: "biz-media-a", productId: current.id, expectedUpdatedAt: current.updatedAt, mediaRef: "https://cdn.example.test/products/media-1.webp" });
  assert(updated?.mediaRef === "https://cdn.example.test/products/media-1.webp", "PRODUCT_MEDIA_UPDATE_READ_AFTER_WRITE_FAILED");
  let conflict = false;
  try { await repository.update({ businessId: "biz-media-a", productId: current.id, expectedUpdatedAt: current.updatedAt, mediaRef: null }); } catch (error) { conflict = error instanceof Error && error.message === "PRODUCT_MEDIA_VERSION_CONFLICT"; }
  assert(conflict, "PRODUCT_MEDIA_VERSION_CONFLICT_NOT_ENFORCED");
  const auditCount = await prisma.auditEvent.count({ where: { businessId: "biz-media-a", entityType: "Product" } });
  assert(auditCount === 1, `PRODUCT_MEDIA_AUDIT_MISSING:${auditCount}`);
  const outboxRows = await prisma.$queryRaw<Array<{ payloadJson: string }>>`SELECT "payloadJson" FROM "OutboxEvent" WHERE "businessId" = 'biz-media-a'`;
  assert(outboxRows.length === 1 && !outboxRows[0].payloadJson.includes("cdn.example"), "PRODUCT_MEDIA_OUTBOX_NOT_MINIMIZED");
  console.log("product_media_runtime=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}).then(async () => {
  await prisma.$disconnect();
});
