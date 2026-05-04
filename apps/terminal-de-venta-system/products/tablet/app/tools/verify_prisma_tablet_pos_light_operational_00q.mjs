#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const failures = [];
function read(rel){ const full=path.join(root, rel); if(!fs.existsSync(full)){ failures.push(`missing ${rel}`); return ''; } return fs.readFileSync(full,'utf8'); }
const checks = [
  [read('styles/prisma-visual-os/prisma-light-operational-pos.tokens.00p.css').includes('PRISMA_LIGHT_OPERATIONAL_POS'), '00P token CSS missing'],
  [read('products/tablet/app/app/globals.css').includes('prisma-light-operational-pos.tokens.00p.css'), 'globals import missing'],
  [read('products/tablet/app/components/tablet-shell/prisma-tablet-shell.tsx').includes('data-prisma-preset={visualPreset}'), 'shell preset data binding missing'],
  [read('products/tablet/app/components/pos/pos-screen.tsx').includes('visualPreset="PRISMA_LIGHT_OPERATIONAL_POS"'), 'pos preset activation missing'],
  [read('products/tablet/app/components/pos/pos-screen.tsx').includes('data-prisma-light-operational="00Q"'), '00Q workspace hook missing'],
  [read('products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css').includes('PRISMA_TABLET_POS_LIGHT_OPERATIONAL_00Q'), 'shell css marker missing'],
  [read('products/tablet/app/components/pos/pos.module.css').includes('--prisma-light-brand-primary'), 'pos css does not consume light tokens']
];
for (const [ok,msg] of checks) if(!ok) failures.push(msg);
if (failures.length) { console.error('BLOCKED PRISMA_TABLET_POS_LIGHT_OPERATIONAL_00Q'); for(const f of failures) console.error(`- ${f}`); process.exit(1); }
console.log('READY PRISMA_TABLET_POS_LIGHT_OPERATIONAL_00Q');
