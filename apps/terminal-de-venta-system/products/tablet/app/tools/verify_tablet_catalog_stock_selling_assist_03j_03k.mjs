#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}

const root = path.resolve(arg("--root", process.cwd()));
const requiredFiles = [
  "app/catalog/page.tsx",
  "app/stock/page.tsx",
  "app/existencias/page.tsx",
  "components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx",
  "components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css",
  "src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-contract.ts",
  "src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model.ts",
  "src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts",
  "docs/architecture/PRISMA_TABLET_CATALOG_STOCK_SELLING_ASSIST_03J_03K_CONTRACT.md",
  "docs/ux/PRISMA_TABLET_CATALOG_STOCK_SELLING_ASSIST_03J_03K.md",
  "docs/qa/PRISMA_TABLET_CATALOG_STOCK_SELLING_ASSIST_03J_03K_CASEBOOK.md",
  "tools/fixtures/tablet_catalog_stock_selling_assist_casebook_03j_03k.json"
];

const checks = [];
function read(rel) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) throw new Error(`Missing required file: ${rel}`);
  return fs.readFileSync(full, "utf8");
}
function expect(rel, needle, label = needle) {
  const text = read(rel);
  if (!text.includes(needle)) throw new Error(`Expected ${label} in ${rel}`);
  checks.push(`OK ${rel} includes ${label}`);
}
for (const rel of requiredFiles) {
  read(rel);
  checks.push(`OK exists ${rel}`);
}
expect("app/catalog/page.tsx", "mode=\"catalog\"", "catalog mode");
expect("app/stock/page.tsx", "mode=\"stock\"", "stock mode");
expect("app/existencias/page.tsx", "mode=\"stock\"", "existencias stock mode");
expect("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx", "buildProductSearchUrl", "product search integration");
expect("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx", "resolveCode", "barcode/SKU resolve flow");
expect("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx", "OfflineStrip", "offline visible strip");
expect("components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx", "addSellingAssistProductToCart", "cart handoff");
expect("src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts", "POS_CART_STORAGE_KEY", "existing POS cart key");
expect("src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts", "addProductToCart", "existing cart engine");
for (const state of ["available", "low_stock", "out_of_stock", "inactive"]) {
  expect("src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model.ts", state, `state ${state}`);
}

console.log(checks.join("\n"));
console.log(`READY PRISMA_TABLET_CATALOG_STOCK_SELLING_ASSIST_03J_03K ${checks.length} checks`);
