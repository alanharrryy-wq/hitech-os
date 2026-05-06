#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}
function signal(item) {
  if (!item.isActive) return "inactive";
  if ((item.stockOnHand ?? 0) <= 0) return "out_of_stock";
  if ((item.stockOnHand ?? 0) <= Math.max(1, item.lowStockThreshold ?? 5)) return "low_stock";
  return "available";
}
function canAdd(item) {
  const s = signal(item);
  return s === "available" || s === "low_stock";
}
const root = path.resolve(arg("--root", process.cwd()));
const file = path.join(root, "tools/fixtures/tablet_catalog_stock_selling_assist_extended_scenarios_03j_03k.json");
const data = JSON.parse(fs.readFileSync(file, "utf8"));
const summary = { available: 0, low_stock: 0, out_of_stock: 0, inactive: 0 };
for (const scenario of data.scenarios) {
  const actualSignal = signal(scenario);
  if (actualSignal !== scenario.expectedSignal) {
    throw new Error(`${scenario.id} expected ${scenario.expectedSignal} got ${actualSignal}`);
  }
  if (canAdd(scenario) !== scenario.canAddToSale) {
    throw new Error(`${scenario.id} expected canAddToSale ${scenario.canAddToSale}`);
  }
  if (!Array.isArray(scenario.searchTerms) || scenario.searchTerms.length < 4) {
    throw new Error(`${scenario.id} missing search terms`);
  }
  summary[actualSignal] += 1;
}
for (const required of ["available", "low_stock", "out_of_stock", "inactive"]) {
  if (!summary[required]) throw new Error(`No scenarios for ${required}`);
}
console.log(`OK extended scenarios ${data.scenarioCount}`);
console.log(`OK buckets ${JSON.stringify(summary)}`);
console.log("READY extended catalog-stock-selling-assist scenarios");
