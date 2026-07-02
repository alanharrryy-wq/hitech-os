#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const cwd = process.cwd();
const appRoot = fs.existsSync(path.join(cwd, "package.json")) && fs.existsSync(path.join(cwd, "components"))
  ? cwd
  : path.join(cwd, "apps", "terminal-de-venta-system", "products", "tablet", "app");

const checks = [];
const expectedFinal = ["/pos", "/shift", "/stock", "/sales/today", "/returns", "/sync", "/settings/license"];
const forbiddenHomeRoutes = ["/events/outbox", "/prisma-pulse", "/visual-os", "/release-gate", "/settings/export", "/screen-standard-preview"];

function read(rel) {
  const file = path.join(appRoot, rel);
  if (!fs.existsSync(file)) {
    checks.push({ name: `exists ${rel}`, ok: false });
    return "";
  }
  checks.push({ name: `exists ${rel}`, ok: true });
  return fs.readFileSync(file, "utf8");
}

function check(name, ok, detail = "") {
  checks.push({ name, ok: Boolean(ok), detail });
}

const manifest = JSON.parse(read("src/navigation/tablet-product-navigation.manifest.json") || "{}");
const nav = read("components/tablet-shell/tablet-nav.ts");
const shell = read("components/tablet-shell/prisma-tablet-shell.tsx");
const home = read("components/tablet-home/tablet-home-screen.tsx");

check("manifest final nav routes are product routes only", JSON.stringify(manifest.tablet?.finalMenuRoutes) === JSON.stringify(expectedFinal), JSON.stringify(manifest.tablet?.finalMenuRoutes));
check("dock filter keeps expected final routes", expectedFinal.every((route) => shell.includes(`"${route}"`)));
check("top nav is not rendered in shell", !shell.includes("styles.topNav"));
check("sync dock label is human", nav.includes('"/sync": { shortLabel: "Pendientes"'));
check("legacy sync label absent from nav presentation", !nav.includes('shortLabel: "Sync"'));
for (const route of forbiddenHomeRoutes) {
  check(`home does not link ${route}`, !home.includes(`href: "${route}"`) && !home.includes(`href="${route}"`));
}
check("candidate support route not final menu", manifest.tablet?.candidateSupportRoutes?.includes("/prisma-pulse") && !manifest.tablet?.finalMenuRoutes?.includes("/prisma-pulse"));
check("internal support route not final menu", manifest.tablet?.internalSupportRoutes?.includes("/events/outbox") && !manifest.tablet?.finalMenuRoutes?.includes("/events/outbox"));

const failed = checks.filter((item) => !item.ok);
if (failed.length) {
  console.error("TABREST_NON_POS_NAVIGATION_0207 FAIL");
  for (const item of failed) console.error(`- ${item.name}${item.detail ? ` :: ${item.detail}` : ""}`);
  process.exit(1);
}
console.log(`TABREST_NON_POS_NAVIGATION_0207 PASS ${checks.length} checks`);
