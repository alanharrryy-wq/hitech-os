#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const appRoot = path.join(root, "products", "pc", "app");
const pageRoot = path.join(appRoot, "app");
const baselineFile = path.join(appRoot, "src", "uiux", "pc-uiux-baseline.json");
const ignoreDirs = new Set(["node_modules", ".next", "out", "dist", "build", "coverage", "test-results", "playwright-report"]);

function walk(dir, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, acc);
    else acc.push(full);
  }
  return acc;
}

function toRoute(pageFile) {
  const rel = path.relative(pageRoot, pageFile).replace(/\\/g, "/");
  if (/^page\.(tsx|jsx|ts|js)$/i.test(rel)) return "/";
  return "/" + rel.replace(/\/page\.(tsx|jsx|ts|js)$/i, "").replace(/^\/+|\/+$/g, "");
}

function snapshot() {
  const pages = walk(pageRoot).filter(f => /\/page\.(tsx|jsx|ts|js)$/i.test(f.replace(/\\/g, "/")) && !f.replace(/\\/g, "/").includes("/api/"));
  const files = walk(appRoot).filter(f => /\.(tsx|jsx|ts|js|mjs|css)$/.test(f));
  const routes = pages.map(toRoute).sort();
  let buttonCount = 0, linkCount = 0, tableCount = 0, chartHintCount = 0;
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    buttonCount += (text.match(/<(button|Button)\b/g) || []).length;
    linkCount += (text.match(/href\s*=/g) || []).length;
    tableCount += (text.match(/<table\b|DataTable|OpsTable|ActionableTable/g) || []).length;
    chartHintCount += (text.match(/EChart|Chart|chart|PrismaEChart/g) || []).length;
  }
  return { routes, routeCount: routes.length, buttonCount, linkCount, tableCount, chartHintCount };
}

if (!fs.existsSync(baselineFile)) {
  console.log(JSON.stringify({ verifier: "verify_pc_uiux_no_downgrade", status: "FAIL", missingBaseline: true, baselineFile: path.relative(root, baselineFile).replace(/\\/g, "/") }, null, 2));
  process.exit(1);
}

const baseline = JSON.parse(fs.readFileSync(baselineFile, "utf8"));
const current = snapshot();
const missingRoutes = (baseline.routes || []).filter(r => !current.routes.includes(r));
const drops = [];

for (const key of ["buttonCount", "linkCount", "tableCount", "chartHintCount"]) {
  const base = Number(baseline[key] || 0);
  const now = Number(current[key] || 0);
  if (base > 0 && now < Math.floor(base * 0.75)) drops.push({ key, baseline: base, current: now });
}

const fail = missingRoutes.length || drops.length;
console.log(JSON.stringify({ verifier: "verify_pc_uiux_no_downgrade", status: fail ? "FAIL" : "PASS", missingRoutes, drops, baselineSummary: { routeCount: baseline.routeCount, buttonCount: baseline.buttonCount, linkCount: baseline.linkCount, tableCount: baseline.tableCount, chartHintCount: baseline.chartHintCount }, currentSummary: { routeCount: current.routeCount, buttonCount: current.buttonCount, linkCount: current.linkCount, tableCount: current.tableCount, chartHintCount: current.chartHintCount } }, null, 2));
process.exit(fail ? 1 : 0);
