#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const failures = [];

function fail(message) {
  failures.push(message);
}

function readRel(rel) {
  const full = path.join(appRoot, rel);
  if (!existsSync(full)) {
    fail(`Missing file: ${full}`);
    return "";
  }
  return readFileSync(full, "utf8");
}

function requireMarker(file, marker) {
  const text = readRel(file);
  if (text && !text.includes(marker)) {
    fail(`${file} missing marker: ${marker}`);
  }
}

const dashboard = readRel("src/lib/backoffice/dashboard.ts");
const route = readRel("app/api/backoffice/dashboard/route.ts");
const card = readRel("components/backoffice/kpi-card.tsx");
const executive = readRel("components/backoffice/executive-dashboard.tsx");

for (const key of [
  "netSalesTodayCents",
  "ticketCountToday",
  "averageTicketCents",
  "topSkus",
  "lowStockCount",
  "inventoryAccuracy",
  "shrinkage",
  "cancellationsReturns",
  "fillRate",
  "offlineModeUsage",
  "syncLatency"
]) {
  if (!dashboard.includes(`key: "${key}"`)) fail(`Dashboard missing KPI key: ${key}`);
}

for (const marker of [
  'status: "supported"',
  'status: "partial"',
  'status: "unavailable"',
  "source: string",
  "Sin fuente canónica",
  "No disponible",
  "prisma.sale.aggregate",
  "prisma.sale.count",
  "prisma.saleLine.findMany",
  "prisma.stockSnapshot.count",
  "prisma.auditCount.findMany",
  "prisma.saleReturn.count",
  "prisma.purchaseOrderLine.aggregate",
  "prisma.goodsReceiptLine.aggregate",
  "prisma.outboxEvent.findMany",
  "sentAt",
  "lastIngestAt: lastOutbox"
]) {
  if (!dashboard.includes(marker)) fail(`dashboard.ts missing marker: ${marker}`);
}

for (const marker of ["soportado", "parcial", "sin fuente", "Fuente:"]) {
  if (!card.includes(marker)) fail(`KpiCard does not display KPI source/status marker: ${marker}`);
}

if (!route.includes("GET /api/backoffice/dashboard")) {
  fail("Dashboard API route must expose endpoint metadata.");
}

if (!executive.includes("Top SKUs del día") || !executive.includes("Estado de sincronización")) {
  fail("Executive dashboard must render top SKUs and sync state sections.");
}

const unavailableKpis = ["shrinkage", "offlineModeUsage"];
for (const key of unavailableKpis) {
  const kpiBlock = dashboard.slice(dashboard.indexOf(`key: "${key}"`), dashboard.indexOf(`key: "${key}"`) + 450);
  if (!kpiBlock.includes('status: "unavailable"') || !kpiBlock.includes("No disponible")) {
    fail(`${key} must be explicitly unavailable, not faked.`);
  }
}

const partialKpis = ["inventoryAccuracy", "cancellationsReturns", "fillRate", "syncLatency"];
for (const key of partialKpis) {
  const kpiBlock = dashboard.slice(dashboard.indexOf(`key: "${key}"`), dashboard.indexOf(`key: "${key}"`) + 550);
  if (!kpiBlock.includes('status: "partial"')) {
    fail(`${key} must be classified as partial.`);
  }
}

if (failures.length) {
  console.error("PRISMA_PC_KPI_DASHBOARD_02 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_PC_KPI_DASHBOARD_02 passed");
console.log(JSON.stringify({
  supported: ["netSalesTodayCents", "ticketCountToday", "averageTicketCents", "topSkus", "lowStockCount", "pendingEvents", "conflictCount"],
  partial: partialKpis,
  unavailable: unavailableKpis,
  metadata: "per-kpi status/source"
}, null, 2));
