#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const matrix = JSON.parse(fs.readFileSync(path.join(root, "tools", "fixtures", "tablet_runtime_builder_03b_matrix.json"), "utf8"));
const builder = fs.readFileSync(path.join(root, "src", "server", "tablet-runtime-snapshot", "build.ts"), "utf8");
let failed = false;
function ok(message){ console.log(`OK ${message}`); }
function fail(message){ console.error(`FAIL ${message}`); failed = true; }
function expectedConnection(input){ if(input.conflictEvents>0 || input.failedEvents>0) return "Revisar pendientes"; if(input.pendingEvents>0) return "Pendientes por enviar"; return "En linea"; }
function expectedCatalog(input){ if(input.activeProducts<=0) return "Catalogo vacio"; if(input.lowStockProducts>0) return "Revisar existencias"; return "Catalogo listo"; }
function expectedShift(input){ return input.openShift ? "Turno abierto" : "Turno cerrado"; }
const sourceContracts = [
  "resolveConnectionState",
  "resolveCatalogState",
  "buildTabletRuntimeSnapshot",
  "localSalesAllowed: true",
  "pcRequiredForBasicSale: false",
  "TABLET_RUNTIME_VISIBLE_COPY.connection",
  "TABLET_RUNTIME_VISIBLE_COPY.catalog"
];
for (const needle of sourceContracts) builder.includes(needle) ? ok(`builder source ${needle}`) : fail(`builder source missing ${needle}`);
for (const item of matrix.cases) {
  const input = item.input;
  if (item.expected.shift !== expectedShift(input)) fail(`${item.name}: shift matrix mismatch`);
  if (item.expected.connection !== expectedConnection(input)) fail(`${item.name}: connection matrix mismatch`);
  if (item.expected.catalog !== expectedCatalog(input)) fail(`${item.name}: catalog matrix mismatch`);
  if (item.expected.localSalesAllowed !== true) fail(`${item.name}: local sales must remain true`);
  if (item.expected.pcRequiredForBasicSale !== false) fail(`${item.name}: pc requirement must remain false`);
  ok(`runtime builder matrix ${item.name}`);
}
if (failed) process.exit(1);
ok(`runtime builder matrix passed ${matrix.cases.length} cases`);
