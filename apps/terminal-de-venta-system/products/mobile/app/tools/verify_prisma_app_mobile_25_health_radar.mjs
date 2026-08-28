#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const verifier = "PRISMA_APP_MOBILE_HEALTH_RADAR_CURRENT_TECHNICAL_CONTRACT";
const HEALTH_RADAR_MIN_VERSION = "0.25.3";

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, verifier, message, details }, null, 2));
  process.exit(1);
}

function read(rel) {
  const file = join(root, rel);
  if (!existsSync(file)) fail(`missing ${rel}`);
  return readFileSync(file, "utf8");
}

function numericVersion(value) {
  const match = String(value ?? "").match(/^(\d+)\.(\d+)\.(\d+)/);
  if (!match) fail(`invalid package version ${value}`);
  return match.slice(1).map((item) => Number.parseInt(item, 10));
}

function compareVersion(left, right) {
  const a = numericVersion(left);
  const b = numericVersion(right);
  for (let index = 0; index < 3; index += 1) {
    if (a[index] !== b[index]) return a[index] - b[index];
  }
  return 0;
}

const required = [
  "package.json",
  "app/api/mobile/health-radar/route.ts",
  "src/lib/prisma-app/prisma-mobile-health-radar.ts",
  "src/components/prisma-app/PrismaMobileHealthRadar.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json",
  "docs/prisma-app/PRISMA_APP_MOBILE_25D_HEALTH_RADAR_DUPLICATE_KEY_FINAL.md",
  "docs/prisma-app/PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT_FINAL.md"
];
for (const rel of required) read(rel);

const pkg = JSON.parse(read("package.json"));
if (compareVersion(pkg.version, HEALTH_RADAR_MIN_VERSION) < 0) {
  fail("current Mobile package is older than the Health Radar technical baseline", { version: pkg.version, minimum: HEALTH_RADAR_MIN_VERSION });
}
if (pkg.scripts?.["verify:health-radar"] !== "node tools/verify_prisma_app_mobile_25_health_radar.mjs") fail("script verify:health-radar missing");
if (!String(pkg.scripts?.["check:all"] ?? "").includes("verify:health-radar")) fail("check:all missing verify:health-radar");
if (pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== "0.25.3") fail("historical duplicate-key closure marker missing");

const canon = JSON.parse(read("docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json"));
const canonRow = (canon.secondaryOrDormantCapabilities ?? []).find((row) => row.id === "health-radar" && row.component === "PrismaMobileHealthRadar");
if (!canonRow || canonRow.mountRequiredByCanon !== false) fail("Health Radar canon row must remain secondary/dormant", { canonRow });

const component = read("src/components/prisma-app/PrismaMobileHealthRadar.tsx");
for (const token of [
  "function stableKey(scope: string, index: number, value: string): string",
  "return `${scope}-${index}-${normalized || \"item\"}`",
  'key={stableKey(`${axis.id}-evidence`, index, item)}',
  'key={stableKey("watch", index, item.id)}',
  'key={stableKey("guardrail", index, item)}',
  "Sin evidencia delicada."
]) {
  if (!component.includes(token)) fail("Health Radar lost duplicate-key safety invariant", { token });
}
for (const forbidden of [
  "key={item}",
  "radar.guardrails.map((item) => <li key={item}",
  "axis.evidence.slice(0, 2).map((item) => <li key={item}"
]) {
  if (component.includes(forbidden)) fail("Health Radar restored an unsafe duplicate-key pattern", { forbidden });
}

function cleanKeyPart(value) {
  return String(value ?? "item")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "") || "item";
}
function stableEvidenceKey(scope, index, value) {
  return `${scope}-${index}-${cleanKeyPart(value)}`;
}

const regressionVectors = [
  ["datos-evidence", ["tablet: OK", "tablet: OK", "tablet: OK"]],
  ["guardrail", ["Sincronizar", "Sincronizar", "Sincronizar"]],
  ["watch", ["stock-critical", "stock-critical", "stock-critical"]],
  ["accented", ["Operación crítica", "Operación crítica"]],
  ["empty-normalized", ["***", "***", "***"]]
];
for (const [scope, values] of regressionVectors) {
  const keys = values.map((value, index) => stableEvidenceKey(scope, index, value));
  if (new Set(keys).size !== keys.length) fail("duplicate-key regression vector is not unique", { scope, values, keys });
}

const lib = read("src/lib/prisma-app/prisma-mobile-health-radar.ts");
for (const token of ["buildPrismaMobileHealthRadar", "weakestArea", "guardrails", "timeline.events"]) {
  if (!lib.includes(token)) fail("Health Radar builder contract drifted", { token });
}

const route = read("app/api/mobile/health-radar/route.ts");
for (const token of ["force-dynamic", "noStoreJsonInit", "health_radar"]) {
  if (!route.includes(token)) fail("Health Radar route contract drifted", { token });
}

const dashboard = read("src/components/prisma-app/PrismaMobileDashboard.tsx");
const navigator = read("src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
if (!dashboard.includes("PrismaMobilePremiumNavigator")) fail("dashboard does not delegate to premium navigator");
if (dashboard.includes("<PrismaMobileHealthRadar")) fail("dashboard must not mount dormant Health Radar in the current canon");
if (navigator.includes("<PrismaMobileHealthRadar")) fail("premium navigator must not mount dormant Health Radar in the current canon");

console.log(JSON.stringify({
  ok: true,
  verifier,
  appVersion: pkg.version,
  minimumTechnicalVersion: HEALTH_RADAR_MIN_VERSION,
  historicalUpperVersionFenceRetired: true,
  retiredCorpusRequired: false,
  mountRequiredByCanon: false,
  duplicateKeyRegressionVectors: regressionVectors.length,
  message: "Health Radar current technical invariants pass without resurrecting retired QA corpus artifacts."
}, null, 2));
