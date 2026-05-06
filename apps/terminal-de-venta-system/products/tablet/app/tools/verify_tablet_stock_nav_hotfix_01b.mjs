#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const appRoot = process.cwd();
const navPath = path.join(appRoot, "components", "tablet-shell", "tablet-nav.ts");
const stockPath = path.join(appRoot, "app", "stock", "page.tsx");

function ok(message) {
  console.log(`OK ${message}`);
}

function fail(message) {
  console.error(`FAIL ${message}`);
  process.exitCode = 1;
}

function readRequired(filePath, label) {
  if (!fs.existsSync(filePath)) {
    fail(`missing ${label}: ${filePath}`);
    return "";
  }
  ok(`exists ${label}`);
  return fs.readFileSync(filePath, "utf8");
}

const nav = readRequired(navPath, "components/tablet-shell/tablet-nav.ts");

const checks = [
  [nav.includes('href: "/stock", label: "Existencias"'), 'Existencias points to /stock'],
  [!nav.includes('href: "/inventory/low-stock", label: "Existencias"'), 'Existencias no longer points directly to low-stock'],
  [nav.includes('if (href === "/stock")'), 'active matcher handles /stock'],
  [nav.includes('currentPath === "/inventory/low-stock"'), 'low-stock still highlights Existencias'],
  [nav.includes('href: "/settings/export"'), 'export navigation preserved'],
  [nav.includes('href: "/returns"'), 'returns navigation preserved'],
  [nav.includes('href: "/sync"'), 'sync navigation preserved'],
];

for (const [condition, message] of checks) {
  if (condition) ok(message);
  else fail(message);
}

if (fs.existsSync(stockPath)) {
  const stock = fs.readFileSync(stockPath, "utf8");
  if (stock.includes("PrismaOperationalScreen") && stock.includes('currentPath: "/stock"')) {
    ok("stock route is the real operational screen");
  } else {
    console.log("WARN stock route exists but does not look like PRISMA_TABLET_STOCK_SCREEN_01A_REAL_VIEW yet");
  }
} else {
  console.log("WARN app/stock/page.tsx is missing; nav fix is installed but /stock needs its screen package");
}

if (process.exitCode) {
  process.exit(process.exitCode);
}
console.log("OK PRISMA_TABLET_STOCK_NAV_HOTFIX_01B verification passed");
