#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const enginePath = path.join(root, 'src', 'lib', 'pos', 'cart-engine.ts');
const screenPath = path.join(root, 'components', 'pos', 'pos-screen.tsx');
const paymentFlowPath = path.join(root, 'src', 'lib', 'pos', 'payment-flow.ts');

function fail(message) {
  console.error(`[PRISMA TABLET CART ENGINE V02 FAIL] ${message}`);
  process.exit(1);
}

for (const p of [enginePath, screenPath, paymentFlowPath]) {
  if (!fs.existsSync(p)) fail(`missing file ${path.relative(root, p)}`);
}

const engine = fs.readFileSync(enginePath, 'utf8');
const screen = fs.readFileSync(screenPath, 'utf8');
const payment = fs.readFileSync(paymentFlowPath, 'utf8');

const required = [
  'warning?: string',
  'export type CheckoutPayloadInput',
  'export type CheckoutPayload',
  'function normalizeCheckoutPayloadInput(input: CartLine[] | CheckoutPayloadInput)',
  'export function buildCheckoutPayload(input: CartLine[] | CheckoutPayloadInput): CheckoutPayload',
  'Array.isArray(input)',
  'normalized.terminalId ?? "terminal_tablet_local_01"',
  'export function calculateCartTotalCents',
  'export function calculateCartTotalQty',
  'export function getCartLineStockSignal',
  'export function validateCartForCheckout'
];
for (const marker of required) {
  if (!engine.includes(marker)) fail(`cart-engine missing marker: ${marker}`);
}

if (screen.includes('result.warning') && !engine.includes('warning?: string')) {
  fail('pos-screen consumes result.warning but CartMutationResult does not expose warning');
}

if (payment.includes('buildCheckoutPayload(input.lines)') && !engine.includes('CartLine[] | CheckoutPayloadInput')) {
  fail('payment-flow uses legacy buildCheckoutPayload(lines), but engine is not backward compatible');
}

if (/export function buildCheckoutPayload\(input:\s*\{\s*lines:/s.test(engine)) {
  fail('buildCheckoutPayload is still object-only; legacy array call will break typecheck');
}

console.log('OK PRISMA_TABLET_CART_ENGINE_EXPORTS_TYPECHECK_260503_v02 verified warning + legacy checkout payload compatibility');
