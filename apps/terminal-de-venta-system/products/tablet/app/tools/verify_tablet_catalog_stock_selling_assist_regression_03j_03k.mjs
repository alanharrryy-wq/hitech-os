#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}
function normalize(value) {
  return String(value ?? "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
}
function signal(product) {
  if (!product.isActive) return "inactive";
  if ((product.stockOnHand ?? 0) <= 0) return "out_of_stock";
  if ((product.stockOnHand ?? 0) <= Math.max(1, product.lowStockThreshold ?? 5)) return "low_stock";
  return "available";
}
function canAdd(product) {
  const s = signal(product);
  return s === "available" || s === "low_stock";
}
function matches(product, query) {
  const q = normalize(query);
  const haystack = [product.name, product.sku, product.category, product.barcode, ...(product.barcodes ?? [])].map(normalize).join(" ");
  return haystack.includes(q);
}

const root = path.resolve(arg("--root", process.cwd()));
const fixturePath = path.join(root, "tools/fixtures/tablet_catalog_stock_selling_assist_casebook_03j_03k.json");
const regressionPath = path.join(root, "tools/fixtures/tablet_catalog_stock_selling_assist_regression_03j_03k.json");
const fixture = JSON.parse(fs.readFileSync(fixturePath, "utf8"));
const regression = JSON.parse(fs.readFileSync(regressionPath, "utf8"));
const checks = [];

for (const product of fixture.products) {
  const actualSignal = signal(product);
  if (actualSignal !== product.expectedSignal) throw new Error(`${product.id} expected ${product.expectedSignal} got ${actualSignal}`);
  if (canAdd(product) !== product.canAdd) throw new Error(`${product.id} expected canAdd ${product.canAdd}`);
  checks.push(`OK product ${product.sku} -> ${actualSignal} canAdd=${product.canAdd}`);
}

const searchCases = [
  ["refresco", "p_available"],
  ["AGU-1L", "p_low"],
  ["7501000000058", "p_available_2"],
  ["promocion", "p_inactive_2"]
];
for (const [query, expectedId] of searchCases) {
  const found = fixture.products.find((product) => matches(product, query));
  if (!found || found.id !== expectedId) throw new Error(`Search ${query} expected ${expectedId}`);
  checks.push(`OK search ${query} -> ${expectedId}`);
}

for (const gate of regression.gates) {
  if (gate.requiredRoutes) {
    for (const rel of gate.requiredRoutes) {
      if (!fs.existsSync(path.join(root, rel))) throw new Error(`Missing route ${rel}`);
      checks.push(`OK route ${rel}`);
    }
  }
  if (gate.requiredStates) {
    const vm = fs.readFileSync(path.join(root, "src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model.ts"), "utf8");
    for (const state of gate.requiredStates) {
      if (!vm.includes(state)) throw new Error(`Missing state ${state}`);
      checks.push(`OK state ${state}`);
    }
  }
}

console.log(checks.join("\n"));
console.log(`READY regression ${checks.length} checks`);
