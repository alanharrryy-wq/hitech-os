#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const verifierId = "PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT";
const read = (relativePath) => readFileSync(join(root, relativePath), "utf8");
const fail = (message, details = {}) => {
  console.error(JSON.stringify({ ok: false, verifier: verifierId, message, details }, null, 2));
  process.exit(1);
};

const pkg = JSON.parse(read("package.json"));
const healthVerifier = read("tools/verify_prisma_app_mobile_25_health_radar.mjs");
const canon = JSON.parse(read("docs/prisma-app/PRISMA_MOBILE_INTERFACE_CANON.contract.json"));
const corpus = read("docs/prisma-app/qa/prisma-app-mobile-25f-health-radar-verifier-compat-corpus.jsonl")
  .trim()
  .split(/\r?\n/)
  .filter(Boolean);

for (const token of [
  "HEALTH_RADAR_MIN_VERSION",
  "assertCompatibleHealthRadarVersion(pkg.version)",
  "historicalUpperVersionFenceRetired",
  "premium navigator must not mount dormant Health Radar in the current canon"
]) {
  if (!healthVerifier.includes(token)) fail("health-radar verifier missing current compatibility token", { token });
}
if (healthVerifier.includes("HEALTH_RADAR_MAX_EXCLUSIVE")) fail("historical upper-version fence still exists");
if (healthVerifier.includes('pkg.version !== "0.25.3"')) fail("health-radar verifier pins an obsolete exact app version");

if (pkg.scripts?.["verify:health-radar"] !== "node tools/verify_prisma_app_mobile_25_health_radar.mjs") fail("verify:health-radar script drifted");
if (pkg.scripts?.["verify:health-radar-compat"] !== "node tools/verify_prisma_app_mobile_25f_health_radar_verifier_compat.mjs") fail("verify:health-radar-compat script missing");
if (pkg.prismaMobileHealthRadarVerifierCompatibilityVersion !== "0.25.4") fail("25F compatibility marker missing");
if (pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== "0.25.3") fail("25D duplicate-key marker missing");

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

const healthRow = (canon.secondaryOrDormantCapabilities ?? []).find((row) => row.id === "health-radar");
if (!healthRow || healthRow.mountRequiredByCanon !== false) fail("canon no longer marks Health Radar as non-mandatory", { healthRow });

if (corpus.length < 6000) fail("25F historical corpus too small", { count: corpus.length });
let parsed = 0;
let historicalPass = 0;
let historicalFail = 0;
for (const line of corpus) {
  const row = JSON.parse(line);
  if (row.expectedContract !== "PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT_FINAL") fail("wrong 25F contract in corpus");
  if (!['pass', 'fail'].includes(row.expected)) fail("invalid historical expected value", { expected: row.expected });
  if (row.expected === "pass") historicalPass += 1;
  else historicalFail += 1;
  parsed += 1;
}

console.log(JSON.stringify({
  ok: true,
  verifier: verifierId,
  appVersion: pkg.version,
  minimumVersion: minMatch[1],
  upperVersionFence: null,
  historicalCorpusRole: "evidence-only-not-current-version-authority",
  historicalVectorsParsed: parsed,
  historicalPass,
  historicalFail
}, null, 2));
