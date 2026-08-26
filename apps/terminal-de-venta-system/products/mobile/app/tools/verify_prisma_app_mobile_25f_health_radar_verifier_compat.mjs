#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const verifierId = "PRISMA_APP_MOBILE_HEALTH_RADAR_VERIFIER_COMPAT_CURRENT";
const read = (relativePath) => readFileSync(join(root, relativePath), "utf8");
const fail = (message, details = {}) => {
  console.error(JSON.stringify({ ok: false, verifier: verifierId, message, details }, null, 2));
  process.exit(1);
};

const pkg = JSON.parse(read("package.json"));
const healthVerifier = read("tools/verify_prisma_app_mobile_25_health_radar.mjs");
const canon = JSON.parse(read("docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json"));
const historicalDoc = read("docs/prisma-app/PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT_FINAL.md");

for (const token of [
  "HEALTH_RADAR_MIN_VERSION",
  "historicalUpperVersionFenceRetired: true",
  "retiredCorpusRequired: false",
  "premium navigator must not mount dormant Health Radar in the current canon"
]) {
  if (!healthVerifier.includes(token)) fail("health-radar verifier missing current compatibility invariant", { token });
}
for (const forbidden of [
  "HEALTH_RADAR_MAX_EXCLUSIVE",
  'pkg.version !== "0.25.3"',
  "prisma-app-mobile-25d-health-radar-key-regression-corpus.jsonl",
  "prisma-app-mobile-25f-health-radar-verifier-compat-corpus.jsonl"
]) {
  if (healthVerifier.includes(forbidden)) fail("health-radar verifier still depends on retired compatibility machinery", { forbidden });
}

if (pkg.scripts?.["verify:health-radar"] !== "node tools/verify_prisma_app_mobile_25_health_radar.mjs") fail("verify:health-radar script drifted");
if (pkg.scripts?.["verify:health-radar-compat"] !== "node tools/verify_prisma_app_mobile_25f_health_radar_verifier_compat.mjs") fail("verify:health-radar-compat script missing");
if (pkg.prismaMobileHealthRadarVerifierCompatibilityVersion !== "0.25.4") fail("historical 25F compatibility marker missing");
if (pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== "0.25.3") fail("historical 25D duplicate-key marker missing");

const minMatch = healthVerifier.match(/const HEALTH_RADAR_MIN_VERSION = "([^"]+)"/);
if (!minMatch) fail("health-radar verifier does not expose a parseable minimum version");
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
if (compareVersion(pkg.version, minMatch[1]) < 0) fail("current package is older than Health Radar technical baseline", { version: pkg.version, minimum: minMatch[1] });

const healthRow = (canon.secondaryOrDormantCapabilities ?? []).find((row) => row.id === "health-radar" && row.component === "PrismaMobileHealthRadar");
if (!healthRow || healthRow.mountRequiredByCanon !== false) fail("canon no longer marks Health Radar as non-mandatory", { healthRow });

if (!historicalDoc.includes("25D sí corrigió las llaves duplicadas")) fail("historical compatibility rationale disappeared");
if (!historicalDoc.includes("su verificador quedó amarrado")) fail("historical version-pin diagnosis disappeared");

console.log(JSON.stringify({
  ok: true,
  verifier: verifierId,
  appVersion: pkg.version,
  minimumVersion: minMatch[1],
  upperVersionFence: null,
  historicalCorpusRole: "retired-artifact-not-current-gate-input",
  mountRequiredByCanon: false,
  message: "Health Radar compatibility follows current source invariants and no longer requires deleted historical corpora."
}, null, 2));
