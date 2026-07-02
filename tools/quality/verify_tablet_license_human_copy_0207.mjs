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
const files = [
  'apps/terminal-de-venta-system/products/tablet/app/app/settings/license/page.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/license/license-status-card.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/license/license-refresh-panel.tsx'
];
const forbiddenVisible = [
  'Modo runtime',
  'Modo desarrollo',
  'Entorno de desarrollo',
  'issuer',
  'governor',
  'runtime signed payload',
  'bootstrap Ed25519',
  'active_local_signed',
  'ADLANT4',
  'LICFLOW2'
];
const failures = [];

for (const rel of files) {
  const text = fs.readFileSync(path.join(repoRoot, rel), 'utf8');
  text.split(/\r?\n/).forEach((line, index) => {
    if (!/[`"']|>[^<]+</.test(line)) return;
    if (/^\s*import\s|\sfrom\s+["']|RuntimeContext|runtimeContext|governor|data-prisma|className=|styles\.|\.includes\(/i.test(line)) return;
    for (const term of forbiddenVisible) {
      if (line.includes(term)) failures.push(`${rel}:${index + 1}: forbidden license copy remains: ${term}`);
    }
  });
}

const statusCard = fs.readFileSync(path.join(repoRoot, files[1]), 'utf8');
if (!statusCard.includes('sourceLabel(status.source)')) failures.push(`${files[1]}: raw license source is still exposed.`);
if (!statusCard.includes('featureReasonLabel(feature.reason)')) failures.push(`${files[1]}: raw feature reasons are still exposed.`);
if (!statusCard.includes('Ver detalle para soporte')) failures.push(`${files[1]}: support details disclosure missing.`);

if (failures.length) {
  console.error('TABLET LICENSE HUMAN COPY GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET LICENSE HUMAN COPY GATE: PASS');
