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
  'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/tablet-nav.ts',
  'apps/terminal-de-venta-system/products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-product-search.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/sync/pending-offline-sync-panel-screen.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/app/settings/license/page.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/license/license-status-card.tsx',
  'apps/terminal-de-venta-system/products/tablet/app/components/license/license-refresh-panel.tsx'
];
const forbidden = [
  { label: 'runtime', pattern: /\bruntime\b/i },
  { label: 'governor', pattern: /\bgovernor\b/i },
  { label: 'shell', pattern: /\bshell\b/i },
  { label: 'route', pattern: /\broute\b/i },
  { label: 'contract', pattern: /\bcontract\b/i },
  { label: 'source-certified', pattern: /\bsource-certified\b/i },
  { label: 'lab', pattern: /\blab\b/i },
  { label: 'qa', pattern: /\bqa\b/i },
  { label: 'visual os', pattern: /\bvisual os\b/i },
  { label: 'reference', pattern: /\breference\b/i },
  { label: 'chart-lab', pattern: /\bchart-lab\b/i },
  { label: 'debug', pattern: /\bdebug\b/i },
  { label: 'outbox', pattern: /\boutbox\b/i },
  { label: 'internal', pattern: /\binternal\b/i },
  { label: 'issuer', pattern: /\bissuer\b/i },
  { label: 'signed payload', pattern: /\bsigned payload\b/i },
  { label: 'adlant4', pattern: /\badlant4\b/i },
  { label: 'licflow2', pattern: /\blicflow2\b/i }
];
const skip = [
  /data-prisma/i,
  /^\s*import\s/,
  /\sfrom\s+["']/,
  /^\s*type\s/,
  /^\s*interface\s/,
  /^\s*function\s/,
  /^\s*export function\s/,
  /^\s*const\s+[A-Z0-9_]+/,
  /RuntimeContext/,
  /runtimeSnapshot/,
  /currentPath/,
  /routeId/,
  /canonical/i,
  /normalizeTabletPath/,
  /routePatternMatches/,
  /contract\./,
  /\.includes\(/,
  /\.startsWith\(/,
  /href\s*===/,
  /href=/,
  /href:/,
  /normalizedPath/,
  /tablet-[a-z-]+root/,
  /PRISMA_|resolvedVisual|VisualPreset/,
  /className=|styles\./,
  /src\/|@\//,
  /data-[a-z-]+=/i
];
const failures = [];

for (const rel of files) {
  const text = fs.readFileSync(path.join(repoRoot, rel), 'utf8');
  text.split(/\r?\n/).forEach((line, index) => {
    if (!/[`"']|>[^<]+</.test(line)) return;
    if (skip.some((pattern) => pattern.test(line))) return;
    for (const term of forbidden) {
      if (term.pattern.test(line)) {
        failures.push(`${rel}:${index + 1}: forbidden visible vocab candidate "${term.label}" -> ${line.trim()}`);
      }
    }
  });
}

if (failures.length) {
  console.error('TABLET NO TECHNICAL VOCAB GATE: FAIL');
  for (const failure of failures) console.error(`- ${failure}`);
  process.exit(1);
}

console.log('TABLET NO TECHNICAL VOCAB GATE: PASS');
