#!/usr/bin/env node
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const terminalRoot = path.resolve(fileURLToPath(new URL("..", import.meta.url)));
const mode = process.argv.find((arg) => arg.startsWith("--mode="))?.slice("--mode=".length) ?? "all";
const outPath = process.argv.find((arg) => arg.startsWith("--out="))?.slice("--out=".length) ?? "";
const certifiedDay = process.env.PRISMA_DATA_SURFACE_DATE ?? "2026-07-05";
const forbiddenCopy = /\b(demo|dummy|seed|test|prueba|sandbox|mock|fixture)\b/i;

function rel(...parts) {
  return path.join(terminalRoot, ...parts);
}

function read(file) {
  return fs.readFileSync(rel(file), "utf8");
}

function assert(condition, message, evidence = undefined) {
  if (!condition) {
    const error = new Error(message);
    error.evidence = evidence;
    throw error;
  }
}

function openDb(file) {
  return new DatabaseSync(rel(file), { readOnly: true });
}

function scalar(db, sql, params = []) {
  const row = db.prepare(sql).get(...params);
  return Number(Object.values(row ?? { value: 0 })[0] ?? 0);
}

function rows(db, sql, params = []) {
  return db.prepare(sql).all(...params);
}

function startOfDay(day) {
  return new Date(`${day}T00:00:00`);
}

function addDays(date, days) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function stamp(date) {
  return date.toISOString().slice(0, 19);
}

function salesStats(db, businessId, from, toExclusive) {
  const row = db.prepare(`
    SELECT COUNT(*) AS tickets, COALESCE(SUM(totalCents), 0) AS totalCents
    FROM Sale
    WHERE businessId = ? AND status IN ('PAID', 'COMPLETED') AND createdAt >= ? AND createdAt < ?
  `).get(businessId, stamp(from), stamp(toExclusive));
  const tickets = Number(row?.tickets ?? 0);
  const totalCents = Number(row?.totalCents ?? 0);
  return {
    tickets,
    totalCents,
    averageTicketCents: tickets ? Math.round(totalCents / tickets) : 0
  };
}

function businessId(db) {
  return String(db.prepare("SELECT id FROM Business ORDER BY createdAt ASC LIMIT 1").get()?.id ?? "");
}

