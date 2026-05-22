import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const requiredIds = ["pc.tablet-catalog-freshness-grid", "pc.sync-command-lifecycle-timeline"];
const fail = (message) => {
  console.error(`[PC Sync Chart Promotion] FAIL: ${message}`);
  process.exitCode = 1;
};
const pass = (message) => console.log(`[PC Sync Chart Promotion] PASS: ${message}`);

function abs(relativePath) {
  return path.join(root, relativePath);
}

function read(relativePath) {
  return fs.readFileSync(abs(relativePath), "utf8");
}

function exists(relativePath) {
  return fs.existsSync(abs(relativePath));
}

function json(relativePath) {
  return JSON.parse(read(relativePath));
}

function assertContains(relativePath, needles, label = relativePath) {
  const source = read(relativePath);
  for (const needle of needles) {
    if (source.includes(needle)) pass(`${label} contains ${needle}`);
    else fail(`${label} missing ${needle}`);
  }
}

function assertNotContains(relativePath, needles, label = relativePath) {
  const source = read(relativePath);
  for (const needle of needles) {
    if (!source.includes(needle)) pass(`${label} avoids ${needle}`);
    else fail(`${label} contains forbidden ${needle}`);
  }
}

function walk(dir, acc = []) {
  const target = abs(dir);
  if (!fs.existsSync(target)) return acc;
  for (const entry of fs.readdirSync(target, { withFileTypes: true })) {
    const relative = path.join(dir, entry.name).replaceAll("\\", "/");
    if (entry.isDirectory()) {
      if (["node_modules", ".next", "dist", "build", "coverage"].includes(entry.name)) continue;
      walk(relative, acc);
    } else {
      acc.push(relative);
    }
  }
  return acc;
}

for (const file of [
  "shared/prisma-charts/prismaChartContracts.ts",
  "shared/prisma-charts/prismaChartRegistry.ts",
  "shared/prisma-charts/prismaChartAdapters.ts",
  "shared/prisma-charts/prismaChartMocks.ts",
  "shared/prisma-charts/prismaChartOptions.ts",
  "shared/prisma-charts/prismaChartAtlas.ts",
  "products/chart-lab/app/src/prisma-charts/chart-lab-registry.tsx",
  "products/chart-lab/app/src/prisma-charts/chart-data-registry.json",
  "products/pc/app/src/server/services/pc-sync-chart-data.service.ts",
  "products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts",
  "products/pc/app/app/api/charts/pc/sync-command-lifecycle-timeline/route.ts",
  "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  "products/pc/app/components/sync/pc-sync-chart-promotion-panel.module.css",
  "products/pc/app/components/control/pc-command-center-page.tsx",
  "docs/charts/PC_SYNC_CHART_PROMOTION_01.md"
]) {
  if (exists(file)) pass(`required file exists: ${file}`);
  else fail(`missing required file: ${file}`);
}

for (const id of requiredIds) {
  assertContains("shared/prisma-charts/prismaChartContracts.ts", [id], "contracts");
  assertContains("shared/prisma-charts/prismaChartRegistry.ts", [`id: "${id}"`, 'route: "/sync"'], "registry");
  const passportFile = `shared/prisma-charts/passports/${id}.passport.ts`;
  if (exists(passportFile)) pass(`passport exists: ${passportFile}`);
  else fail(`missing passport: ${passportFile}`);
  assertContains("shared/prisma-charts/prismaChartAtlas.ts", [id.split(/[.-]/).map((part, index) => index === 0 ? part : part.charAt(0).toUpperCase() + part.slice(1)).join("")], "atlas");
  assertContains("products/chart-lab/app/src/prisma-charts/chart-lab-registry.tsx", [id], "lab registry");
}

assertContains("shared/prisma-charts/prismaChartContracts.ts", [
  "TabletCatalogFreshnessGridRow",
  "TabletCatalogEntityFreshness",
  "SyncCommandLifecycleEvent",
  "PcSyncLifecycleStatus",
  "TabletCatalogRecommendedAction"
], "contracts");
assertContains("shared/prisma-charts/prismaChartAdapters.ts", [
  "buildPcTabletCatalogFreshnessGridViewModel",
  "buildPcSyncCommandLifecycleTimelineViewModel",
  "mockFallback: sources.mockFallback"
], "adapters");
assertContains("shared/prisma-charts/prismaChartMocks.ts", [
  "tabletCatalogFreshnessGrid",
  "syncCommandLifecycleTimeline",
  "pc.catalog.delta.v1"
], "mocks");
assertContains("shared/prisma-charts/prismaChartOptions.ts", [
  "function tabletCatalogFreshnessGridOption",
  "function syncCommandLifecycleTimelineOption"
], "options");

const registryData = json("products/chart-lab/app/src/prisma-charts/chart-data-registry.json");
for (const id of requiredIds) {
  const entry = (registryData.charts ?? []).find((chart) => chart.chartId === id);
  if (!entry) {
    fail(`chart data registry missing ${id}`);
    continue;
  }
  if (entry.sourceMode === "live-real") fail(`${id} must not be live-real in Chart Lab registry without Lab runtime endpoint`);
  else pass(`${id} sourceMode is honest: ${entry.sourceMode}`);
  if (entry.fixturePath && exists(entry.fixturePath)) pass(`${id} fixturePath exists`);
  else fail(`${id} fixturePath missing: ${entry.fixturePath}`);
  if (entry.adapterPath && !String(entry.adapterPath).includes("prismaChartMocks")) pass(`${id} adapterPath is not mock`);
  else fail(`${id} adapterPath invalid`);
}

