#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const fail = (message, details = {}) => {
  console.error(JSON.stringify({
    ok: false,
    verifier: "PRISMA_APP_MOBILE_37_RELEASE_HARDENING",
    message,
    details
  }, null, 2));
  process.exit(1);
};
const read = (relativePath) => {
  const file = join(root, relativePath);
  if (!existsSync(file)) fail(`Missing file: ${relativePath}`);
  return readFileSync(file, "utf8");
};
const requireIncludes = (file, snippets) => {
  const text = read(file);
  const missing = snippets.filter((snippet) => !text.includes(snippet));
  if (missing.length) fail(`${file} missing required release-hardening snippets`, { missing });
  return text;
};

const pkg = JSON.parse(read("package.json"));
if (pkg.version !== "0.37.0") fail("package version must stay pinned to i04 release hardening", { version: pkg.version });
if (pkg.prismaMobileI04ReleaseHardeningVersion !== "0.37.0") fail("i04 release hardening package marker missing");
if (pkg.scripts?.["verify:release-hardening"] !== "node tools/verify_prisma_app_mobile_37_release_hardening.mjs") {
  fail("verify:release-hardening script missing");
}
if (!String(pkg.scripts?.["check:all"] || "").includes("verify:release-hardening")) {
  fail("check:all must include verify:release-hardening");
}

const dashboard = requireIncludes("src/components/prisma-app/PrismaMobileDashboard.tsx", [
  "PrismaMobilePremiumNavigator",
  "data-prisma-readiness",
  "data-prisma-source",
  "data-prisma-stale",
  "onClearCache"
]);
const navigator = read("src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
const longSurfaces = [
  "PrismaMobileCommandCenter",
  "PrismaMobileActionInbox",
  "PrismaMobileDailyBrief",
  "PrismaMobileDecisionLedger",
  "PrismaMobilePulseTimeline",
  "PrismaMobileHealthRadar"
];

for (const surface of longSurfaces) {
  if (dashboard.includes(`<${surface}`)) {
    fail("Dashboard must stay light and not mount long mando surfaces directly", { surface });
  }
  if (!navigator.includes(`<${surface}`)) {
    fail("Premium Navigator must own long mando surface", { surface });
  }
}

requireIncludes("tools/verify_prisma_app_mobile_22_daily_brief.mjs", [
  "PrismaMobilePremiumNavigator.tsx",
  "dashboard must not render daily brief directly",
  "0.38.0"
]);
requireIncludes("tools/verify_prisma_app_mobile_23_decision_ledger.mjs", [
  "PrismaMobilePremiumNavigator.tsx",
  "dashboard must not render decision ledger directly",
  "0.38.0"
]);
requireIncludes("tools/verify_prisma_app_mobile_24_pulse_timeline.mjs", [
  "PrismaMobilePremiumNavigator.tsx",
  "dashboard must not render pulse timeline directly",
  "0.38.0"
]);
requireIncludes("tools/verify_prisma_app_mobile_25_health_radar.mjs", [
  "HEALTH_RADAR_MIN_VERSION",
  "HEALTH_RADAR_MAX_EXCLUSIVE",
  "const HEALTH_RADAR_MAX_EXCLUSIVE = \"0.38.0\"",
  "assertCompatibleHealthRadarVersion(pkg.version)",
  "dashboard must not render health radar directly"
]);
requireIncludes("tools/verify_prisma_app_mobile_33_mando_contracts.mjs", [
  "Mando surface must not be mounted directly in Dashboard.",
  "premium-navigator-owned"
]);

console.log(JSON.stringify({
  ok: true,
  verifier: "PRISMA_APP_MOBILE_37_RELEASE_HARDENING",
  version: pkg.version,
  ownership: "dashboard-light-premium-navigator-owned",
  longSurfaces: longSurfaces.length
}, null, 2));
