#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");
const repoRoot = path.resolve(terminalRoot, "..", "..");
const tabletRoot = path.resolve(appRoot, "..", "..", "tablet", "app");

let failed = false;

function readRel(root, rel) {
  const full = path.resolve(root, rel);
  if (!existsSync(full)) return null;
  return readFileSync(full, "utf8");
}

function checkFile(root, rel, marker) {
  const text = readRel(root, rel);
  if (text === null) {
    console.error(`[pc-backoffice-03] missing file: ${path.resolve(root, rel)}`);
    failed = true;
    return;
  }
  if (marker && !text.includes(marker)) {
    console.error(`[pc-backoffice-03] marker missing in ${rel}: ${marker}`);
    failed = true;
    return;
  }
  console.log(`[pc-backoffice-03] ok ${rel}${marker ? `: ${marker}` : ""}`);
}

const routeChecks = [
  ["app/dashboard/page.tsx", "ExecutiveDashboard"],
  ["app/catalog/page.tsx", "getBackofficeModuleOverview(\"catalog\")"],
  ["app/stock/page.tsx", "getBackofficeModuleOverview(\"stock\")"],
  ["app/movements/page.tsx", "getBackofficeModuleOverview(\"movements\")"],
  ["app/counts/page.tsx", "getBackofficeModuleOverview(\"counts\")"],
  ["app/purchasing/page.tsx", "getBackofficeModuleOverview(\"purchasing\")"],
  ["app/receiving/page.tsx", "getBackofficeModuleOverview(\"receiving\")"],
  ["app/replenishment/page.tsx", "getBackofficeModuleOverview(\"replenishment\")"],
  ["app/audit/page.tsx", "getBackofficeModuleOverview(\"audit\")"],
  ["app/sync/page.tsx", "IngestEventPanel"],
  ["app/settings/page.tsx", "getBackofficeModuleOverview(\"settings\")"]
];

for (const [rel, marker] of routeChecks) checkFile(appRoot, rel, marker);

const implementationChecks = [
  ["components/layout/app-shell.tsx", "sidebar"],
  ["components/backoffice/executive-dashboard.tsx", "Backoffice de sincronización y gobierno"],
  ["components/backoffice/kpi-card.tsx", "KpiCard"],
  ["components/backoffice/module-overview-page.tsx", "ModuleOverviewPage"],
  ["components/backoffice/ingest-event-panel.tsx", "accepted, rejected, duplicate, conflict"],
  ["src/lib/backoffice/dashboard.ts", "netSalesTodayCents"],
  ["src/lib/backoffice/event-contract.ts", "RECOGNIZED_EVENT_TOPICS"],
  ["src/lib/backoffice/event-contract.ts", "sale.completed"],
  ["src/lib/backoffice/event-contract.ts", "accepted"],
  ["src/lib/backoffice/conflicts.ts", "negative_stock"],
  ["app/api/backoffice/dashboard/route.ts", "GET /api/backoffice/dashboard"],
  ["app/api/backoffice/sync/ingest/route.ts", "POST /api/backoffice/sync/ingest"],
  ["app/api/backoffice/sync/conflicts/route.ts", "GET /api/backoffice/sync/conflicts"],
  ["app/api/backoffice/audit/recent/route.ts", "GET /api/backoffice/audit/recent"],
  ["app/api/backoffice/catalog/route.ts", "GET /api/backoffice/catalog"],
  ["app/api/backoffice/stock/route.ts", "GET /api/backoffice/stock"],
  ["app/api/backoffice/movements/route.ts", "GET /api/backoffice/movements"]
];

for (const [rel, marker] of implementationChecks) checkFile(appRoot, rel, marker);

const tabletChecks = [
  ["app/pos/page.tsx", "PosScreen"],
  ["app/checkout/page.tsx", "CheckoutScreen"],
  ["app/prisma-dark-pos-reference/page.tsx", "PrismaDarkPosShell"],
  ["app/api/pos/events/outbox/route.ts", "GET"],
  ["app/api/pos/export/events/route.ts", "buildEventsExport"],
  ["src/server/pos-outbox/index.ts", "listOutboxEvents"]
];

for (const [rel, marker] of tabletChecks) checkFile(tabletRoot, rel, marker);

const docChecks = [
  "docs/contracts/EVENT_CONTRACT.md",
  "docs/contracts/SYNC_RECONCILIATION_CONTRACT.md",
  "docs/contracts/API_RESPONSE_CONTRACT.md",
  "docs/architecture/PC_BACKOFFICE_CONTRACT.md"
];

for (const rel of docChecks) checkFile(terminalRoot, rel);

const salePathFiles = [
  "app/pos/page.tsx",
  "app/checkout/page.tsx",
  "components/tablet-pos/touch-pos-ui.tsx",
  "app/api/pos/sales/complete/route.ts",
  "src/server/pos-engine/repository.prisma.ts",
  "src/server/pos-engine/event-factory.ts"
];
const forbiddenSaleMarkers = ["PC_REQUIRED_TO_SELL", "PC required", "canonical.db", "tools/_local/data/terminal-de-venta-system/canonical.db"];

for (const rel of salePathFiles) {
  const text = readRel(tabletRoot, rel);
  if (text === null) continue;
  for (const marker of forbiddenSaleMarkers) {
    if (text.includes(marker)) {
      console.error(`[pc-backoffice-03] forbidden Tablet sale dependency marker in ${rel}: ${marker}`);
      failed = true;
    }
  }
}

const implementationFiles = [
  ...routeChecks.map(([rel]) => rel),
  ...implementationChecks.map(([rel]) => rel),
  "tools/verify_pc_backoffice_sync_dashboard_03.mjs"
];
const forbiddenImplementationPatterns = [/\.zip$/i, /\.log$/i, /\.db$/i, /\.sqlite3?$/i, /(^|\/)\.next(\/|$)/, /(^|\/)node_modules(\/|$)/, /(^|\/)data(\/|$)/];

for (const rel of implementationFiles) {
  const normalized = rel.replace(/\\/g, "/");
  if (forbiddenImplementationPatterns.some((pattern) => pattern.test(normalized))) {
    console.error(`[pc-backoffice-03] forbidden implementation artifact listed: ${rel}`);
    failed = true;
  }
}

if (failed) {
  console.error("[pc-backoffice-03] Verify failed.");
  process.exit(1);
}

console.log(`[pc-backoffice-03] repoRoot=${repoRoot}`);
console.log("[pc-backoffice-03] Verify OK.");
