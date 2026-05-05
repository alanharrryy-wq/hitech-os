#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const checks = [
  ['products/tablet/app/src/lib/pos/shift-flow.ts', 'ensureLocalShiftOpenForSale'],
  ['products/tablet/app/src/lib/pos/shift-flow.ts', '/api/pos/shift/open'],
  ['products/tablet/app/src/lib/pos/payment-flow.ts', 'SHIFT_NOT_OPEN'],
  ['products/tablet/app/src/lib/pos/payment-flow.ts', 'ensureLocalShiftOpenForSale'],
  ['products/tablet/app/src/lib/pos/pos-visible-errors.ts', 'No había caja abierta'],
  ['products/tablet/app/components/pos/pos-payment-panel.tsx', 'friendlyPosError'],
  ['products/tablet/app/components/pos/pos-payment-panel.tsx', 'visibleError']
];
const failures=[];
for (const [rel, needle] of checks) {
  const full = path.join(root, rel);
  if (!fs.existsSync(full)) { failures.push(`missing ${rel}`); continue; }
  if (!fs.readFileSync(full, 'utf8').includes(needle)) failures.push(`missing ${needle} in ${rel}`);
}
if (failures.length) { console.error('BLOCKED PRISMA_TABLET_POS_CHECKOUT_SHIFT_AUTOFIX_00S'); failures.forEach(f=>console.error(`- ${f}`)); process.exit(1); }
console.log('READY PRISMA_TABLET_POS_CHECKOUT_SHIFT_AUTOFIX_00S');
