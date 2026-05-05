import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const root = process.cwd();
const required = [
  "app/api/mobile/decision-ledger/route.ts",
  "src/lib/prisma-app/prisma-mobile-decision-ledger.ts",
  "src/components/prisma-app/PrismaMobileDecisionLedger.tsx",
  "src/components/prisma-app/PrismaMobileDashboard.tsx",
  "src/components/prisma-app/index.ts",
  "src/components/prisma-app/prisma-mobile-dashboard.module.css",
  "docs/prisma-app/PRISMA_APP_MOBILE_23_DECISION_LEDGER.md",
  "docs/prisma-app/qa/prisma-app-mobile-23-decision-ledger-scenarios.json",
  "docs/prisma-app/qa/prisma-app-mobile-23-decision-ledger-regression-corpus.jsonl"
];

function fail(message) {
  console.error(`[PRISMA APP MOBILE 23 FAIL] ${message}`);
  process.exit(1);
}

function text(rel) {
  const file = path.join(root, rel);
  if (!existsSync(file)) fail(`missing ${rel}`);
  return readFileSync(file, "utf8");
}

for (const rel of required) text(rel);

const lib = text("src/lib/prisma-app/prisma-mobile-decision-ledger.ts");
const component = text("src/components/prisma-app/PrismaMobileDecisionLedger.tsx");
const dashboard = text("src/components/prisma-app/PrismaMobileDashboard.tsx");
const route = text("app/api/mobile/decision-ledger/route.ts");
const css = text("src/components/prisma-app/prisma-mobile-dashboard.module.css");
const pkg = JSON.parse(text("package.json"));
const scenarios = JSON.parse(text("docs/prisma-app/qa/prisma-app-mobile-23-decision-ledger-scenarios.json"));
const corpus = text("docs/prisma-app/qa/prisma-app-mobile-23-decision-ledger-regression-corpus.jsonl").trim().split(/\r?\n/);

if (!lib.includes("PRISMA_APP_MOBILE_23_DECISION_LEDGER")) fail("contract id missing in decision ledger builder");
if (!lib.includes("buildPrismaMobileCommandCenter") || !lib.includes("buildPrismaMobileActionInbox") || !lib.includes("buildPrismaMobileDailyBrief")) fail("decision ledger does not reuse prior v20/v21/v22 builders");
if (!lib.includes("exportText") || !lib.includes("ownerDigest") || !lib.includes("proofCards")) fail("decision ledger contract incomplete");
if (!component.includes("Bitácora móvil de decisiones") || !component.includes("ledger.exportText") || !component.includes("decisionLedgerTimeline")) fail("decision ledger component incomplete");
if (!dashboard.includes("PrismaMobileDecisionLedger") || !dashboard.includes("<PrismaMobileDecisionLedger clientSnapshot={clientSnapshot}")) fail("dashboard does not render decision ledger");
if (!route.includes("dynamic = \"force-dynamic\"") || !route.includes("revalidate = 0") || !route.includes("noStoreJsonInit")) fail("decision ledger endpoint is not no-store dynamic");
if (!css.includes("PRISMA_APP_MOBILE_23_DECISION_LEDGER START") || !css.includes("decisionLedgerTimeline")) fail("decision ledger css missing");
if (pkg.version !== "0.23.0") fail("package version not bumped to 0.23.0");
if (pkg.scripts["verify:decision-ledger"] !== "node tools/verify_prisma_app_mobile_23_decision_ledger.mjs") fail("verify:decision-ledger script missing");
if (!pkg.scripts["check:all"].includes("verify:decision-ledger")) fail("check:all does not include decision ledger");
if (!Array.isArray(scenarios.scenarios) || scenarios.scenarios.length < 480) fail("not enough QA scenarios");
if (corpus.length < 3000) fail("not enough regression traces");

for (const banned of ["mock", "lorem", "placeholder", "TODO"] ) {
  const hay = [lib, component, dashboard, route].join("\n").toLowerCase();
  if (hay.includes(banned.toLowerCase())) fail(`banned marker found: ${banned}`);
}

console.log("OK PRISMA_APP_MOBILE_23_DECISION_LEDGER verified");
