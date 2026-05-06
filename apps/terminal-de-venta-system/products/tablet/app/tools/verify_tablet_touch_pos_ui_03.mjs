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
  if (text && !text.includes(marker)) fail(`${file} missing marker: ${marker}`);
}

const ui = readRel("components/tablet-pos/touch-pos-ui.tsx");
const css = readRel("components/tablet-pos/touch-pos.module.css");

for (const [file, marker] of [
  ["app/pos/page.tsx", "PosScreen"],
  ["app/checkout/page.tsx", "CheckoutScreen"],
  ["app/sales/today/page.tsx", "SalesTodayScreen"],
  ["app/inventory/low-stock/page.tsx", "LowStockScreen"],
  ["app/events/outbox/page.tsx", "OutboxEventsScreen"],
  ["app/settings/export/page.tsx", "ExportSettingsScreen"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TouchProductSearch"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TouchCart"],
  ["components/tablet-pos/touch-pos-ui.tsx", "CheckoutButton"],
  ["components/tablet-pos/touch-pos-ui.tsx", "OperationalError"],
  ["components/tablet-pos/touch-pos-ui.tsx", "OutboxMiniPanel"],
  ["components/tablet-pos/touch-pos-ui.tsx", "RuntimeStatus"],
  ["components/tablet-pos/touch-pos-ui.tsx", "ExportButton"]
]) {
  requireMarker(file, marker);
}

for (const marker of [
  "Buscar producto, SKU o código",
  "Resolver código",
  "Ticket actual",
  "COBRAR",
  "Nueva venta",
  "navigator.onLine",
  "pendientes por enviar",
  "/api/pos/products/search",
  "/api/pos/products/resolve",
  "/api/pos/sales/complete",
  "/api/pos/reports/operational-today",
  "/api/pos/events/outbox",
  "/api/pos/inventory/low-stock",
  "/api/pos/export/sales-today?format=json",
  "/api/pos/export/events?format=csv",
  "INSUFFICIENT_STOCK",
  "NETWORK_UNAVAILABLE",
  "SYNC_PENDING"
]) {
  if (!ui.includes(marker)) fail(`touch-pos-ui.tsx missing operator-flow marker: ${marker}`);
}

for (const marker of [
  "min-height: 76px",
  "grid-template-columns: minmax(0, 1fr) minmax(360px, 430px)",
  "grid-template-columns: repeat(3, minmax(0, 1fr))",
  "@media (max-width: 900px)",
  ".checkoutButton",
  ".searchInput",
  ".cartPanel",
  ".runtimeBar",
  ".operationalError"
]) {
  if (!css.includes(marker)) fail(`touch-pos.module.css missing touch/responsive marker: ${marker}`);
}

const forbidden = [
  "tools/_local/data/terminal-de-venta-system/canonical.db",
  "PC_REQUIRED_TO_SELL",
  "PC required",
  "/api/backoffice",
  "getBackofficeModuleOverview"
];

for (const rel of ["components/tablet-pos/touch-pos-ui.tsx", "app/pos/page.tsx", "app/checkout/page.tsx"]) {
  const text = readRel(rel);
  for (const marker of forbidden) {
    if (text.includes(marker)) fail(`${rel} contains forbidden PC/backoffice dependency marker: ${marker}`);
  }
}

const posErrors = readRel("src/server/pos-api/errors.ts");
for (const code of [
  "EMPTY_CART",
  "INVALID_QUANTITY",
  "PRODUCT_NOT_FOUND",
  "PRODUCT_INACTIVE",
  "INSUFFICIENT_STOCK",
  "TERMINAL_NOT_FOUND",
  "NETWORK_UNAVAILABLE",
  "SYNC_PENDING",
  "BUSINESS_NOT_FOUND"
]) {
  if (!posErrors.includes(code) || !ui.includes(code)) {
    fail(`POS error code must be mapped server-side and visible client-side: ${code}`);
  }
}

if (failures.length) {
  console.error("PRISMA_TABLET_TOUCH_POS_UI_03 failed");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("PRISMA_TABLET_TOUCH_POS_UI_03 passed");
console.log(JSON.stringify({
  routes: ["/pos", "/checkout", "/sales/today", "/inventory/low-stock", "/events/outbox", "/settings/export"],
  checks: ["search", "cart", "checkout", "errors", "offline/sync", "outbox", "exports"],
  browser: "static route/component verifier; final release gate performs live HTTP smoke"
}, null, 2));
