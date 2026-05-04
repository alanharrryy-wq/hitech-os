#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}
const root = path.resolve(arg("--root", process.cwd()));
const smokePath = path.join(root, "tools/fixtures/tablet_catalog_stock_selling_assist_route_smokes_03j_03k.json");
const data = JSON.parse(fs.readFileSync(smokePath, "utf8"));
const routes = new Set();
const conditions = new Set();
for (const item of data.cases) {
  routes.add(item.route);
  conditions.add(item.condition);
  if (!Array.isArray(item.steps) || item.steps.length < 4) throw new Error(`${item.id} missing useful steps`);
  if (!String(item.expected || "").trim()) throw new Error(`${item.id} missing expected result`);
}
for (const requiredRoute of ["/catalog", "/stock", "/existencias", "/pos"]) {
  if (!routes.has(requiredRoute)) throw new Error(`Missing route smoke for ${requiredRoute}`);
}
for (const state of ["available", "low_stock", "out_of_stock", "inactive"]) {
  if (!conditions.has(state)) throw new Error(`Missing condition ${state}`);
}
console.log(`OK route smokes ${data.cases.length}`);
console.log("READY route smoke matrix");
