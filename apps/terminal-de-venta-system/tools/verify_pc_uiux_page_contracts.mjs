#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const appRoot = path.join(root, "products", "pc", "app");
const pageRoot = path.join(appRoot, "app");
const contractFile = path.join(appRoot, "src", "uiux", "page-contracts.ts");
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

const pages = walk(pageRoot).filter(f => /\/page\.(tsx|jsx|ts|js)$/i.test(f.replace(/\\/g, "/")) && !f.replace(/\\/g, "/").includes("/api/"));
const routes = pages.map(toRoute).sort();
const result = { verifier: "verify_pc_uiux_page_contracts", status: "PASS", routeCount: routes.length, contractFile: path.relative(root, contractFile).replace(/\\/g, "/"), missingContractFile: false, missingRoutes: [], missingFields: [] };

if (!fs.existsSync(contractFile)) {
  result.status = "FAIL";
  result.missingContractFile = true;
  result.missingRoutes = routes;
} else {
  const text = fs.readFileSync(contractFile, "utf8");
  for (const route of routes) {
    if (!text.includes(`"route": "${route}"`) && !text.includes(`route: "${route}"`) && !text.includes(`route: '${route}'`)) {
      result.missingRoutes.push(route);
    }
  }
  for (const token of ["humanName", "primaryQuestion", "requiredBlocks", "dataSourceKind"]) {
    if (!text.includes(token)) result.missingFields.push(token);
  }
  if (result.missingRoutes.length || result.missingFields.length) result.status = "FAIL";
}

console.log(JSON.stringify(result, null, 2));
process.exit(result.status === "PASS" ? 0 : 1);
