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

function rulesForSelector(css, selector) {
  const rules = [];
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let match;
  while ((match = re.exec(css))) {
    const selectors = match[1].split(',').map((part) => part.trim());
    if (selectors.includes(selector)) rules.push(match[2]);
  }
  return rules;
}

function lastRule(css, selector) {
  const rules = rulesForSelector(css, selector);
  return rules[rules.length - 1] || '';
}

function propValue(rule, prop) {
  const re = new RegExp(`${prop}\\s*:\\s*([^;]+)`, 'i');
  return rule.match(re)?.[1]?.trim() || '';
}

function maxPx(value) {
  const matches = [...value.matchAll(/(\d+(?:\.\d+)?)px/g)].map((match) => Number(match[1]));
  return matches.length ? Math.max(...matches) : NaN;
}

function assertRange(failures, label, value, min, max) {
  if (!Number.isFinite(value) || value < min || value > max) {
    failures.push(`${label}: expected ${min}-${max}px, got ${Number.isFinite(value) ? `${value}px` : 'missing'}`);
  }
}

const repoRoot = findRepoRoot(process.cwd());
const posCssPath = 'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css';
const terminalCssPath = 'apps/terminal-de-venta-system/products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.module.css';
const shellCssPath = 'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css';
const posSafeShellCssPath = 'apps/terminal-de-venta-system/products/tablet/app/app/pos/prisma-pos-light-safe-shell.module.css';
const searchPath = 'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-product-search.tsx';
const ticketPath = 'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx';
const listPath = 'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-product-list.tsx';
const posCss = fs.readFileSync(path.join(repoRoot, posCssPath), 'utf8');
const terminalCss = fs.readFileSync(path.join(repoRoot, terminalCssPath), 'utf8');
const shellCss = fs.readFileSync(path.join(repoRoot, shellCssPath), 'utf8');
const posSafeShellCss = fs.readFileSync(path.join(repoRoot, posSafeShellCssPath), 'utf8');
const search = fs.readFileSync(path.join(repoRoot, searchPath), 'utf8');
const ticket = fs.readFileSync(path.join(repoRoot, ticketPath), 'utf8');
const list = fs.readFileSync(path.join(repoRoot, listPath), 'utf8');
const failures = [];

assertRange(failures, '.posPremiumSearchInputWrap min-height', maxPx(propValue(lastRule(posCss, '.posPremiumSearchInputWrap'), 'min-height')), 52, 58);
assertRange(failures, '.posPremiumProductCard min-height', maxPx(propValue(lastRule(posCss, '.posPremiumProductCard'), 'min-height')), 154, 186);
assertRange(failures, '.posPremiumProductStage min-height', maxPx(propValue(lastRule(posCss, '.posPremiumProductStage'), 'min-height')), 54, 78);
assertRange(failures, '.posPremiumCategoryButton min-height', maxPx(propValue(lastRule(posCss, '.posPremiumCategoryButton'), 'min-height')), 44, 52);
assertRange(failures, '.cobrarReferenceButton min-height', maxPx(propValue(lastRule(posCss, '.cobrarReferenceButton'), 'min-height')), 68, 78);

const gridValue = propValue(lastRule(posCss, '.posPremiumProductGrid'), 'grid-template-columns');
const gridMin = Number(gridValue.match(/minmax\((\d+(?:\.\d+)?)px/i)?.[1]);
if (!Number.isFinite(gridMin) || gridMin < 150 || gridMin > 170) {
  failures.push(`.posPremiumProductGrid minmax: expected 150-170px, got ${gridValue || 'missing'}`);
}

const bodyGrid = rulesForSelector(terminalCss, '.body')
  .map((rule) => propValue(rule, 'grid-template-columns'))
  .find((value) => value.includes('clamp') || [...value.matchAll(/(\d+(?:\.\d+)?)px/g)].length >= 2) || '';
const railValues = [...bodyGrid.matchAll(/(\d+(?:\.\d+)?)px/g)].map((match) => Number(match[1]));
if (railValues.length < 2 || Math.min(...railValues) < 320 || Math.max(...railValues) > 420) {
  failures.push(`terminal ticket rail: expected 320-420px in final body grid, got ${bodyGrid || 'missing'}`);
}

const headerRule = lastRule(terminalCss, '.header');
if (!/display\s*:\s*none/i.test(headerRule)) {
  failures.push('terminal context header: expected duplicate POS context header to be visually hidden.');
}
if (
  !shellCss.includes('.compactSellingShell') ||
  !shellCss.includes('padding: 0') ||
  !shellCss.includes('border: 0') ||
  !shellCss.includes('background: transparent') ||
  !shellCss.includes('box-shadow: none')
) {
  failures.push(`${shellCssPath}: compact POS shell must remove outer frame and title band.`);
}
const compactTopbarRule = rulesForSelector(shellCss, '.compactSellingShell .topbar').join('\n');
if (!compactTopbarRule.includes('background: transparent') || !compactTopbarRule.includes('box-shadow: none')) {
  failures.push(`${shellCssPath}: compact POS topbar must not render a white bar.`);
}
if (
  !posSafeShellCss.includes('PRISMA_TABLET_PRODUCT_SURFACE_EDGELESS_0207_START') ||
  !posSafeShellCss.includes('width: 100%') ||
  !posSafeShellCss.includes('margin: 0') ||
  !posSafeShellCss.includes('padding: 0')
) {
  failures.push(`${posSafeShellCssPath}: POS safe shell must not add the white outer margin/padding.`);
}

for (const [file, text, token] of [
  [searchPath, search, 'Buscar producto o escanear código'],
  [listPath, list, 'Productos'],
  [ticketPath, ticket, 'Ticket actual'],
  [ticketPath, ticket, 'Total a cobrar'],
  [ticketPath, ticket, 'Cobrar'],
  [ticketPath, ticket, 'Guardar ticket'],
  [ticketPath, ticket, 'Opciones de ticket']
]) {
  if (!text.includes(token)) failures.push(`${file}: required POS copy/control missing: ${token}`);
}

if (search.includes('Resolver código')) failures.push(`${searchPath}: resolver action still visible in POS search.`);
if (ticket.includes('<span>Reembolso</span>')) failures.push(`${ticketPath}: disabled refund teaser still visible in ticket actions.`);

if (failures.length) {
  console.error('TABLET POS VISUAL DENSITY GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET POS VISUAL DENSITY GATE: PASS');
