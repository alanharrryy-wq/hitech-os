import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "src/lib/prisma-app/mobile-data-plane/types.ts",
  "src/lib/prisma-app/mobile-data-plane/config.ts",
  "src/lib/prisma-app/mobile-data-plane/http.ts",
  "src/lib/prisma-app/mobile-data-plane/sales-adapter.ts",
  "src/lib/prisma-app/mobile-data-plane/inventory-adapter.ts",
  "src/lib/prisma-app/mobile-data-plane/outbox-adapter.ts",
  "src/lib/prisma-app/mobile-data-plane/pc-adapter.ts",
  "src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
  "src/lib/prisma-app/mobile-data-plane/state-loader.ts",
  "src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts",
  "src/lib/prisma-app/prisma-app-api-contracts.ts",
  "src/lib/prisma-app/prisma-mobile-api-client.ts",
  "app/api/mobile/snapshot/route.ts",
  "app/api/mobile/sales/today/route.ts",
  "tools/prisma_mobile_17_data_plane_regression_scenarios.ts"
];

const forbidden = [
  "prisma-app-api-demo-source",
  "prisma-app-demo-data",
  "demo-contract-fixture"
];

function read(rel) {
  const file = path.join(root, rel);
  if (!fs.existsSync(file)) throw new Error(`Falta archivo requerido: ${rel}`);
  return fs.readFileSync(file, "utf8");
}

let totalLoc = 0;
for (const rel of required) {
  const content = read(rel);
  totalLoc += content.split(/\r?\n/).filter((line) => line.trim()).length;
}

const routes = [
  "app/api/mobile/alerts/route.ts",
  "app/api/mobile/branches/route.ts",
  "app/api/mobile/cash/current/route.ts",
  "app/api/mobile/health/route.ts",
  "app/api/mobile/inventory/watchlist/route.ts",
  "app/api/mobile/reports/daily/route.ts",
  "app/api/mobile/sales/today/route.ts",
  "app/api/mobile/snapshot/route.ts",
  "app/api/mobile/summary/route.ts"
];

for (const rel of routes) {
  const content = read(rel);
  if (!content.includes("mobileDataPlane")) throw new Error(`${rel} no usa mobile data-plane.`);
  for (const bad of forbidden) {
    if (content.includes(bad)) throw new Error(`${rel} todavía contiene ${bad}.`);
  }
}

for (const rel of [
  "src/lib/prisma-app/prisma-app-api-contracts.ts",
  "src/lib/prisma-app/prisma-mobile-snapshot-contract.ts",
  "src/lib/prisma-app/prisma-mobile-api-client.ts"
]) {
  const content = read(rel);
  if (content.includes("demo-contract-fixture")) throw new Error(`${rel} conserva demo-contract-fixture.`);
}

const registry = read("tools/prisma_mobile_17_data_plane_regression_scenarios.ts");
const scenarioCount = (registry.match(/regression_data_plane_mapping/g) || []).length;
if (scenarioCount < 300) throw new Error(`Matriz de regresión demasiado chica: ${scenarioCount}`);
if (totalLoc < 2500) throw new Error(`LOC funcional insuficiente para esta integración: ${totalLoc}`);

console.log(JSON.stringify({ ok: true, integration: "PRISMA_APP_MOBILE_17_DATA_PLANE", files: required.length + routes.length, totalLoc, scenarioCount }, null, 2));
