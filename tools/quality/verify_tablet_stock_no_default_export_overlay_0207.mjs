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
const stockPagePath = 'apps/terminal-de-venta-system/products/tablet/app/app/stock/page.tsx';
const stockScreenPath = 'apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx';
const cssPath = 'apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist.module.css';
const page = fs.readFileSync(path.join(repoRoot, stockPagePath), 'utf8');
const screen = fs.readFileSync(path.join(repoRoot, stockScreenPath), 'utf8');
const css = fs.readFileSync(path.join(repoRoot, cssPath), 'utf8');
const failures = [];

if (page.includes('ContextualExportBand')) failures.push(`${stockPagePath}: ContextualExportBand still mounted on /stock.`);
if (/actions=\{/.test(page)) failures.push(`${stockPagePath}: /stock still passes default actions overlay.`);
if (!screen.includes('function StockExportMenu')) failures.push(`${stockScreenPath}: stock export menu is missing.`);
if (!screen.includes('<details className={styles.exportMenu}>')) failures.push(`${stockScreenPath}: export affordance must be collapsed by default.`);
if (!css.includes('.exportMenuBody')) failures.push(`${cssPath}: collapsed export menu styles missing.`);

if (failures.length) {
  console.error('TABLET STOCK EXPORT OVERLAY GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET STOCK EXPORT OVERLAY GATE: PASS');
