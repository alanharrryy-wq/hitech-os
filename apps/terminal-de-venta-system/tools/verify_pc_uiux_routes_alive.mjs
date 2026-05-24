#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const appRoot = path.join(root, "products", "pc", "app");
const pageRoot = path.join(appRoot, "app");
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

function routePatternToRegex(route) {
  if (route === "/") return /^\/$/;
  const escaped = route.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/\\\[[^/]+\\\]/g, "[^/]+");
  return new RegExp("^" + escaped + "$");
}

function routeExists(routes, href) {
  if (routes.has(href)) return true;
  for (const route of routes) {
    if (route.includes("[") && routePatternToRegex(route).test(href)) return true;
  }
  return false;
}

const pages = walk(pageRoot).filter(f => /\/page\.(tsx|jsx|ts|js)$/i.test(f.replace(/\\/g, "/")) && !f.replace(/\\/g, "/").includes("/api/"));
const routes = new Set(pages.map(toRoute));
const scanFiles = [path.join(appRoot, "components"), path.join(appRoot, "src", "composition"), path.join(appRoot, "src", "uiux"), path.join(appRoot, "app")]
  .flatMap(d => walk(d)).filter(f => /\.(tsx|jsx|ts|js|mjs)$/.test(f));

const hrefs = [];
const hrefRegexes = [
  /href\s*=\s*["'`]([^"'`]+)["'`]/g,
  /href\s*:\s*["'`]([^"'`]+)["'`]/g,
  /router\.push\(\s*["'`]([^"'`]+)["'`]\s*\)/g,
  /router\.replace\(\s*["'`]([^"'`]+)["'`]\s*\)/g,
];

for (const file of scanFiles) {
  const txt = fs.readFileSync(file, "utf8");
  for (const rx of hrefRegexes) {
    let m;
    while ((m = rx.exec(txt))) {
      const href = m[1].split("?")[0].split("#")[0];
      if (!href || href.startsWith("http") || href.startsWith("mailto:") || href.startsWith("#")) continue;
      if (!href.startsWith("/") || href.startsWith("/api/")) continue;
      hrefs.push({ file: path.relative(root, file).replace(/\\/g, "/"), href });
    }
  }
}

const missing = hrefs.filter(x => !routeExists(routes, x.href));
console.log(JSON.stringify({ verifier: "verify_pc_uiux_routes_alive", status: missing.length ? "FAIL" : "PASS", routeCount: routes.size, hrefCount: hrefs.length, missingCount: missing.length, missing: missing.slice(0, 100) }, null, 2));
process.exit(missing.length ? 1 : 0);
