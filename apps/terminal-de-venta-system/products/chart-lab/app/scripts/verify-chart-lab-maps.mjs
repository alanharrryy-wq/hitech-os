import { chartOpsIds, fail, pass, read } from "./chart-lab-script-utils.mjs";

const maps = read("src/prisma-charts/maps/chart-lab-maps.ts");
const shell = read("src/components/PrismaChartLabShell.tsx");
const chartIds = chartOpsIds();

const requiredMaps = [
  "chartAtlasMap",
  "dataSourceMap",
  "runtimeControlMap",
  "visualKnobMap",
  "visualRecipeMap",
  "stateGalleryMap",
  "humanIntentMap",
  "surfaceTransportMap",
  "promotionManifestMap",
  "routeMap",
  "dependencyImportMap",
  "cloudflareExposureMap",
  "validationMap",
  "handoffZipMap"
];

for (const mapName of requiredMaps) {
  if (maps.includes(`export const ${mapName}`)) pass(`map exported: ${mapName}`);
  else fail(`missing map export: ${mapName}`);
}

for (const id of chartIds) {
  if (maps.includes("chartLabMapChartIds") && maps.includes("chartOpsEntries")) pass(`map derives chart coverage from registry: ${id}`);
  else fail(`map coverage derivation missing for chart id: ${id}`);
}

for (const family of ["flow", "density", "network", "treemap", "timeline", "waterfall", "strip", "matrix", "stack", "radar", "rings", "sparks", "bands"]) {
  if (maps.includes(`"${family}"`)) pass(`recipe family mapped: ${family}`);
  else fail(`missing recipe family: ${family}`);
}

for (const state of ["happy", "empty", "partial", "stale", "offline", "unknown", "dense", "critical"]) {
  if (maps.includes(`${state}:`)) pass(`state mapped: ${state}`);
  else fail(`missing state: ${state}`);
}

for (const needle of ["Maps", "Sources", "Promotion", "Intent", "States", "Health"]) {
  if (shell.includes(needle)) pass(`map UI tab present: ${needle}`);
  else fail(`missing map UI tab: ${needle}`);
}

if (!process.exitCode) pass("maps verification complete");
