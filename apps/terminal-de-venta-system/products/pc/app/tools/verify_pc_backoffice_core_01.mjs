#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");
const failures = [];

function fail(message) {
  failures.push(message);
}

function readRel(root, rel) {
  const full = path.resolve(root, rel);
  if (!existsSync(full)) {
    fail(`Missing file: ${full}`);
    return "";
  }
  return readFileSync(full, "utf8");
}

function assertIncludes(root, rel, marker) {
  const text = readRel(root, rel);
  if (text && !text.includes(marker)) {
    fail(`${rel} missing marker: ${marker}`);
  }
}

const coreModules = [
  "catalog",
  "stock",
  "counts",
  "purchasing",
  "receiving",
  "replenishment",
  "audit",
  "sync"
];

const registry = readRel(appRoot, "src/composition/module-registry.ts");
for (const moduleKey of coreModules) {
  const manifestName = `${moduleKey}/module.manifest.ts`;
  assertIncludes(appRoot, `src/modules/${manifestName}`, "TwinModuleManifest");
  assertIncludes(appRoot, `app/${moduleKey}/page.tsx`, `getBackofficeModuleOverview("${moduleKey}")`);
  assertIncludes(appRoot, `app/api/backoffice/${moduleKey}/route.ts`, `GET /api/backoffice/${moduleKey}`);
  if (!registry.toLowerCase().includes(`${moduleKey}module`) && !registry.includes(`"${moduleKey}"`)) {
    fail(`module-registry does not expose ${moduleKey}`);
  }
}

const routeAndApiContracts = [
  ["app/catalog/page.tsx", "CatalogPage"],
  ["app/stock/page.tsx", "StockPage"],
  ["app/counts/page.tsx", "CountsPage"],
  ["app/purchasing/page.tsx", "PurchasingPage"],
  ["app/receiving/page.tsx", "ReceivingPage"],
  ["app/replenishment/page.tsx", "ReplenishmentPage"],
  ["app/audit/page.tsx", "AuditPage"],
  ["app/sync/page.tsx", "IngestEventPanel"],
  ["app/api/backoffice/catalog/route.ts", "GET /api/backoffice/catalog"],
  ["app/api/backoffice/stock/route.ts", "GET /api/backoffice/stock"],
  ["app/api/backoffice/movements/route.ts", "GET /api/backoffice/movements"],
  ["app/api/backoffice/audit/recent/route.ts", "GET /api/backoffice/audit/recent"],
  ["app/api/backoffice/sync/ingest/route.ts", "POST /api/backoffice/sync/ingest"],
  ["app/api/backoffice/sync/conflicts/route.ts", "GET /api/backoffice/sync/conflicts"]
];

for (const [rel, marker] of routeAndApiContracts) {
  assertIncludes(appRoot, rel, marker);
}

const overview = readRel(appRoot, "src/lib/backoffice/overview.ts");
for (const marker of [
  "prisma.product.findMany",
  "include: { barcodes: true }",
  "prisma.stockSnapshot.findMany",
  "prisma.stockMovement.findMany",
  "prisma.auditCount.findMany",
  "prisma.purchaseOrder.findMany",
  "prisma.goodsReceipt.findMany",
  "prisma.replenishmentSignal.findMany",
  "prisma.outboxEvent.findMany",
  "GoodsReceipt reciente",
  "Tablet decrementa localmente",
  "no bloquea ventas locales Tablet"
]) {
  if (!overview.includes(marker)) fail(`overview.ts missing backoffice core marker: ${marker}`);
}

const repositoryChecks = [
  ["src/server/repositories/product-repository.prisma.ts", "barcodes"],
  ["src/server/repositories/stock-repository.prisma.ts", "stockSnapshot"],
  ["src/server/repositories/purchase-order-repository.prisma.ts", "goodsReceipt"],
  ["src/server/repositories/audit-repository.prisma.ts", "auditCount"],
  ["src/server/repositories/outbox-repository.prisma.ts", "outboxEvent"]
];

for (const [rel, marker] of repositoryChecks) {
  assertIncludes(appRoot, rel, marker);
}

const navigation = readRel(appRoot, "src/composition/navigation.ts");
if (navigation.includes("/pos") || registry.includes("/pos")) {
  fail("PC navigation or module registry must not expose POS routes.");
}

const pcPosPath = path.join(appRoot, "app", "pos", "page.tsx");
if (existsSync(pcPosPath)) {
  fail("PC app must not define a POS page.");
}

const pcDataModel = readRel(appRoot, "docs/DATA_MODEL.md");
assertIncludes(appRoot, "tools/db_summary.py", "GoodsReceipt");
if (readRel(appRoot, "tools/db_summary.py").includes("ReceivingReceipt")) {
  fail("PC db_summary.py still references legacy ReceivingReceipt.");
}
if (!pcDataModel.includes("`ReceivingReceipt` quedó reemplazado por `GoodsReceipt`")) {
  fail("PC DATA_MODEL.md must document GoodsReceipt as the canonical receiving model.");
}

const productEligibility = readRel(terminalRoot, "docs/product/PRISMA_TABLET_COMERCIAL_ELIGIBILITY_BASE.me");
if (productEligibility.includes("- `ReceivingReceipt`") && !productEligibility.includes("GoodsReceipt` (canonical replacement")) {
  fail("Product docs still present ReceivingReceipt as canonical.");
}

if (failures.length) {
  console.error("PRISMA_PC_BACKOFFICE_CORE_01 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_PC_BACKOFFICE_CORE_01 passed");
console.log(JSON.stringify({
  modules: coreModules,
  apiRoutes: coreModules.map((moduleKey) => `/api/backoffice/${moduleKey}`),
  pcIsPos: false,
  receivingModel: "GoodsReceipt"
}, null, 2));
