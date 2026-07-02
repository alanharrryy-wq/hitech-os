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
const navPath = 'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/tablet-nav.ts';
const contractsPath = 'apps/terminal-de-venta-system/products/tablet/app/src/navigation/tablet-page-contracts.ts';
const nav = fs.readFileSync(path.join(repoRoot, navPath), 'utf8');
const contracts = fs.readFileSync(path.join(repoRoot, contractsPath), 'utf8');
const failures = [];
const labRoutes = [
  '/visual-os',
  '/referencia-visual',
  '/release-gate',
  '/screen-standard-preview',
  '/prisma-dark-pos-reference',
  '/prisma-visual-catalog'
];

for (const route of labRoutes) {
  if (nav.includes(route)) failures.push(`${navPath}: lab/reference route appears in final nav owner: ${route}`);
}

const labLines = contracts.split(/\r?\n/).filter((line) => line.includes("visibility: 'lab'"));
for (const line of labLines) {
  if (line.includes('finalMenu: true')) failures.push(`${contractsPath}: lab route is marked final: ${line.trim()}`);
}
if (!contracts.includes('export const TABLET_FINAL_NAVIGATION = TABLET_PAGE_CONTRACTS.filter((contract) => contract.finalMenu);')) {
  failures.push(`${contractsPath}: final navigation filter missing or changed.`);
}

if (failures.length) {
  console.error('TABLET LAB HIDDEN FROM FINAL NAV GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET LAB HIDDEN FROM FINAL NAV GATE: PASS');
