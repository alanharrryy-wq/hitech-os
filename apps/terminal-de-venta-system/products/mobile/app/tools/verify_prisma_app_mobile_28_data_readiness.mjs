#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const verifier = "PRISMA_APP_MOBILE_DATA_READINESS_CURRENT_TECHNICAL_CONTRACT";

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, verifier, message, details }, null, 2));
  process.exit(1);
}

function read(relativePath) {
  const file = join(root, relativePath);
  if (!existsSync(file)) fail(`missing ${relativePath}`);
  return readFileSync(file, "utf8");
}

function compareVersion(left, right) {
  const parse = (value) => String(value ?? "0.0.0")
    .split(".")
    .map((part) => Number.parseInt(part.replace(/[^0-9].*$/, ""), 10) || 0);
  const a = parse(left);
  const b = parse(right);
  for (let index = 0; index < 3; index += 1) {
    if ((a[index] || 0) !== (b[index] || 0)) return (a[index] || 0) - (b[index] || 0);
  }
  return 0;
}

const requiredFiles = [
  "package.json",
  "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
  "src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
  "src/lib/prisma-app/prisma-app-api-contracts.ts",
  "src/lib/prisma-app/prisma-mobile-view-model.ts",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_28_DATA_READINESS.md",
  "docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json"
];
for (const file of requiredFiles) read(file);

const pkg = JSON.parse(read("package.json"));
if (compareVersion(pkg.version, "0.28.0") < 0) {
  fail("current Mobile package is older than the Data Readiness technical baseline", { version: pkg.version, minimum: "0.28.0" });
}
if (pkg.scripts?.["verify:data-readiness"] !== "node tools/verify_prisma_app_mobile_28_data_readiness.mjs") {
  fail("verify:data-readiness script drifted", { actual: pkg.scripts?.["verify:data-readiness"] });
}
if (!String(pkg.scripts?.["check:all"] ?? "").includes("verify:data-readiness")) fail("check:all no longer runs Data Readiness technical verification");

const contracts = read("src/lib/prisma-app/prisma-app-api-contracts.ts");
const expectedDomains = {
  level: ["ready", "partial", "empty", "offline", "blocked"],
  salesState: ["with_sales", "empty", "unavailable"],
  inventoryState: ["with_items", "empty", "unavailable"],
  pcState: ["connected", "unavailable"],
  syncState: ["clean", "pending", "failed", "unknown"]
};
const contractTokens = [
  'PrismaMobileDataReadinessLevelSchema = z.enum(["ready", "partial", "empty", "offline", "blocked"])',
  'salesState: z.enum(["with_sales", "empty", "unavailable"])',
  'inventoryState: z.enum(["with_items", "empty", "unavailable"])',
  'pcState: z.enum(["connected", "unavailable"])',
  'syncState: z.enum(["clean", "pending", "failed", "unknown"])',
  "facts: z.array(z.string().min(1)).default([])",
  "actions: z.array(PrismaMobileDataReadinessActionSchema).default([])"
];
for (const token of contractTokens) {
  if (!contracts.includes(token)) fail("Data Readiness API contract drifted", { token });
}

const readiness = read("src/lib/prisma-app/mobile-data-plane/data-readiness.ts");
for (const token of [
  'export type MobileDataReadinessLevel = "ready" | "partial" | "empty" | "offline" | "blocked"',
  "export function deriveMobileDataReadiness",
  "function classifySync",
  'if (state.outbox.failed > 0) return "failed"',
  'if (state.outbox.pending > 0) return "pending"',
  'state.runtimeMode === "offline" ? "offline" : "blocked"',
  'empty ? "empty"',
  'attention || partial',
  'ready: "Datos listos"',
  'partial: "Lectura parcial"',
  'offline: "Sin fuente certificada"',
  "PRISMA_MOBILE_TABLET_ORIGIN"
]) {
  if (!readiness.includes(token)) fail("Data Readiness derivation drifted", { token });
}

const builders = read("src/lib/prisma-app/mobile-data-plane/payload-builders.ts");
for (const token of ["deriveMobileDataReadiness", "dataReadiness"]) {
  if (!builders.includes(token)) fail("payload builder lost Data Readiness integration", { token });
}

const viewModel = read("src/lib/prisma-app/prisma-mobile-view-model.ts");
for (const token of ["snapshot.summary.dataReadiness.headline", "snapshot.summary.dataReadiness.label"]) {
  if (!viewModel.includes(token)) fail("view-model lost Data Readiness projection", { token });
}

const navigator = read("src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
for (const token of ["PrismaMobileReadinessPanel", "getPrismaMobileDataReadiness", "dataReadinessPanel", "Madurez y calidad de datos", "Ventas:"]) {
  if (!navigator.includes(token)) fail("Premium Navigator lost Data Readiness evidence", { token });
}

const css = read("src/components/prisma-app/prisma-mobile-dashboard.module.css");
for (const token of [".dataReadinessPanel", ".dataReadinessGrid"]) {
  if (!css.includes(token)) fail("Data Readiness styling contract drifted", { token });
}

const canon = JSON.parse(read("docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json"));
if (canon.noFakeGreen?.staleOrPartialIsHealthy !== false) fail("canon must forbid presenting stale/partial data as healthy");
if (canon.productRole?.mobile !== "supervision_and_decision") fail("Data Readiness verifier must remain under Mobile supervision role");
if (canon.productRole?.mobileMutationsAuthorizedByThisCanon !== false) fail("interface canon must not authorize Mobile mutations");

const domainVectors = [];
for (const level of expectedDomains.level) {
  for (const salesState of expectedDomains.salesState) {
    for (const inventoryState of expectedDomains.inventoryState) {
      for (const pcState of expectedDomains.pcState) {
        for (const syncState of expectedDomains.syncState) {
          domainVectors.push(`${level}|${salesState}|${inventoryState}|${pcState}|${syncState}`);
        }
      }
    }
  }
}
if (domainVectors.length !== 360 || new Set(domainVectors).size !== 360) {
  fail("deterministic Data Readiness state-domain matrix is incomplete", { count: domainVectors.length, unique: new Set(domainVectors).size });
}

for (const file of [
  "src/lib/prisma-app/mobile-data-plane/data-readiness.ts",
  "src/lib/prisma-app/mobile-data-plane/diagnostics.ts",
  "src/lib/prisma-app/mobile-data-plane/payload-builders.ts",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx"
]) {
  const text = read(file);
  if (/\b(lorem|fakeChart|demo mode)\b/i.test(text)) fail("non-product placeholder language found in current Data Readiness path", { file });
}

console.log(JSON.stringify({
  ok: true,
  verifier,
  appVersion: pkg.version,
  minimumTechnicalVersion: "0.28.0",
  historicalUpperVersionFenceRetired: true,
  retiredQaDirectoryRequired: false,
  deterministicStateDomainVectors: domainVectors.length,
  claimsRuntimeBehaviorMatrix: false,
  message: "Data Readiness current source contracts pass without resurrecting retired generated QA artifacts."
}, null, 2));
