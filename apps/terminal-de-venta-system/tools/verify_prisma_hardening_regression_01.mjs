#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];

function fail(message) {
  failures.push(message);
}

function assert(condition, message) {
  if (!condition) fail(message);
}

function readProjectFile(rel) {
  const full = path.join(projectRoot, rel);
  assert(existsSync(full), `Missing file: ${rel}`);
  return existsSync(full) ? readFileSync(full, "utf8") : "";
}

function count(text, needle) {
  return text.split(needle).length - 1;
}

function modelBlock(schema, modelName) {
  const marker = `model ${modelName} {`;
  const start = schema.indexOf(marker);
  if (start === -1) return "";
  const next = schema.indexOf("\nmodel ", start + marker.length);
  return schema.slice(start, next === -1 ? schema.length : next);
}

const tabletUi = readProjectFile("products/tablet/app/components/tablet-pos/touch-pos-ui.tsx");
assert(count(tabletUi, "clientRequestId:") === 1, "Tablet UI must send exactly one clientRequestId field in sale completion payload.");
assert(tabletUi.includes("makeClientRequestId()"), "Tablet UI must generate clientRequestId at completion time.");

const tabletValidators = readProjectFile("products/tablet/app/src/server/pos-api/validators.ts");
assert(tabletValidators.includes("clientRequestId: asString(body?.clientRequestId"), "Tablet API validator must preserve clientRequestId from request body.");

const tabletRepository = readProjectFile("products/tablet/app/src/server/pos-engine/repository.prisma.ts");
assert(tabletRepository.includes("if (input.clientRequestId)"), "Tablet sale repository must branch on clientRequestId.");
assert(tabletRepository.includes("tx.sale.findFirst"), "Tablet sale repository must look up an existing sale for idempotency.");
assert(tabletRepository.includes("where: { businessId, clientRequestId: input.clientRequestId }"), "Tablet sale repository must scope idempotency by businessId + clientRequestId.");
assert(tabletRepository.includes("clientRequestId: input.clientRequestId ?? null"), "Tablet sale repository must persist clientRequestId on new sales.");
assert(tabletRepository.includes("events: []"), "Tablet duplicate sale response must not emit a second event batch.");

const tabletSchema = readProjectFile("products/tablet/app/prisma/schema.prisma");
const saleBlock = modelBlock(tabletSchema, "Sale");
const purchaseOrderBlock = modelBlock(tabletSchema, "PurchaseOrder");
const goodsReceiptBlock = modelBlock(tabletSchema, "GoodsReceipt");
assert(saleBlock.includes("clientRequestId String?"), "Tablet Sale model must include nullable clientRequestId.");
assert(saleBlock.includes("@@unique([businessId, clientRequestId])"), "Tablet Sale model must enforce businessId + clientRequestId uniqueness.");
assert(!purchaseOrderBlock.includes("@@unique([businessId, clientRequestId])"), "PurchaseOrder must not carry a clientRequestId unique index without a field.");
assert(!goodsReceiptBlock.includes("@@unique([businessId, clientRequestId])"), "GoodsReceipt must not carry a clientRequestId unique index without a field.");

const tabletSeed = readProjectFile("products/tablet/app/scripts/tablet-db.mjs");
assert(count(tabletSeed, "const resetDemoStock") === 1, "Tablet seed must define resetDemoStock once.");
assert(count(tabletSeed, "const operationalSales") === 1, "Tablet seed must define operationalSales once.");
assert(count(tabletSeed, "const operationalMovements") === 1, "Tablet seed must define operationalMovements once.");
assert(count(tabletSeed, "const canResetDemoStock") === 1, "Tablet seed must define canResetDemoStock once.");
assert(tabletSeed.includes("operationalSales === 0 && operationalMovements === 0"), "Tablet seed must only reset demo stock on empty operational DB.");
assert(tabletSeed.includes("--reset-demo-stock"), "Tablet seed must require explicit --reset-demo-stock for demo stock reset.");
assert(tabletSeed.includes("ensureSaleClientRequestIdSchema"), "Tablet DB helper must preflight Sale.clientRequestId schema drift safely.");
assert(tabletSeed.includes('ALTER TABLE "Sale" ADD COLUMN "clientRequestId" TEXT'), "Tablet DB helper must add missing nullable Sale.clientRequestId without resetting data.");
assert(tabletSeed.includes('CREATE UNIQUE INDEX IF NOT EXISTS "Sale_businessId_clientRequestId_key"'), "Tablet DB helper must ensure the clientRequestId uniqueness index exists.");

const pcEventContract = readProjectFile("products/pc/app/src/lib/backoffice/event-contract.ts");
assert(pcEventContract.includes('event.topic === "sale.completed"'), "PC cash-session policy must apply to sale.completed only.");
assert(pcEventContract.includes("payload.cashSessionRequired === true"), "PC cash-session policy must require an explicit policy flag.");
assert(pcEventContract.includes("sale_outside_shift"), "PC event contract must keep sale_outside_shift conflict code available.");

const pcSyncStore = readProjectFile("products/pc/app/src/lib/backoffice/sync-ingest-store.ts");
assert(pcSyncStore.includes("function stableJsonDeep"), "PC sync ingest must use deep stable JSON normalization.");
assert(pcSyncStore.includes("Array.isArray(value)") && pcSyncStore.includes("value.map(stableJsonDeep)"), "PC stable JSON hashing must recurse through arrays.");
assert(pcSyncStore.includes("Object.keys(value).sort()") && pcSyncStore.includes("stableJsonDeep(value[key])"), "PC stable JSON hashing must sort and recurse through object keys.");
assert(pcSyncStore.includes("createHash(\"sha256\").update(stableJson(candidate))"), "PC rejected-event id must hash the deep stable JSON string.");

const pcPrismaClient = readProjectFile("products/pc/app/src/server/prisma/client.ts");
assert(pcPrismaClient.includes("function findTerminalRoot"), "PC Prisma client must discover terminal project root from cwd.");
assert(pcPrismaClient.includes("process.env.TV_SYSTEM_ROOT"), "PC Prisma client must support explicit TV_SYSTEM_ROOT.");
assert(pcPrismaClient.includes("terminal_de_venta.cmd"), "PC Prisma root detection must identify the terminal project wrapper.");
assert(pcPrismaClient.includes('path.join(current, "apps", "terminal-de-venta-system")'), "PC Prisma root detection must work from repo root cwd.");
assert(!pcPrismaClient.includes('path.resolve(process.env.TV_SYSTEM_ROOT ?? process.cwd(), "..", "..", "..")'), "PC Prisma client must not use fragile fixed-depth root traversal.");

if (failures.length) {
  console.error("PRISMA_HARDENING_REGRESSION_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_HARDENING_REGRESSION_01 passed");
