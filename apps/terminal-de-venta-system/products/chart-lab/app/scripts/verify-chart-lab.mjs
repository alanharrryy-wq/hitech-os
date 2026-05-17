import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const appRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const terminalRoot = path.resolve(appRoot, "..", "..", "..");
const requireFromLab = createRequire(path.join(appRoot, "package.json"));

const pass = (message) => console.log(`[PRISMA Chart Lab] PASS: ${message}`);
const fail = (message) => {
  console.error(`[PRISMA Chart Lab] FAIL: ${message}`);
  process.exitCode = 1;
};

function read(relativePath, root = appRoot) {
  return fs.readFileSync(path.join(root, relativePath), "utf8");
}

function exists(relativePath, root = appRoot) {
  return fs.existsSync(path.join(root, relativePath));
}

function resolveDependency(specifier) {
  try {
    requireFromLab.resolve(specifier);
    pass(`resolves ${specifier}`);
  } catch (error) {
    fail(`cannot resolve ${specifier}: ${error.message}`);
  }
}

for (const specifier of ["echarts", "echarts/core", "echarts/charts", "echarts/components", "echarts/renderers"]) {
  resolveDependency(specifier);
}

const requiredFiles = [
  "package.json",
  "next.config.mjs",
  "app/page.tsx",
  "app/globals.css",
  "src/components/PrismaChartLabShell.tsx",
  "src/components/ChartControlDeck.tsx",
  "src/prisma-charts/chart-lab-registry.tsx",
  "src/prisma-charts/chart-lab-control-model.ts",
  "src/prisma-charts/maps/chart-lab-maps.ts",
  "src/prisma-charts/components/LabEChartFrame.tsx",
  "src/prisma-charts/components/ExampleFutureChart.tsx",
  "wrangler.jsonc",
  "deploy/cloudflare-pages.json",
  "deploy/cloudflare-tunnel/prisma-chart-lab.tunnel.template.yml",
  "NEW_CHART_TEMPLATE.md",
  "README.md"
];

for (const file of requiredFiles) {
  if (exists(file)) pass(`required file exists: ${file}`);
  else fail(`missing required file: ${file}`);
}

const pkg = JSON.parse(read("package.json"));
if (pkg.scripts?.dev?.includes("-p 3000") && pkg.scripts.dev.includes("127.0.0.1")) pass("dev script binds localhost:3000 explicitly");
else fail("dev script must bind localhost:3000 explicitly");
if (pkg.dependencies?.echarts === "5.6.0") pass("echarts dependency is declared in the lab package");
else fail("echarts@5.6.0 must be declared in the lab package");

const registry = read("src/prisma-charts/chart-lab-registry.tsx");
const chartIds = [...registry.matchAll(/id: "([^"]+)"/g)].map((match) => match[1]);
const uniqueChartIds = new Set(chartIds);
if (chartIds.length === uniqueChartIds.size) pass("chart ids are unique");
else fail("chart ids must be unique");

const chartOpsIds = [
  "pc.causal-flow-ribbon",
  "pc.operational-density-field",
  "pc.service-dependency-graph",
  "pc.inventory-risk-treemap",
  "pc.decision-ledger-timeline",
  "pc.financial-operational-waterfall",
  "tablet.shift-pulse-strip",
  "tablet.sync-outbox-status-matrix",
  "mobile.owner-pulse-timeline",
  "mobile.action-inbox-priority-stack",
  "mobile.health-radar-compact",
  "mobile.freshness-beacon-grid",
  "mobile.incident-spark-cards",
  "mobile.confidence-meter-bands"
];

const missingChartOps = chartOpsIds.filter((id) => !uniqueChartIds.has(id));
if (missingChartOps.length === 0) pass("all 14 ChartOps charts are registered");
else fail(`missing ChartOps chart ids: ${missingChartOps.join(", ")}`);
if (uniqueChartIds.has("example.future-chart")) pass("Example Future Chart placeholder is registered");
else fail("Example Future Chart placeholder is missing");
if (chartIds[0] === "pc.causal-flow-ribbon") pass("Causal Flow Ribbon is first in the registry");
else fail(`Causal Flow Ribbon must be first; first chart is ${chartIds[0] ?? "none"}`);
if (registry.includes("causalFlowRibbonOption") && registry.includes("renderer: \"canvas\"")) pass("Causal Flow Ribbon has a functional ECharts option entry");
else fail("Causal Flow Ribbon option entry is incomplete");

const tsconfig = JSON.parse(read("tsconfig.json"));
const paths = tsconfig.compilerOptions?.paths ?? {};
if (!("react" in paths) && !("react/jsx-runtime" in paths) && !("react/jsx-dev-runtime" in paths)) pass("React runtime aliases are not configured");
else fail("React runtime aliases must not be configured");

const shell = read("src/components/PrismaChartLabShell.tsx");
if (shell.includes("chartLabRegistry.map") || shell.includes("filteredCharts.map")) pass("navigation is registry-driven");
else fail("lab navigation must be registry-driven");
if (shell.includes("ChartControlDeck") && shell.includes("Copy Current Config JSON")) pass("runtime controls are visible in the lab shell");
else fail("runtime controls must be visible in the lab shell");

const maps = read("src/prisma-charts/maps/chart-lab-maps.ts");
if (maps.includes("chartLabMapCatalog") && maps.includes("promotionManifestMap")) pass("Chart Lab maps are first-class assets");
else fail("Chart Lab maps are incomplete");

const terminalPackage = JSON.parse(read("package.json", terminalRoot));
if (terminalPackage.scripts?.["chart-lab:dev"]?.includes("products/chart-lab/app")) pass("terminal root chart-lab scripts are registered");
else fail("terminal root chart-lab scripts are missing");

const docsToCheck = [
  path.join(terminalRoot, "README.md"),
  path.join(terminalRoot, "docs", "prisma", "PRISMA_CHART_LAB_LOCAL_AND_CLOUDFLARE.md"),
  path.join(appRoot, "README.md"),
  path.join(appRoot, "PROMOTION.md"),
  path.join(appRoot, "NEW_CHART_TEMPLATE.md")
];
for (const doc of docsToCheck) {
  if (!fs.existsSync(doc)) {
    fail(`missing documentation: ${doc}`);
    continue;
  }
  const content = fs.readFileSync(doc, "utf8");
  if (content.includes("3000") && content.includes("Chart Lab")) pass(`doc mentions Chart Lab and port 3000: ${path.relative(terminalRoot, doc)}`);
  else fail(`doc must mention Chart Lab and port 3000: ${doc}`);
}

if (!process.exitCode) pass("verification complete");
