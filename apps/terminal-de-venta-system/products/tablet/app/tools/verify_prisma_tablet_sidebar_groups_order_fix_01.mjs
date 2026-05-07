#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const tabletRoot = path.join(root, "apps", "terminal-de-venta-system", "products", "tablet", "app");

const checks = [
  {
    rel: "components/tablet-shell/tablet-nav.ts",
    needles: [
      '{ href: "/", label: "Inicio"',
      '{ href: "/shift", label: "Turno y caja"',
      '{ href: "/pos", label: "Vender"',
      '{ href: "/catalog", label: "Catálogo"',
      '{ href: "/stock", label: "Existencias"',
      '{ href: "/sales/today", label: "Ventas de hoy"'
    ]
  },
  {
    rel: "components/tablet-shell/prisma-tablet-shell.tsx",
    needles: [
      'data-prisma-component="CollapsibleNavGroup"',
      "className={styles.navGroupSummary}",
      "className={styles.navGroupTitle}",
      "className={styles.navGroupChevron}"
    ]
  },
  {
    rel: "components/tablet-shell/prisma-tablet-shell.module.css",
    needles: [
      "PRISMA_TABLET_SIDEBAR_GROUPS_ORDER_FIX_01",
      ".navGroupSummary",
      ".navGroup:not([open]) .navGroupTitle",
      ".navGroup[open] .navGroupTitle"
    ]
  }
];

function read(rel) {
  const file = path.join(tabletRoot, rel);
  if (!fs.existsSync(file)) throw new Error(`Missing required file: ${rel}`);
  return fs.readFileSync(file, "utf8");
}

for (const check of checks) {
  const text = read(check.rel);
  for (const needle of check.needles) {
    if (!text.includes(needle)) {
      throw new Error(`Verification failed for ${check.rel}: missing ${needle}`);
    }
  }
}

const navText = read("components/tablet-shell/tablet-nav.ts");
const order = [
  'href: "/", label: "Inicio"',
  'href: "/shift", label: "Turno y caja"',
  'href: "/pos", label: "Vender"',
  'href: "/catalog", label: "Catálogo"',
  'href: "/stock", label: "Existencias"'
];
let cursor = -1;
for (const marker of order) {
  const index = navText.indexOf(marker);
  if (index < 0) throw new Error(`Order marker not found: ${marker}`);
  if (index <= cursor) throw new Error(`Navigation order is wrong around: ${marker}`);
  cursor = index;
}

console.log("PRISMA_TABLET_SIDEBAR_GROUPS_ORDER_FIX_01 verification OK");
