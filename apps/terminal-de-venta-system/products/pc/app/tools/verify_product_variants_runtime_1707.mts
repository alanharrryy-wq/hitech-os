import { prisma } from "../src/server/prisma/client";
import { ProductVariantRepository } from "../src/server/repositories/product-variant.repository";

function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

async function bootstrap() {
  const ddl = [
    `CREATE TABLE "Business" ("id" TEXT NOT NULL PRIMARY KEY, "name" TEXT NOT NULL, "taxId" TEXT, "currency" TEXT NOT NULL DEFAULT 'MXN', "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "Product" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "sku" TEXT NOT NULL, "name" TEXT NOT NULL, "category" TEXT NOT NULL, "brandId" TEXT, "priceCents" INTEGER NOT NULL, "costCents" INTEGER NOT NULL, "stockOnHand" INTEGER NOT NULL DEFAULT 0, "taxRateId" TEXT, "isActive" BOOLEAN NOT NULL DEFAULT true, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "ProductVariant" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "productId" TEXT NOT NULL, "variantProductId" TEXT NOT NULL, "label" TEXT NOT NULL, "attributesJson" TEXT, "sortOrder" INTEGER NOT NULL DEFAULT 0, "status" TEXT NOT NULL DEFAULT 'ACTIVE', "idempotencyKey" TEXT, "version" INTEGER NOT NULL DEFAULT 1, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE UNIQUE INDEX "ProductVariant_businessId_idempotencyKey_key" ON "ProductVariant"("businessId", "idempotencyKey")`,
    `CREATE UNIQUE INDEX "ProductVariant_businessId_variantProductId_key" ON "ProductVariant"("businessId", "variantProductId")`,
    `CREATE TABLE "AuditEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "actorId" TEXT, "topic" TEXT NOT NULL, "entityType" TEXT NOT NULL, "entityId" TEXT, "summary" TEXT NOT NULL, "beforeJson" TEXT, "afterJson" TEXT, "metadataJson" TEXT, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)`,
    `CREATE TABLE "OutboxEvent" ("id" TEXT NOT NULL PRIMARY KEY, "businessId" TEXT NOT NULL, "terminalId" TEXT, "topic" TEXT NOT NULL, "eventType" TEXT, "aggregateId" TEXT NOT NULL, "idempotencyKey" TEXT, "correlationId" TEXT, "payloadJson" TEXT NOT NULL, "source" TEXT, "schemaVersion" TEXT, "status" TEXT NOT NULL, "lifecycleStatus" TEXT, "attempts" INTEGER NOT NULL DEFAULT 0, "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, "sentAt" DATETIME, "receivedAt" DATETIME, "validatedAt" DATETIME, "acceptedAt" DATETIME, "projectedAt" DATETIME, "reconciledAt" DATETIME, "failedAt" DATETIME, "deadLetterAt" DATETIME, "conflictCode" TEXT, "diagnosticsJson" TEXT, "lastError" TEXT)`
  ];
  for (const statement of ddl) await prisma.$executeRawUnsafe(statement);
  await prisma.$executeRawUnsafe(`INSERT INTO "Business" ("id", "name", "currency") VALUES ('biz-variant-a', 'Variant A', 'MXN'), ('biz-variant-b', 'Variant B', 'MXN')`);
  await prisma.$executeRawUnsafe(`INSERT INTO "Product" ("id", "businessId", "sku", "name", "category", "priceCents", "costCents", "stockOnHand", "isActive") VALUES ('p-parent', 'biz-variant-a', 'CAM-BASE', 'Camisa base', 'Ropa', 10000, 5000, 0, true), ('p-blue-m', 'biz-variant-a', 'CAM-AZM', 'Camisa azul M', 'Ropa', 10900, 5200, 4, true), ('p-blue-l', 'biz-variant-a', 'CAM-AZL', 'Camisa azul L', 'Ropa', 10900, 5200, 3, true), ('p-other', 'biz-variant-b', 'OTHER-1', 'Otro negocio', 'Ropa', 10000, 5000, 1, true)`);
}

