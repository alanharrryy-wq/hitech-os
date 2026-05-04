import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
let failed = false;

function ok(message) {
  console.log(`OK ${message}`);
}

function fail(message) {
  failed = true;
  console.error(`FAIL ${message}`);
}

function read(rel) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) {
    fail(`missing ${rel}`);
    return "";
  }
  ok(`exists ${rel}`);
  return fs.readFileSync(abs, "utf8");
}

const standardFiles = [
  "components/operational-screen/prisma-operational-screen.tsx",
  "components/operational-screen/prisma-operational-screen.module.css",
  "components/operational-screen/index.ts",
  "src/lib/ui/prisma-operational-screen-contract.ts",
  "src/lib/ui/prisma-operational-screen-engine.ts"
];

for (const rel of standardFiles) read(rel);

const page = read("app/stock/page.tsx");
read("docs/ux/PRISMA_TABLET_STOCK_SCREEN_01A_REAL_VIEW.md");
read("docs/qa/tablet-stock-screen-01a/acceptance.md");

function includes(text, needle, message) {
  if (text.includes(needle)) ok(message);
  else fail(`${message} (${needle})`);
}

function notIncludes(text, needle, message) {
  if (!text.toLowerCase().includes(needle.toLowerCase())) ok(message);
  else fail(`${message} (${needle})`);
}

includes(page, "PrismaOperationalScreen", "stock page uses operational standard");
includes(page, "getStockConsole", "stock page connects to stock service");
includes(page, "buildStockScreenModel", "stock page builds a screen model");
includes(page, "currentPath: \"/stock\"", "stock route marks active path");
includes(page, "Stock operativo", "stock page title is operational");
includes(page, "Vigilancia de existencias", "stock page declares primary table");
includes(page, "Reabasto sugerido", "stock page declares replenishment section");
includes(page, "Pulso por categoría", "stock page declares category pulse section");
includes(page, "Alertas de barcode", "stock page declares barcode alerts section");
includes(page, "catch (error)", "stock page handles service failure");

notIncludes(page, "<main style", "stock page removed inline main shell");
notIncludes(page, "Área operativa", "stock page removed old stub copy");
notIncludes(page, "según el plan activo", "stock page removed plan stub copy");
notIncludes(page, "placeholder", "stock page has no placeholder copy");
notIncludes(page, "provisional", "stock page has no provisional copy");
notIncludes(page, "new PrismaClient", "stock page does not create prisma client directly");
notIncludes(page, "schema.prisma", "stock page does not touch schema");
notIncludes(page, "create database", "stock page has no DB creation marker");

const forbiddenTargets = [
  "prisma/schema.prisma",
  "packages/shared-kernel",
  "shared-kernel"
];
for (const target of forbiddenTargets) {
  if (page.includes(target)) fail(`forbidden target reference present: ${target}`);
}

if (failed) {
  console.error("FAIL PRISMA_TABLET_STOCK_SCREEN_01A verification failed");
  process.exit(1);
}

console.log("OK PRISMA_TABLET_STOCK_SCREEN_01A verification passed");
