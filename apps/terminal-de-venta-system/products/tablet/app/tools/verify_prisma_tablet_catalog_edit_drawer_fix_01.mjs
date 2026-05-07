#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const checks = [
  ["components/catalog/catalog-screen.tsx", "beginEditProduct"],
  ["components/catalog/catalog-screen.tsx", "drawerDockRef"],
  ["components/catalog/catalog-screen.tsx", "scrollIntoView"],
  ["components/catalog/catalog-screen.tsx", "[data-catalog-field='name']"],
  ["components/catalog/catalog-product-table.tsx", "aria-pressed"],
  ["components/catalog/catalog-product-table.tsx", "Editando"],
  ["components/catalog/catalog-product-form.tsx", "data-catalog-field=\"name\""],
  ["components/catalog/catalog-product-form.tsx", "Modo edición"],
  ["components/catalog/catalog.module.css", "PRISMA_TABLET_CATALOG_EDIT_DRAWER_FIX_01"],
  ["components/catalog/catalog.module.css", ".drawerDock[data-editing=\"true\"] .drawer"],
];

const missing = [];
for (const [rel, needle] of checks) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    missing.push(`${rel} missing`);
    continue;
  }
  const text = fs.readFileSync(file, "utf8");
  if (!text.includes(needle)) missing.push(`${rel} missing marker ${needle}`);
}

const forbiddenNeedles = [
  "app/api/pos/sales/complete",
  "products/pc/app",
  "shared-kernel",
  "prisma/schema",
];
for (const rel of [
  "components/catalog/catalog-screen.tsx",
  "components/catalog/catalog-product-table.tsx",
  "components/catalog/catalog-product-form.tsx",
  "components/catalog/catalog.module.css",
]) {
  const file = path.join(appRoot, rel);
  const text = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  for (const needle of forbiddenNeedles) {
    if (text.includes(needle)) missing.push(`${rel} contains forbidden marker ${needle}`);
  }
}

if (missing.length) {
  console.error(`[PRISMA_TABLET_CATALOG_EDIT_DRAWER_FIX_01] BLOCKED`);
  for (const item of missing) console.error(` - ${item}`);
  process.exit(1);
}

console.log(`[PRISMA_TABLET_CATALOG_EDIT_DRAWER_FIX_01] READY`);
console.log("Catalog edit feedback markers are installed.");
