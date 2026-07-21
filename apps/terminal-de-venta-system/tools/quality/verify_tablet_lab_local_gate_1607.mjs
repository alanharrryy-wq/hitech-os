#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const MARKER = "TABLET_LAB_LOCAL_GATE_1607";

function findRepoRoot(startDir) {
  let current = path.resolve(startDir);
  while (true) {
    if (fs.existsSync(path.join(current, ".git")) || fs.existsSync(path.join(current, "PRISMA Factory Ledger"))) return current;
    const parent = path.dirname(current);
    if (parent === current) throw new Error(`No pude localizar el repo desde ${startDir}`);
    current = parent;
  }
}

const repoRoot = findRepoRoot(process.cwd());
const tabletRoot = path.join(repoRoot, "apps", "terminal-de-venta-system", "products", "tablet", "app");
const routeRoot = path.join(tabletRoot, "app", "tablet-lab");
const middlewarePath = path.join(tabletRoot, "middleware.ts");
const contractsPath = path.join(tabletRoot, "src", "navigation", "tablet-page-contracts.ts");
const compositionPath = path.join(tabletRoot, "src", "composition", "navigation.ts");
const navPath = path.join(tabletRoot, "components", "tablet-shell", "tablet-nav.ts");
const failures = [];
const checks = [];

function read(file) { return fs.readFileSync(file, "utf8"); }
function check(name, condition, detail) {
  checks.push({ name, pass: Boolean(condition), detail });
  if (!condition) failures.push(`${name}: ${detail}`);
}

const pageCandidates = ["page.tsx", "page.ts", "page.jsx", "page.js"].map((name) => path.join(routeRoot, name));
check("Tablet Lab page exists", pageCandidates.some((file) => fs.existsSync(file) && fs.statSync(file).isFile()), routeRoot);
check("Tablet Lab install marker exists", fs.existsSync(path.join(routeRoot, ".prisma-internal-lab.json")), routeRoot);

const middleware = read(middlewarePath);
check("local gate marker", middleware.includes(MARKER), middlewarePath);
check("production remains blocked", middleware.includes('process.env.NODE_ENV === "production"'), middlewarePath);
check("localhost allowed", middleware.includes('"localhost"') && middleware.includes('"127.0.0.1"'), middlewarePath);
check("retired routes still return 404", middleware.includes("status: 404"), middlewarePath);
check("no-store response", middleware.includes('"cache-control", "no-store"'), middlewarePath);

const contracts = read(contractsPath);
const activeRegion = contracts.split("export const TABLET_RETIRED_INTERNAL_ROUTES")[0];
check("Tablet Lab absent from active customer contracts", !activeRegion.includes("route: '/tablet-lab'"), contractsPath);
check("Tablet Lab remains documented as retired internal", contracts.includes("route: '/tablet-lab'"), contractsPath);
check("Tablet Lab absent from composition navigation", !read(compositionPath).includes("/tablet-lab"), compositionPath);
check("Tablet Lab absent from shell navigation", !read(navPath).includes("/tablet-lab"), navPath);

const sourceFiles = [];
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else sourceFiles.push(full);
  }
}
if (fs.existsSync(routeRoot)) walk(routeRoot);
const forbidden = ["products/pc", "products/mobile", "products/chart-lab", "shared-ui"];
for (const file of sourceFiles.filter((file) => /\.(?:ts|tsx|js|jsx|css|scss)$/.test(file))) {
  const text = read(file).replaceAll("\\", "/");
  for (const token of forbidden) check(`no forbidden surface import: ${token}`, !text.includes(token), file);
}

const report = {
  schema: "prisma.tablet-lab.local-gate.verify.v1",
  status: failures.length ? "FAIL" : "PASS_TABLET_LAB_LOCAL_ONLY",
  repoRoot,
  routeRoot,
  sourceFileCount: sourceFiles.length,
  checks,
  failures
};

if (process.env.PRISMA_TABLET_LAB_REPORT) fs.writeFileSync(process.env.PRISMA_TABLET_LAB_REPORT, JSON.stringify(report, null, 2) + "\n", "utf8");
if (failures.length) {
  console.error("TABLET LAB LOCAL GATE: FAIL");
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}
console.log("TABLET LAB LOCAL GATE: PASS");
console.log(`- files: ${sourceFiles.length}`);
console.log("- route: /tablet-lab");
console.log("- availability: localhost + non-production only");
