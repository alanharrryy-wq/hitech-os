#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const read = (relativePath) => readFileSync(join(root, relativePath), "utf8");
const fail = (message) => {
  console.error(`[PRISMA APP MOBILE 25F FAIL] ${message}`);
  process.exit(1);
};

const pkg = JSON.parse(read("package.json"));
const verifier = read("tools/verify_prisma_app_mobile_25_health_radar.mjs");
const corpus = read("docs/prisma-app/qa/prisma-app-mobile-25f-health-radar-verifier-compat-corpus.jsonl").trim().split(/\r?\n/).filter(Boolean);

const requiredVerifierTokens = [
  "HEALTH_RADAR_MIN_VERSION",
  "HEALTH_RADAR_MAX_EXCLUSIVE",
  "assertCompatibleHealthRadarVersion(pkg.version)",
  "compareVersion(version, HEALTH_RADAR_MIN_VERSION) < 0",
  "compareVersion(version, HEALTH_RADAR_MAX_EXCLUSIVE) >= 0",
  "pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== \"0.25.3\""
];
for (const token of requiredVerifierTokens) {
  if (!verifier.includes(token)) fail(`verifier missing compatibility token: ${token}`);
}
if (verifier.includes('pkg.version !== "0.25.3"')) fail("verifier still pins exact app version 0.25.3");
if (pkg.scripts?.["verify:health-radar"] !== "node tools/verify_prisma_app_mobile_25_health_radar.mjs") fail("verify:health-radar script drifted");
if (pkg.scripts?.["verify:health-radar-compat"] !== "node tools/verify_prisma_app_mobile_25f_health_radar_verifier_compat.mjs") fail("verify:health-radar-compat script missing");
if (pkg.prismaMobileHealthRadarVerifierCompatibilityVersion !== "0.25.4") fail("25F compatibility marker missing");
if (pkg.prismaMobileHealthRadarDuplicateKeyFinalVersion !== "0.25.3") fail("25D duplicate-key marker missing");

if (corpus.length < 6000) fail(`25F corpus too small: ${corpus.length}`);
let parsed = 0;
let sawCurrent = false;
let sawFutureMinorBlocked = false;
for (const line of corpus) {
  const row = JSON.parse(line);
  if (row.expectedContract !== "PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT_FINAL") fail("wrong 25F contract in corpus");
  if (row.version === pkg.version && row.expected === "pass") sawCurrent = true;
  if (String(row.version).startsWith("0.26.") && row.expected === "fail") sawFutureMinorBlocked = true;
  if (!['pass', 'fail'].includes(row.expected)) fail(`invalid expected value ${row.expected}`);
  parsed += 1;
}
if (!sawCurrent) fail(`corpus does not cover current package version ${pkg.version}`);
if (!sawFutureMinorBlocked) fail("corpus does not cover future-minor blocking");
console.log(`OK PRISMA_APP_MOBILE_25F_HEALTH_RADAR_VERIFIER_COMPAT verified ${parsed} version-compat vectors`);
