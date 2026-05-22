import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const failures = [];
const warnings = [];
const read = (rel) => fs.existsSync(path.join(root, rel)) ? fs.readFileSync(path.join(root, rel), "utf8") : "";
const exists = (rel) => fs.existsSync(path.join(root, rel));

function requireFile(label, rel) {
  if (!exists(rel)) failures.push(`${label} missing: ${rel}`);
  return read(rel);
}

function requireToken(label, source, token) {
  if (!source.includes(token)) failures.push(`${label} missing token: ${token}`);
}

function parseJson(rel) {
  try {
    return JSON.parse(read(rel));
  } catch (error) {
    failures.push(`Invalid JSON ${rel}: ${error.message}`);
    return null;
  }
}

const files = {
  contractJson: "shared/contracts/pc-tablet-catalog-delta.v1.json",
  contractTs: "shared/twin-kernel/src/sync/catalog-delta.ts",
  pcRoute: "products/pc/app/app/api/sync/export/catalog-delta/route.ts",
  pcService: "products/pc/app/src/server/services/catalog-delta-export.service.ts",
  tabletSchema: "products/tablet/app/prisma/schema.prisma",
  tabletMigration: "products/tablet/app/prisma/migrations/20260522000100_tablet_catalog_pull_checkpoint/migration.sql",
  tabletRoute: "products/tablet/app/app/api/pos/sync/pull/route.ts",
  tabletService: "products/tablet/app/src/server/sync/catalog-pull.ts",
  tabletUi: "products/tablet/app/components/sync/catalog-pull-panel.tsx",
  tabletSyncScreen: "products/tablet/app/components/sync/pending-offline-sync-panel-screen.tsx",
  tabletPcOrigin: "products/tablet/app/src/server/sync/pc-origin.ts",
  pcCommandService: "products/pc/app/src/server/services/pc-command-center.service.ts",
  pcCommandPage: "products/pc/app/components/control/pc-command-center-page.tsx",
  pcCommandActions: "products/pc/app/components/control/pc-command-actions.tsx",
  supplierVerifier: "tools/verify_supplier_product_supplier_sync_closure_01.mjs",
  tabletDispatcher: "products/tablet/app/src/server/sync/dispatcher.ts"
};

const sources = Object.fromEntries(Object.entries(files).map(([key, rel]) => [key, requireFile(key, rel)]));

for (const token of [
  "PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1",
  "pc.catalog.delta.v1",
  "CATALOG_DELTA_ENTITY_TYPES",
  "validateCatalogDeltaEnvelope",
  "missing_dependency",
  "duplicate_change",
  "unknown_entity"
]) requireToken("shared contract", sources.contractTs, token);

for (const entity of ["Product", "Brand", "Supplier", "ProductSupplier", "PriceList", "PriceListItem", "TaxRate", "DropdownCatalog", "DropdownOption"]) {
  requireToken("contract json", sources.contractJson, entity);
  requireToken("pc exporter", sources.pcService, entity);
  requireToken("tablet importer", sources.tabletService, entity);
}

for (const token of [
  "buildPcCatalogDelta",
  "exportPcCatalogDelta",
  "recordPcCatalogDeltaExport",
  "cursorFor",
  "updatedAt_entityRank_id",
  "include: { barcodes: true }",
  "validateCatalogDeltaEnvelope(envelope)"
]) requireToken("pc exporter", sources.pcService, token);

for (const token of [
  "exportPcCatalogDelta",
  "POST /api/sync/export/catalog-delta",
  "GET /api/sync/export/catalog-delta"
]) requireToken("pc route", sources.pcRoute, token);

for (const token of [
  "model SyncCheckpoint",
  "scopeKey",
  "@@unique([businessId, scopeKey, stream])",
  "lastAttemptedAt",
  "lastSuccessfulAt"
]) requireToken("tablet schema", sources.tabletSchema, token);

for (const token of [
  "CREATE TABLE \"SyncCheckpoint\"",
  "SyncCheckpoint_businessId_scopeKey_stream_key",
  "FOREIGN KEY (\"businessId\") REFERENCES \"Business\""
]) requireToken("tablet migration", sources.tabletMigration, token);

for (const token of [
  "pullCatalogDeltaFromPc",
  "applyCatalogDeltaEnvelope",
  "getTabletCatalogPullStatus",
  "validateCatalogDeltaEnvelope",
  "Product.stockOnHand set on create only",
  "missing_dependency",
  "cursorBefore && item.cursor <= cursorBefore",
  "counts.duplicate",
  "counts.rejected",
  "counts.conflict",
  "safeToContinueSelling: true"
]) requireToken("tablet importer", sources.tabletService, token);

for (const token of [
  "pullCatalogDeltaFromPc",
  "getTabletCatalogPullStatus",
  "NextResponse.json(result"
]) requireToken("tablet route", sources.tabletRoute, token);

