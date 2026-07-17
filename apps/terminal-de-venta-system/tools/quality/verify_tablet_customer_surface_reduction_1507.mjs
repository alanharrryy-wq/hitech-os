#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const RETIRED_ROUTE_DIRS = [
  "events/outbox",
  "prisma-pulse",
  "prisma-dark-pos-reference",
  "prisma-visual-catalog",
  "referencia-visual",
  "release-gate",
  "screen-standard-preview",
  "visual-os"
];

const RETIRED_ROUTES = [
  "/events/outbox",
  "/prisma-pulse",
  "/prisma-dark-pos-reference",
  "/prisma-visual-catalog",
  "/referencia-visual",
  "/release-gate",
  "/screen-standard-preview",
  "/tablet-lab",
  "/visual-os",
  "/visual-os/detached",
  "/visual-os/materiality-catalog",
  "/visual-os/pro",
  "/visual-os/realtime",
  "/visual-os/tablet-background-gallery",
  "/visual-os/tablet-codex-gallery"
];

const REQUIRED_CUSTOMER_PAGES = [
  "page.tsx",
  "pos/page.tsx",
  "checkout/page.tsx",
  "catalog/page.tsx",
  "stock/page.tsx",
  "inventory/page.tsx",
  "inventory/low-stock/page.tsx",
  "existencias/page.tsx",
  "shift/page.tsx",
  "sales/page.tsx",
  "sales/today/page.tsx",
  "sales/history/page.tsx",
  "returns/page.tsx",
  "sync/page.tsx",
  "offline/page.tsx",
  "settings/license/page.tsx",
  "settings/export/page.tsx",
  "settings/data/page.tsx",
  "setup/page.tsx"
];

function findRepoRoot(startDir) {
  let current = path.resolve(startDir);
  while (true) {
    if (fs.existsSync(path.join(current, ".git")) || fs.existsSync(path.join(current, "PRISMA Factory Ledger"))) return current;
    const parent = path.dirname(current);
    if (parent === current) throw new Error(`No pude localizar el repo desde ${startDir}`);
    current = parent;
  }
}

function read(file) {
  return fs.readFileSync(file, "utf8");
}

const repoRoot = findRepoRoot(process.cwd());
const systemRoot = path.join(repoRoot, "apps", "terminal-de-venta-system");
const tabletRoot = path.join(systemRoot, "products", "tablet", "app");
const appRoot = path.join(tabletRoot, "app");
const failures = [];
const warnings = [];
const checks = [];

function check(name, condition, detail) {
  checks.push({ name, pass: Boolean(condition), detail });
  if (!condition) failures.push(`${name}: ${detail}`);
}

for (const rel of RETIRED_ROUTE_DIRS) {
  const target = path.join(appRoot, ...rel.split("/"));
  check(`retired route directory absent: /${rel}`, !fs.existsSync(target), target);
}

// TABLET_LAB_LOCAL_GATE_1607: source is restored for localhost development, while middleware
// and navigation contracts keep it unavailable to customers.
const tabletLabPage = path.join(appRoot, "tablet-lab", "page.tsx");
const tabletLabMarker = path.join(appRoot, "tablet-lab", ".prisma-internal-lab.json");
check("internal Tablet Lab source restored", fs.existsSync(tabletLabPage) && fs.statSync(tabletLabPage).isFile(), tabletLabPage);
check("internal Tablet Lab marker present", fs.existsSync(tabletLabMarker) && fs.statSync(tabletLabMarker).isFile(), tabletLabMarker);

for (const rel of REQUIRED_CUSTOMER_PAGES) {
  const target = path.join(appRoot, ...rel.split("/"));
  check(`customer page preserved: ${rel}`, fs.existsSync(target) && fs.statSync(target).isFile(), target);
}

const apiOutbox = path.join(appRoot, "api", "pos", "events", "outbox", "route.ts");
check("outbox API preserved", fs.existsSync(apiOutbox) && fs.statSync(apiOutbox).isFile(), apiOutbox);

const chartLabRequired = [
  path.join(systemRoot, "products", "chart-lab", "app", "app", "page.tsx"),
  path.join(systemRoot, "products", "chart-lab", "app", "app", "recipe-studio-v2", "page.tsx"),
  path.join(systemRoot, "products", "chart-lab", "app", "app", "api", "health", "route.ts")
];
for (const target of chartLabRequired) check("Chart Lab preserved", fs.existsSync(target) && fs.statSync(target).isFile(), target);

const contractsPath = path.join(tabletRoot, "src", "navigation", "tablet-page-contracts.ts");
const compositionPath = path.join(tabletRoot, "src", "composition", "navigation.ts");
const navPath = path.join(tabletRoot, "components", "tablet-shell", "tablet-nav.ts");
const middlewarePath = path.join(tabletRoot, "middleware.ts");

for (const target of [contractsPath, compositionPath, navPath, middlewarePath]) {
  check("replacement marker present", read(target).includes("CUSTOMER_SURFACE_REDUCTION_1507"), target);
}

const contracts = read(contractsPath);
const activeRegion = contracts.split("export const TABLET_RETIRED_INTERNAL_ROUTES")[0];
for (const route of RETIRED_ROUTES) {
  check(`retired route removed from active contracts: ${route}`, !activeRegion.includes(`route: '${route}'`), contractsPath);
  check(`retired route documented: ${route}`, contracts.includes(`route: '${route}'`), contractsPath);
}

const composition = read(compositionPath);
check("internal-support excluded from secondary navigation", !composition.includes('"internal-support"') && !composition.includes("'internal-support'"), compositionPath);

const nav = read(navPath);
check("outbox removed from shell active aliases", !nav.includes('normalizedPath === "/events/outbox"'), navPath);

const middlewareSource = read(middlewarePath);
check("middleware returns 404", middlewareSource.includes("status: 404"), middlewarePath);
check("Tablet Lab local gate marker present", middlewareSource.includes("TABLET_LAB_LOCAL_GATE_1607"), middlewarePath);
check("Tablet Lab blocked in production", middlewareSource.includes('process.env.NODE_ENV === "production"'), middlewarePath);
check("Tablet Lab restricted to localhost", middlewareSource.includes('"localhost"') && middlewareSource.includes('"127.0.0.1"'), middlewarePath);
for (const prefix of ["/events/outbox", "/prisma-pulse", "/tablet-lab", "/visual-os"]) {
  check(`middleware guards ${prefix}`, middlewareSource.includes(`"${prefix}"`), middlewarePath);
}

const report = {
  schema: "prisma.tablet.customer-surface-reduction.verify.v1",
  status: failures.length ? "FAIL" : "PASS_TABLET_CUSTOMER_SURFACES_REDUCED_CHART_LAB_PRESERVED",
  repoRoot,
  retiredRoutes: RETIRED_ROUTES,
  checks,
  warnings,
  failures
};

if (process.env.PRISMA_CUSTOMER_SURFACE_REPORT) {
  fs.writeFileSync(process.env.PRISMA_CUSTOMER_SURFACE_REPORT, JSON.stringify(report, null, 2) + "\n", "utf8");
}

if (failures.length) {
  console.error("TABLET CUSTOMER SURFACE REDUCTION: FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log("TABLET CUSTOMER SURFACE REDUCTION: PASS");
console.log(`- retired route groups: ${RETIRED_ROUTE_DIRS.length}`);
console.log(`- protected customer pages: ${REQUIRED_CUSTOMER_PAGES.length}`);
console.log("- Chart Lab: preserved");
console.log("- Tablet APIs: preserved");
