import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const root = process.cwd();
const requiredFiles = [
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "src/components/prisma-app/index.ts",
  "docs/prisma-app/PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION.md",
  "docs/prisma-app/qa/prisma-app-mobile-27-premium-navigation-scenarios.json"
];

function read(relativePath) {
  const absolutePath = join(root, relativePath);
  if (!existsSync(absolutePath)) {
    throw new Error(`Missing required file: ${relativePath}`);
  }
  return readFileSync(absolutePath, "utf8");
}

for (const file of requiredFiles) {
  read(file);
}

const dashboard = read("src/components/prisma-app/PrismaMobileDashboard.tsx");
const navigator = read("src/components/prisma-app/PrismaMobilePremiumNavigator.tsx");
const css = read("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const pkg = JSON.parse(read("package.json"));
const qa = JSON.parse(read("docs/prisma-app/qa/prisma-app-mobile-27-premium-navigation-scenarios.json"));

const checks = [
  [dashboard.includes("PrismaMobilePremiumNavigator"), "dashboard binds premium navigator"],
  [!dashboard.includes("<PrismaMobileCommandCenter"), "dashboard no longer renders long modules in one waterfall"],
  [navigator.includes('role="tablist"') && navigator.includes('role="tab"') && navigator.includes('role="tabpanel"'), "navigator exposes accessible tab roles"],
  [navigator.includes("ArrowRight") && navigator.includes("ArrowLeft") && navigator.includes("Home") && navigator.includes("End"), "navigator supports keyboard tab rail"],
  [navigator.includes("PrismaMobileHealthRadar") && navigator.includes("PrismaMobileDecisionLedger") && navigator.includes("PrismaMobilePulseTimeline"), "navigator sections include previously raw modules"],
  [css.includes("PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION START"), "css marker present"],
  [css.includes(".premiumTabRail") && css.includes(".premiumTabPanel") && css.includes(".premiumTabActive"), "premium navigation styles present"],
  [css.includes(".decisionLedger") && css.includes(".pulseTimeline") && css.includes(".healthRadarAxes"), "raw text components have formatting styles"],
  [css.includes("content-visibility:auto"), "heavy panel rendering is guarded with content visibility"],
  [pkg.version === "0.27.0", "package version bumped to 0.27.0"],
  [pkg.scripts?.["verify:premium-navigation"] === "node tools/verify_prisma_app_mobile_27_premium_navigation.mjs", "verify script registered"],
  [Array.isArray(qa.scenarios) && qa.scenarios.length >= 5, "qa scenarios are present"]
];

const failed = checks.filter(([ok]) => !ok);
for (const [ok, label] of checks) {
  console.log(`${ok ? "OK" : "FAIL"} ${label}`);
}
if (failed.length > 0) {
  throw new Error(`PRISMA App Mobile 27 premium navigation verification failed: ${failed.map(([, label]) => label).join(", ")}`);
}
console.log("OK PRISMA_APP_MOBILE_27_PREMIUM_NAVIGATION verified");
