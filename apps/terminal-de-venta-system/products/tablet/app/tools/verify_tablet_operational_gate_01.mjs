#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const failures = [];
function full(rel) { return path.join(appRoot, rel); }
function read(rel) { return fs.readFileSync(full(rel), "utf8"); }
function mustExist(rel) { if (!fs.existsSync(full(rel))) failures.push(`missing ${rel}`); }
function mustInclude(rel, needle) { if (!read(rel).includes(needle)) failures.push(`missing ${needle} in ${rel}`); }
function mustNotInclude(rel, needle) { if (read(rel).includes(needle)) failures.push(`forbidden ${needle} in ${rel}`); }

const required = [
  "src/lib/operational-gate/can-sell.ts",
  "src/lib/tablet-runtime-snapshot/shell-contract.ts",
  "src/server/tablet-runtime-snapshot/build.ts",
  "components/tablet-shell/tablet-nav.ts",
  "src/lib/tablet-home/home-view-model.ts",
  "components/tablet-home/tablet-home-screen.tsx",
  "app/pos/page.tsx",
  "app/checkout/page.tsx",
  "app/api/pos/products/search/route.ts",
  "app/api/pos/products/resolve/route.ts",
  "components/pos/pos-screen.tsx",
  "components/pos/pos-product-list.tsx",
  "components/pos/pos-ticket-panel.tsx",
  "src/lib/pos/payment-flow.ts",
  "src/lib/pos/shift-flow.ts",
  "src/server/pos-engine/repository.prisma.ts"
];
required.forEach(mustExist);

if (!failures.length) {
  mustInclude("src/lib/operational-gate/can-sell.ts", "decideCanSellFromRuntimeSnapshot");
  mustInclude("src/lib/operational-gate/can-sell.ts", "canShowSellNavigation");
  mustInclude("src/lib/operational-gate/can-sell.ts", "canAddProduct");
  mustInclude("src/lib/operational-gate/can-sell.ts", "canCheckout");
  mustInclude("src/lib/operational-gate/can-sell.ts", "SHIFT_NOT_OPEN");
  mustInclude("src/lib/operational-gate/can-sell.ts", "LICENSE_BLOCKED");
  mustInclude("src/lib/operational-gate/can-sell.ts", "buildLicenseBlockedDecision");
  mustInclude("src/lib/operational-gate/can-sell.ts", "license.canUseLocalPos");
  mustInclude("src/lib/tablet-runtime-snapshot/shell-contract.ts", "TabletRuntimeLicense");
  mustInclude("src/lib/tablet-runtime-snapshot/shell-contract.ts", "license: TabletRuntimeLicense");
  mustInclude("src/server/tablet-runtime-snapshot/build.ts", "getTabletLicenseGovernor");
  mustInclude("src/server/tablet-runtime-snapshot/build.ts", "licenseGovernor.canUseLocalPos");
  mustInclude("app/api/pos/products/search/route.ts", "guardTabletFeatureForApi(\"pos.product.search\")");
  mustInclude("app/api/pos/products/resolve/route.ts", "guardTabletFeatureForApi(\"pos.product.search\")");
  mustInclude("components/tablet-shell/tablet-nav.ts", "Devoluciones");
  mustInclude("components/tablet-shell/tablet-nav.ts", "la pantalla /pos ya decide si permite cobrar");
  mustInclude("components/tablet-shell/tablet-nav.ts", "return TABLET_NAV_ITEMS");
  mustInclude("src/lib/tablet-home/home-view-model.ts", "gate.canShowSellNavigation");
  mustInclude("components/tablet-home/tablet-home-screen.tsx", `shiftOpen ? "/pos" : "/shift"`);
  mustInclude("app/pos/page.tsx", "getTabletRuntimeSnapshot");
  mustInclude("app/checkout/page.tsx", "getTabletRuntimeSnapshot");
  mustInclude("components/pos/pos-screen.tsx", `data-prisma-operational-gate="closed-cash"`);
  mustInclude("components/pos/pos-screen.tsx", "gate.canAddProduct");
  mustInclude("components/pos/pos-screen.tsx", "gate.canCheckout");
  mustInclude("components/pos/pos-product-list.tsx", "canAddProduct");
  mustInclude("components/pos/pos-ticket-panel.tsx", "!canCheckout || !lines.length");
  mustNotInclude("src/lib/pos/payment-flow.ts", "ensureLocalShiftOpenForSale");
  mustNotInclude("src/lib/pos/payment-flow.ts", "apiErrorCode(error)");
  mustNotInclude("src/lib/pos/shift-flow.ts", "/api/pos/shift/open");
  mustInclude("src/server/pos-engine/repository.prisma.ts", `PosEngineError("SHIFT_NOT_OPEN"`);
  mustInclude("tools/verify_prisma_tablet_pos_checkout_shift_autofix_00s.mjs", "NO_SHIFT_AUTOFIX");
}

const filesToScan = [
  "components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx",
  "components/sales/sales-today-screen.tsx",
  "components/sales/sales-ticket-detail-screen.tsx",
  "components/shift/shift-cash-closure-screen.tsx"
];
for (const rel of filesToScan) {
  if (!fs.existsSync(full(rel))) continue;
  const source = read(rel);
  if (source.includes('href="/pos"')) failures.push(`unguarded static href=/pos remains in ${rel}`);
}

if (failures.length) {
  console.error("BLOCKED PRISMA_TABLET_OPERATIONAL_GATE_01");
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log("PASS PRISMA_TABLET_OPERATIONAL_GATE_01");
console.log("Closed cash and license state both gate Tablet POS before product add, lookup, checkout and sale completion.");