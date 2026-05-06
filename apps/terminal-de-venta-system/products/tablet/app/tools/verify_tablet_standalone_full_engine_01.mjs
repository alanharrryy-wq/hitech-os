#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const checks = [
  ["src/server/prisma/client.ts", "TABLET_DATABASE_URL"],
  ["src/server/prisma/client.ts", "tablet-local-default"],
  ["src/server/pos-runtime/index.ts", "pcRequiredForBasicSale: false"],
  ["src/server/pos-engine/repository.prisma.ts", "completeLocalSale"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.outboxEvent.create"],
  ["src/server/pos-engine/event-factory.ts", "schemaVersion"],
  ["src/server/pos-engine/constants.ts", "inventory.low_stock_detected"],
  ["src/server/pos-engine/errors.ts", "NETWORK_UNAVAILABLE"],
  ["src/server/pos-api/responses.ts", "meta: meta ?? {}"],
  ["src/server/pos-outbox/index.ts", "OUTBOX_STATUSES"],
  ["src/server/pos-reports/index.ts", "getOperationalTodayReport"],
  ["src/server/pos-export/index.ts", "text/csv; charset=utf-8"],
  ["app/api/pos/products/search/route.ts", "GET /api/pos/products/search"],
  ["app/api/pos/products/resolve/route.ts", "GET /api/pos/products/resolve"],
  ["app/api/pos/sales/complete/route.ts", "POST /api/pos/sales/complete"],
  ["app/api/pos/sales/today/route.ts", "GET /api/pos/sales/today"],
  ["app/api/pos/events/recent/route.ts", "GET /api/pos/events/recent"],
  ["app/api/pos/events/outbox/route.ts", "GET /api/pos/events/outbox"],
  ["app/api/pos/inventory/low-stock/route.ts", "GET /api/pos/inventory/low-stock"],
  ["app/api/pos/inventory/movements/recent/route.ts", "GET /api/pos/inventory/movements/recent"],
  ["app/api/pos/reports/operational-today/route.ts", "GET /api/pos/reports/operational-today"],
  ["app/api/pos/export/sales-today/route.ts", "GET /api/pos/export/sales-today"],
  ["app/api/pos/export/events/route.ts", "GET /api/pos/export/events"],
  ["app/api/pos/export/inventory-movements/route.ts", "GET /api/pos/export/inventory-movements"],
  ["../../../MANIFEST.tablet-pos-standalone-full-engine-01.json", "PRISMA_TABLET_POS_STANDALONE_FULL_ENGINE_01"]
];

let failed = false;
for (const [rel, marker] of checks) {
  const full = path.resolve(appRoot, rel);
  if (!existsSync(full)) {
    console.error(`[tablet-pos-01] missing file: ${rel}`);
    failed = true;
    continue;
  }
  const text = readFileSync(full, "utf8");
  if (!text.includes(marker)) {
    console.error(`[tablet-pos-01] marker missing in ${rel}: ${marker}`);
    failed = true;
  } else {
    console.log(`[tablet-pos-01] ok ${rel}: ${marker}`);
  }
}

const forbiddenSalePathText = [
  "tools/_local/data/terminal-de-venta-system/canonical.db",
  "PC_REQUIRED_TO_SELL",
  "PC required"
];

for (const rel of [
  "src/server/prisma/client.ts",
  "src/server/pos-engine/repository.prisma.ts",
  "src/server/pos-api/validators.ts",
  "src/server/pos-runtime/index.ts"
]) {
  const text = readFileSync(path.resolve(appRoot, rel), "utf8");
  for (const marker of forbiddenSalePathText) {
    if (text.includes(marker)) {
      console.error(`[tablet-pos-01] forbidden sale-path marker in ${rel}: ${marker}`);
      failed = true;
    }
  }
}

if (failed) {
  console.error("[tablet-pos-01] Verify failed.");
  process.exit(1);
}

console.log("[tablet-pos-01] Verify OK.");
