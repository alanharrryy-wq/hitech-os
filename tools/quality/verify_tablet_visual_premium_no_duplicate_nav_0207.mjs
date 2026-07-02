#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function findRepoRoot(startDir) {
  let current = path.resolve(startDir);
  while (true) {
    if (fs.existsSync(path.join(current, '.git'))) return current;
    const parent = path.dirname(current);
    if (parent === current) return path.resolve(startDir);
    current = parent;
  }
}

const repoRoot = findRepoRoot(process.cwd());
const shellPath = 'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx';
const navPath = 'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/tablet-nav.ts';
const shell = fs.readFileSync(path.join(repoRoot, shellPath), 'utf8');
const nav = fs.readFileSync(path.join(repoRoot, navPath), 'utf8');
const failures = [];

if (shell.includes('const primaryTopItems = visibleNavItems')) {
  failures.push(`${shellPath}: topbar still mirrors the full final nav array.`);
}
if (shell.includes('data-prisma-component="TopNavItem"') || /<nav\s+className=\{styles\.topNav\}/.test(shell)) {
  failures.push(`${shellPath}: topbar still renders top nav items; topbar must be context only.`);
}
if (!shell.includes('data-prisma-component="TabletBottomNav"')) {
  failures.push(`${shellPath}: bottom dock owner was not found.`);
}
if (!shell.includes('compactSellingSurface') || !shell.includes('!compactSellingSurface')) {
  failures.push(`${shellPath}: POS/checkout must use compact shell without the oversized title header.`);
}
if (!shell.includes('/prisma/logo-prisma-mark-transparent.png')) {
  failures.push(`${shellPath}: compact transparent logo mark is not installed in the shell brand.`);
}
for (const bad of ['shortLabel: "Stock"', 'shortLabel: "Dev."', 'shortLabel: "Sinc."', 'shortLabel: "Lic."']) {
  if (nav.includes(bad)) failures.push(`${navPath}: old dock label remains: ${bad}`);
}
for (const expected of ['shortLabel: "Vender"', 'shortLabel: "Turno"', 'shortLabel: "Inventario"', 'shortLabel: "Ventas"', 'shortLabel: "Devol."', 'shortLabel: "Sync"', 'shortLabel: "Licencia"']) {
  if (!nav.includes(expected)) failures.push(`${navPath}: expected final dock label missing: ${expected}`);
}

if (failures.length) {
  console.error('TABLET VISUAL PREMIUM NAV GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET VISUAL PREMIUM NAV GATE: PASS');
