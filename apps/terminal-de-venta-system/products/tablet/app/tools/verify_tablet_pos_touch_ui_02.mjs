#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const checks = [
  ["app/pos/page.tsx", "PosScreen"],
  ["app/checkout/page.tsx", "CheckoutScreen"],
  ["app/catalog/page.tsx", "CatalogScreen"],
  ["app/sales/today/page.tsx", "SalesTodayScreen"],
  ["app/inventory/low-stock/page.tsx", "LowStockScreen"],
  ["app/events/outbox/page.tsx", "OutboxEventsScreen"],
  ["app/settings/export/page.tsx", "ExportSettingsScreen"],
  ["app/prisma-dark-pos-reference/page.tsx", "PrismaDarkPosShell"],
  ["app/referencia-visual/page.tsx", "PrismaDarkSelector"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TouchProductSearch"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TouchProductList"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TouchCart"],
  ["components/tablet-pos/touch-pos-ui.tsx", "CheckoutButton"],
  ["components/tablet-pos/touch-pos-ui.tsx", "TicketSummary"],
  ["components/tablet-pos/touch-pos-ui.tsx", "RuntimeStatus"],
  ["components/tablet-pos/touch-pos-ui.tsx", "OutboxMiniPanel"],
  ["components/tablet-pos/touch-pos-ui.tsx", "OperationalError"],
  ["components/tablet-pos/touch-pos-ui.tsx", "ExportButton"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/products/search"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/products/resolve"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/sales/complete"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/sales/today"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/events/outbox"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/inventory/low-stock"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/reports/operational-today"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/export/sales-today?format=json"],
  ["components/tablet-pos/touch-pos-ui.tsx", "/api/pos/export/events?format=csv"],
  ["components/tablet-pos/touch-pos.module.css", "checkoutButton"],
  ["src/modules/pos/module.manifest.ts", "/pos"],
  ["src/composition/module-registry.ts", "PosModule"],
  ["../../../MANIFEST.tablet-pos-touch-ui-full-02.json", "PRISMA_TABLET_POS_TOUCH_UI_FULL_02"]
];

let failed = false;
for (const [rel, marker] of checks) {
  const full = path.resolve(appRoot, rel);
  if (!existsSync(full)) {
    console.error(`[tablet-pos-ui-02] missing file: ${rel}`);
    failed = true;
    continue;
  }
  const text = readFileSync(full, "utf8");
  if (!text.includes(marker)) {
    console.error(`[tablet-pos-ui-02] marker missing in ${rel}: ${marker}`);
    failed = true;
  } else {
    console.log(`[tablet-pos-ui-02] ok ${rel}: ${marker}`);
  }
}

const forbidden = [
  "tools/_local/data/terminal-de-venta-system/canonical.db",
  "PC_REQUIRED_TO_SELL",
  "fake success",
  "*.zip",
  "*.log"
];

for (const rel of ["components/tablet-pos/touch-pos-ui.tsx", "app/pos/page.tsx", "app/checkout/page.tsx"]) {
  const text = readFileSync(path.resolve(appRoot, rel), "utf8");
  for (const marker of forbidden) {
    if (text.includes(marker)) {
      console.error(`[tablet-pos-ui-02] forbidden marker in ${rel}: ${marker}`);
      failed = true;
    }
  }
}

if (failed) {
  console.error("[tablet-pos-ui-02] Verify failed.");
  process.exit(1);
}

console.log("[tablet-pos-ui-02] Verify OK.");
