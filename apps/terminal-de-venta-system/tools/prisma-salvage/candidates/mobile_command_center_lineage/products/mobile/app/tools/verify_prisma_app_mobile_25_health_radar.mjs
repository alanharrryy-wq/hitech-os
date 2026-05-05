#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const HEALTH_RADAR_MIN_VERSION = "0.25.3";
const HEALTH_RADAR_MAX_EXCLUSIVE = "0.26.0";

const required = [
  "package.json",
  "app/api/mobile/health-radar/route.ts",
  "src/lib/prisma-app/prisma-mobile-health-radar.ts",
  "src/components/prisma-app/PrismaMobileHealthRadar.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/index.ts",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_25D_HEALTH_RADAR_DUPLICATE_KEY_FINAL.md",
  "docs/prisma-app/qa/prisma-app-mobile-25d-health-radar-key-regression-corpus.jsonl",
  "tools/verify_prisma_app_mobile_25_health_radar.mjs"
];

function fail(message) {
  console.error(`[PRISMA APP MOBILE 25D FAIL] ${message}`);
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

function assertCompatibleHealthRadarVersion(version) {
  if (compareVersion(version, HEALTH_RADAR_MIN_VERSION) < 0) {
    fail(`version ${version} is older than required ${HEALTH_RADAR_MIN_VERSION}`);
  }
  if (compareVersion(version, HEALTH_RADAR_MAX_EXCLUSIVE) >= 0) {
    fail(`version ${version} needs a new health-radar verifier contract`);
  }
}

for (const rel of required) read(rel);

const pkg = JSON.parse(read("package.json"));
assertCompatibleHealthRadarVersion(pkg.version);
if (pkg.scripts?.["verify:health-radar"] !== "node tools/verify_prisma_app_mobile_25_health_radar.mjs") fail("script verify:health-radar missing");
if (!pkg.scripts?.["check:all"]?.includes("verify:health-radar")) fail("check:all missing verify:health-radar");
if (pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== "0.25.3") fail("package missing 25D marker");

const component = read("src/components/prisma-app/PrismaMobileHealthRadar.tsx");
const requiredComponentTokens = [
  "stableKey(",
  ".map((item, index)",
  'key={stableKey(`${axis.id}-evidence`, index, item)}',
  'key={stableKey("guardrail", index, item)}',
  'key={stableKey("watch", index, item.id)}',
  "Sin evidencia delicada."
];
for (const token of requiredComponentTokens) {
  if (!component.includes(token)) fail(`component missing ${token}`);
}

const forbiddenComponentTokens = [
  "key={item}",
  "radar.guardrails.map((item) => <li key={item}",
  "axis.evidence.slice(0, 2).map((item) => <li key={item}",
  "axis.evidence.slice(0, 2).map((item) =>"
];
for (const token of forbiddenComponentTokens) {
  if (component.includes(token)) fail(`component still has unsafe key pattern: ${token}`);
}

function cleanKeyPart(value) {
  return String(value ?? "sin-dato")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase() || "sin-dato";
}

function stableEvidenceKey(axisId, index, value) {
  return `${axisId}-evidence-${index}-${cleanKeyPart(value)}`;
}

const duplicateExample = ["tablet: OK", "tablet: OK", "tablet: OK"];
const exampleKeys = duplicateExample.map((item, index) => stableEvidenceKey("datos", index, item));
if (new Set(exampleKeys).size !== duplicateExample.length) fail("stable key simulation still duplicates tablet: OK");

const corpusLines = read("docs/prisma-app/qa/prisma-app-mobile-25d-health-radar-key-regression-corpus.jsonl")
  .trim()
  .split("\n")
  .filter(Boolean);
if (corpusLines.length < 6000) fail("25D key regression corpus too small");

let checked = 0;
for (const line of corpusLines) {
  const row = JSON.parse(line);
  if (row.expectedContract !== "PRISMA_APP_MOBILE_25D_HEALTH_RADAR_DUPLICATE_KEY_FINAL") fail("25D contract mismatch in corpus");
  const evidence = Array.isArray(row.evidence) ? row.evidence : [];
  const keys = evidence.map((item, index) => stableEvidenceKey(row.axisId ?? "datos", index, item));
  if (new Set(keys).size !== keys.length) fail(`duplicate generated key in corpus case ${row.caseId}`);
  checked += 1;
}

const lib = read("src/lib/prisma-app/prisma-mobile-health-radar.ts");
for (const token of ["buildPrismaMobileHealthRadar", "weakestArea", "guardrails", "timeline.events"]) {
  if (!lib.includes(token)) fail(`lib missing ${token}`);
}

const route = read("app/api/mobile/health-radar/route.ts");
for (const token of ["force-dynamic", "noStoreJsonInit", "health_radar"]) {
  if (!route.includes(token)) fail(`route missing ${token}`);
}

console.log(`OK PRISMA_APP_MOBILE_25D_HEALTH_RADAR_DUPLICATE_KEY_FINAL verified ${checked} duplicate-key vectors on app version ${pkg.version}`);