function stringLiterals(source) {
  const matches = [];
  const regex = /(["'`])((?:\\.|(?!\1)[\s\S])*?)\1/g;
  for (const match of source.matchAll(regex)) {
    matches.push({ value: match[2], index: match.index ?? 0 });
  }
  return matches;
}

function lineForIndex(source, index) {
  return source.slice(0, index).split(/\r?\n/).length;
}

function assertNoForbiddenVisibleCopy(files, exemptions = []) {
  const hits = [];
  for (const file of files) {
    const source = read(file);
    for (const literal of stringLiterals(source)) {
      if (!forbiddenCopy.test(literal.value)) continue;
      const line = lineForIndex(source, literal.index);
      const lineText = source.split(/\r?\n/)[line - 1] ?? "";
      if (exemptions.some((exemption) => exemption(file, literal.value, lineText))) continue;
      hits.push({ file, line, value: literal.value });
    }
  }
  assert(hits.length === 0, "Forbidden customer-facing copy detected", hits);
}

function pcVerifier() {
  const db = openDb("products/pc/app/data/canonical.db");
  try {
    const biz = businessId(db);
    const today = startOfDay(certifiedDay);
    const tomorrow = addDays(today, 1);
    const recentFrom = addDays(today, -29);
    const todayStats = salesStats(db, biz, today, tomorrow);
    const recentStats = salesStats(db, biz, recentFrom, tomorrow);
    const storeCount = scalar(db, "SELECT COUNT(*) FROM Store WHERE businessId = ?", [biz]);
    const terminalCount = scalar(db, "SELECT COUNT(*) FROM Terminal WHERE businessId = ? AND isActive = 1", [biz]);

    const page = read("products/pc/app/app/sales-control/page.tsx");
    const api = read("products/pc/app/app/api/backoffice/sales-control/route.ts");
    const service = read("products/pc/app/src/server/services/pc-command-center.service.ts");
    const component = read("products/pc/app/components/control/sales-control-branch-view.tsx");
    const dropdown = read("products/pc/app/src/server/services/pc-data-mode-contract.service.ts");
    const smartDock = read("products/pc/app/components/uiux/smart-dropdown-dock.tsx");

    assert(page.includes("getPcSalesControl"), "PC sales-control page does not call getPcSalesControl");
    assert(api.includes("getPcSalesControl"), "PC sales-control API does not call getPcSalesControl");
    assert(service.includes("lastThirtyDayRange") && service.includes("recentActivity"), "PC loader lacks recent activity range");
    assert(service.includes("db.sale.findMany") && service.includes("paymentTenders") && service.includes("terminal: { include: { store: true } }"), "PC loader does not include real Sale relations");
    assert(component.includes("recentActivity") && component.includes("actividad reciente"), "PC UI does not surface recent activity");
    assert(dropdown.includes("Store") && dropdown.includes("Terminal") && dropdown.includes("Product"), "PC dropdown contract lacks canonical table candidates");
    assert(smartDock.includes("dbBackedCount"), "PC SmartDropdownDock does not expose DB-backed coverage");
    assert(recentStats.tickets > 0 && recentStats.totalCents > 0, "PC canonical.db has no recent activity to prove");
    assert(storeCount > 0 && terminalCount > 0, "PC stores/tablets are not readable from canonical.db", { storeCount, terminalCount });
    assert(todayStats.tickets === 0 || todayStats.totalCents > 0, "PC today metrics are inconsistent");

    assertNoForbiddenVisibleCopy([
      "products/pc/app/app/sales-control/page.tsx",
      "products/pc/app/components/control/sales-control-branch-view.tsx",
      "products/pc/app/components/uiux/smart-dropdown-dock.tsx"
    ]);

    return { surface: "pc-sales-control", ok: true, todayStats, recentStats, storeCount, terminalCount };
  } finally {
    db.close();
  }
}

function tabletVerifier() {
  const db = openDb("products/tablet/app/data/tablet-pos.db");
  try {
    const biz = businessId(db);
    const today = startOfDay(certifiedDay);
    const tomorrow = addDays(today, 1);
    const recentFrom = addDays(today, -29);
    const todayStats = salesStats(db, biz, today, tomorrow);
    const recentStats = salesStats(db, biz, recentFrom, tomorrow);
    const productCount = scalar(db, "SELECT COUNT(*) FROM Product WHERE businessId = ? AND isActive = 1", [biz]);
    const stockCount = scalar(db, "SELECT COUNT(*) FROM StockSnapshot WHERE businessId = ?", [biz]);
    const cashCount = scalar(db, "SELECT COUNT(*) FROM CashSession WHERE businessId = ?", [biz]);

    const page = read("products/tablet/app/app/pos/page.tsx");
    const salesRoute = read("products/tablet/app/app/api/pos/sales/today/route.ts");
    const salesLoader = read("products/tablet/app/src/server/pos-api/sales-summary.prisma.ts");
    const runtimeLoader = read("products/tablet/app/src/server/tablet-runtime-snapshot/queries.prisma.ts");
    const productSearch = read("products/tablet/app/app/api/pos/products/search/route.ts");
    const lowStock = read("products/tablet/app/app/api/pos/inventory/low-stock/route.ts");

    assert(page.includes("getTabletRuntimeSnapshot") && page.includes("PosScreen"), "Tablet POS page is not wired to runtime snapshot and PosScreen");
    assert(salesRoute.includes("getTodaySalesSummary"), "Tablet sales today route does not call sales loader");
    assert(salesLoader.includes("prisma.sale.findMany") && salesLoader.includes("include: { lines: true }") && salesLoader.includes("PAID"), "Tablet sales loader does not read closed Sale/SaleLine rows");
    assert(runtimeLoader.includes("resolveCatalog") && runtimeLoader.includes("resolveOpenShift") && runtimeLoader.includes("resolveSales"), "Tablet summary loader does not cover catalog/cash/sales");
    assert(productSearch.includes("searchProducts") && productSearch.includes("listLocalCatalogProducts"), "Tablet product search route lacks DB/local catalog path");
    assert(lowStock.includes("getLowStockProducts"), "Tablet low-stock route lacks inventory loader");
    assert(productCount > 0 && stockCount > 0 && cashCount > 0 && recentStats.tickets > 0, "Tablet DB operational data not readable", { productCount, stockCount, cashCount, recentStats });

    assertNoForbiddenVisibleCopy([
      "products/tablet/app/app/pos/page.tsx",
      "products/tablet/app/src/server/tablet-runtime-snapshot/build.ts",
      "products/tablet/app/src/lib/tablet-runtime-snapshot/visible-copy.ts"
    ]);

    return { surface: "tablet-pos", ok: true, contract: "operative sales surface, not required to be historical dashboard", todayStats, recentStats, productCount, stockCount, cashCount };
  } finally {
    db.close();
  }
}

function mobileVerifier() {
  const tabletDb = openDb("products/tablet/app/data/tablet-pos.db");
  try {
    const biz = businessId(tabletDb);
    const today = startOfDay(certifiedDay);
    const tomorrow = addDays(today, 1);
    const recentFrom = addDays(today, -29);
    const todayStats = salesStats(tabletDb, biz, today, tomorrow);
    const recentStats = salesStats(tabletDb, biz, recentFrom, tomorrow);
    const productCount = scalar(tabletDb, "SELECT COUNT(*) FROM Product WHERE businessId = ? AND isActive = 1", [biz]);

    const route = read("products/mobile/app/app/api/mobile/snapshot/route.ts");
    const stateLoader = read("products/mobile/app/src/lib/prisma-app/mobile-data-plane/state-loader.ts");
    const localDb = read("products/mobile/app/src/lib/prisma-app/mobile-data-plane/local-db-snapshot.ts");
    const readiness = read("products/mobile/app/src/lib/prisma-app/mobile-data-plane/data-readiness.ts");
    const contracts = read("products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts");
    const dashboard = read("products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx");
    const navigator = read("products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");

    assert(route.includes("runtime = \"nodejs\"") && route.includes("loadMobileDataPlaneState"), "Mobile snapshot API is not server/node loader backed");
    assert(stateLoader.includes("readLocalDbSnapshot") && stateLoader.includes("localOnlySnapshot"), "Mobile state loader lacks local DB-backed fallback");
    assert(localDb.includes("tablet-pos.db") && localDb.includes("readOnly: true") && localDb.includes("PAID"), "Mobile local adapter is not read-only tablet-pos backed for closed sales");
    assert(!/\b(INSERT|UPDATE|DELETE|CREATE|DROP)\b/i.test(localDb), "Mobile local adapter contains write SQL");
    assert(contracts.includes("recentActivity"), "Mobile sales contract lacks recent activity");
    assert(readiness.includes("heartbeat Tablet no certificado") && !readiness.includes("Tablet POS no respondió") && !readiness.includes("Tablet sin respuesta"), "Mobile readiness still exposes false unavailable copy");
    assert(!navigator.includes("contractMountShelf"), "Mobile customer navigator still contains hidden contractMountShelf");
    assert(!navigator.includes("systemCrystalHome") && !navigator.includes("systemContextSwitcher"), "Mobile customer navigator exposes Crystal/Contexto props");
    assert(dashboard.includes("/branding/prisma/prisma-mobile-header-mark-256.webp"), "Mobile dashboard does not use clean branding asset");
    assert(recentStats.tickets > 0 && productCount > 0, "Mobile source DB has no available operational data", { recentStats, productCount });
    assert(todayStats.tickets === 0 || todayStats.totalCents > 0, "Mobile today metrics are inconsistent");

    assertNoForbiddenVisibleCopy([
      "products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx",
      "products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
      "products/mobile/app/src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
      "products/mobile/app/src/lib/prisma-app/mobile-data-plane/diagnostics.ts",
      "products/mobile/app/src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
      "products/mobile/app/src/lib/prisma-app/mobile-intelligence/alert-engine.ts",
      "products/mobile/app/src/lib/prisma-app/mobile-intelligence/health-radar-engine.ts",
      "products/mobile/app/src/lib/prisma-app/prisma-mobile-api-client.ts"
    ]);

    return { surface: "mobile", ok: true, todayStats, recentStats, productCount };
  } finally {
    tabletDb.close();
  }
}

function chartSignatureCount(db, table, specs) {
  const columns = rows(db, `PRAGMA table_info("${table}")`).map((row) => String(row.name));
  const wh = [];
  const params = [];
  for (const [column, op, value] of specs) {
    if (!columns.includes(column)) continue;
    wh.push(`"${column}" ${op} ?`);
    params.push(value);
  }
  if (!wh.length) return 0;
  return scalar(db, `SELECT COUNT(*) FROM "${table}" WHERE ${wh.join(" OR ")}`, params);
}

function chartVerifier() {
  const db = openDb("products/chart-lab/app/data/chart-runtime-governance.db");
  try {
    const specs = {
      runtime_sources: [["sourceKey", "LIKE", "lifecycle-%"], ["path", "=", "PRISMA_DATA_LIFECYCLE"], ["sourceKind", "=", "generated"]],
      runtime_metadata: [["key", "LIKE", "lifecycle.batch.%"]],
      runtime_chart_payloads: [["chartKey", "LIKE", "lifecycle-%"], ["sourceMode", "=", "prisma_data_lifecycle"], ["payloadJson", "LIKE", "%PRISMA Data Lifecycle%"]]
    };
    const counts = Object.fromEntries(Object.entries(specs).map(([table, tableSpecs]) => [table, chartSignatureCount(db, table, tableSpecs)]));
    const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
    const lifecycleApi = read("prisma-control-center/internal/py/lifecycle_api.py");
    const shell = read("products/chart-lab/app/src/components/PrismaChartLabShell.tsx");
    const runtimeData = read("products/chart-lab/app/src/prisma-charts/chart-runtime-data.ts");

    assert(counts.runtime_chart_payloads === 6, "Chart Lab runtime payload count should be six without predicate double count", counts);
    assert(total === 8, "Chart Lab external signature total should separate sources/metadata/payloads", counts);
    assert(lifecycleApi.includes("if table in _V6_CHART_SIGNATURES") && lifecycleApi.includes("external_signature_records_open"), "Data Lifecycle API does not guard Chart Lab double count");
    assert(shell.includes("publicDataStatusLabel") && shell.includes("Reference"), "Chart Lab shell does not sanitize visible technical labels");
    assert(runtimeData.includes("reference data") && !runtimeData.includes("deterministic mocks"), "Chart Lab freshness label is not customer-safe");

    assertNoForbiddenVisibleCopy([
      "products/chart-lab/app/src/components/PrismaChartLabShell.tsx",
      "products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts",
      "products/chart-lab/app/src/prisma-charts/chart-runtime-data.ts"
    ], [
      (_file, value) => value === "stress-demo",
      (_file, value, line) => line.includes("sourceMode") && value === "mock-fallback",
      (_file, value) => value === "shared/mock" || value === "lab/mock"
    ]);

    return { surface: "chart-lab", ok: true, counts, total };
  } finally {
    db.close();
  }
}

function lifecycleVerifier() {
  const api = read("prisma-control-center/internal/py/lifecycle_api.py");
  const consoleJs = read("prisma-control-center/internal/web/lifecycle_console.js");
  assert(api.includes("CREATE TABLE IF NOT EXISTS lifecycle_pins"), "Lifecycle API does not create/use lifecycle_pins");
  assert(!api.includes("CREATE TABLE IF NOT EXISTS lifecycle_pin_tokens"), "Lifecycle API still creates lifecycle_pin_tokens");
  assert(api.includes("clear_candidates_open") && api.includes("ledger_records_open") && api.includes("external_signature_records_open"), "Lifecycle API does not expose separated counters");
  assert(consoleJs.includes("lifecycleTotalDbRows") && consoleJs.includes("lifecycleGeneratedLifecycleRows") && consoleJs.includes("lifecycleManualBaseRows"), "Lifecycle console does not render separated counters");
  assert(!consoleJs.includes("payload.ledger_records_open ?? payload.generated_records_open"), "Lifecycle console still mixes ledger and generated counters");
  return { surface: "data-lifecycle", ok: true, counters: ["clear_candidates_open", "ledger_records_open", "external_signature_records_open", "total_db_rows_open", "generated_lifecycle_records_open", "manual_or_base_records_open"], pinTable: "lifecycle_pins" };
}

const verifiers = {
  pc: pcVerifier,
  tablet: tabletVerifier,
  mobile: mobileVerifier,
  chart: chartVerifier,
  lifecycle: lifecycleVerifier
};

const selected = mode === "all" ? Object.keys(verifiers) : mode.split(",").map((item) => item.trim()).filter(Boolean);
const results = [];
const failures = [];

for (const key of selected) {
  const verifier = verifiers[key];
  if (!verifier) {
    failures.push({ surface: key, error: "unknown verifier mode" });
    continue;
  }
  try {
    results.push(verifier());
  } catch (error) {
    failures.push({ surface: key, error: error.message, evidence: error.evidence ?? null });
  }
}

const payload = {
  ok: failures.length === 0,
  checkedAt: new Date().toISOString(),
  certifiedDay,
  mode,
  results,
  failures
};

if (outPath) {
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(payload, null, 2));
}

console.log(JSON.stringify(payload, null, 2));
if (!payload.ok) process.exit(1);
