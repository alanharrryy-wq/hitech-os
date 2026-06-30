import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const dashboardPath = path.join(appRoot, "app", "dashboard", "page.tsx");
const decisionScreenPath = path.join(appRoot, "components", "uiux", "decision-screen.tsx");
const dropdownPath = path.join(appRoot, "components", "uiux", "smart-dropdown-dock.tsx");

function fail(message, details = {}) {
  console.error(JSON.stringify({ ok: false, message, details }, null, 2));
  process.exit(1);
}

function readRequired(filePath) {
  if (!fs.existsSync(filePath)) fail("Missing required file", { filePath });
  return fs.readFileSync(filePath, "utf8");
}

const dashboard = readRequired(dashboardPath);
const decisionScreen = readRequired(decisionScreenPath);
const dropdown = readRequired(dropdownPath);

const requiredDashboardMarkers = [
  'data-prisma-component="DashboardTaskBoard"',
  'summaryCards={dashboardSummaryCards}',
  'recommendedAction={dashboardRecommendedAction}',
  'evidence={dashboardEvidence}',
  'Atender productos críticos',
  'Revisar sincronización',
  'Validar caja',
  'Marcar revisado',
  'Posponer',
  'Pendiente de endpoint auditable',
  'currentPath="/dashboard"'
];

for (const marker of requiredDashboardMarkers) {
  if (!dashboard.includes(marker)) {
    fail("Dashboard marker missing", { marker });
  }
}

const forbiddenPatterns = [
  /router\.push\(["'`]\/dashboard\/[^"'`]+/g,
  /href=["'`]\/dashboard\/[^"'`]+/g,
  new RegExp("!" + "important", "g")
];

for (const pattern of forbiddenPatterns) {
  const match = dashboard.match(pattern);
  if (match) fail("Forbidden dashboard pattern found", { pattern: String(pattern), match });
}

if (!decisionScreen.includes("SmartDropdownDock")) {
  fail("DecisionScreen must keep SmartDropdownDock integration for dashboard filters");
}

if (!dropdown.includes("branches") || !dropdown.includes("periods") || !dropdown.includes("users")) {
  fail("SmartDropdownDock must expose dashboard dropdown catalogs");
}

const actionLinks = ["/existencias-criticas", "/sync-operativo", "/sales-control"];
for (const href of actionLinks) {
  if (!dashboard.includes(`href: "${href}"`) && !dashboard.includes(`href={task.href}`)) {
    fail("Expected actionable route missing", { href });
  }
}

console.log(JSON.stringify({
  ok: true,
  verifier: "verify_pcdash_dashboard_2406",
  dashboard: path.relative(appRoot, dashboardPath),
  checks: {
    taskBoard: true,
    dropdownDockThroughDecisionScreen: true,
    noNewDashboardRoutes: true,
    noImportant: true,
    honestBlockedActions: true,
    actionableRoutes: actionLinks
  }
}, null, 2));