async function main() {
  if (!process.env.DATABASE_URL) throw new Error("PRODUCT_VARIANT_RUNTIME_DATABASE_URL_REQUIRED");
  await bootstrap();
  const repository = new ProductVariantRepository();
  const created = await repository.create("biz-variant-a", { productId: "p-parent", variantProductId: "p-blue-m", label: "Azul · M", attributes: { color: "Azul", size: "M" }, sortOrder: 10, idempotencyKey: "product-variant-runtime-create-1" });
  assert(!created.replayed && created.variant.status === "ACTIVE" && created.variant.variantSku === "CAM-AZM", "PRODUCT_VARIANT_CREATE_READ_AFTER_WRITE_FAILED");
  const replay = await repository.create("biz-variant-a", { productId: "p-parent", variantProductId: "p-blue-m", label: "Ignored", attributes: {}, sortOrder: 0, idempotencyKey: "product-variant-runtime-create-1" });
  assert(replay.replayed && replay.variant.id === created.variant.id, "PRODUCT_VARIANT_IDEMPOTENCY_REPLAY_FAILED");

  let selfReference = false;
  try { await repository.create("biz-variant-a", { productId: "p-parent", variantProductId: "p-parent", label: "Inválida", attributes: {}, sortOrder: 0, idempotencyKey: "product-variant-runtime-self" }); } catch (error) { selfReference = error instanceof Error && error.message === "PRODUCT_VARIANT_SELF_REFERENCE"; }
  assert(selfReference, "PRODUCT_VARIANT_SELF_REFERENCE_NOT_ENFORCED");

  let nested = false;
  try { await repository.create("biz-variant-a", { productId: "p-blue-m", variantProductId: "p-blue-l", label: "No anidar", attributes: {}, sortOrder: 0, idempotencyKey: "product-variant-runtime-nested" }); } catch (error) { nested = error instanceof Error && error.message === "PRODUCT_VARIANT_NESTED_PARENT"; }
  assert(nested, "PRODUCT_VARIANT_NESTED_PARENT_NOT_ENFORCED");

  let scope = false;
  try { await repository.create("biz-variant-a", { productId: "p-parent", variantProductId: "p-other", label: "Otro negocio", attributes: {}, sortOrder: 0, idempotencyKey: "product-variant-runtime-scope" }); } catch (error) { scope = error instanceof Error && error.message === "PRODUCT_VARIANT_PRODUCT_NOT_AVAILABLE"; }
  assert(scope, "PRODUCT_VARIANT_BUSINESS_SCOPE_NOT_ENFORCED");

  const inactive = await repository.update("biz-variant-a", created.variant.id, { expectedVersion: created.variant.version, status: "INACTIVE" });
  assert(inactive?.status === "INACTIVE" && inactive.version === 2, "PRODUCT_VARIANT_DEACTIVATE_READ_AFTER_WRITE_FAILED");
  let conflict = false;
  try { await repository.update("biz-variant-a", created.variant.id, { expectedVersion: 1, status: "ACTIVE" }); } catch (error) { conflict = error instanceof Error && error.message === "PRODUCT_VARIANT_VERSION_CONFLICT"; }
  assert(conflict, "PRODUCT_VARIANT_VERSION_CONFLICT_NOT_ENFORCED");

  const activeProducts = await repository.listProducts("biz-variant-a");
  assert(activeProducts.length === 3 && activeProducts.every((product) => product.isActive), "PRODUCT_VARIANT_SELLABLE_PRODUCT_LIST_FAILED");
  const auditCount = await prisma.auditEvent.count({ where: { businessId: "biz-variant-a", entityType: "ProductVariant" } });
  assert(auditCount === 2, `PRODUCT_VARIANT_AUDIT_COUNT_INVALID:${auditCount}`);
  const outboxRows = await prisma.$queryRaw<Array<{ idempotencyKey: string; payloadJson: string }>>`SELECT "idempotencyKey", "payloadJson" FROM "OutboxEvent" WHERE "businessId" = 'biz-variant-a'`;
  assert(outboxRows.length === 2 && outboxRows.every((row) => row.idempotencyKey.startsWith("product_variant:")), "PRODUCT_VARIANT_OUTBOX_MISSING");
  assert(outboxRows.every((row) => !row.payloadJson.includes("Azul · M") && !row.payloadJson.includes("attributes")), "PRODUCT_VARIANT_OUTBOX_NOT_MINIMIZED");
  console.log("product_variants_runtime=PASS");
}

main().catch(async (error) => {
  await prisma.$disconnect().catch(() => undefined);
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
}).then(async () => {
  await prisma.$disconnect();
});
