import fs from "node:fs";
import path from "node:path";

function detectRoot() {
  const arg = process.argv[2];
  if (arg) return path.resolve(arg);
  const cwd = process.cwd();
  if (fs.existsSync(path.join(cwd, "products/mobile/app/package.json"))) return cwd;
  if (fs.existsSync(path.join(cwd, "package.json")) && fs.existsSync(path.join(cwd, "app/api/mobile/snapshot/route.ts"))) return path.resolve(cwd, "../../..");
  return cwd;
}

const root = detectRoot();
const failures = [];
function full(rel) { return path.join(root, rel); }
function read(rel) {
  if (!fs.existsSync(full(rel))) { failures.push(`missing ${rel}`); return ""; }
  return fs.readFileSync(full(rel), "utf8");
}
function mustContain(rel, markers) {
  const text = read(rel);
  for (const marker of markers) if (!text.includes(marker)) failures.push(`missing marker ${rel}: ${marker}`);
}
function mustNotContain(rel, markers) {
  const text = read(rel);
  for (const marker of markers) if (text.includes(marker)) failures.push(`forbidden marker ${rel}: ${marker}`);
}

const routeFiles = [
  "products/mobile/app/app/api/mobile/summary/route.ts",
  "products/mobile/app/app/api/mobile/sales/today/route.ts",
  "products/mobile/app/app/api/mobile/cash/current/route.ts",
  "products/mobile/app/app/api/mobile/inventory/watchlist/route.ts",
  "products/mobile/app/app/api/mobile/alerts/route.ts",
  "products/mobile/app/app/api/mobile/reports/daily/route.ts",
  "products/mobile/app/app/api/mobile/branches/route.ts",
  "products/mobile/app/app/api/mobile/health/route.ts"
];

for (const rel of routeFiles) {
  mustContain(rel, ["prisma-mobile-connected-source", "await getMobile", "okMobileResponse"]);
  mustNotContain(rel, ["prisma-app-api-demo-source"]);
}

mustContain("products/mobile/app/app/api/mobile/snapshot/route.ts", ["await getPrismaMobileSnapshotPayload()"]);
mustContain("products/mobile/app/src/lib/prisma-app/prisma-mobile-connected-source.ts", [
  "PRISMA_MOBILE_TABLET_ORIGIN",
  "PRISMA_MOBILE_PC_ORIGIN",
  "/api/pos/sales/today",
  "/api/pos/inventory/low-stock",
  "/api/backoffice/dashboard",
  "Sin fixture demo"
]);
mustContain("products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts", ["connected-runtime", "runtimeMode: \"connected\""]);
mustContain("products/mobile/app/src/lib/prisma-app/prisma-mobile-snapshot-contract.ts", ["connected-runtime", "runtimeMode: source === \"local-cache\" ? \"offline\" : \"connected\""]);
mustContain("products/mobile/app/src/lib/prisma-app/prisma-mobile-api-client.ts", ["No hay snapshot conectado", "Snapshot conectado", "APIs conectadas"]);
mustNotContain("products/mobile/app/src/lib/prisma-app/prisma-mobile-api-client.ts", ["Demo fallback", "demoClientSnapshot"]);
mustContain("docs/mobile/PRISMA_APP_MOBILE_16_CONNECTED_DATA_BRIDGE.md", ["Connected Data Bridge", "PRISMA_MOBILE_TABLET_ORIGIN", "Regla anti-demo"]);

if (failures.length) {
  console.error("PRISMA App Mobile 16 connected data bridge verification failed:");
  for (const failure of failures) console.error(`- ${failure}`);
  console.error(`root=${root}`);
  process.exit(1);
}
console.log(`[CONNECTED DATA BRIDGE OK] PRISMA App Mobile routes no longer use demo source. root=${root}`);
