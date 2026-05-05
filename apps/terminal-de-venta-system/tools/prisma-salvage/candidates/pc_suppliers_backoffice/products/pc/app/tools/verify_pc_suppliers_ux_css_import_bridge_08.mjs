#!/usr/bin/env node
import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';

const root = process.argv[2];
if (!root) {
  console.error('Usage: node verify_pc_suppliers_ux_css_import_bridge_08.mjs <pc-app-root>');
  process.exit(2);
}

const layoutPath = join(root, 'app', 'layout.tsx');
const cssPath = join(root, 'app', 'suppliers-ux-v08.css');
const workbenchPath = join(root, 'components', 'suppliers', 'smart-purchase-workbench.tsx');

for (const file of [layoutPath, cssPath, workbenchPath]) {
  if (!existsSync(file)) {
    console.error(`FAIL missing ${file}`);
    process.exit(1);
  }
}

const layout = readFileSync(layoutPath, 'utf8');
const css = readFileSync(cssPath, 'utf8');
const workbench = readFileSync(workbenchPath, 'utf8');

const checks = [
  ['layout imports v08 css', layout.includes('import "./suppliers-ux-v08.css";')],
  ['css bridge marker', css.includes('PRISMA PC Suppliers UX v08')],
  ['gold CTA style loaded', css.includes('.reason-callout-v07 summary') && css.includes('PRISMA LO RECOMIENDA') === false],
  ['product rows style loaded', css.includes('.product-line-v07') && css.includes('grid-template-columns')],
  ['trust checklist style loaded', css.includes('.trust-checklist-v07')],
  ['calendar timeline style loaded', css.includes('.calendar-timeline-v07')],
  ['audit roadmap style loaded', css.includes('.audit-roadmap-v07')],
  ['workbench v07 structure present', workbench.includes('supplier-readable-v07')],
  ['workbench visible reason CTA present', workbench.includes('¿POR QUÉ PRISMA LO RECOMIENDA?')],
  ['no visible api route copy', !workbench.includes('POST /api') && !workbench.includes('/api/proveedores')]
];

for (const [label, ok] of checks) {
  if (!ok) {
    console.error(`FAIL ${label}`);
    process.exit(1);
  }
  console.log(`OK ${label}`);
}

console.log(`NODE READY suppliers ux css import bridge v08 ${checks.length} checks`);
