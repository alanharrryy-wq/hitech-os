#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const matrix = JSON.parse(fs.readFileSync(path.join(root, "tools", "fixtures", "tablet_home_view_model_03c_matrix.json"), "utf8"));
const source = fs.readFileSync(path.join(root, "src", "lib", "tablet-home", "home-view-model.ts"), "utf8");
let failed = false;
function ok(message){ console.log(`OK ${message}`); }
function fail(message){ console.error(`FAIL ${message}`); failed = true; }
function expectedPrimary(input){ if(input.shift === "closed") return "Abrir turno"; if(input.pending > 0) return "Ver pendientes"; if(input.lowStockProducts > 0) return "Ver existencias"; return "Ir a vender"; }
[
  "buildTabletHomeViewModel",
  "const primaryHref = getRuntimeActionHref(snapshot)",
  "const primaryLabel = getRuntimeActionLabel(snapshot)",
  "metrics:",
  "actions:",
  "alerts:",
  "checklist:"
].forEach((needle)=> source.includes(needle) ? ok(`home source ${needle}`) : fail(`home source missing ${needle}`));
for (const item of matrix.cases) {
  const expected = expectedPrimary(item.input);
  if (item.expected.primaryLabel !== expected) fail(`${item.name}: expected primary ${expected} got ${item.expected.primaryLabel}`);
  if (!Array.isArray(item.expected.mustHaveMetrics) || item.expected.mustHaveMetrics.length !== 4) fail(`${item.name}: metric contract incomplete`);
  ok(`home view model matrix ${item.name}`);
}
if (failed) process.exit(1);
ok(`home view model matrix passed ${matrix.cases.length} cases`);
