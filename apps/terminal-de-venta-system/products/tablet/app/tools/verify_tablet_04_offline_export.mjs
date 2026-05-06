#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const toolsDir = path.dirname(__filename);
const appRoot = path.resolve(toolsDir, "..");

function exists(p) {
  return fs.existsSync(p);
}

function read(p) {
  return fs.readFileSync(p, "utf8");
}

function readJson(p) {
  return JSON.parse(read(p));
}

const checks = [];
function check(id, ok, detail) {
  checks.push({ id, ok, detail });
}

const files = {
  auditRoute: path.join(appRoot, "app", "api", "pos", "offline", "audit", "route.ts"),
  offlinePage: path.join(appRoot, "app", "offline", "page.tsx"),
  offlineScreen: path.join(appRoot, "components", "offline", "offline-export-audit-screen.tsx"),
  offlineCss: path.join(appRoot, "components", "offline", "offline-export-audit.module.css"),
  posReports: path.join(appRoot, "src", "server", "pos-reports", "index.ts"),
  posOutbox: path.join(appRoot, "src", "server", "pos-outbox", "index.ts"),
  posExport: path.join(appRoot, "src", "server", "pos-export", "index.ts"),
  posEngineRepo: path.join(appRoot, "src", "server", "pos-engine", "repository.prisma.ts"),
  eventsRoute: path.join(appRoot, "app", "api", "pos", "events", "outbox", "route.ts"),
  salesExportRoute: path.join(appRoot, "app", "api", "pos", "export", "sales-today", "route.ts"),
  eventsExportRoute: path.join(appRoot, "app", "api", "pos", "export", "events", "route.ts"),
  inventoryExportRoute: path.join(appRoot, "app", "api", "pos", "export", "inventory-movements", "route.ts"),
  qa: path.join(appRoot, "docs", "qa", "TABLET_04_OFFLINE_REPORTES_EXPORT.md"),
  workflow: path.join(appRoot, "docs", "qa", "TABLET_LOCAL_PY_WORKFLOW_CONTRACT.md"),
  pkg: path.join(appRoot, "package.json")
};

for (const [key, file] of Object.entries(files)) {
  check(`T04-EXISTS-${key}`, exists(file), file);
}

if (exists(files.auditRoute)) {
  const text = read(files.auditRoute);
  check("T04-001 audit route uses operational report", text.includes("getOperationalTodayReport"), files.auditRoute);
  check("T04-002 audit route uses outbox", text.includes("getOutboxEvents"), files.auditRoute);
  check("T04-003 audit route uses movements", text.includes("getRecentInventoryMovements"), files.auditRoute);
  check("T04-004 audit route exposes CSV exports", text.includes("salesCsv") && text.includes("eventsCsv") && text.includes("inventoryMovementsCsv"), files.auditRoute);
  check("T04-005 audit route says no PC dependency", text.includes("no depende de PC"), files.auditRoute);
}

if (exists(files.offlineScreen)) {
  const text = read(files.offlineScreen);
  check("T04-006 screen calls offline audit endpoint", text.includes("/api/pos/offline/audit"), files.offlineScreen);
  check("T04-007 screen renders exports", text.includes("Ventas CSV") && text.includes("Eventos JSON") && text.includes("Movimientos CSV"), files.offlineScreen);
  check("T04-008 screen renders outbox", text.includes("Outbox reciente"), files.offlineScreen);
  check("T04-009 screen renders movements", text.includes("Movimientos recientes"), files.offlineScreen);
}

if (exists(files.posEngineRepo)) {
  const text = read(files.posEngineRepo);
  check("T04-010 engine creates Sale", text.includes("tx.sale.create"), files.posEngineRepo);
  check("T04-011 engine creates SaleLine", text.includes("tx.saleLine.create"), files.posEngineRepo);
  check("T04-012 engine creates StockMovement", text.includes("tx.stockMovement.create"), files.posEngineRepo);
  check("T04-013 engine creates OutboxEvent", text.includes("tx.outboxEvent.create"), files.posEngineRepo);
}

if (exists(files.posExport)) {
  const text = read(files.posExport);
  check("T04-014 export builds sales today", text.includes("buildSalesTodayExport"), files.posExport);
  check("T04-015 export builds events", text.includes("buildEventsExport"), files.posExport);
  check("T04-016 export builds inventory movements", text.includes("buildInventoryMovementsExport"), files.posExport);
  check("T04-017 export has csvResponse", text.includes("text/csv"), files.posExport);
}

if (exists(files.posReports)) {
  const text = read(files.posReports);
  check("T04-018 report has pending outbox count", text.includes("pendingOutboxCount"), files.posReports);
  check("T04-019 report has low stock count", text.includes("lowStockCount"), files.posReports);
  check("T04-020 report has recent movements count", text.includes("recentMovementsCount"), files.posReports);
}

if (exists(files.workflow)) {
  const text = read(files.workflow);
  check("T04-021 workflow one py", text.includes("un solo `.py` autocontenido"), files.workflow);
  check("T04-022 workflow run rollback", text.includes("--run") && text.includes("--rollback"), files.workflow);
  check("T04-023 workflow descargas", text.includes("F:\\descargasf"), files.workflow);
}

if (exists(files.pkg)) {
  const pkg = readJson(files.pkg);
  const scripts = pkg.scripts || {};
  check("T04-024 script tablet:04:offline exists", Boolean(scripts["tablet:04:offline"]), files.pkg);
  check("T04-025 script verify:04-offline exists", Boolean(scripts["verify:04-offline"]), files.pkg);
}

const ok = checks.every((item) => item.ok);
const evidenceDir = path.join(appRoot, "evidence", "verifier-output");
fs.mkdirSync(evidenceDir, { recursive: true });
const report = {
  ok,
  appRoot,
  checks,
  verdict: ok ? "PASS" : "FAIL",
  note: "T04 verifies offline audit, outbox visibility, exports, report wiring, and durable engine persistence markers."
};
fs.writeFileSync(path.join(evidenceDir, "verify_tablet_04_offline_export.json"), JSON.stringify(report, null, 2) + "\n", "utf8");
console.log(JSON.stringify(report, null, 2));
process.exit(ok ? 0 : 2);
