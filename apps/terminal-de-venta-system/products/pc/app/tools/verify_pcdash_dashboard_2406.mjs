import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const dashboardPath = path.join(appRoot, "app", "dashboard", "page.tsx");
const decisionScreenPath = path.join(appRoot, "components", "uiux", "decision-screen.tsx");

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
const requiredDashboardMarkers = [
  'data-prisma-component="DashboardTaskBoard"',
  'getBackofficeDashboard',
  'getOperationalTaskWorkspace',
  'summaryCards={summaryCards}',
  'recommendedAction={recommendedAction}',
  'evidence={evidence}',
  'OperationalTaskWorkspace',
  'currentPath="/dashboard"'
];
for (const marker of requiredDashboardMarkers) {
  if (!dashboard.includes(marker)) fail("Dashboard marker missing", { marker });
}
if (decisionScreen.includes("SmartDropdownDock")) fail("DecisionScreen must not inject global SmartDropdownDock into dashboard or other customer screens");
for (const pattern of [/router\.push\(["'`]\/dashboard\/[^"'`]+/g, /href=["'`]\/dashboard\/[^"'`]+/g, new RegExp("!" + "important", "g")]) {
  const match = dashboard.match(pattern);
  if (match) fail("Forbidden dashboard pattern found", { pattern: String(pattern), match });
}
for (const href of ["/sync-operativo", "/stock", "/sales-control"]) {
  if (!dashboard.includes(`href: "${href}"`) && !dashboard.includes("href={task.href}")) fail("Expected actionable route missing", { href });
}
console.log(JSON.stringify({ ok: true, verifier: "verify_pcdash_dashboard_2406", checks: { taskBoard: true, realDashboardLoader: true, globalSmartDropdownRemoved: true, noNewDashboardRoutes: true, noImportant: true } }, null, 2));
