#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const appRoot = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
function read(rel) { return fs.readFileSync(path.join(appRoot, rel), 'utf8'); }
function has(rel, needle) { return read(rel).includes(needle); }

const failures = [];
const paymentFlow = read('src/lib/pos/payment-flow.ts');
const shiftFlow = read('src/lib/pos/shift-flow.ts');

if (paymentFlow.includes('ensureLocalShiftOpenForSale')) failures.push('payment-flow.ts must not import or call ensureLocalShiftOpenForSale');
if (paymentFlow.includes('apiErrorCode(error) !== "SHIFT_NOT_OPEN"')) failures.push('payment-flow.ts still catches SHIFT_NOT_OPEN to retry sale');
if (shiftFlow.includes('/api/pos/shift/open')) failures.push('shift-flow.ts must not open /api/pos/shift/open from sale flow');
if (!has('src/lib/pos/pos-visible-errors.ts', 'Caja cerrada')) failures.push('SHIFT_NOT_OPEN visible copy must say Caja cerrada');
if (!has('src/server/pos-engine/repository.prisma.ts', 'PosEngineError("SHIFT_NOT_OPEN"')) failures.push('backend SHIFT_NOT_OPEN guard is missing');

if (failures.length) {
  console.error('BLOCKED PRISMA_TABLET_POS_CHECKOUT_NO_SHIFT_AUTOFIX_00S');
  failures.forEach((failure) => console.error(`- ${failure}`));
  process.exit(1);
}

console.log('READY PRISMA_TABLET_POS_CHECKOUT_NO_SHIFT_AUTOFIX_00S');
