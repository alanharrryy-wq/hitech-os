import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "app/api/mobile/daily-brief/route.ts",
  "src/lib/prisma-app/prisma-mobile-daily-brief.ts",
  "src/components/prisma-app/PrismaMobileDailyBrief.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/index.ts",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_22_DAILY_BRIEF.md",
  "docs/prisma-app/qa/prisma-app-mobile-22-daily-brief-scenarios.json",
  "docs/prisma-app/qa/prisma-app-mobile-22-daily-brief-regression-corpus.jsonl"
];

function fail(message) {
  console.error(`[PRISMA APP MOBILE 22 FAIL] ${message}`);
  process.exit(1);
}

function text(rel) {
  const file = path.join(root, rel);
  if (!existsSync(file)) fail(`missing ${rel}`);
  return readFileSync(file, "utf8");
}

for (const rel of required) text(rel);

const lib = text("src/lib/prisma-app/prisma-mobile-daily-brief.ts");
const component = text("src/components/prisma-app/PrismaMobileDailyBrief.tsx");
const dashboard = text("src/components/prisma-app/PrismaMobileDashboard.tsx");
const route = text("app/api/mobile/daily-brief/route.ts");
const css = text("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const pkg = JSON.parse(text("package.json"));
const scenarios = JSON.parse(text("docs/prisma-app/qa/prisma-app-mobile-22-daily-brief-scenarios.json"));
const corpus = text("docs/prisma-app/qa/prisma-app-mobile-22-daily-brief-regression-corpus.jsonl").trim().split(/\r?\n/);

if (!lib.includes("PRISMA_APP_MOBILE_22_DAILY_BRIEF")) fail("contract id missing in daily brief builder");
if (!lib.includes("buildPrismaMobileCommandCenter") || !lib.includes("buildPrismaMobileActionInbox")) fail("daily brief does not reuse command center and action inbox");
if (!lib.includes("whatsappText") || !lib.includes("emailBody") || !lib.includes("exportText")) fail("share/export contract incomplete");
if (!component.includes("https://wa.me/?text=") || !component.includes("mailto:?subject=")) fail("share links missing");
if (!component.includes("<details") || !component.includes("brief.exportText")) fail("export details missing");
if (!dashboard.includes("PrismaMobileDailyBrief") || !dashboard.includes("<PrismaMobileDailyBrief clientSnapshot={clientSnapshot}")) fail("dashboard does not render daily brief");
if (!route.includes("dynamic = \"force-dynamic\"") || !route.includes("revalidate = 0") || !route.includes("noStoreJsonInit")) fail("daily brief endpoint is not no-store dynamic");
if (!css.includes("PRISMA_APP_MOBILE_22_DAILY_BRIEF START") || !css.includes("dailyBriefShareBox")) fail("daily brief css missing");
if (pkg.version !== "0.22.0") fail("package version not bumped to 0.22.0");
if (pkg.scripts["verify:daily-brief"] !== "node tools/verify_prisma_app_mobile_22_daily_brief.mjs") fail("verify:daily-brief script missing");
if (!pkg.scripts["check:all"].includes("verify:daily-brief")) fail("check:all does not include daily brief");
if (!Array.isArray(scenarios.scenarios) || scenarios.scenarios.length < 360) fail("not enough QA scenarios");
if (corpus.length < 2400) fail("not enough regression traces");

for (const banned of ["demo", "mock", "lorem", "placeholder", "TODO"]) {
  const hay = [lib, component, dashboard, route].join("\n").toLowerCase();
  if (hay.includes(banned.toLowerCase())) fail(`banned marker found: ${banned}`);
}

console.log("OK PRISMA_APP_MOBILE_22_DAILY_BRIEF verified");
