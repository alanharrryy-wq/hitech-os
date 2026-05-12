#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const verifier = "PRISMA_APP_MOBILE_40_CRYSTAL_INTELLIGENCE";

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, verifier, message, details }, null, 2));
  process.exit(1);
}

function read(rel) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) fail(`Missing file: ${rel}`);
  return fs.readFileSync(full, "utf8");
}

const files = {
  contracts: "src/lib/prisma-app/mobile-intelligence/contracts.ts",
  connectors: "src/lib/prisma-app/mobile-intelligence/connectors.ts",
  dataQuality: "src/lib/prisma-app/mobile-intelligence/data-quality-engine.ts",
  alerts: "src/lib/prisma-app/mobile-intelligence/alert-engine.ts",
  actions: "src/lib/prisma-app/mobile-intelligence/action-inbox-engine.ts",
  charts: "src/lib/prisma-app/mobile-intelligence/chart-series-engine.ts",
  snapshot: "src/lib/prisma-app/mobile-intelligence/snapshot-engine.ts",
  viewModels: "src/lib/prisma-app/mobile-intelligence/view-models.ts",
  dashboard: "src/components/prisma-app/PrismaMobileDashboard.tsx",
  ui: "src/components/prisma-app/PrismaMobileCrystalCommand.tsx",
  css: "src/components/prisma-app/prisma-crystal-command.module.css",
  navigator: "src/components/prisma-app/PrismaMobilePremiumNavigator.tsx",
  route: "app/api/mobile/data-quality/route.ts",
  pkg: "package.json"
};

const textByFile = Object.fromEntries(Object.entries(files).map(([key, rel]) => [key, read(rel)]));
const all = Object.values(textByFile).join("\n");

const requiredTokens = [
  "live",
  "partial",
  "offline",
  "stale",
  "unknown",
  "demo-disabled",
  "PrismaMobileApiResponseSchema",
  "DataQualityReportSchema",
  "TabletConnector",
  "PcConnector",
  "ControlConnector",
  "BlackBoxConnector",
  "LocalSnapshotConnector",
  "evaluateDataQuality",
  "buildIntelligenceAlerts",
  "buildIntelligenceActionInbox",
  "buildChartViewModels",
  "buildPrismaMobileIntelligenceSnapshot",
  "mapSnapshotToHomeViewModel",
  "PrismaMobileCrystalCommand",
  "operational-health-gauge",
  "sales-rhythm-hourly",
  "revenue-momentum",
  "inventory-risk-ranking",
  "alert-severity-donut",
  "sync-freshness-outbox",
  "cash-variance-bullet",
  "health-radar-dimensions"
];

for (const token of requiredTokens) {
  if (!all.includes(token)) fail("Missing required crystal intelligence token", { token });
}

const chartKeys = Array.from(textByFile.charts.matchAll(/chartKey:\s*"([^"]+)"/g)).map((match) => match[1]);
const uniqueChartKeys = [...new Set(chartKeys)];
if (uniqueChartKeys.length < 6) fail("Expected at least 6 chart view models", { uniqueChartKeys });

const highCriticalEvidenceGuard = /draft\.severity === "critical" \|\| draft\.severity === "high"[\s\S]*!hasEvidence/.test(textByFile.alerts);
if (!highCriticalEvidenceGuard) fail("High/critical alerts must be downgraded or blocked without evidence");

if (!textByFile.dashboard.includes("mobile-crystal-first-viewport")) {
  fail("Crystal Command must own the first visible Mobile viewport");
}

if (!textByFile.dashboard.includes('mode="home"')) {
  fail("Dashboard must mount PrismaMobileCrystalCommand home mode before long secondary surfaces");
}

const homeStart = textByFile.ui.indexOf('if (mode === "home")');
const operationStart = textByFile.ui.indexOf('if (mode === "operation")');
const homeModeBlock = homeStart >= 0 && operationStart > homeStart
  ? textByFile.ui.slice(homeStart, operationStart)
  : "";
for (const token of [
  "HealthGauge",
  "MomentumSparkline",
  "SalesRhythmChart",
  "InventoryRiskRanking",
  "AlertSeverityDonut",
  "SyncFreshnessChart"
]) {
  if (!homeModeBlock.includes(token)) fail("Home Crystal Command must render the six rescue KPI/chart modules", { token });
}

const forbiddenUi = ["Math.random", "faker", "mockProduction", "demo fallback", "authorization:", "cookie:", "password:", "apiKey", "private key"];
for (const token of forbiddenUi) {
  if (all.toLowerCase().includes(token.toLowerCase())) fail("Forbidden production-data or sensitive-token pattern found", { token });
}

const pkg = JSON.parse(textByFile.pkg);
if (pkg.scripts?.["verify:crystal-intelligence"] !== "node tools/verify_prisma_app_mobile_40_crystal_intelligence.mjs") {
  fail("Missing package script verify:crystal-intelligence");
}

console.log(JSON.stringify({
  ok: true,
  verifier,
  chartModules: uniqueChartKeys,
  runtimeModes: ["live", "partial", "offline", "stale", "unknown", "demo-disabled"],
  evidenceRule: "high-critical-requires-evidence"
}, null, 2));