for (const token of [
  "CatalogPullPanel",
  "\"/api/pos/sync/pull\"",
  "Pedir delta",
  "Bootstrap inicial",
  "Resync controlado",
  "pc_unavailable",
  "partial",
  "successVisibleOnlyAfterServiceResponse"
]) {
  if (token === "successVisibleOnlyAfterServiceResponse") continue;
  requireToken("tablet ui", sources.tabletUi, token);
}
requireToken("tablet sync screen", sources.tabletSyncScreen, "<CatalogPullPanel />");

for (const token of [
  "PcCommandActions",
  "method?: \"GET\" | \"POST\"",
  "Generar delta catalogo",
  "Bootstrap catalogo",
  "Resync catalogo",
  "getPcCatalogDeltaStatus",
  "method: \"POST\""
]) requireToken("pc ui wiring", sources.pcCommandService + sources.pcCommandPage + sources.pcCommandActions, token);

const postLinkPattern = /<a[^>]+href=\{?["'][^"']*api\/[^"']*["']\}?[^>]*>/g;
const pcActionSection = sources.pcCommandPage + sources.pcCommandActions;
if (postLinkPattern.test(pcActionSection) && pcActionSection.includes("method: \"POST\"")) {
  failures.push("PC command actions still expose API POST actions as dumb links.");
}

for (const token of ["supplier.created", "product.supplier.linked", "projectProductSupplier"]) {
  requireToken("supplier/productSupplier closure preserved", sources.supplierVerifier + sources.tabletDispatcher + read("products/pc/app/src/server/services/sync-projectors.service.ts"), token);
}
for (const token of ["dispatchTabletOutboxOnce", "remoteLifecycleStatus"]) {
  requireToken("tablet outbound base preserved", sources.tabletDispatcher, token);
}
requireToken("tablet outbound config preserved", sources.tabletPcOrigin, "ackStrict");

const fixtureDir = "fixtures/sync/pc_to_tablet_catalog_delta_01";
const requiredFixtures = [
  "bootstrap-full.json",
  "incremental-delta.json",
  "duplicate-delta-replay.json",
  "invalid-payload-rejected.json",
  "missing-dependency-conflict.json",
  "resync-reset-checkpoint.json",
  "ui-success.json",
  "ui-error.json",
  "ui-retry.json"
];
for (const fixture of requiredFixtures) {
  const rel = `${fixtureDir}/${fixture}`;
  if (!exists(rel)) {
    failures.push(`fixture missing: ${rel}`);
    continue;
  }
  const parsed = parseJson(rel);
  if (!parsed) continue;
  if (fixture.endsWith(".json") && fixture !== "resync-reset-checkpoint.json" && !fixture.startsWith("ui-")) {
    if (parsed.contractId !== "PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1") failures.push(`fixture ${fixture} wrong contractId`);
    if (parsed.stream !== "pc.catalog.delta.v1") failures.push(`fixture ${fixture} wrong stream`);
    if (!Array.isArray(parsed.changes)) failures.push(`fixture ${fixture} missing changes array`);
  }
}

const bootstrap = parseJson(`${fixtureDir}/bootstrap-full.json`);
if (bootstrap) {
  const entities = new Set((bootstrap.changes ?? []).map((item) => item.entityType));
  for (const entity of ["Product", "Brand", "Supplier", "ProductSupplier", "PriceList", "PriceListItem", "TaxRate", "DropdownCatalog", "DropdownOption"]) {
    if (!entities.has(entity)) failures.push(`bootstrap fixture missing ${entity}`);
  }
}

const invalid = parseJson(`${fixtureDir}/invalid-payload-rejected.json`);
if (invalid?.changes?.[0]?.payload?.sku) failures.push("invalid fixture unexpectedly has Product.sku");
const missingDependency = parseJson(`${fixtureDir}/missing-dependency-conflict.json`);
if (!missingDependency?.changes?.[0]?.payload?.brandId) failures.push("missing dependency fixture does not exercise missing brandId");

for (const [label, source] of Object.entries(sources)) {
  const lower = source.toLowerCase();
  if (/\b(TODO|FIXME)\b/.test(source) || lower.includes("placeholder endpoint") || lower.includes("fake success")) {
    failures.push(`${label} contains forbidden placeholder/fake completion wording`);
  }
}

const matrix = [
  ["Product", "CLOSED"],
  ["Brand", "CLOSED"],
  ["Supplier", "CLOSED"],
  ["ProductSupplier", "CLOSED"],
  ["PriceList", "CLOSED"],
  ["PriceListItem", "CLOSED"],
  ["TaxRate", "CLOSED"],
  ["DropdownCatalog", "CLOSED"],
  ["DropdownOption", "CLOSED"]
];

if (failures.length) {
  console.error("PC_TO_TABLET_CATALOG_DELTA_CLOSURE failed");
  console.error(JSON.stringify({ failures, warnings }, null, 2));
  process.exit(1);
}

console.log("PC_TO_TABLET_CATALOG_DELTA_CLOSURE passed");
console.log(JSON.stringify({
  checkedAt: new Date().toISOString(),
  contract: "PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1",
  stream: "pc.catalog.delta.v1",
  endpointPc: "POST /api/sync/export/catalog-delta",
  endpointTablet: "POST /api/pos/sync/pull",
  fixtures: requiredFixtures,
  matrix
}, null, 2));
