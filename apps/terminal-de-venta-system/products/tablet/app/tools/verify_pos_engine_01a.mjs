#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const checks = [
  ["src/server/pos-engine/repository.prisma.ts", "completeLocalSale"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.sale.create"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.saleLine.create"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.product.update"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.stockMovement.create"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.outboxEvent.create"],
  ["src/server/pos-engine/repository.prisma.ts", "clientRequestId: input.clientRequestId"],
  ["src/server/pos-engine/repository.prisma.ts", "tx.sale.findFirst"],
  ["src/server/pos-engine/repository.prisma.ts", "events: []"],
  ["src/server/pos-engine/event-factory.ts", "sale.completed"],
  ["src/server/pos-engine/event-factory.ts", "ticket.closed"],
  ["src/server/pos-engine/event-factory.ts", "stock.decremented"],
  ["src/server/pos-engine/errors.ts", "INSUFFICIENT_STOCK"],
  ["src/server/pos-engine/types.ts", "CompleteLocalSaleInput"],
  ["src/server/pos-engine/index.ts", "repository.prisma"],
  ["docs/pos/STANDALONE_CORE_01A_ENGINE.md", "Acceptance criteria"],
  ["docs/qa/pos-01a/acceptance.md", "POS-01A-AC-001"]
];

let failed = false;
for (const [rel, marker] of checks) {
  const full = path.join(appRoot, rel);
  if (!existsSync(full)) {
    console.error(`[pos-01a] missing file: ${rel}`);
    failed = true;
    continue;
  }
  const text = readFileSync(full, "utf8");
  if (!text.includes(marker)) {
    console.error(`[pos-01a] marker missing in ${rel}: ${marker}`);
    failed = true;
  } else {
    console.log(`[pos-01a] ok ${rel}: ${marker}`);
  }
}

if (failed) {
  console.error("[pos-01a] Verify failed.");
  process.exit(1);
}

console.log("[pos-01a] Verify OK.");
