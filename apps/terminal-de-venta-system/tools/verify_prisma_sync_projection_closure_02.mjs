import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];
const read = (rel) => fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), "utf8") : "";
const mustInclude = (label, source, tokens) => {
  for (const token of tokens) if (!source.includes(token)) failures.push(`${label} missing token: ${token}`);
};

const projector = read("products/pc/app/src/server/services/sync-projectors.service.ts");
const tabletCatalog = read("products/tablet/app/src/server/pos-api/product-mutations.prisma.ts");
const tabletReturns = read("products/tablet/app/src/server/pos-api/returns.prisma.ts");
const pcOrigin = read("products/tablet/app/src/server/sync/pc-origin.ts");

mustInclude("PC sync projectors", projector, [
  "projectSaleCreated",
  "projectSaleCompleted",
  "createSalePaymentTenders",
  "projectTicketClosed",
  "projectStockDecremented",
  "stockOnHand",
  "projectStockAdjusted",
  "projectCatalogProduct",
  "catalog.product.created",
  "catalog.product.updated",
  "projectSaleRefunded",
  "sale.refunded",
  "SaleReturnLine",
  "projectSaleCancelled",
  "shift.closed",
  "projectSupplier",
  "projectProductSupplier",
  "supplier.created",
  "supplier.updated",
  "supplier.disabled",
  "product.supplier.linked",
  "product.supplier.unlinked",
  "product.supplier.updated"
]);

mustInclude("Tablet catalog outbox", tabletCatalog, [
  "POS_EVENT_SCHEMA_VERSION",
  "terminalId",
  "actorId",
  "schemaVersion: POS_EVENT_SCHEMA_VERSION",
  "catalog.product.created",
  "catalog.product.updated",
  "costCents",
  "barcodes"
]);
if (tabletCatalog.includes('schemaVersion: "1.0"')) failures.push("Tablet catalog still emits schemaVersion 1.0");

mustInclude("Tablet return outbox", tabletReturns, [
  'const topic = "sale.refunded"',
  "POS_EVENT_SCHEMA_VERSION",
  "terminalId",
  "actorId",
  "eventType: topic",
  "saleReturnLine.create",
  "stockMovement.create",
  "stockOnHand",
  "schemaVersion: POS_EVENT_SCHEMA_VERSION"
]);
if (tabletReturns.includes("sale.return.created")) failures.push("Tablet returns still emits deprecated sale.return.created topic");
if (tabletReturns.includes('schemaVersion: "1.0"')) failures.push("Tablet returns still emits schemaVersion 1.0");

mustInclude("Tablet PC origin", pcOrigin, ['readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", false)']);
if (pcOrigin.includes('readFlag("PRISMA_TABLET_PC_SYNC_ENABLED", true)')) failures.push("Tablet PC sync flag still defaults on");

if (failures.length) {
  console.error("PRISMA_SYNC_PROJECTION_CLOSURE_02 failed");
  console.error(JSON.stringify({ failures }, null, 2));
  process.exit(1);
}

console.log("PRISMA_SYNC_PROJECTION_CLOSURE_02 passed");
console.log(JSON.stringify({
  projectorTopicsClosed: ["sale.created", "sale.completed", "ticket.closed", "stock.decremented", "stock.adjusted", "catalog.product.created", "catalog.product.updated", "sale.refunded", "sale.cancelled", "shift.closed", "supplier.created", "supplier.updated", "supplier.disabled", "product.supplier.linked", "product.supplier.unlinked", "product.supplier.updated"],
  tabletEmittersFixed: ["catalog.product.created", "catalog.product.updated", "sale.refunded"],
  checkedAt: new Date().toISOString()
}, null, 2));