const fixtureDir = "fixtures/charts/pc_sync_chart_promotion_01";
const fixtureNames = [
  "freshness-all-tablets-fresh.json",
  "freshness-one-tablet-stale.json",
  "freshness-one-tablet-error.json",
  "freshness-mixed-entity-freshness.json",
  "freshness-resync-recommended.json",
  "freshness-empty-no-checkpoint-data.json",
  "lifecycle-successful-catalog-delta.json",
  "lifecycle-bootstrap.json",
  "lifecycle-resync.json",
  "lifecycle-rejected-payload.json",
  "lifecycle-conflict.json",
  "lifecycle-duplicate-replay.json",
  "lifecycle-empty.json"
];
for (const fixture of fixtureNames) {
  const relative = `${fixtureDir}/${fixture}`;
  if (!exists(relative)) {
    fail(`missing fixture: ${relative}`);
    continue;
  }
  const parsed = json(relative);
  if (requiredIds.includes(parsed.chartId)) pass(`fixture ${fixture} has supported chartId`);
  else fail(`fixture ${fixture} has wrong chartId`);
  if (Array.isArray(parsed.data)) pass(`fixture ${fixture} data is array`);
  else fail(`fixture ${fixture} data is not array`);
}
const allFresh = json(`${fixtureDir}/freshness-all-tablets-fresh.json`);
const entities = new Set((allFresh.data?.[0]?.entityStatuses ?? []).map((item) => item.entityType));
for (const entity of ["Product", "Brand", "Supplier", "ProductSupplier", "PriceList", "PriceListItem", "TaxRate", "DropdownCatalog", "DropdownOption"]) {
  if (entities.has(entity)) pass(`freshness fixture covers ${entity}`);
  else fail(`freshness fixture missing ${entity}`);
}

assertContains("products/pc/app/src/server/services/pc-sync-chart-data.service.ts", [
  "getPcTabletCatalogFreshnessGridChart",
  "getPcSyncCommandLifecycleTimelineChart",
  "getPcCatalogDeltaStatus",
  "deviceHeartbeat",
  "syncCheckpoint",
  "syncConflict",
  "buildPrismaInsightEnvelope",
  "Production PC chart endpoint does not use shared mocks."
], "pc chart service");
assertContains("products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts", [
  "GET",
  "getPcTabletCatalogFreshnessGridChart",
  "GET /api/charts/pc/tablet-catalog-freshness-grid",
  "PC_SYNC_CHART_DATA_ERROR"
], "freshness endpoint");
assertContains("products/pc/app/app/api/charts/pc/sync-command-lifecycle-timeline/route.ts", [
  "GET",
  "getPcSyncCommandLifecycleTimelineChart",
  "GET /api/charts/pc/sync-command-lifecycle-timeline",
  "PC_SYNC_CHART_DATA_ERROR"
], "lifecycle endpoint");
assertContains("products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx", [
  "pc.tablet-catalog-freshness-grid",
  "pc.sync-command-lifecycle-timeline",
  "FRESHNESS_ENDPOINT",
  "LIFECYCLE_ENDPOINT",
  "fetch(endpoint",
  "Cargando",
  "Sin Tablets",
  "role={state.error ? \"alert\" : \"status\"}",
  "Actualizar",
  "disabled={state.loading}"
], "pc sync chart panel");
assertContains("products/pc/app/components/control/pc-command-center-page.tsx", [
  "PcSyncChartPromotionPanel",
  "model.mode === \"sync\""
], "pc sync mount");

const pcSources = walk("products/pc/app").filter((file) => /\.(ts|tsx)$/.test(file));
const chartLabImports = pcSources.filter((file) => {
  const source = read(file);
  return source.includes("products/chart-lab") || source.includes("PrismaChartLabShell") || source.includes("chart-lab-registry");
});
if (chartLabImports.length === 0) pass("PC does not import Chart Lab app shell or Lab registry");
else fail(`PC imports Chart Lab surface: ${chartLabImports.join(", ")}`);

for (const file of [
  "shared/prisma-charts/prismaChartContracts.ts",
  "shared/prisma-charts/prismaChartAdapters.ts",
  "products/pc/app/src/server/services/pc-sync-chart-data.service.ts",
  "products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx",
  "docs/charts/PC_SYNC_CHART_PROMOTION_01.md"
]) {
  assertNotContains(file, ["TODO", "placeholder completion", "fake success"], file);
}

assertContains("package.json", ["\"verify:pc-sync-chart-promotion\""], "terminal package script");
assertContains("docs/charts/PC_SYNC_CHART_PROMOTION_01.md", [
  "pc.tablet-catalog-freshness-grid",
  "pc.sync-command-lifecycle-timeline",
  "GET /api/charts/pc/tablet-catalog-freshness-grid",
  "GET /api/charts/pc/sync-command-lifecycle-timeline",
  "sourceMode",
  "Chart Lab"
], "docs");

const syncVerifier = spawnSync("node", ["tools/verify_pc_to_tablet_catalog_delta_closure_01.mjs"], {
  cwd: root,
  shell: process.platform === "win32",
  encoding: "utf8"
});
if (syncVerifier.status === 0) pass("existing PC -> Tablet catalog sync verifier still passes");
else fail(`existing PC -> Tablet catalog sync verifier failed\n${syncVerifier.stdout}\n${syncVerifier.stderr}`);

if (!process.exitCode) pass("PC sync chart promotion verification complete");
