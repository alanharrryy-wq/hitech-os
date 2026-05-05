import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const fail = (message) => {
  console.error(`[PRISMA 28] FAIL ${message}`);
  process.exitCode = 1;
};
const ok = (message) => console.log(`[PRISMA 28] OK ${message}`);
const read = (path) => readFileSync(join(root, path), "utf8");
const exists = (path) => existsSync(join(root, path));

const requiredFiles = [
  "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
  "src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
  "src/lib/prisma-app/prisma-app-api-contracts.ts",
  "src/lib/prisma-app/prisma-mobile-view-model.ts",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "tools/verify_prisma_app_mobile_28_data_readiness.mjs",
  "docs/prisma-app/PRISMA_APP_MOBILE_28_DATA_READINESS.md",
  "docs/prisma-app/qa/prisma-app-mobile-28-data-readiness-scenarios.json",
  "docs/prisma-app/qa/prisma-app-mobile-28-data-readiness-state-matrix.json"
];

for (const file of requiredFiles) {
  exists(file) ? ok(`existe ${file}`) : fail(`falta ${file}`);
}

const packageJson = JSON.parse(read("package.json"));
if (packageJson.version === "0.28.0") ok("package version 0.28.0");
else fail(`package version esperada 0.28.0, recibida ${packageJson.version}`);
if (packageJson.scripts?.["verify:data-readiness"] === "node tools/verify_prisma_app_mobile_28_data_readiness.mjs") ok("script verify:data-readiness registrado");
else fail("script verify:data-readiness ausente o distinto");

const contracts = read("src/lib/prisma-app/prisma-app-api-contracts.ts");
for (const token of [
  "PrismaMobileDataReadinessSchema",
  "dataReadiness: PrismaMobileDataReadinessSchema.default",
  "salesState: z.enum",
  "syncState: z.enum"
]) {
  contracts.includes(token) ? ok(`contrato incluye ${token}`) : fail(`contrato no incluye ${token}`);
}

const readiness = read("src/lib/prisma-app/mobile-data-plane/data-readiness.ts");
for (const token of [
  "deriveMobileDataReadiness",
  "Tablet conectada",
  "Confirmar primera venta real",
  "No es error ni dato inventado",
  "PRISMA_MOBILE_TABLET_ORIGIN"
]) {
  readiness.includes(token) ? ok(`readiness incluye ${token}`) : fail(`readiness no incluye ${token}`);
}

const builders = read("src/lib/prisma-app/mobile-data-plane/payload-builders.ts");
for (const token of [
  "deriveMobileDataReadiness",
  "dataReadiness",
  "esperando consolidado PC",
  "esperando primer ticket real",
  "watchlist sin SKUs recibidos"
]) {
  builders.includes(token) ? ok(`payload builder incluye ${token}`) : fail(`payload builder no incluye ${token}`);
}

const viewModel = read("src/lib/prisma-app/prisma-mobile-view-model.ts");
for (const token of [
  "snapshot.summary.dataReadiness.headline",
  "snapshot.summary.dataReadiness.label",
  "Watchlist esperando SKUs reales"
]) {
  viewModel.includes(token) ? ok(`view-model incluye ${token}`) : fail(`view-model no incluye ${token}`);
}

const navigator = read("src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
for (const token of [
  "PrismaMobileReadinessPanel",
  "dataReadinessPanel",
  "Madurez y calidad de datos",
  "Ventas:"
]) {
  navigator.includes(token) ? ok(`navigator incluye ${token}`) : fail(`navigator no incluye ${token}`);
}

const css = read("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const impureSelector = /(^|,)\s*\[(data-tone|data-axis-tone|data-watch-tone)=/m;
if (!impureSelector.test(css)) ok("CSS Modules sin selectores data-* impuros");
else fail("CSS Modules conserva selector data-* impuro");
for (const token of [
  ".dataReadinessPanel",
  ".dataReadinessPanel[data-readiness-level=\"ready\"]",
  ".dataReadinessGrid",
  ".healthRadarAxis[data-axis-tone=\"offline\"]"
]) {
  css.includes(token) ? ok(`CSS incluye ${token}`) : fail(`CSS no incluye ${token}`);
}

const matrix = JSON.parse(read("docs/prisma-app/qa/prisma-app-mobile-28-data-readiness-state-matrix.json"));
if (matrix.scenarioCount === 96 && Array.isArray(matrix.scenarios) && matrix.scenarios.length === 96) ok("matriz de 96 escenarios readiness presente");
else fail("matriz readiness debe contener 96 escenarios");

const sourceFiles = [
  "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
  "src/lib/prisma-app/mobile-data-plane/diagnostics.ts",
  "src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "app/prisma-app/prisma-app.module.css"
];
const forbidden = /\b(demo|mock|fixture|fakeChart|prueba)\b/i;
for (const file of sourceFiles) {
  const content = read(file);
  if (forbidden.test(content)) fail(`residuo visible no productivo en ${file}`);
  else ok(`sin residuos demo/mock/fixture en ${file}`);
}

if (process.exitCode) {
  console.error("[PRISMA 28] BLOCKED data readiness verifier failed");
} else {
  console.log("[PRISMA 28] READY data readiness verifier passed");
}
